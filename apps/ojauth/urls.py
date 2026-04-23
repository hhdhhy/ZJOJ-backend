from django.urls import path
from apps.ojauth.views import (
    LoginView,
    RegisterView,
    UserProfileView,
    ChangePasswordView,
    ResetPasswordView,
    ClassListView,
    ClassDetailView,
    ClassMemberView
)

app_name = "ojauth"
urlpatterns = [
    # 认证接口
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    
    # 用户信息接口
    path('user/profile/', UserProfileView.as_view(), name="user-profile"),
    
    # 密码管理接口
    path('password/change/', ChangePasswordView.as_view(), name="change-password"),
    path('password/reset/', ResetPasswordView.as_view(), name="reset-password"),
    
    # 班级管理接口
    path('classes/', ClassListView.as_view(), name="class-list"),
    path('classes/<int:class_id>/', ClassDetailView.as_view(), name="class-detail"),
    path('classes/<int:class_id>/members/', ClassMemberView.as_view(), name="class-member"),
]
