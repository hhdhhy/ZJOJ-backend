"""
MYJWT - JWT 认证模块
提供 JWT Token 生成和验证功能
"""
from .authentication import get_token, JWTAuthentication

__all__ = ['get_token', 'JWTAuthentication']