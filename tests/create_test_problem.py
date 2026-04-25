"""
创建测试题目
"""
import requests
import json

BASE_URL = "http://101.35.233.33:8000"

def login(username, password):
    """登录获取 Token"""
    response = requests.post(f"{BASE_URL}/api/login/", json={
        'username': username,
        'password': password
    })
    
    if response.status_code == 200:
        data = response.json()
        return data['token']
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(response.json())
        return None


def create_problem(token):
    """创建测试题目"""
    headers = {'Authorization': f'jwt {token}'}
    
    problem_data = {
        'problem_id': 'A001',
        'title': 'A+B Problem',
        'description': '''## 题目描述

计算两个整数的和。

## 输入格式

输入两个整数 a 和 b (0 <= a, b <= 1000)。

## 输出格式

输出 a + b 的值。

## 样例输入

```
1 2
```

## 样例输出

```
3
```
''',
        'input_format': '两个整数 a 和 b，用空格分隔',
        'output_format': '一个整数，表示 a + b 的结果',
        'sample_input': '1 2',
        'sample_output': '3',
        'difficulty': 'EASY',
        'time_limit': 1000,
        'memory_limit': 256,
        'tags': ['入门', '模拟']
    }
    
    print("📝 创建题目 A+B Problem...")
    response = requests.post(f"{BASE_URL}/api/problems/create/", 
                            headers=headers, 
                            json=problem_data)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ 题目创建成功!")
        print(f"   完整响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        # 尝试不同的字段名
        problem_id = data.get('data', {}).get('id') or data.get('data', {}).get('problem_id')
        if problem_id:
            print(f"   题目ID: {problem_id}")
            return problem_id
        else:
            print(f"   ⚠️ 无法获取题目ID")
            return None
    else:
        print(f"❌ 创建失败: {response.status_code}")
        print(response.json())
        return None


def main():
    print("=" * 60)
    print("📝 创建测试题目")
    print("=" * 60)
    
    # 登录
    print("\n[步骤 1] 登录...")
    token = login('admin', 'Admin@123456')
    if not token:
        return
    
    print(f"✅ 登录成功")
    
    # 创建题目
    print("\n[步骤 2] 创建题目...")
    problem_id = create_problem(token)
    
    if problem_id:
        print(f"\n✅ 完成！题目ID: {problem_id}")
    else:
        print("\n❌ 创建失败")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ 出错: {str(e)}")
        import traceback
        traceback.print_exc()
