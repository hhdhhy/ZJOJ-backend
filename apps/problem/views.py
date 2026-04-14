from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.problem.models import Problem, Tag
from apps.problem.serializers import (
    ProblemListSerializer,
    ProblemDetailSerializer,
    CreateProblemSerializer,
    TagSerializer
)


class ProblemListView(generics.ListAPIView):
    """
    题目列表接口
    GET /api/problems/ - 获取题目列表（支持搜索和过滤）
    """
    serializer_class = ProblemListSerializer
    permission_classes = [IsAuthenticated]  # 需要登录
    
    def get_queryset(self):
        queryset = Problem.objects.all().order_by('-upload_time')
        
        # 按标题搜索
        title = self.request.query_params.get('title', None)
        if title:
            queryset = queryset.filter(title__icontains=title)
        
        # 按标签过滤
        tag_id = self.request.query_params.get('tag_id', None)
        if tag_id:
            queryset = queryset.filter(tag__id=tag_id)
        
        # 按创建者过滤
        creator = self.request.query_params.get('creator', None)
        if creator:
            queryset = queryset.filter(creator__username=creator)
        
        return queryset


class ProblemCreateView(APIView):
    """
    创建题目接口
    POST /api/problems/create/ - 上传新题目
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CreateProblemSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            problem = serializer.save()
            response_serializer = ProblemDetailSerializer(problem)
            return Response({
                'message': '题目创建成功',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'message': '创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProblemDetailView(APIView):
    """
    题目详情接口
    GET /api/problems/<problem_id>/ - 获取题目详情
    PUT/PATCH /api/problems/<problem_id>/ - 更新题目
    DELETE /api/problems/<problem_id>/ - 删除题目
    """
    permission_classes = [IsAuthenticated]  # 需要登录
    
    def get_object(self, problem_id):
        return get_object_or_404(Problem, problem_id=problem_id)
    
    def get(self, request, problem_id):
        """获取题目详情"""
        problem = self.get_object(problem_id)
        serializer = ProblemDetailSerializer(problem)
        return Response(serializer.data)
    
    def put(self, request, problem_id):
        """更新题目（仅创建者可操作）- 完整更新"""
        problem = self.get_object(problem_id)
        
        # 权限检查：只有创建者可以修改
        if problem.creator != request.user:
            return Response({
                'message': '无权限修改此题目'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProblemDetailSerializer(
            problem,
            data=request.data,
            partial=False  # 需要完整数据
        )
        
        if serializer.is_valid():
            updated_problem = serializer.save()
            response_serializer = ProblemDetailSerializer(updated_problem)
            return Response({
                'message': '题目更新成功',
                'data': response_serializer.data
            })
        
        return Response({
            'message': '更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, problem_id):
        """部分更新题目（仅创建者可操作）"""
        problem = self.get_object(problem_id)
        
        # 权限检查：只有创建者可以修改
        if problem.creator != request.user:
            return Response({
                'message': '无权限修改此题目'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProblemDetailSerializer(
            problem,
            data=request.data,
            partial=True  # 支持部分更新
        )
        
        if serializer.is_valid():
            updated_problem = serializer.save()
            response_serializer = ProblemDetailSerializer(updated_problem)
            return Response({
                'message': '题目更新成功',
                'data': response_serializer.data
            })
        
        return Response({
            'message': '更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, problem_id):
        """删除题目（仅创建者可操作）"""
        problem = self.get_object(problem_id)
        
        # 权限检查：只有创建者可以删除
        if problem.creator != request.user:
            return Response({
                'message': '无权限删除此题目'
            }, status=status.HTTP_403_FORBIDDEN)
        
        problem.delete()
        return Response({
            'message': '题目删除成功'
        }, status=status.HTTP_204_NO_CONTENT)


class TagListView(generics.ListAPIView):
    """
    标签列表接口
    GET /api/problems/tags/ - 获取所有标签
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]  # 需要登录


class TagCreateView(APIView):
    """
    创建标签接口
    POST /api/problems/tags/create/ - 创建新标签
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        name = request.data.get('name')
        
        if not name:
            return Response({
                'message': '标签名称不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查标签是否已存在
        if Tag.objects.filter(name=name).exists():
            return Response({
                'message': '该标签已存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tag = Tag.objects.create(name=name)
        serializer = TagSerializer(tag)
        
        return Response({
            'message': '标签创建成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
