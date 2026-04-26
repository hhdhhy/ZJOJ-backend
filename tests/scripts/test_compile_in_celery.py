#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/zjoj')

from apps.judge.adapter import judge_adapter

code = """#include<bits/stdc++.h>
using namespace std;
int main() { int x; cin>>x; cout<<1; return 0; }"""

print("Testing compile...")
try:
    result = judge_adapter._compile_code(code, 'cpp', judge_adapter._get_compile_command('cpp'))
    print(f"Result: {result}")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    print(traceback.format_exc())
