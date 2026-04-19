from django.urls import path
from apps.problem.views import (
    ProblemListView,
    ProblemCreateView,
    ProblemDetailView,
    TagListView,
    TagCreateView
)
from apps.problem.submission_views import (
    SubmitCodeView,
    SubmissionListView,
    SubmissionDetailView
)
from apps.problem.testcase_views import (
    TestCaseUploadView,
    TestCaseListView,
    TestCaseDeleteView
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
    
    # 测试用例相关接口
    path('problems/<str:problem_id>/testcases/', TestCaseListView.as_view(), name='testcase-list'),
    path('problems/<str:problem_id>/testcases/upload/', TestCaseUploadView.as_view(), name='testcase-upload'),
    path('problems/<str:problem_id>/testcases/delete/', TestCaseDeleteView.as_view(), name='testcase-delete'),
    
    # 提交相关接口
    path('submissions/', SubmissionListView.as_view(), name='submission-list'),
    path('submissions/submit/', SubmitCodeView.as_view(), name='submit-code'),
    path('submissions/<int:submission_id>/', SubmissionDetailView.as_view(), name='submission-detail'),
]
