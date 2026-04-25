"""
测试代码提交功能
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


def get_problem_list(token):
    """获取题目列表"""
    headers = {'Authorization': f'jwt {token}'}
    response = requests.get(f"{BASE_URL}/api/problems/?page=1&page_size=5", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # DRF ListAPIView 返回的是分页数据
        if isinstance(data, dict) and 'results' in data:
            problems = data['results']
            count = data.get('count', len(problems))
        else:
            problems = data
            count = len(problems)
        
        print(f"\n📋 题目列表（共 {count} 个）:")
        for problem in problems[:3]:
            # 打印第一个题目的所有字段
            if problem == problems[0]:
                print(f"   第一个题目的字段: {list(problem.keys())}")
            problem_id = problem.get('problem_id') or problem.get('id')
            title = problem.get('title', 'N/A')
            print(f"  - {problem_id}: {title}")
        return problems
    else:
        print(f"❌ 获取题目列表失败: {response.status_code}")
        print(response.text)
        return []


def submit_code(token, problem_id, language="cpp"):
    """提交代码"""
    headers = {'Authorization': f'jwt {token}'}
    
    # 简单的 A+B 代码
    code = """#include <iostream>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}
"""
    
    payload = {
        'problem': problem_id,  # 使用 problem 字段
        'language': language,
        'code': code
    }
    
    print(f"\n📤 提交代码到题目 {problem_id}...")
    response = requests.post(f"{BASE_URL}/api/submissions/submit/", 
                            headers=headers, 
                            json=payload)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ 提交成功!")
        print(f"   提交ID: {data['submission_id']}")
        print(f"   状态: {data['status']}")
        print(f"   消息: {data['message']}")
        return data['submission_id']
    else:
        print(f"❌ 提交失败: {response.status_code}")
        print(response.json())
        return None


def get_submission_detail(token, submission_id):
    """获取提交详情"""
    headers = {'Authorization': f'jwt {token}'}
    
    print(f"\n🔍 查询提交 {submission_id} 的详情...")
    response = requests.get(f"{BASE_URL}/api/submissions/{submission_id}/", 
                           headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 提交详情:")
        print(f"   题目: {data.get('problem_title', 'N/A')}")
        print(f"   语言: {data.get('language', 'N/A')}")
        print(f"   状态: {data.get('status', 'N/A')} ({data.get('status_display', 'N/A')})")
        print(f"   结果: {data.get('result', 'N/A')} ({data.get('result_display', 'N/A')})")
        print(f"   得分: {data.get('score', 0)}")
        print(f"   用时: {data.get('execution_time', 0)}ms")
        print(f"   内存: {data.get('memory_usage', 0)}KB")
        
        if data.get('test_case_results'):
            print(f"\n   测试点详情:")
            for tc in data['test_case_results'][:3]:
                print(f"     - 测试点 #{tc['test_case_id']}: {tc['status']} "
                      f"(得分:{tc['score']}, 用时:{tc['execution_time']}ms)")
        
        return data
    else:
        print(f"❌ 获取详情失败: {response.status_code}")
        print(response.json())
        return None


def get_submission_list(token, limit=5):
    """获取提交列表"""
    headers = {'Authorization': f'jwt {token}'}
    
    print(f"\n📊 获取最近的提交记录...")
    response = requests.get(f"{BASE_URL}/api/submissions/?page_size={limit}", 
                           headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # 兼容分页和非分页响应
        if isinstance(data, dict) and 'results' in data:
            submissions = data['results']
            count = data.get('count', len(submissions))
        elif isinstance(data, list):
            submissions = data
            count = len(submissions)
        else:
            print(f"⚠️ 未知的响应格式: {type(data)}")
            return None
        
        print(f"✅ 共有 {count} 条提交记录")
        
        if submissions:
            print(f"\n最近 {len(submissions)} 条提交:")
            for sub in submissions:
                print(f"   - ID:{sub['id']} | 题目:{sub.get('problem_title', 'N/A')} | "
                      f"结果:{sub.get('result', 'N/A')} | "
                      f"时间:{sub['submit_time'][:19]}")
        
        return data
    else:
        print(f"❌ 获取列表失败: {response.status_code}")
        return None


def main():
    print("=" * 60)
    print("🧪 测试代码提交功能")
    print("=" * 60)
    
    # 1. 登录
    print("\n[步骤 1] 登录...")
    token = login('admin', 'Admin@123456')
    if not token:
        print("❌ 无法继续，请先创建测试用户")
        return
    
    print(f"✅ 登录成功，Token: {token[:20]}...")
    
    # 2. 获取题目列表
    print("\n[步骤 2] 获取题目列表...")
    problems = get_problem_list(token)
    if not problems:
        print("⚠️ 没有可用的题目，请先创建题目")
        return
    
    problem_id = problems[0].get('problem_id') or problems[0].get('id')
    print(f"\n📝 选择题目: {problem_id}")
    
    # 3. 提交代码
    print("\n[步骤 3] 提交代码...")
    submission_id = submit_code(token, problem_id)
    if not submission_id:
        print("❌ 提交失败")
        return
    
    # 4. 等待评测完成
    print("\n[步骤 4] 等待评测完成（最多等待 30 秒）...")
    import time
    for i in range(10):
        time.sleep(3)
        detail = get_submission_detail(token, submission_id)
        if detail and detail.get('status') == 2:  # 已完成
            print(f"\n✅ 评测完成！")
            break
        elif detail:
            print(f"⏳ 当前状态: {detail.get('status_text', '未知')} (第 {i+1} 次检查)")
    else:
        print("\n⚠️ 超时，评测可能仍在进行中")
    
    # 5. 获取提交列表
    print("\n[步骤 5] 获取提交列表...")
    get_submission_list(token, limit=5)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
