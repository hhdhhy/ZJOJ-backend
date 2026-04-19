"""
HydroJudge API 客户端
负责与 HydroJudge 沙箱服务通信
"""
import requests
import json
import zipfile
from django.conf import settings


class HydroJudgeClient:
    """
    HydroJudge 评测客户端
    
    使用示例：
        client = HydroJudgeClient()
        result = client.judge(submission)
    """
    
    def __init__(self):
        # HydroJudge 服务地址（可配置）
        self.base_url = getattr(settings, 'HYDRO_JUDGE_URL', 'http://localhost:5050')
        self.timeout = getattr(settings, 'HYDRO_JUDGE_TIMEOUT', 30)
    
    def judge(self, submission):
        """
        提交代码进行评测
        
        Args:
            submission: Submission 模型实例
            
        Returns:
            dict: 评测结果
                {
                    'status': 'success' or 'error',
                    'result': 'AC/WA/TLE/MLE/RE/CE',
                    'score': 总分,
                    'time': 总运行时间(ms),
                    'memory': 总内存使用(KB),
                    'test_cases': [测试点详情列表],
                    'error': 错误信息（如果有）
                }
        """
        try:
            # 准备评测数据
            payload = self._prepare_judge_payload(submission)
            
            # 调用 HydroJudge API
            response = requests.post(
                f'{self.base_url}/judge',
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_result(result)
            else:
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
        
        except requests.exceptions.Timeout:
            return {
                'status': 'error',
                'error': '评测超时'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'error',
                'error': '无法连接到评测服务'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _prepare_judge_payload(self, submission):
        """
        准备评测请求数据
        
        Args:
            submission: Submission 模型实例
            
        Returns:
            dict: 评测请求数据
        """
        problem = submission.problem
        
        # 构建测试用例列表
        test_cases = self._get_test_cases(problem)
        
        payload = {
            'submission_id': submission.id,
            'problem_id': problem.problem_id,
            'language': submission.language,
            'code': submission.code,
            'time_limit': problem.time_limit,  # ms
            'memory_limit': problem.memory_limit * 1024,  # KB -> KB (保持单位一致)
            'test_cases': test_cases,
        }
        
        return payload
    
    def _get_test_cases(self, problem):
        """
        获取题目的测试用例
        
        Args:
            problem: Problem 模型实例
            
        Returns:
            list: 测试用例列表
        """
        from pathlib import Path
        import tempfile
        import shutil
        
        # 测试用例ZIP文件路径
        zip_path = Path(f'media/problems/{problem.problem_id}/testcases.zip')
        
        if not zip_path.exists():
            return []
        
        # 创建临时目录解压
        temp_dir = tempfile.mkdtemp()
        test_cases = []
        
        try:
            # 解压ZIP文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                
                # 查找所有.in文件
                tests_dir = Path(temp_dir)
                for input_file in sorted(tests_dir.glob('*.in')):
                    case_id = int(input_file.stem)
                    output_file = tests_dir / f'{case_id}.out'
                    
                    if output_file.exists():
                        test_cases.append({
                            'id': case_id,
                            'input': str(input_file),
                            'output': str(output_file),
                            'score': 10,  # 默认每个测试点10分
                        })
        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        return test_cases
    
    def _parse_result(self, raw_result):
        """
        解析 HydroJudge 返回的结果
        
        Args:
            raw_result: HydroJudge 原始返回数据
            
        Returns:
            dict: 标准化后的评测结果
        """
        # HydroJudge 返回格式可能因版本而异，这里做适配
        try:
            test_cases = raw_result.get('test_cases', [])
            
            # 计算总分和最大时间/内存
            total_score = sum(tc.get('score', 0) for tc in test_cases)
            max_time = max((tc.get('time', 0) for tc in test_cases), default=0)
            max_memory = max((tc.get('memory', 0) for tc in test_cases), default=0)
            
            # 确定最终结果（最差的评测状态）
            final_result = self._determine_final_result(test_cases)
            
            return {
                'status': 'success',
                'result': final_result,
                'score': total_score,
                'time': max_time,
                'memory': max_memory,
                'test_cases': test_cases,
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': f'解析评测结果失败: {str(e)}'
            }
    
    def _determine_final_result(self, test_cases):
        """
        根据所有测试点结果确定最终评测结果
        
        优先级：CE > SE > RE > TLE > MLE > WA > AC
        
        Args:
            test_cases: 测试点结果列表
            
        Returns:
            str: 最终评测结果
        """
        if not test_cases:
            return 'SE'  # System Error
        
        # 检查是否有编译错误或系统错误
        for tc in test_cases:
            status = tc.get('status', '')
            if status in ['CE', 'SE']:
                return status
        
        # 检查是否有运行时错误
        has_re = any(tc.get('status') == 'RE' for tc in test_cases)
        if has_re:
            return 'RE'
        
        # 检查是否有超时
        has_tle = any(tc.get('status') == 'TLE' for tc in test_cases)
        if has_tle:
            return 'TLE'
        
        # 检查是否有超内存
        has_mle = any(tc.get('status') == 'MLE' for tc in test_cases)
        if has_mle:
            return 'MLE'
        
        # 检查是否有答案错误
        has_wa = any(tc.get('status') == 'WA' for tc in test_cases)
        if has_wa:
            return 'WA'
        
        # 全部通过
        return 'AC'
