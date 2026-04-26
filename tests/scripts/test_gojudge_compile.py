#!/usr/bin/env python3
"""测试 go-judge 编译功能"""
import requests
import json

url = "http://101.35.233.33:5050/run"

# 测试 C++ 编译
payload = {
    "cmd": [
        {
            "args": ["/host-usr/bin/g++", "-std=c++17", "-O2", "-o", "/w/main", "/w/main.cpp"],
            "env": ["PATH=/usr/bin:/bin", "HOME=/w"],
            "cpuLimit": 5000000000,
            "memoryLimit": 536870912,
            "copyIn": {
                "main.cpp": {
                    "content": "#include<iostream>\nusing namespace std;\nint main(){cout<<1;return 0;}"
                }
            }
        }
    ]
}

print("发送请求到 go-judge...")
response = requests.post(url, json=payload, timeout=10)

print(f"状态码: {response.status_code}")
print(f"响应:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
