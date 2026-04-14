"""
Celery 异步任务
"""
from celery import shared_task
import logging
from apps.judge.task_processor import JudgeTaskProcessor

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def judge_submission_task(self, submission_id):
    """
    异步评测试卷任务
    
    Args:
        submission_id: 提交记录ID
        
    Returns:
        dict: 评测结果
    """
    try:
        logger.info(f'开始异步评测试卷 #{submission_id}')
        
        processor = JudgeTaskProcessor()
        success = processor.process(submission_id)
        
        if success:
            logger.info(f'评测试卷 #{submission_id} 成功')
            return {'status': 'success', 'submission_id': submission_id}
        else:
            logger.error(f'评测试卷 #{submission_id} 失败')
            return {'status': 'failed', 'submission_id': submission_id}
    
    except Exception as exc:
        logger.error(f'评测试卷 #{submission_id} 异常: {str(exc)}', exc_info=True)
        # 重试机制
        raise self.retry(exc=exc)
