#!/usr/bin/env python3
"""
测试代码提交 API
"""
import requests
import json
import time

# 服务器地址
BASE_URL = "http://101.35.233.33:8000"

def login():
    """登录获取 token"""
    print("=== 登录 ===")
    response = requests.post(f"{BASE_URL}/api/login/", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"✓ 登录成功")
        return token
    else:
        print(f"✗ 登录失败: {response.text}")
        return None

def get_problems(token):
    """获取题目列表"""
    print("\n=== 获取题目列表 ===")
    headers = {"Authorization": f"JWT {token}"}
    response = requests.get(f"{BASE_URL}/api/problems/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        problems = data.get('results', [])
        print(f"✓ 找到 {len(problems)} 个题目")
        for p in problems:
            print(f"  - {p['problem_id']}: {p['title']}")
        return problems
    else:
        print(f"✗ 获取失败: {response.text}")
        return []

def submit_code(token, problem_id):
    """提交代码"""
    print(f"\n=== 提交代码到题目 {problem_id} ===")
    
    # Python A+B 代码（go-judge 容器中有 Python3）
    python_code = """a, b = map(int, input().split())
print(a + b)
"""
    
    headers = {"Authorization": f"JWT {token}"}
    data = {
        "problem": problem_id,
        "language": "python3",
        "code": python_code
    }
    
    response = requests.post(f"{BASE_URL}/api/submissions/submit/", 
                            headers=headers, 
                            json=data)
    
    if response.status_code == 201:
        result = response.json()
        submission_id = result.get('submission_id')
        print(f"✓ 提交成功! Submission ID: {submission_id}")
        print(f"  状态: {result.get('status')}")
        return submission_id
    else:
        print(f"✗ 提交失败: {response.text}")
        return None

def check_submission(token, submission_id):
    """检查提交结果"""
    print(f"\n=== 检查提交 #{submission_id} ===")
    
    headers = {"Authorization": f"JWT {token}"}
    
    # 最多等待 30 秒
    for i in range(30):
        response = requests.get(f"{BASE_URL}/api/submissions/{submission_id}/", 
                               headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            result = data.get('result')
            
            print(f"  [{i+1}s] 状态: {status}, 结果: {result}")
            
            # 如果已完成，打印详细信息
            if status == 2:  # 已完成
                print(f"\n✓ 评测完成!")
                print(f"  结果: {result}")
                print(f"  得分: {data.get('score')}")
                print(f"  时间: {data.get('execution_time')}ms")
                print(f"  内存: {data.get('memory_usage')}KB")
                
                # 打印测试点详情
                test_cases = data.get('test_case_results', [])
                if test_cases:
                    print(f"\n  测试点详情:")
                    for tc in test_cases:
                        print(f"    #{tc['test_case_id']}: {tc['status']} "
                              f"(时间: {tc['execution_time']}ms, "
                              f"内存: {tc['memory_usage']}KB, "
                              f"得分: {tc['score']})")
                
                return True
            elif status == 4:  # 系统错误
                print(f"\n✗ 系统错误: {data.get('result')}")
                return False
        else:
            print(f"✗ 查询失败: {response.text}")
            return False
        
        time.sleep(1)
    
    print("\n⚠ 超时，评测可能还在进行中")
    return False

def main():
    print("ZJOJ 代码提交测试\n")
    print("=" * 60)
    
    # 1. 登录
    token = login()
    if not token:
        print("\n无法继续，请先创建管理员账户")
        return
    
    # 2. 获取题目列表
    problems = get_problems(token)
    if not problems:
        print("\n没有可用的题目")
        return
    
    # 3. 提交代码（使用第一个题目）
    problem_id = problems[0]['problem_id']
    submission_id = submit_code(token, problem_id)
    
    if not submission_id:
        print("\n提交失败")
        return
    
    # 4. 等待并检查结果
    time.sleep(2)
    check_submission(token, submission_id)
    
    print("\n" + "=" * 60)
    print("测试完成!")

if __name__ == "__main__":
    main()
