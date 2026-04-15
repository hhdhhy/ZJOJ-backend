"""
AI助手 API 视图
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .rag_engine import RAGEngine
from .models import ChatHistory, UserProfile
from .serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    ChatHistorySerializer,
    UsageStatsSerializer
)
from .limits import AILimitChecker


class AIChatView(APIView):
    """AI 智能问答"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 1. 检查每日配额
        profile = AILimitChecker.check_daily_quota(request.user)
        
        # 2. 检查频率限制
        AILimitChecker.check_rate_limit(request.user)
        
        # 3. 验证请求
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        question = serializer.validated_data['question']
        top_k = serializer.validated_data.get('top_k', 5)
        use_rag = serializer.validated_data.get('use_rag', True)
        
        try:
            # 4. 调用 RAG 引擎或简单对话
            engine = RAGEngine()
            
            if use_rag:
                result = engine.ask(question, top_k=top_k)
            else:
                result = engine.chat(question)
            
            # 5. 保存对话历史
            chat = ChatHistory.objects.create(
                user=request.user,
                question=question,
                answer=result['answer'],
                sources=result.get('sources', []),
                tokens_used=result['tokens_used']
            )
            
            # 6. 增加使用次数
            AILimitChecker.increment_usage(request.user)
            
            # 7. 修剪历史记录
            AILimitChecker.trim_history(request.user)
            
            # 8. 返回结果
            response_data = {
                'answer': result['answer'],
                'tokens_used': result['tokens_used'],
                'remaining_quota': profile.daily_quota - profile.used_today - 1,
                'chat_id': chat.id
            }
            
            if use_rag and 'sources' in result:
                response_data['sources'] = result['sources']
            
            return Response(response_data)
        
        except Exception as e:
            return Response({
                'error': f'处理失败: {str(e)}'
            }, status=500)


class ChatHistoryView(APIView):
    """获取对话历史"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 获取查询参数
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        # 查询对话历史
        histories = ChatHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')[offset:offset + limit]
        
        serializer = ChatHistorySerializer(histories, many=True)
        
        # 获取总数
        total = ChatHistory.objects.filter(user=request.user).count()
        
        return Response({
            'count': total,
            'results': serializer.data
        })


class UsageStatsView(APIView):
    """获取使用情况统计"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # 重置今日计数
        today = timezone.now().date()
        if profile.last_reset_date != today:
            profile.used_today = 0
            profile.last_reset_date = today
            profile.save()
        
        # 获取历史记录数
        history_count = ChatHistory.objects.filter(user=request.user).count()
        
        return Response({
            'daily_quota': profile.daily_quota,
            'used_today': profile.used_today,
            'remaining': profile.daily_quota - profile.used_today,
            'max_history': profile.max_history,
            'history_count': history_count,
            'reset_time': '明天 00:00'
        })


class ClearHistoryView(APIView):
    """清空对话历史"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        # 删除所有对话历史
        deleted_count, _ = ChatHistory.objects.filter(user=request.user).delete()
        
        return Response({
            'message': f'已清空 {deleted_count} 条对话记录'
        })
