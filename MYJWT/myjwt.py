import binascii
import time
import jwt
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from ZJOJ import settings
from django.utils.translation import gettext_lazy as _

# TOKEN有效期（14天）
TOKEN_EXPIRATION_SECONDS = 60 * 24 * 14

def get_token(user):
    exp_time = time.time() + TOKEN_EXPIRATION_SECONDS
    return jwt.encode({"userid": user.uid, "exp": exp_time}, settings.SECRET_KEY, algorithm="HS256")

class JWTAuthentication(BaseAuthentication):
    """
    JWT authentication.
    """
    www_authenticate_realm = 'api'
    JWT_ALGORITHM = 'HS256'
    JWT_PREFIX = b'jwt'
    def authenticate(self, request):
        """
        Returns a `User` if a correct JWT token have been supplied.
        Otherwise returns `None`.
        """


        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.JWT_PREFIX:
            return None

        if len(auth) == 1:
            msg = _('Invalid JWT header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid JWT header. Credentials string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            # 添加leeway参数和binascii异常处理
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
            userid = jwt_decoded.get("userid")

            if userid is None:
                raise exceptions.AuthenticationFailed('Invalid token payload.')

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.InvalidSignatureError:
            raise exceptions.AuthenticationFailed('Invalid token signature.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token.')
        except binascii.Error:
            raise exceptions.AuthenticationFailed('Invalid token format.')

        return self.authenticate_credentials(userid, request)

    @staticmethod
    def authenticate_credentials(userid, request=None):
        """
        Authenticate the userid against user model
        with optional request for context.
        """
        try:
            # ShortUUIDField不需要转换为整数
            pass
        except (ValueError, TypeError):
            raise exceptions.AuthenticationFailed('Invalid user ID in token.')

        try:
            user = get_user_model().objects.get(uid=userid)
        except get_user_model().DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found.')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return user, None

    def authenticate_header(self, request):
        return 'JWT realm="%s"' % self.www_authenticate_realm