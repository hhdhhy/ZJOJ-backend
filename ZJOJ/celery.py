"""
Celery 配置
"""
import os
from celery import Celery

# 设置 Django 默认设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')

# 创建 Celery 应用
app = Celery('ZJOJ')

# 从 Django settings 中读取配置，使用 CELERY_ 前缀
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有 app 中的 tasks.py
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """测试任务"""
    print(f'Request: {self.request!r}')
