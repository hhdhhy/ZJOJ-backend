#!/usr/bin/env python3
import requests
import json

url = 'http://localhost:5050/run'

# 测试简单命令
payload = {
    'cmd': [
        {
            'args': ['/bin/echo', 'Hello World'],
            'env': ['PATH=/usr/bin:/bin'],
            'cpuLimit': 1000000000,
            'memoryLimit': 268435456,
        }
    ]
}

print('Testing simple echo command...')
response = requests.post(url, json=payload, timeout=10)

print(f'Status code: {response.status_code}')
result = response.json()
print(f'Response:\n{json.dumps(result, indent=2, ensure_ascii=False)}')
