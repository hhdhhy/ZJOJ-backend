"""
权限中间件 - 实现教练/学生权限隔离
"""
from functools import wraps
from rest_framework.exceptions import PermissionDenied


def coach_required(view_func):
    """
    教练权限装饰器
    只有教练或管理员可以访问
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("请先登录")
        
        if not (request.user.is_coach() or request.user.is_admin_user()):
            raise PermissionDenied("需要教练权限")
        
        return view_func(self, request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    """
    学生权限装饰器
    只有学生可以访问
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("请先登录")
        
        if not request.user.is_student():
            raise PermissionDenied("需要学生权限")
        
        return view_func(self, request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """
    管理员权限装饰器
    只有管理员可以访问
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("请先登录")
        
        if not request.user.is_admin_user():
            raise PermissionDenied("需要管理员权限")
        
        return view_func(self, request, *args, **kwargs)
    return wrapper


class CoachPermissionMixin:
    """
    教练权限混入类
    用于ViewSet或APIView
    """
    def check_coach_permission(self, user):
        """检查用户是否有教练权限"""
        if not user.is_authenticated:
            raise PermissionDenied("请先登录")
        
        if not (user.is_coach() or user.is_admin_user()):
            raise PermissionDenied("需要教练权限")


class StudentPermissionMixin:
    """
    学生权限混入类
    """
    def check_student_permission(self, user):
        """检查用户是否是学生"""
        if not user.is_authenticated:
            raise PermissionDenied("请先登录")
        
        if not user.is_student():
            raise PermissionDenied("需要学生权限")
