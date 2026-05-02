#!/usr/bin/env python3
"""AI 问答测试脚本 - 服务器端运行"""
import requests
import sys

BASE_URL = 'http://localhost:8000'

print('=' * 60)
print('AI 问答功能测试')
print('=' * 60)

# 步骤 1: 登录
print('\n步骤 1: 登录获取 Token')
print('-' * 60)

try:
    login_response = requests.post(f'{BASE_URL}/api/login/', json={
        'username': 'test_ai',
        'password': 'test123456'
    }, timeout=10)
    
    if login_response.status_code != 200:
        print(f'❌ 登录失败: {login_response.json()}')
        sys.exit(1)
    
    token = login_response.json()['token']
    print(f'✅ 登录成功！')
    print(f'Token: {token[:30]}...')
except Exception as e:
    print(f'❌ 登录异常: {e}')
    sys.exit(1)

# 步骤 2: 测试简单对话
print('\n步骤 2: 测试简单对话')
print('-' * 60)

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

try:
    chat_response = requests.post(
        f'{BASE_URL}/api/ai/chat/',
        headers=headers,
        json={
            'question': '如何实现快速排序？',
            'use_rag': False,
            'top_k': 3
        },
        timeout=30
    )
    
    if chat_response.status_code == 200:
        result = chat_response.json()
        print(f'✅ 回答成功！')
        print(f'Token 使用: {result.get("tokens_used", "N/A")}')
        print(f'剩余配额: {result.get("remaining_quota", "N/A")}')
        print(f'\nAI 回答:\n{result["answer"][:300]}...')
    else:
        print(f'❌ 请求失败: {chat_response.status_code}')
        print(f'错误信息: {chat_response.json()}')
except Exception as e:
    print(f'❌ 请求异常: {e}')

# 步骤 3: 查看使用情况
print('\n步骤 3: 查看使用情况')
print('-' * 60)

try:
    usage_response = requests.get(
        f'{BASE_URL}/api/ai/usage/',
        headers=headers,
        timeout=10
    )
    
    if usage_response.status_code == 200:
        stats = usage_response.json()
        print(f'✅ 使用情况:')
        print(f'  每日配额: {stats["daily_quota"]}')
        print(f'  今日已用: {stats["used_today"]}')
        print(f'  剩余配额: {stats["remaining"]}')
        print(f'  历史记录: {stats["history_count"]}')
    else:
        print(f'❌ 请求失败: {usage_response.json()}')
except Exception as e:
    print(f'❌ 请求异常: {e}')

print('\n' + '=' * 60)
print('✅ 测试完成！')
print('=' * 60)
