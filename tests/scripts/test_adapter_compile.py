#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/zjoj')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings_production')

import django
django.setup()

from apps.judge.adapter import judge_adapter

# 测试编译功能
code = """#include<bits/stdc++.h>
using namespace std;

int main()
{
    int x;
    cin>>x;
    cout<<1;
    return 0;
}
"""

print("=== 测试编译 C++ 代码 ===")
try:
    result = judge_adapter._compile_code(code, 'cpp', judge_adapter._get_compile_command('cpp'))
    print(f"编译结果: {result}")
except Exception as e:
    import traceback
    print(f"编译异常: {e}")
    print(traceback.format_exc())
