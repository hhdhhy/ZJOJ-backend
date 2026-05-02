#!/usr/bin/env python3
"""
AI 问答功能测试脚本
"""
import requests
import json
import sys

# 配置
BASE_URL = "http://localhost:8000"  # 修改为您的服务器地址
USERNAME = "test_student"  # 测试用户名
PASSWORD = "test123456"    # 测试密码

def login():
    """登录获取 Token"""
    print("=" * 60)
    print("步骤 1: 登录获取 Token")
    print("=" * 60)
    
    response = requests.post(f"{BASE_URL}/api/login/", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json()["token"]
        print(f"✅ 登录成功！")
        print(f"Token: {token[:20]}...")
        return token
    else:
        print(f"❌ 登录失败: {response.json()}")
        sys.exit(1)

def test_ai_chat(token):
    """测试 AI 问答"""
    print("\n" + "=" * 60)
    print("步骤 2: 测试 AI 问答（简单对话）")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试问题
    questions = [
        "如何实现快速排序？",
        "什么是动态规划？",
        "请解释一下 BFS 和 DFS 的区别"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n--- 问题 {i}: {question} ---")
        
        response = requests.post(
            f"{BASE_URL}/api/ai/chat/",
            headers=headers,
            json={
                "question": question,
                "use_rag": False,  # 先测试简单对话
                "top_k": 3
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 回答成功！")
            print(f"Token 使用: {result.get('tokens_used', 'N/A')}")
            print(f"剩余配额: {result.get('remaining_quota', 'N/A')}")
            print(f"\nAI 回答:\n{result['answer'][:500]}...")  # 只显示前500字符
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.json()}")

def test_ai_chat_with_rag(token):
    """测试 RAG 增强问答"""
    print("\n" + "=" * 60)
    print("步骤 3: 测试 RAG 增强问答")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    question = "如何使用 go-judge 编译 C++ 代码？"
    print(f"\n问题: {question}")
    
    response = requests.post(
        f"{BASE_URL}/api/ai/chat/",
        headers=headers,
        json={
            "question": question,
            "use_rag": True,  # 启用 RAG
            "top_k": 5
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ RAG 问答成功！")
        print(f"Token 使用: {result.get('tokens_used', 'N/A')}")
        print(f"剩余配额: {result.get('remaining_quota', 'N/A')}")
        
        if 'sources' in result:
            print(f"\n参考来源 ({len(result['sources'])} 个):")
            for source in result['sources'][:3]:
                print(f"  - {source}")
        
        print(f"\nAI 回答:\n{result['answer'][:500]}...")
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(f"错误信息: {response.json()}")

def test_usage_stats(token):
    """查看使用情况"""
    print("\n" + "=" * 60)
    print("步骤 4: 查看使用情况")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/ai/usage/",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ 使用情况:")
        print(f"  每日配额: {stats['daily_quota']}")
        print(f"  今日已用: {stats['used_today']}")
        print(f"  剩余配额: {stats['remaining']}")
        print(f"  历史记录: {stats['history_count']}")
    else:
        print(f"❌ 请求失败: {response.json()}")

def test_chat_history(token):
    """查看对话历史"""
    print("\n" + "=" * 60)
    print("步骤 5: 查看对话历史")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/ai/history/?limit=5",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 对话历史 (共 {result['count']} 条):")
        
        for i, chat in enumerate(result['results'][:5], 1):
            print(f"\n  [{i}] {chat['question'][:50]}...")
            print(f"      时间: {chat['created_at']}")
            print(f"      Token: {chat.get('tokens_used', 'N/A')}")
    else:
        print(f"❌ 请求失败: {response.json()}")

def main():
    """主函数"""
    print("\n🚀 开始测试 AI 问答功能\n")
    
    try:
        # 1. 登录
        token = login()
        
        # 2. 测试简单对话
        test_ai_chat(token)
        
        # 3. 测试 RAG 问答
        test_ai_chat_with_rag(token)
        
        # 4. 查看使用情况
        test_usage_stats(token)
        
        # 5. 查看对话历史
        test_chat_history(token)
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
