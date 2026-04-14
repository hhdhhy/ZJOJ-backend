from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import exceptions
from rest_framework.status import HTTP_403_FORBIDDEN

from ZJOJ import settings
from rest_framework.authentication import get_authorization_header
from django.utils.translation import gettext_lazy as _
import jwt

class LoginCheckMiddleware(MiddlewareMixin):
    keyword = 'JWT'
    JWT_ALGORITHM = 'HS256'
    JWT_PREFIX = b'jwt'
    # 不需要JWT验证的路径
    EXEMPT_PATHS = ['/auth/login/']
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # 检查是否为豁免路径（支持前缀匹配）
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return None
        try:
            auth = get_authorization_header(request).split()

            if not auth or auth[0].lower() != self.JWT_PREFIX:
                raise exceptions.ValidationError("请传入JWT!")

            if len(auth) == 1:
                msg = _('Invalid JWT header. No credentials provided.')
                raise exceptions.AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = _('Invalid JWT header. Credentials string should not contain spaces.')
                raise exceptions.AuthenticationFailed(msg)

            try:
                # 添加leeway参数容忍时间偏差
                jwt_decoded = jwt.decode(
                    auth[1], 
                    settings.SECRET_KEY, 
                    algorithms=[self.JWT_ALGORITHM], 
                    options={
                        "verify_signature": True,
                        "require": ["exp", "userid"]
                    }, 
                    leeway=10
                )
                # userid已通过require选项验证，直接获取
                userid = jwt_decoded.get("userid")

            except jwt.ExpiredSignatureError:
                raise exceptions.AuthenticationFailed('Token has expired.')
            except jwt.InvalidSignatureError:
                raise exceptions.AuthenticationFailed('Invalid token signature.')
            except jwt.InvalidTokenError:
                raise exceptions.AuthenticationFailed('Invalid token.')

        except (exceptions.APIException, Exception):
            return JsonResponse(data={"detail":"请登录!"},status=HTTP_403_FORBIDDEN)