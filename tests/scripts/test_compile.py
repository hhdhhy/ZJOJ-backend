#!/usr/bin/env python3
import requests
import json

url = 'http://localhost:5050/run'

payload = {
    'cmd': [
        {
            'args': ['/host-usr/bin/g++', '-std=c++17', '-O2', '-o', '/w/main', '/w/main.cpp'],
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

print('Sending request to go-judge...')
response = requests.post(url, json=payload, timeout=10)

print(f'Status code: {response.status_code}')
print(f'Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}')
