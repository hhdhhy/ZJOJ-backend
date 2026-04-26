"""
评测任务处理器
负责异步执行评测任务并更新数据库
"""
import logging
from datetime import datetime
from django.db import transaction
from apps.problem.models import Submission, TestCaseResult
from apps.judge.gojudge_client import GoJudgeClient

logger = logging.getLogger(__name__)


class JudgeTaskProcessor:
    """
    评测任务处理器
    
    使用示例：
        processor = JudgeTaskProcessor()
        processor.process(submission)
    """
    
    def __init__(self):
        self.client = GoJudgeClient()
    
    def process(self, submission_id):
        """
        处理评测任务
        
        Args:
            submission_id: 提交记录ID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 获取提交记录
            submission = Submission.objects.select_related('problem').get(id=submission_id)
            
            # 更新状态为评测中
            self._update_status(submission, status=1)
            
            logger.info(f'开始评测试卷 #{submission_id}')
            
            # 调用 go-judge 进行评测
            result = self.client.judge(submission)
            
            if result['status'] == 'success':
                # 评测成功，保存结果
                self._save_result(submission, result)
                logger.info(f'评测试卷 #{submission_id} 完成: {result["result"]}')
                return True
            else:
                # 评测失败
                error_msg = result.get('error', '未知错误')
                logger.error(f'评测试卷 #{submission_id} 失败: {error_msg}')
                self._mark_as_error(submission, error_msg)
                return False
        
        except Submission.DoesNotExist:
            logger.error(f'提交记录 #{submission_id} 不存在')
            return False
        except Exception as e:
            logger.error(f'处理评测试卷 #{submission_id} 时发生异常: {str(e)}', exc_info=True)
            try:
                submission = Submission.objects.get(id=submission_id)
                self._mark_as_error(submission, str(e))
            except:
                pass
            return False
    
    def _update_status(self, submission, status):
        """
        更新提交状态
        
        Args:
            submission: Submission 实例
            status: 状态码
        """
        submission.status = status
        submission.save(update_fields=['status'])
    
    def _save_result(self, submission, result):
        """
        保存评测结果
        
        Args:
            submission: Submission 实例
            result: 评测结果字典
        """
        with transaction.atomic():
            # 更新提交记录
            submission.status = 2  # 已完成
            submission.result = result['result']
            submission.score = result['score']
            submission.execution_time = result['time']
            submission.memory_usage = result['memory']
            submission.judge_time = datetime.now()
            submission.save()
            
            # 删除旧的测试点结果（如果有）
            submission.test_case_results.all().delete()
            
            # 保存每个测试点的详细结果
            for idx, tc_data in enumerate(result.get('test_cases', [])):
                TestCaseResult.objects.create(
                    submission=submission,
                    test_case_id=tc_data.get('id', idx + 1),  # 使用索引+1作为默认值
                    status=tc_data.get('status', 'SE'),
                    execution_time=tc_data.get('time', 0),
                    memory_usage=tc_data.get('memory', 0),
                    score=tc_data.get('score', 0),
                    message=tc_data.get('error', '') or tc_data.get('message', ''),
                )
    
    def _mark_as_error(self, submission, error_message):
        """
        标记为系统错误
        
        Args:
            submission: Submission 实例
            error_message: 错误信息
        """
        submission.status = 4  # 系统错误
        submission.result = 'SE'
        submission.judge_time = datetime.now()
        submission.save(update_fields=['status', 'result', 'judge_time'])
        
        # 保存错误信息到第一个测试点结果
        TestCaseResult.objects.create(
            submission=submission,
            test_case_id=0,
            status='SE',
            execution_time=0,
            memory_usage=0,
            score=0,
            message=f'系统错误: {error_message}',
        )
