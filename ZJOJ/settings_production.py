"""
ZJOJ 生产环境配置
在服务器上使用时，设置环境变量: export DJANGO_SETTINGS_MODULE=ZJOJ.settings_production
"""

from .settings import *
import os

# ==================== 安全配置 ====================
DEBUG = False

# 生成安全的SECRET_KEY（首次部署时需要手动设置）
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'CHANGE-THIS-IN-PRODUCTION')

# 允许的主机
ALLOWED_HOSTS = [
    '101.35.233.33',
    'localhost',
    '127.0.0.1',
]

# ==================== 数据库配置 ====================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "zjoj_db",
        "USER": "zjoj_user",
        "PASSWORD": "ZjoJ@2026!Secure",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}

# ==================== 静态文件配置 ====================
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# 媒体文件
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# ==================== 安全增强 ====================
# HTTPS重定向（如果启用HTTPS）
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# HSTS
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# XSS保护
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Clickjacking保护
X_FRAME_OPTIONS = 'DENY'

# ==================== CORS配置 ====================
# 生产环境应该限制允许的源
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://101.35.233.33",
    "https://yourdomain.com",  # 如果有域名
]

# ==================== 日志配置 ====================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/zjoj/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# ==================== AI助手配置 ====================
# 修改缓存路径为Linux路径
EMBEDDING_CACHE_DIR = '/home/ubuntu/ai_models/cache'
CHROMA_DB_PATH = '/home/ubuntu/ai_data/chroma_db'

# HydroJudge配置
HYDRO_JUDGE_URL = 'http://localhost:5050'
HYDRO_JUDGE_TIMEOUT = 30

# ==================== Celery配置 ====================
# 生产环境建议使用Redis或RabbitMQ
# CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
