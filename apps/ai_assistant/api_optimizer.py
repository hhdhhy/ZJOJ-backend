"""
AI API 调用优化工具
- 结果缓存（24小时有效期）
- 调用频率限制
- 网络异常重试机制
"""
import time
import hashlib
import json
from functools import wraps
from django.utils import timezone
from datetime import timedelta
from .models import APICache


class APICallOptimizer:
    """API调用优化器"""
    
    CACHE_TTL = 24 * 3600  # 24小时缓存
    
    @staticmethod
    def generate_cache_key(func_name: str, params: dict) -> str:
        """生成缓存键"""
        key_str = f"{func_name}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    @staticmethod
    def get_cached_response(cache_key: str) -> dict | None:
        """获取缓存的响应"""
        try:
            cache = APICache.objects.get(cache_key=cache_key)
            if cache.is_expired:
                cache.delete()
                return None
            return cache.response_data
        except APICache.DoesNotExist:
            return None
    
    @staticmethod
    def cache_response(cache_key: str, response_data: dict):
        """缓存响应数据"""
        expires_at = timezone.now() + timedelta(seconds=APICallOptimizer.CACHE_TTL)
        
        APICache.objects.update_or_create(
            cache_key=cache_key,
            defaults={
                'response_data': response_data,
                'expires_at': expires_at,
            }
        )
    
    @staticmethod
    def clear_expired_cache():
        """清理过期缓存"""
        deleted_count, _ = APICache.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        return deleted_count
    
    @staticmethod
    def retry_on_failure(max_retries=3, delay=1, backoff=2):
        """
        重试装饰器
        :param max_retries: 最大重试次数
        :param delay: 初始延迟（秒）
        :param backoff: 退避倍数
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                current_delay = delay
                
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_retries - 1:
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            raise
                
                raise last_exception
            return wrapper
        return decorator


def cached_api_call(func):
    """
    API调用缓存装饰器
    自动缓存函数返回结果，24小时有效
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 生成缓存键
        params = {
            'args': [str(arg) for arg in args],
            'kwargs': kwargs
        }
        cache_key = APICallOptimizer.generate_cache_key(func.__name__, params)
        
        # 尝试从缓存获取
        cached = APICallOptimizer.get_cached_response(cache_key)
        if cached is not None:
            return cached
        
        # 执行函数
        result = func(*args, **kwargs)
        
        # 缓存结果
        APICallOptimizer.cache_response(cache_key, result)
        
        return result
    return wrapper
