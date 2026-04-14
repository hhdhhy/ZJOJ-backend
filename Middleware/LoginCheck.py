from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import exceptions
from rest_framework.status import HTTP_403_FORBIDDEN

from ZJOJ import settings
from rest_framework.authentication import get_authorization_header
from django.utils.translation import gettext_lazy as _
import jwt

class LoginCheckMiddleware(MiddlewareMixin):
    """
    JWT登录验证中间件
    注意：实际的认证由DRF的JWTAuthentication类处理
    这个中间件主要用于豁免某些路径的认证检查
    """
    # 不需要JWT验证的路径
    EXEMPT_PATHS = [
        '/auth/login/',
        '/auth/register/',
        '/admin/',
    ]
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # 检查是否为豁免路径（支持前缀匹配）
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return None
        
        # 其他路径交给DRF的认证类处理
        return None