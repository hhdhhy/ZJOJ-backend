"""
AI助手完整功能测试脚本
测试所有API接口和RAG流程
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"


def test_login():
    """测试登录并获取JWT Token"""
    print("=" * 60)
    print("📋 测试1: 用户登录")
    print("=" * 60)
    
    # 使用已创建的测试用户
    login_data = {
        "username": "test_ai",
        "password": "TestPass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ 登录成功！Token: {token[:30]}...")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None


def test_chat(token):
    """测试AI聊天接口"""
    print("\n" + "=" * 60)
    print("💬 测试2: AI智能问答")
    print("=" * 60)
    
    headers = {
        "Authorization": f"jwt {token}",
        "Content-Type": "application/json"
    }
    
    # 测试问题1：简单对话（不使用RAG）
    print("\n🔍 问题1: 你好，请介绍一下自己")
    chat_data = {
        "question": "你好，请介绍一下自己",
        "use_rag": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/chat/",
            headers=headers,
            json=chat_data,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 回答: {data['answer'][:100]}...")
            print(f"   Tokens使用: {data['tokens_used']}")
            print(f"   剩余配额: {data.get('remaining_quota', 'N/A')}")
            print(f"   Chat ID: {data.get('chat_id', 'N/A')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试问题2：技术问题
    print("\n🔍 问题2: 什么是二分查找算法？")
    chat_data = {
        "question": "什么是二分查找算法？",
        "use_rag": True,
        "top_k": 3
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/chat/",
            headers=headers,
            json=chat_data,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 回答: {data['answer'][:150]}...")
            print(f"   引用来源数: {len(data.get('sources', []))}")
            for i, source in enumerate(data.get('sources', [])[:2], 1):
                print(f"   来源{i}: {source['content'][:80]}...")
            print(f"   剩余配额: {data.get('remaining_quota', 'N/A')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")


def test_history(token):
    """测试对话历史接口"""
    print("\n" + "=" * 60)
    print("📜 测试3: 获取对话历史")
    print("=" * 60)
    
    headers = {
        "Authorization": f"jwt {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/ai/history/?page=1&page_size=5",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取成功！")
            print(f"   总记录数: {data['count']}")
            
            if data['results']:
                print(f"\n   最近{len(data['results'])}条对话:")
                for i, chat in enumerate(data['results'][:3], 1):
                    print(f"   {i}. Q: {chat['question'][:50]}...")
                    print(f"      A: {chat['answer'][:50]}...")
                    print(f"      时间: {chat['created_at']}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")


def test_usage(token):
    """测试使用情况统计"""
    print("\n" + "=" * 60)
    print("📊 测试4: 使用情况统计")
    print("=" * 60)
    
    headers = {
        "Authorization": f"jwt {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/ai/usage/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 统计信息:")
            print(f"   今日使用: {data['used_today']} / {data['daily_quota']}")
            print(f"   剩余配额: {data['remaining']}")
            print(f"   历史记录数: {data['history_count']}")
            print(f"   历史上限: {data['max_history']}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")


def test_clear_history(token):
    """测试清空历史"""
    print("\n" + "=" * 60)
    print("🗑️  测试5: 清空对话历史")
    print("=" * 60)
    
    headers = {
        "Authorization": f"jwt {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.delete(
            f"{BASE_URL}/api/ai/history/clear/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")


def main():
    """主测试流程"""
    print("\n" + "🚀" * 30)
    print("开始AI助手完整功能测试")
    print("🚀" * 30 + "\n")
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/api/", timeout=5)
        print(f"✅ 服务器正常运行 (状态码: {response.status_code})\n")
    except:
        print("❌ 无法连接到服务器，请先启动Django服务:")
        print("   python manage.py runserver")
        sys.exit(1)
    
    # Step 1: 登录
    token = test_login()
    if not token:
        print("\n❌ 登录失败，终止测试")
        return
    
    # Step 2: AI聊天
    test_chat(token)
    
    # Step 3: 查看历史
    test_history(token)
    
    # Step 4: 查看使用情况
    test_usage(token)
    
    # Step 5: 清空历史
    test_clear_history(token)
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)
    print("\n💡 提示:")
    print("  - 如果某些测试失败，请检查:")
    print("    1. Django服务是否正常运行")
    print("    2. DeepSeek API密钥是否正确")
    print("    3. 数据库迁移是否完成")
    print("    4. Embedding模型是否下载成功")


if __name__ == "__main__":
    main()
