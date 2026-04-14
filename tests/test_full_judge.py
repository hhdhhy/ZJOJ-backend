"""
完整评测流程测试
"""
import requests
import json
import time

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
    
    if response.status_code == 200:
        token = response.json()['token']
        print(f"✅ 登录成功")
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
    
    response = requests.post(
        f"{BASE_URL}/api/submissions/submit/",
        headers=headers,
        json=submission_data
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ 提交成功")
        print(f"   提交ID: {data['submission_id']}")
        print(f"   消息: {data['message']}")
        return data['submission_id']
    else:
        print(f"❌ 提交失败: {response.text}")
        return None


def check_submission_status(token, submission_id, max_wait=30):
    """检查提交状态，等待评测完成"""
    print("\n" + "="*60)
    print(f"步骤3: 等待并检查评测结果 (最多等待{max_wait}秒)")
    print("="*60)
    
    headers = {
        "Authorization": f"jwt {token}"
    }
    
    for i in range(max_wait):
        response = requests.get(
            f"{BASE_URL}/api/submissions/{submission_id}/",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data['status']
            result = data.get('result', 'None')
            
            print(f"   [{i+1}s] 状态: {data['status_display']} | 结果: {result}")
            
            # 如果评测完成，返回结果
            if status == 2:  # 已完成
                print(f"\n✅ 评测完成!")
                return data
        
        time.sleep(1)
    
    print(f"\n⚠️  超时，评测可能还在进行中")
    return None


def display_result(data):
    """显示评测结果"""
    if not data:
        return
    
    print("\n" + "="*60)
    print("评测结果详情")
    print("="*60)
    
    print(f"\n基本信息:")
    print(f"  提交ID: {data['id']}")
    print(f"  题目: {data['problem_id']} - {data['problem_title']}")
    print(f"  用户: {data['username']}")
    print(f"  语言: {data['language_display']}")
    print(f"  代码长度: {data['code_length']} bytes")
    
    print(f"\n评测结果:")
    print(f"  状态: {data['status_display']}")
    print(f"  结果: {data.get('result_display', 'N/A')}")
    print(f"  得分: {data.get('score', 0)}")
    print(f"  运行时间: {data.get('execution_time', 0)}ms")
    print(f"  内存使用: {data.get('memory_usage', 0)}KB")
    
    print(f"\n时间信息:")
    print(f"  提交时间: {data['submit_time']}")
    print(f"  评测时间: {data.get('judge_time', 'N/A')}")
    
    if data.get('test_case_results'):
        print(f"\n测试点详情:")
        for tc in data['test_case_results']:
            status_icon = "✅" if tc['status'] == 'AC' else "❌"
            print(f"  {status_icon} 测试点#{tc['test_case_id']}: {tc['status']}")
            print(f"     时间: {tc['execution_time']}ms | "
                  f"内存: {tc['memory_usage']}KB | "
                  f"得分: {tc['score']}")
            if tc.get('message'):
                print(f"     信息: {tc['message']}")


def main():
    print("\n🚀 开始完整评测流程测试")
    print("="*60)
    print("此测试将:")
    print("  1. 登录获取Token")
    print("  2. 提交C++代码")
    print("  3. 等待Celery异步评测")
    print("  4. 显示评测结果")
    print("="*60)
    
    # 1. 登录
    token = login()
    if not token:
        print("\n❌ 登录失败，终止测试")
        return
    
    # 2. 提交代码
    submission_id = submit_code(token)
    if not submission_id:
        print("\n❌ 提交失败，终止测试")
        return
    
    # 3. 等待并检查评测结果
    result_data = check_submission_status(token, submission_id, max_wait=30)
    
    # 4. 显示结果
    display_result(result_data)
    
    print("\n" + "="*60)
    print("✅ 测试完成!")
    print("="*60)
    print("\n提示:")
    print("  - 如果看到 '等待评测'，说明 Celery Worker 未运行")
    print("  - 如果看到 '系统错误'，可能是 HydroJudge 服务未启动")
    print("  - 查看 Celery Worker 日志了解详细评测过程")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
