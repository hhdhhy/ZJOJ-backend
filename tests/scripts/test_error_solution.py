#!/usr/bin/env python3
"""
测试错误解决方案接口
"""
import requests
import json

BASE_URL = 'http://localhost:8000'

def test_error_solution():
    """测试错误解决方案接口"""
    
    # 步骤 1: 登录获取 Token
    print("=" * 60)
    print("步骤 1: 登录获取 Token")
    print("=" * 60)
    
    login_data = {
        'username': 'test_ai',
        'password': 'test123456'
    }
    
    response = requests.post(f'{BASE_URL}/api/login/', json=login_data, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()['token']
    print(f"✅ 登录成功！")
    print(f"Token: {token[:30]}...")
    print()
    
    # 步骤 2: 测试错误解决方案接口
    print("=" * 60)
    print("步骤 2: 测试错误解决方案接口 (submission_id=40)")
    print("=" * 60)
    
    headers = {
        'Authorization': f'jwt {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f'{BASE_URL}/api/ai/error-solution/40/',
            headers=headers,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功！")
            print(f"提交ID: {data.get('submission_id')}")
            print(f"解决方案数量: {data.get('count')}")
            print(f"剩余配额: {data.get('remaining_quota')}")
            
            if data.get('solutions'):
                print(f"\n第一个解决方案:")
                print(json.dumps(data['solutions'][0], ensure_ascii=False, indent=2))
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    print()
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    test_error_solution()
