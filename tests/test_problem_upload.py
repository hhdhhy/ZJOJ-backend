"""
题目上传接口测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """测试登录"""
    print("=" * 60)
    print("测试1: 登录")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"username": "liu", "password": "123456"}
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        token = response.json()['token']
        print(f"✅ 登录成功!")
        print(f"Token: {token[:30]}...")
        return token
    else:
        print(f"❌ 登录失败: {response.text}")
        return None

def test_create_problem(token):
    """测试创建题目"""
    print("\n" + "=" * 60)
    print("测试2: 创建题目")
    print("=" * 60)
    
    headers = {"Authorization": f"jwt {token}"}
    problem_data = {
        "problem_id": "TEST001",
        "title": "测试题目 A+B",
        "description": "计算两个整数的和",
        "time_limit": 1000,
        "memory_limit": 65536,
        "tag_ids": []
    }
    
    response = requests.post(
        f"{BASE_URL}/api/problems/create/",
        json=problem_data,
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"原始响应: {response.text[:500]}")
    
    if response.status_code == 201:
        print("✅ 题目创建成功!")
        return True
    else:
        print("❌ 题目创建失败!")
        return False

def test_list_problems():
    """测试获取题目列表"""
    print("\n" + "=" * 60)
    print("测试3: 获取题目列表")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/problems/")
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        problems = response.json()
        print(f"✅ 获取成功! 共有 {len(problems)} 个题目")
        for p in problems[:3]:  # 只显示前3个
            print(f"  - {p['problem_id']}: {p['title']}")
        return True
    else:
        print(f"❌ 获取失败: {response.text}")
        return False

if __name__ == "__main__":
    print("\n🚀 开始测试题目上传接口\n")
    
    # 测试登录
    token = test_login()
    if not token:
        print("\n❌ 登录失败，终止测试")
        exit(1)
    
    # 测试创建题目
    if not test_create_problem(token):
        print("\n❌ 创建题目失败")
        exit(1)
    
    # 测试获取题目列表
    test_list_problems()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成!")
    print("=" * 60)
