"""
AI助手 URL 路由
"""
from django.urls import path
from .views import (
    AIChatView, 
    ChatHistoryView, 
    UsageStatsView, 
    ClearHistoryView,
    StudentLearningReportView,
    ClassLearningReportView,
    ErrorSolutionView
)

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
    
    # 学情分析
    path('report/student/', StudentLearningReportView.as_view(), name='student-report'),
    path('report/class/<int:class_id>/', ClassLearningReportView.as_view(), name='class-report'),
    
    # 错误解决方案
    path('error-solution/<int:submission_id>/', ErrorSolutionView.as_view(), name='error-solution'),
]
