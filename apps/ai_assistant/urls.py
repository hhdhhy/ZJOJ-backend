"""
AI助手 URL 路由
"""
from django.urls import path
from .views import AIChatView, ChatHistoryView, UsageStatsView, ClearHistoryView

app_name = 'ai_assistant'

urlpatterns = [
    # AI 智能问答
    path('chat/', AIChatView.as_view(), name='chat'),
    
    # 对话历史
    path('history/', ChatHistoryView.as_view(), name='history'),
    
    # 使用情况统计
    path('usage/', UsageStatsView.as_view(), name='usage'),
    
    # 清空历史
    path('history/clear/', ClearHistoryView.as_view(), name='clear_history'),
]
