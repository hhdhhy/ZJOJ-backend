#!/usr/bin/env python3
import requests
import json

url = 'http://localhost:5050/run'

# 使用绝对路径测试
payload = {
    'cmd': [
        {
            'args': ['/host-usr/bin/x86_64-linux-gnu-g++-13', '-std=c++17', '-O2', '-o', '/w/main', '/w/main.cpp'],
            'env': ['PATH=/usr/bin:/bin', 'HOME=/w'],
            'cpuLimit': 5000000000,
            'memoryLimit': 536870912,
            'copyIn': {
                'main.cpp': {
                    'content': '#include<iostream>\nusing namespace std;\nint main(){cout<<1;return 0;}'
                }
            }
        }
    ]
}

print('Testing with absolute path...')
response = requests.post(url, json=payload, timeout=10)

print(f'Status code: {response.status_code}')
result = response.json()
print(f'Response:\n{json.dumps(result, indent=2, ensure_ascii=False)}')

if result and len(result) > 0:
    print(f'\nExit status: {result[0].get("exitStatus")}')
    print(f'Status: {result[0].get("status")}')
    if 'error' in result[0]:
        print(f'Error: {result[0]["error"]}')
