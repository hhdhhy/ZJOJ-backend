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
            tests_dir = Path(settings.MEDIA_ROOT) / 'problems' / problem_id
            tests_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存ZIP文件（不解压）
            zip_filename = 'testcases.zip'
            zip_path = tests_dir / zip_filename
            
            # 删除旧的ZIP文件
            if zip_path.exists():
                zip_path.unlink()
            
            # 保存新文件
            with open(zip_path, 'wb+') as destination:
                for chunk in zip_file.chunks():
                    destination.write(chunk)
            
            # 验证ZIP文件有效性并获取测试用例信息
            try:
                with zipfile.ZipFile(zip_path, 'r') as test_zip:
                    file_list = test_zip.namelist()
                    
                    # 支持两种格式：
                    # 1. 直接在根目录: 1.in, 1.out
                    # 2. 在testdata目录: testdata/1.in, testdata/1.out
                    
                    # 检查是否有testdata目录
                    has_testdata_dir = any(f.startswith('testdata/') for f in file_list)
                    
                    if has_testdata_dir:
                        # 从testdata目录中查找
                        input_files = [f for f in file_list if f.startswith('testdata/') and f.endswith('.in')]
                        output_files = [f for f in file_list if f.startswith('testdata/') and f.endswith('.out')]
                    else:
                        # 从根目录查找
                        input_files = [f for f in file_list if '/' not in f and f.endswith('.in')]
                        output_files = [f for f in file_list if '/' not in f and f.endswith('.out')]
                    
                    if not input_files:
                        zip_path.unlink()
                        return Response({
                            'code': 400,
                            'message': 'ZIP文件中没有找到.in输入文件'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    if len(input_files) != len(output_files):
                        zip_path.unlink()
                        return Response({
                            'code': 400,
                            'message': f'输入文件({len(input_files)}个)和输出文件({len(output_files)}个)数量不匹配'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    test_case_count = len(input_files)
            except zipfile.BadZipFile:
                zip_path.unlink()
                return Response({
                    'code': 400,
                    'message': '无效的ZIP文件'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'code': 200,
                'message': f'测试用例上传成功',
                'data': {
                    'problem_id': problem_id,
                    'test_case_count': test_case_count,
                    'file_size': f'{zip_path.stat().st_size / 1024:.2f} KB',
                    'filename': zip_filename
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
        """获取测试用例信息"""
        problem = get_object_or_404(Problem, problem_id=problem_id)
        
        zip_path = Path(settings.MEDIA_ROOT) / 'problems' / problem_id / 'testcases.zip'
        
        if not zip_path.exists():
            return Response({
                'code': 200,
                'message': '暂无测试用例',
                'data': {
                    'problem_id': problem_id,
                    'has_testcases': False,
                    'test_case_count': 0
                }
            })
        
        # 读取ZIP文件信息
        try:
            with zipfile.ZipFile(zip_path, 'r') as test_zip:
                file_list = test_zip.namelist()
                
                # 支持两种格式
                has_testdata_dir = any(f.startswith('testdata/') for f in file_list)
                
                if has_testdata_dir:
                    input_files = [f for f in file_list if f.startswith('testdata/') and f.endswith('.in')]
                    output_files = [f for f in file_list if f.startswith('testdata/') and f.endswith('.out')]
                else:
                    input_files = [f for f in file_list if '/' not in f and f.endswith('.in')]
                    output_files = [f for f in file_list if '/' not in f and f.endswith('.out')]
                
                test_cases = []
                for input_file in sorted(input_files):
                    # 提取文件名（不含路径）
                    input_basename = Path(input_file).name
                    case_id = Path(input_file).stem
                    output_file_name = f'{case_id}.out'
                    
                    # 查找对应的output文件
                    if has_testdata_dir:
                        output_file = f'testdata/{output_file_name}'
                    else:
                        output_file = output_file_name
                    
                    if output_file in output_files:
                        # 获取文件大小
                        input_info = test_zip.getinfo(input_file)
                        output_info = test_zip.getinfo(output_file)
                        
                        test_cases.append({
                            'id': int(case_id),
                            'input': input_basename,
                            'output': output_file_name,
                            'input_size': f'{input_info.file_size / 1024:.2f} KB',
                            'output_size': f'{output_info.file_size / 1024:.2f} KB'
                        })
                
                return Response({
                    'code': 200,
                    'message': '获取成功',
                    'data': {
                        'problem_id': problem_id,
                        'has_testcases': True,
                        'test_case_count': len(test_cases),
                        'file_size': f'{zip_path.stat().st_size / 1024:.2f} KB',
                        'test_cases': test_cases
                    }
                })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'读取失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestCaseDeleteView(APIView):
    """
    删除测试用例接口
    DELETE /api/problems/<problem_id>/testcases/ - 删除所有测试用例
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, problem_id):
        """删除测试用例ZIP文件"""
        problem = get_object_or_404(Problem, problem_id=problem_id)
        
        # 权限检查：只有创建者可以删除
        if problem.creator != request.user:
            return Response({
                'code': 403,
                'message': '无权限操作此题目'
            }, status=status.HTTP_403_FORBIDDEN)
        
        zip_path = Path(settings.MEDIA_ROOT) / 'problems' / problem_id / 'testcases.zip'
        
        if zip_path.exists():
            zip_path.unlink()
        
        return Response({
            'code': 200,
            'message': '测试用例已删除'
        })
