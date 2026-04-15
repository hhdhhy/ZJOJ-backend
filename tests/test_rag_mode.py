"""
测试AI助手RAG模式
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def login():
    """登录获取Token"""
    login_data = {
        "username": "test_ai",
        "password": "TestPass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"✅ 登录成功")
        return token
    else:
        print(f"❌ 登录失败: {response.status_code}")
        return None


def test_rag_chat(token):
    """测试RAG模式的AI问答"""
    headers = {
        "Authorization": f"jwt {token}",
        "Content-Type": "application/json"
    }
    
    # 测试问题列表
    questions = [
        {
            "question": "什么是二分查找算法？如何实现？",
            "use_rag": True,
            "top_k": 3
        },
        {
            "question": "快速排序的时间复杂度是多少？有什么优化方法？",
            "use_rag": True,
            "top_k": 3
        },
        {
            "question": "BFS和DFS有什么区别？分别适用于什么场景？",
            "use_rag": True,
            "top_k": 3
        },
        {
            "question": "动态规划的核心思想是什么？能举个例子吗？",
            "use_rag": True,
            "top_k": 3
        },
        {
            "question": "哈希表的工作原理是什么？如何处理冲突？",
            "use_rag": True,
            "top_k": 3
        }
    ]
    
    for i, q in enumerate(questions, 1):
        print(f"\n{'=' * 60}")
        print(f"🔍 问题{i}: {q['question']}")
        print('=' * 60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/ai/chat/",
                headers=headers,
                json=q,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"\n💡 回答:")
                print(data['answer'][:500] + "..." if len(data['answer']) > 500 else data['answer'])
                
                print(f"\n📊 统计信息:")
                print(f"   Tokens使用: {data['tokens_used']}")
                print(f"   剩余配额: {data['remaining_quota']}")
                print(f"   Chat ID: {data['chat_id']}")
                
                if 'sources' in data and data['sources']:
                    print(f"\n📚 引用来源 ({len(data['sources'])}个):")
                    for j, source in enumerate(data['sources'][:2], 1):
                        title = source.get('metadata', {}).get('title', '未知')
                        similarity = source.get('similarity', 0)
                        print(f"   {j}. {title} (相似度: {similarity:.2%})")
                        print(f"      内容: {source['content'][:100]}...")
                
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        # 避免频率限制，稍微等待
        import time
        time.sleep(2)


def main():
    print("\n" + "🚀" * 30)
    print("开始测试AI助手RAG模式")
    print("🚀" * 30 + "\n")
    
    # 检查服务器
    try:
        response = requests.get(f"{BASE_URL}/api/", timeout=5)
        print(f"✅ 服务器正常运行\n")
    except:
        print("❌ 无法连接到服务器，请先启动Django服务")
        return
    
    # 登录
    token = login()
    if not token:
        print("\n❌ 登录失败，终止测试")
        return
    
    # 测试RAG问答
    test_rag_chat(token)
    
    print("\n" + "=" * 60)
    print("✅ RAG测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
