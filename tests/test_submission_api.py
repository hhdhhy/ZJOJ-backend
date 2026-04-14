"""
提交代码API测试（不需要Redis）
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def login():
    """登录获取token"""
    print("\n" + "="*60)
    print("步骤1: 登录")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"username": "liu", "password": "123456"}
    )
    
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


def submit_code(token):
    """提交代码"""
    print("\n" + "="*60)
    print("步骤2: 提交代码")
    print("="*60)
    
    headers = {
        "Authorization": f"jwt {token}",
        "Content-Type": "application/json"
    }
    
    # 准备提交数据
    submission_data = {
        "problem": "TEST001",
        "language": "cpp",
        "code": """#include <iostream>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}"""
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/submissions/submit/",
            headers=headers,
            json=submission_data
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 提交成功!")
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return data.get('submission_id')
        else:
            print(f"❌ 提交失败: {response.text}")
            return None
    
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保 Django 服务器正在运行")
        print("   运行: python manage.py runserver")
        return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def get_submissions(token):
    """获取提交列表"""
    print("\n" + "="*60)
    print("步骤3: 获取提交列表")
    print("="*60)
    
    headers = {
        "Authorization": f"jwt {token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/submissions/",
            headers=headers
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            submissions = data if isinstance(data, list) else data.get('results', [])
            print(f"✅ 获取成功! 共有 {len(submissions)} 个提交")
            
            for sub in submissions[:5]:  # 只显示前5个
                print(f"  - ID:{sub['id']} | 题目:{sub['problem_id']} | "
                      f"语言:{sub['language']} | 状态:{sub['status_display']} | "
                      f"结果:{sub.get('result', '待评测')}")
            
            return submissions
        else:
            print(f"❌ 获取失败: {response.text}")
            return []
    
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        return []
    except Exception as e:
        print(f"❌ 错误: {e}")
        return []


def get_submission_detail(token, submission_id):
    """获取提交详情"""
    print("\n" + "="*60)
    print(f"步骤4: 获取提交详情 (ID: {submission_id})")
    print("="*60)
    
    headers = {
        "Authorization": f"jwt {token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/submissions/{submission_id}/",
            headers=headers
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取成功!")
            print(f"\n提交详情:")
            print(f"  提交ID: {data['id']}")
            print(f"  题目: {data['problem_id']} - {data['problem_title']}")
            print(f"  用户: {data['username']}")
            print(f"  语言: {data['language_display']}")
            print(f"  状态: {data['status_display']}")
            print(f"  结果: {data.get('result_display', '待评测')}")
            print(f"  得分: {data.get('score', 0)}")
            print(f"  运行时间: {data.get('execution_time', 0)}ms")
            print(f"  内存使用: {data.get('memory_usage', 0)}KB")
            print(f"  代码长度: {data.get('code_length', 0)} bytes")
            print(f"  提交时间: {data['submit_time']}")
            
            if data.get('test_case_results'):
                print(f"\n  测试点结果:")
                for tc in data['test_case_results']:
                    print(f"    - 测试点#{tc['test_case_id']}: {tc['status']} "
                          f"(时间:{tc['execution_time']}ms, "
                          f"内存:{tc['memory_usage']}KB, "
                          f"得分:{tc['score']})")
            
            return data
        else:
            print(f"❌ 获取失败: {response.text}")
            return None
    
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def test_unauthorized():
    """测试未授权访问"""
    print("\n" + "="*60)
    print("步骤5: 测试未授权访问")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/submissions/")
        print(f"不带Token访问 - 状态码: {response.status_code}")
        
        if response.status_code == 401:
            print(f"✅ 正确拒绝未授权访问")
        else:
            print(f"⚠️  应该返回401，但返回了 {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 错误: {e}")


def main():
    print("\n🚀 开始测试提交代码API")
    print("="*60)
    print("注意: 此测试需要 Django 服务器运行")
    print("      如果还没启动，请先运行: python manage.py runserver")
    print("="*60)
    
    # 1. 登录
    token = login()
    if not token:
        print("\n❌ 登录失败，终止测试")
        return
    
    # 2. 提交代码
    submission_id = submit_code(token)
    
    # 3. 获取提交列表
    submissions = get_submissions(token)
    
    # 4. 获取提交详情
    if submission_id:
        get_submission_detail(token, submission_id)
    elif submissions:
        # 如果没有新提交，查看第一个已有提交
        get_submission_detail(token, submissions[0]['id'])
    
    # 5. 测试未授权访问
    test_unauthorized()
    
    print("\n" + "="*60)
    print("✅ 测试完成!")
    print("="*60)
    print("\n提示:")
    print("  - 如果看到 ConnectionError，请先启动 Django 服务器")
    print("  - 如果要实际评测代码，还需要:")
    print("    1. 启动 Redis: docker run -d -p 6379:6379 redis")
    print("    2. 启动 Celery: celery -A ZJOJ worker --loglevel=info --pool=solo")
    print("    3. (可选) 启动 HydroJudge 沙箱服务")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
