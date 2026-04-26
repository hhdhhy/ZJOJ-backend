#!/usr/bin/env python3
"""
测试 go-judge 评测功能
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings_production')
django.setup()

from apps.judge.adapter import judge_adapter

# 测试 C++ 代码
cpp_code = """
#include <iostream>
using namespace std;
int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}
"""

# 测试用例
test_cases = [
    {'input': '1 2\n', 'output': '3\n'},
    {'input': '10 20\n', 'output': '30\n'},
]

print("开始测试 C++ 评测...")
result = judge_adapter.judge(
    code=cpp_code,
    language='cpp',
    test_cases=test_cases,
    time_limit=1000,  # 1秒
    memory_limit=128  # 128MB
)

print("\n评测结果:")
print(f"状态: {result.get('result')}")
print(f"得分: {result.get('score')}")
print(f"时间: {result.get('time')}ms")
print(f"内存: {result.get('memory')}KB")

if result.get('test_cases'):
    print("\n测试点详情:")
    for i, tc in enumerate(result['test_cases'], 1):
        print(f"  测试点 {i}: {tc['status']} (得分: {tc['score']})")
        if tc.get('stderr'):
            print(f"    错误: {tc['stderr'][:200]}")
