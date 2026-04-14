from django.urls import path
from apps.problem.views import (
    ProblemListView,
    ProblemCreateView,
    ProblemDetailView,
    TagListView,
    TagCreateView
)

app_name = "problem"

urlpatterns = [
    # 标签相关接口（必须放在动态路由之前）
    path('problems/tags/', TagListView.as_view(), name='tag-list'),
    path('problems/tags/create/', TagCreateView.as_view(), name='tag-create'),
    
    # 题目相关接口
    path('problems/', ProblemListView.as_view(), name='problem-list'),
    path('problems/create/', ProblemCreateView.as_view(), name='problem-create'),
    path('problems/<str:problem_id>/', ProblemDetailView.as_view(), name='problem-detail'),
]
