"""
提交相关视图
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.problem.models import Submission, Problem
from apps.problem.serializers import (
    SubmitCodeSerializer,
    SubmissionListSerializer,
    SubmissionDetailSerializer
)
from apps.judge.tasks import judge_submission_task


class SubmitCodeView(APIView):
    """
    提交代码接口
    POST /api/submissions/submit/ - 提交代码进行评测
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = SubmitCodeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # 创建提交记录
            submission = serializer.save()
            
            # 异步执行评测任务
            judge_submission_task.delay(submission.id)
            
            return Response({
                'message': '提交成功，正在评测',
                'submission_id': submission.id,
                'status': '等待评测'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'message': '提交失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class SubmissionListView(generics.ListAPIView):
    """
    提交列表接口
    GET /api/submissions/ - 获取提交列表（支持过滤）
    """
    serializer_class = SubmissionListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Submission.objects.select_related('problem', 'user').all()
        
        # 按题目过滤
        problem_id = self.request.query_params.get('problem_id', None)
        if problem_id:
            queryset = queryset.filter(problem__problem_id=problem_id)
        
        # 按用户过滤
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        
        # 按结果过滤
        result = self.request.query_params.get('result', None)
        if result:
            queryset = queryset.filter(result=result)
        
        # 只显示当前用户的提交（可选，管理员可以看到所有）
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset.order_by('-submit_time')


class SubmissionDetailView(APIView):
    """
    提交详情接口
    GET /api/submissions/<id>/ - 获取提交详情
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, submission_id):
        submission = get_object_or_404(
            Submission.objects.select_related('problem', 'user'),
            id=submission_id
        )
        
        # 权限检查：只能查看自己的提交（管理员除外）
        if submission.user != request.user and not request.user.is_staff:
            return Response({
                'message': '无权限查看此提交'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SubmissionDetailSerializer(submission)
        return Response(serializer.data)
