from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import os
import zipfile
from pathlib import Path
from django.conf import settings

from apps.problem.models import Problem


class TestCaseUploadView(APIView):
    """
    测试用例上传接口
    POST /api/problems/<problem_id>/testcases/upload/ - 上传测试用例（ZIP文件）
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, problem_id):
        """上传测试用例ZIP文件"""
        problem = get_object_or_404(Problem, problem_id=problem_id)
        
        # 权限检查：只有创建者可以上传测试用例
        if problem.creator != request.user:
            return Response({
                'code': 403,
                'message': '无权限操作此题目'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 检查是否有文件
        if 'file' not in request.FILES:
            return Response({
                'code': 400,
                'message': '请上传ZIP文件'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        zip_file = request.FILES['file']
        
        # 验证文件类型
        if not zip_file.name.endswith('.zip'):
            return Response({
                'code': 400,
                'message': '只支持ZIP格式文件'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 创建测试用例目录
            tests_dir = Path(settings.MEDIA_ROOT) / 'problems' / problem_id / 'tests'
            tests_dir.mkdir(parents=True, exist_ok=True)
            
            # 清空旧的测试用例
            for old_file in tests_dir.glob('*'):
                if old_file.is_file():
                    old_file.unlink()
            
            # 解压ZIP文件
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # 检查ZIP内容
                file_list = zip_ref.namelist()
                
                # 验证ZIP结构：应该包含 .in 和 .out 文件
                input_files = [f for f in file_list if f.endswith('.in')]
                output_files = [f for f in file_list if f.endswith('.out')]
                
                if not input_files:
                    return Response({
                        'code': 400,
                        'message': 'ZIP文件中没有找到.in输入文件'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if len(input_files) != len(output_files):
                    return Response({
                        'code': 400,
                        'message': f'输入文件({len(input_files)}个)和输出文件({len(output_files)}个)数量不匹配'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 解压到目标目录
                zip_ref.extractall(tests_dir)
            
            # 验证解压后的文件
            extracted_inputs = sorted([f.stem for f in tests_dir.glob('*.in')])
            extracted_outputs = sorted([f.stem for f in tests_dir.glob('*.out')])
            
            if extracted_inputs != extracted_outputs:
                # 清理已解压的文件
                for f in tests_dir.glob('*'):
                    if f.is_file():
                        f.unlink()
                
                return Response({
                    'code': 400,
                    'message': '输入文件和输出文件的编号不匹配，请确保每个.in文件都有对应的.out文件'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            test_case_count = len(extracted_inputs)
            
            return Response({
                'code': 200,
                'message': f'测试用例上传成功',
                'data': {
                    'problem_id': problem_id,
                    'test_case_count': test_case_count,
                    'test_cases': [
                        {'id': int(stem), 'input': f'{stem}.in', 'output': f'{stem}.out'}
                        for stem in extracted_inputs
                    ]
                }
            })
        
        except zipfile.BadZipFile:
            return Response({
                'code': 400,
                'message': '无效的ZIP文件'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'上传失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestCaseListView(APIView):
    """
    测试用例列表接口
    GET /api/problems/<problem_id>/testcases/ - 获取测试用例列表
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, problem_id):
        """获取测试用例列表"""
        problem = get_object_or_404(Problem, problem_id=problem_id)
        
        tests_dir = Path(settings.MEDIA_ROOT) / 'problems' / problem_id / 'tests'
        
        if not tests_dir.exists():
            return Response({
                'code': 200,
                'message': '暂无测试用例',
                'data': {
                    'problem_id': problem_id,
                    'test_case_count': 0,
                    'test_cases': []
                }
            })
        
        # 获取所有测试用例
        input_files = sorted([f for f in tests_dir.glob('*.in')])
        output_files = sorted([f for f in tests_dir.glob('*.out')])
        
        test_cases = []
        for input_file in input_files:
            case_id = input_file.stem
            output_file = tests_dir / f'{case_id}.out'
            
            if output_file.exists():
                # 获取文件大小
                input_size = input_file.stat().st_size
                output_size = output_file.stat().st_size
                
                test_cases.append({
                    'id': int(case_id),
                    'input': f'{case_id}.in',
                    'output': f'{case_id}.out',
                    'input_size': f'{input_size / 1024:.2f} KB',
                    'output_size': f'{output_size / 1024:.2f} KB'
                })
        
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'problem_id': problem_id,
                'test_case_count': len(test_cases),
                'test_cases': test_cases
            }
        })


class TestCaseDeleteView(APIView):
    """
    删除测试用例接口
    DELETE /api/problems/<problem_id>/testcases/ - 删除所有测试用例
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, problem_id):
        """删除所有测试用例"""
        problem = get_object_or_404(Problem, problem_id=problem_id)
        
        # 权限检查：只有创建者可以删除
        if problem.creator != request.user:
            return Response({
                'code': 403,
                'message': '无权限操作此题目'
            }, status=status.HTTP_403_FORBIDDEN)
        
        tests_dir = Path(settings.MEDIA_ROOT) / 'problems' / problem_id / 'tests'
        
        if tests_dir.exists():
            # 删除所有文件
            for file in tests_dir.glob('*'):
                if file.is_file():
                    file.unlink()
            # 删除目录
            tests_dir.rmdir()
        
        return Response({
            'code': 200,
            'message': '测试用例已删除'
        })
