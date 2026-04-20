"""
Celery 配置
"""
import os
from celery import Celery

# 设置 Django 默认设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings_production')

# 创建 Celery 应用，直接指定 Redis broker
app = Celery('ZJOJ', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# 从 Django settings 中读取配置，使用 CELERY_ 前缀
app.config_from_object('django.conf:settings', namespace='CELERY')

# 确保使用 Redis（覆盖可能的默认配置）
if not app.conf.broker_url.startswith('redis://'):
    app.conf.broker_url = 'redis://localhost:6379/0'
if not app.conf.result_backend.startswith('redis://'):
    app.conf.result_backend = 'redis://localhost:6379/0'

# 自动发现所有 app 中的 tasks.py
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """测试任务"""
    print(f'Request: {self.request!r}')
