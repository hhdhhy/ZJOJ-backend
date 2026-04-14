#!/usr/bin/env python
"""
题目管理接口完整测试脚本
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# 测试数据
LOGIN_DATA = {
    "username": "liu",
    "password": "123456"
}

CREATE_PROBLEM_DATA = {
    "problem_id": "TEST003",
    "title": "测试题目 - 最小公倍数",
    "description": "## 题目描述\n\n求两个正整数的最小公倍数。\n\n## 输入格式\n\n一行两个正整数 a, b\n\n## 输出格式\n\n一个整数，表示最小公倍数",
    "input_description": "一行两个正整数 a, b (1 <= a, b <= 10^9)",
    "output_description": "一个整数，表示 a 和 b 的最小公倍数",
    "time_limit": 1000,
    "memory_limit": 65536,
    "difficulty": 2,
    "tags": ["数学", "数论"]
}

UPDATE_PROBLEM_DATA = {
    "title": "测试题目 - 最小公倍数（已更新）",
    "description": "## 题目描述\n\n求两个正整数的最小公倍数（LCM）。\n\n## 输入格式\n\n一行两个正整数 a, b\n\n## 输出格式\n\n一个整数，表示最小公倍数\n\n## 提示\n\nLCM(a,b) = a * b / GCD(a,b)",
    "difficulty": 3,
    "tags": ["数学", "数论", "LCM"]
}


def login():
    """登录获取token"""
    print("\n" + "="*60)
    print("测试1: 登录")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=LOGIN_DATA)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"✅ 登录成功!")
        print(f"Token: {token[:30]}...")
        return token
    else:
        print(f"❌ 登录失败: {response.text}")
        return None


def create_problem(token):
    """创建题目"""
    print("\n" + "="*60)
    print("测试2: 创建题目")
    print("="*60)
    
    headers = {
        "Authorization": f"jwt {token}"
    }
    
    # 准备文件
    files = {
        'input_1': ('1.in', '6 8\n', 'text/plain'),
        'output_1': ('1.out', '24\n', 'text/plain'),
        'input_2': ('2.in', '12 18\n', 'text/plain'),
        'output_2': ('2.out', '36\n', 'text/plain'),
    }
    
    # 准备表单数据
    data = {
        'problem_id': CREATE_PROBLEM_DATA['problem_id'],
        'title': CREATE_PROBLEM_DATA['title'],
        'description': CREATE_PROBLEM_DATA['description'],
        'input_description': CREATE_PROBLEM_DATA['input_description'],
        'output_description': CREATE_PROBLEM_DATA['output_description'],
        'time_limit': CREATE_PROBLEM_DATA['time_limit'],
        'memory_limit': CREATE_PROBLEM_DATA['memory_limit'],
        'difficulty': CREATE_PROBLEM_DATA['difficulty'],
        'tags': json.dumps(CREATE_PROBLEM_DATA['tags']),
    }
    
    response = requests.post(
        f"{BASE_URL}/api/problems/create/",
        headers=headers,
        data=data,
        files=files
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        print(f"✅ 题目创建成功!")
        return result.get('data', {}).get('problem_id')
    else:
        print(f"❌ 创建失败: {response.text}")
        return None


def get_problem_list(token):
    """获取题目列表"""
    print("\n" + "="*60)
    print("测试3: 获取题目列表")
    print("="*60)
    
    headers = {
        "Authorization": f"jwt {token}"
    }
    
    response = requests.get(f"{BASE_URL}/api/problems/", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        # 兼容两种返回格式
        if isinstance(data, list):
            problems = data
        else:
            problems = data.get('data', [])
        print(f"✅ 获取成功! 共有 {len(problems)} 个题目")
        for p in problems:
            print(f"  - {p['problem_id']}: {p['title']}")
        return problems
    else:
        print(f"❌ 获取失败: {response.text}")
        return []


def get_problem_detail(token, problem_id):
    """获取题目详情"""
    print("\n" + "="*60)
    print(f"测试4: 获取题目详情 ({problem_id})")
    print("="*60)
    
    headers = {
        "Authorization": f"jwt {token}"
    }
    
    response = requests.get(f"{BASE_URL}/api/problems/{problem_id}/", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        # 兼容两种返回格式
        if isinstance(data, dict) and 'data' in data:
            problem = data.get('data', {})
        else:
            problem = data
        print(f"✅ 获取成功!")
        print(f"题目ID: {problem.get('problem_id')}")
        print(f"标题: {problem.get('title')}")
        print(f"难度: {problem.get('difficulty')}")
        print(f"时间限制: {problem.get('time_limit')}ms")
        print(f"内存限制: {problem.get('memory_limit')}KB")
        print(f"标签: {', '.join(problem.get('tags', []))}")
        print(f"测试用例数: {problem.get('test_case_count')}")
        return problem
    else:
        print(f"❌ 获取失败: {response.text}")
        return None


def update_problem(token, problem_id):
    """更新题目"""
    print("\n" + "="*60)
    print(f"测试5: 部分更新题目 ({problem_id})")
    print("="*60)
    
    headers = {
        "Authorization": f"jwt {token}",
        "Content-Type": "application/json"
    }
    
    # 使用PATCH进行部分更新
    response = requests.patch(
        f"{BASE_URL}/api/problems/{problem_id}/",
        headers=headers,
        json=UPDATE_PROBLEM_DATA
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        print(f"✅ 题目更新成功!")
        return True
    else:
        print(f"❌ 更新失败: {response.text}")
        return False


def search_problems(token, keyword):
    """搜索题目"""
    print("\n" + "="*60)
    print(f"测试6: 搜索题目 (关键词: {keyword})")
    print("="*60)
    
    headers = {
        "Authorization": f"jwt {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/problems/",
        headers=headers,
        params={'search': keyword}
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        # 兼容两种返回格式
        if isinstance(data, list):
            problems = data
        else:
            problems = data.get('data', [])
        print(f"✅ 搜索成功! 找到 {len(problems)} 个题目")
        for p in problems:
            print(f"  - {p['problem_id']}: {p['title']}")
        return problems
    else:
        print(f"❌ 搜索失败: {response.text}")
        return []


def get_tags(token):
    """获取标签列表"""
    print("\n" + "="*60)
    print("测试7: 获取标签列表")
    print("="*60)
    
    headers = {
        "Authorization": f"jwt {token}"
    }
    
    response = requests.get(f"{BASE_URL}/api/problems/tags/", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        # 兼容两种返回格式
        if isinstance(data, list):
            tags = data
        else:
            tags = data.get('data', [])
        print(f"✅ 获取成功! 共有 {len(tags)} 个标签")
        for tag in tags:
            print(f"  - {tag['name']} (使用次数: {tag['usage_count']})")
        return tags
    else:
        print(f"❌ 获取失败: {response.text}")
        return []


def test_unauthorized_access():
    """测试未授权访问"""
    print("\n" + "="*60)
    print("测试8: 测试未授权访问")
    print("="*60)
    
    # 不带token访问
    response = requests.get(f"{BASE_URL}/api/problems/")
    print(f"不带Token访问题目列表 - 状态码: {response.status_code}")
    
    if response.status_code == 401:
        print(f"✅ 正确拒绝未授权访问")
    else:
        print(f"⚠️  应该返回401，但返回了 {response.status_code}")


def main():
    print("\n🚀 开始完整测试题目管理接口")
    print("="*60)
    
    # 1. 登录
    token = login()
    if not token:
        print("\n❌ 登录失败，终止测试")
        return
    
    # 2. 创建题目
    problem_id = create_problem(token)
    if not problem_id:
        print("\n❌ 创建题目失败，继续其他测试")
        problem_id = "TEST001"  # 使用之前创建的
    
    # 3. 获取题目列表
    get_problem_list(token)
    
    # 4. 获取题目详情
    get_problem_detail(token, problem_id)
    
    # 5. 更新题目
    update_problem(token, problem_id)
    
    # 6. 搜索题目
    search_problems(token, "最小公倍数")
    
    # 7. 获取标签列表
    get_tags(token)
    
    # 8. 测试未授权访问
    test_unauthorized_access()
    
    print("\n" + "="*60)
    print("✅ 所有测试完成!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
