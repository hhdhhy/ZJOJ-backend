"""
DRF JWT 认证类和 Token 生成工具
"""
import time
import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from ZJOJ import settings
from apps.ojauth.models import OJUser

# TOKEN有效期（14天）
TOKEN_EXPIRATION_SECONDS = 60 * 24 * 14


def get_token(user):
    """
    为用户生成 JWT Token
    :param user: OJUser 实例
    :return: JWT Token 字符串
    """
    exp_time = time.time() + TOKEN_EXPIRATION_SECONDS
    return jwt.encode(
        {"userid": user.uid, "exp": exp_time},
        settings.SECRET_KEY,
        algorithm="HS256"
    )


class JWTAuthentication(BaseAuthentication):
    """
    JWT Token 认证类
    客户端应在 Authorization header 中提供: Bearer <token> 或 jwt <token>
    """
    keywords = ['bearer', 'jwt']  # 支持多种关键词
    algorithm = 'HS256'
    
    def authenticate(self, request):
        """
        尝试验证请求中的JWT token
        返回 (user, token) 元组或 None
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
        
        parts = auth_header.split()
        
        if len(parts) == 0:
            return None
        
        # 支持 Bearer 和 jwt 两种格式
        if parts[0].lower() not in self.keywords:
            return None
        
        if len(parts) != 2:
            raise AuthenticationFailed(
                _('凭证字符串不应包含空格。'),
                code='invalid_header'
            )
        
        token = parts[1]
        
        try:
            # 解码并验证token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "require": ["exp", "userid"]
                },
                leeway=10
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed(
                _('Token已过期。'),
                code='token_expired'
            )
        except jwt.InvalidSignatureError:
            raise AuthenticationFailed(
                _('无效的Token签名。'),
                code='invalid_signature'
            )
        except jwt.InvalidTokenError:
            raise AuthenticationFailed(
                _('无效的Token。'),
                code='invalid_token'
            )
        
        # 从payload中获取userid
        userid = payload.get('userid')
        if not userid:
            raise AuthenticationFailed(
                _('Token中缺少用户ID。'),
                code='invalid_payload'
            )
        
        # 从数据库获取用户
        try:
            user = OJUser.objects.get(uid=userid)
        except OJUser.DoesNotExist:
            raise AuthenticationFailed(
                _('用户不存在。'),
                code='user_not_found'
            )
        
        # 返回(user, token)元组，DRF会自动设置request.user
        return (user, token)
    
    def authenticate_header(self, request):
        """
        返回WWW-Authenticate header的值
        """
        return 'Bearer'
