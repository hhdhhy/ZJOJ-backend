"""
Judge Adapter - 评测适配器
提供简化的 HTTP API，封装 go-judge 的复杂逻辑
支持多测试点、输出比较、状态判断等功能
"""
from django.conf import settings
import requests
import json
import zipfile
import tempfile
import shutil
from pathlib import Path


class JudgeAdapter:
    """
    评测适配器
    
    功能：
    1. 接收评测请求（代码、语言、测试用例、限制）
    2. 遍历所有测试点
    3. 调用 go-judge 执行
    4. 比较输出并评分
    5. 返回聚合结果
    """
    
    def __init__(self, go_judge_url=None):
        self.go_judge_url = go_judge_url or getattr(settings, 'GO_JUDGE_URL', 'http://localhost:5050')
        self.timeout = getattr(settings, 'GO_JUDGE_TIMEOUT', 60)
    
    def judge(self, code, language, test_cases, time_limit, memory_limit):
        """
        执行评测
        
        Args:
            code: 源代码字符串
            language: 编程语言 (cpp/c/python/java)
            test_cases: 测试用例列表 [{'input': '...', 'output': '...'}]
            time_limit: 时间限制 (ms)
            memory_limit: 内存限制 (MB)
            
        Returns:
            dict: {
                'status': 'success/error',
                'result': 'AC/WA/TLE/MLE/RE/CE',
                'score': 总分 (0-100),
                'time': 最大运行时间 (ms),
                'memory': 最大内存使用 (KB),
                'test_cases': [每个测试点的详细结果]
            }
        """
        if not test_cases:
            return {
                'status': 'error',
                'error': 'No test cases provided'
            }
        
        results = []
        max_time = 0
        max_memory = 0
        total_score = 0
        
        # 遍历所有测试点
        for i, test_case in enumerate(test_cases):
            try:
                # 调用 go-judge
                result = self._run_single_test(
                    code, language, 
                    test_case['input'], 
                    test_case['output'],
                    time_limit, memory_limit
                )
                
                results.append(result)
                
                # 更新最大值
                max_time = max(max_time, result.get('time', 0))
                max_memory = max(max_memory, result.get('memory', 0))
                total_score += result.get('score', 0)
                
            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                print(f"ERROR in test case {i+1}: {str(e)}")
                print(error_traceback)
                results.append({
                    'id': i + 1,
                    'status': 'SE',
                    'score': 0,
                    'time': 0,
                    'memory': 0,
                    'error': f'{str(e)}\n{error_traceback}'
                })
        
        # 确定最终结果（最差的评测状态）
        final_result = self._determine_final_result(results)
        
        return {
            'status': 'success',
            'result': final_result,
            'score': total_score,
            'time': max_time,
            'memory': max_memory,
            'test_cases': results
        }
    
    def _run_single_test(self, code, language, input_data, expected_output, time_limit, memory_limit):
        """
        运行单个测试点
        
        Args:
            code: 源代码
            language: 编程语言
            input_data: 输入数据
            expected_output: 预期输出
            time_limit: 时间限制 (ms)
            memory_limit: 内存限制 (MB)
            
        Returns:
            dict: 测试结果
        """
        # 构建 go-judge 请求（编译 + 运行）
        compile_cmd = self._get_compile_command(language)
        run_cmd = self._get_run_command(language)
        
        cmd_list = []
        
        # 添加编译命令（如果需要）
        if compile_cmd:
            cmd_list.append({
                'args': compile_cmd,
                'env': ['PATH=/usr/bin:/bin', 'HOME=/w'],
                'cpuLimit': 5000000000,  # 编译限时5秒
                'memoryLimit': 536870912,  # 512MB
                'copyIn': {
                    f'main.{self._get_file_extension(language)}': {
                        'content': code  # 直接使用字符串，不要 encode
                    }
                },
            })
        
        # 添加运行命令
        files_config = [
            {'content': input_data},  # stdin
            {'name': 'stdout', 'max': 10485760},  # stdout, 10MB
            {'name': 'stderr', 'max': 10485760}   # stderr, 10MB
        ]
        
        run_command_config = {
            'args': run_cmd,
            'env': ['PATH=/usr/bin:/bin', 'HOME=/w'],
            'files': files_config,
            'cpuLimit': time_limit * 1000000,  # ms -> ns
            'memoryLimit': memory_limit * 1024 * 1024,  # MB -> bytes
            'procLimit': 50,
            'copyOut': ['stdout', 'stderr'],
        }
        
        # 如果不需要编译，添加 copyIn
        if not compile_cmd:
            run_command_config['copyIn'] = {
                f'main.{self._get_file_extension(language)}': {
                    'content': code  # 直接使用字符串，不要 encode
                }
            }
        
        cmd_list.append(run_command_config)
        
        payload = {'cmd': cmd_list}
        
        # 调用 go-judge
        response = requests.post(
            f'{self.go_judge_url}/run',
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"go-judge error: {response.text}")
        
        results = response.json()
        
        # 检查编译是否成功
        if compile_cmd and len(results) > 0:
            compile_result = results[0]
            if compile_result.get('exitStatus', 0) != 0:
                return {
                    'status': 'CE',
                    'score': 0,
                    'time': 0,
                    'memory': 0,
                    'stderr': compile_result.get('files', {}).get('stderr', {}).get('content', 'Compilation failed'),
                }
        
        # 获取运行结果
        result = results[-1]  # 最后一个命令是运行
        
        # 解析结果
        exit_status = result.get('exitStatus', -1)
        time_ns = result.get('time', 0)
        memory_bytes = result.get('memory', 0)
        status_raw = result.get('status', '')
        
        time_ms = time_ns // 1000000  # ns -> ms
        memory_kb = memory_bytes // 1024  # bytes -> KB
        
        # 获取实际输出
        actual_output = ''
        if 'files' in result and 'stdout' in result['files']:
            stdout_data = result['files']['stdout']
            # go-judge 可能返回字符串或字典
            if isinstance(stdout_data, dict):
                actual_output = stdout_data.get('content', '')
            else:
                actual_output = str(stdout_data)
        
        stderr_output = ''
        if 'files' in result and 'stderr' in result['files']:
            stderr_data = result['files']['stderr']
            # go-judge 可能返回字符串或字典
            if isinstance(stderr_data, dict):
                stderr_output = stderr_data.get('content', '')
            else:
                stderr_output = str(stderr_data)
        
        # 判断状态
        status = self._judge_status(status_raw, exit_status, time_ms, memory_kb, time_limit, memory_limit)
        
        # 如果 AC，比较输出
        score = 0
        if status == 'AC':
            if self._compare_output(actual_output, expected_output):
                score = 10
            else:
                status = 'WA'
        
        return {
            'status': status,
            'score': score,
            'time': time_ms,
            'memory': memory_kb,
            'stdout': actual_output[:500],  # 限制长度
            'stderr': stderr_output[:500] if stderr_output else '',
        }
    
    def _judge_status(self, status_raw, exit_status, time_ms, memory_kb, time_limit, memory_limit):
        """
        判断评测状态
        
        优先级：CE > SE > RE > TLE > MLE > WA > AC
        """
        # 1. 检查超时
        if time_ms > time_limit * 1000 or status_raw == 'Time Limit Exceeded':
            return 'TLE'
        
        # 2. 检查超内存
        if memory_kb > memory_limit * 1024 or status_raw == 'Memory Limit Exceeded':
            return 'MLE'
        
        # 3. 检查非零退出码
        if exit_status != 0:
            if exit_status == 127:
                return 'CE'  # 命令未找到（编译失败）
            return 'RE'  # 运行时错误
        
        # 4. 检查 go-judge 的状态
        if status_raw and status_raw not in ['Accepted', '']:
            status_map = {
                'Time Limit Exceeded': 'TLE',
                'Memory Limit Exceeded': 'MLE',
                'Output Limit Exceeded': 'OLE',
                'Nonzero Exit Status': 'RE',
                'Signalled': 'RE',
            }
            return status_map.get(status_raw, 'RE')
        
        # 5. 默认 AC（需要后续比较输出）
        return 'AC'
    
    def _compare_output(self, actual, expected):
        """
        比较输出（规范化空白字符）
        
        规则：
        1. 去除首尾空白
        2. 将所有连续空白字符（空格、制表符、换行等）替换为单个空格
        3. 比较规范化后的字符串
        
        例如：
        - "1  2\n3" 和 "1 2 3" 视为相同
        - "hello   world" 和 "hello world" 视为相同
        """
        import re
        # 将连续空白字符替换为单个空格
        actual_normalized = re.sub(r'\s+', ' ', actual.strip())
        expected_normalized = re.sub(r'\s+', ' ', expected.strip())
        return actual_normalized == expected_normalized
    
    def _determine_final_result(self, test_results):
        """
        根据所有测试点确定最终结果
        
        优先级：CE > SE > RE > TLE > MLE > WA > AC
        """
        priority = ['SE', 'CE', 'RE', 'TLE', 'MLE', 'WA', 'AC']
        
        worst_status = 'AC'
        for result in test_results:
            status = result.get('status', 'SE')
            if priority.index(status) < priority.index(worst_status):
                worst_status = status
        
        return worst_status
    
    def _get_compiler_and_runner_args(self, language):
        """获取编译和运行命令（已废弃，保留兼容）"""
        return self._get_run_command(language)
    
    def _get_compile_command(self, language):
        """获取编译命令（返回 None 表示不需要编译）"""
        commands = {
            'cpp': ['/host-usr/bin/g++', '-std=c++17', '-O2', '-o', '/w/main', '/w/main.cpp'],
            'c': ['/host-usr/bin/gcc', '-std=c11', '-O2', '-o', '/w/main', '/w/main.c'],
            'java': ['/host-usr/bin/javac', '/w/Main.java'],
        }
        return commands.get(language, None)
    
    def _get_run_command(self, language):
        """获取运行命令"""
        commands = {
            'cpp': ['/w/main'],
            'c': ['/w/main'],
            'python': ['/host-usr/bin/python3', '/w/main.py'],
            'python3': ['/host-usr/bin/python3', '/w/main.py'],
            'python2': ['/host-usr/bin/python2', '/w/main.py'],
            'java': ['/host-usr/bin/java', '-cp', '/w', 'Main'],
        }
        return commands.get(language, ['/bin/echo', 'Unsupported language'])
    
    def _get_file_extension(self, language):
        """获取文件扩展名"""
        extensions = {
            'cpp': 'cpp',
            'c': 'c',
            'python': 'py',
            'python3': 'py',
            'python2': 'py',
            'java': 'java',
        }
        return extensions.get(language, 'txt')


# 导出单例
judge_adapter = JudgeAdapter()
