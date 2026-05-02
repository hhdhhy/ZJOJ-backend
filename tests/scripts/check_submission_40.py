#!/usr/bin/env python3
"""检查提交记录 40"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings_production')
django.setup()

from apps.problem.models import Submission

try:
    sub = Submission.objects.get(id=40)
    print(f'提交ID: {sub.id}')
    print(f'用户: {sub.user.username}')
    print(f'题目: {sub.problem.title if sub.problem else "N/A"}')
    print(f'状态: {sub.get_status_display()}')
    print(f'结果: {sub.result}')
    print(f'错误信息: {sub.error_message[:100] if sub.error_message else "无"}')
    print(f'语言: {sub.language}')
    print(f'创建时间: {sub.created_at}')
except Submission.DoesNotExist:
    print('提交记录 40 不存在')
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
