"""
HydroJudge API 客户端
负责与评测适配器通信
"""
import requests
import json
import zipfile
from django.conf import settings
from .adapter import judge_adapter


class HydroJudgeClient:
    """
    HydroJudge 评测客户端
    
    使用示例：
        client = HydroJudgeClient()
        result = client.judge(submission)
    """
    
    def __init__(self):
        # 不使用 HTTP，直接调用 adapter
        pass
    
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
            problem = submission.problem
            
            # 获取测试用例
            test_cases_data = self._get_test_cases(problem)
            
            if not test_cases_data:
                return {
                    'status': 'error',
                    'error': 'No test cases found'
                }
            
            # 准备测试用例数据
            test_cases = []
            for tc in test_cases_data:
                try:
                    with open(tc['input'], 'r', errors='ignore') as f:
                        input_content = f.read()
                    with open(tc['output'], 'r', errors='ignore') as f:
                        output_content = f.read()
                    test_cases.append({
                        'input': input_content,
                        'output': output_content
                    })
                except Exception as e:
                    return {
                        'status': 'error',
                        'error': f'Failed to read test case file: {str(e)}'
                    }
            
            # 调用评测适配器
            result = judge_adapter.judge(
                code=submission.code,
                language=submission.language,
                test_cases=test_cases,
                time_limit=problem.time_limit,
                memory_limit=problem.memory_limit
            )
            
            return result
        
        except Exception as e:
            import traceback
            return {
                'status': 'error',
                'error': f'{str(e)}\n{traceback.format_exc()}'
            }
    
    def _get_test_cases(self, problem):
        """
        获取题目的测试用例
        
        Args:
            problem: Problem 模型实例
            
        Returns:
            list: 测试用例列表（包含文件路径）
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
                
                # 测试数据在testdata目录（标准格式）
                tests_dir = Path(temp_dir) / 'testdata'
                
                # 查找所有.in文件
                for input_file in sorted(tests_dir.glob('*.in')):
                    case_id = int(input_file.stem)
                    output_file = tests_dir / f'{case_id}.out'
                    
                    if output_file.exists():
                        test_cases.append({
                            'id': case_id,
                            'input': str(input_file),
                            'output': str(output_file),
                            'score': 10,
                        })
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e
        
        return test_cases
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
