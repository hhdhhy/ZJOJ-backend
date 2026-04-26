"""
AI 知识问答功能本地测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def login():
    """登录获取 Token"""
    response = requests.post(
        f"{BASE_URL}/api/login/",
        json={"username": "coach", "password": "coach123"}
    )
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print(f"登录失败: {response.text}")
        return None

def create_knowledge_doc(token):
    """创建知识库文档"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "二分查找算法",
        "content": "二分查找是一种在有序数组中查找特定元素的搜索算法。搜索过程从数组的中间元素开始，如果中间元素正好是要查找的元素，则搜索过程结束；如果某一特定元素大于或者小于中间元素，则在数组大于或小于中间元素的那一半中查找，而且跟开始一样从中间元素开始比较。如果在某一步骤数组为空，则代表找不到。这种搜索算法每一次比较都使搜索范围缩小一半。时间复杂度为O(log n)。",
        "doc_type": "algorithm"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai/knowledge/",
        headers=headers,
        json=data
    )
    
    print("=== 创建知识库文档 ===")
    print(f"状态码: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()
    
    return response.status_code == 201 or (response.status_code == 200 and response.json().get('is_duplicate'))

def test_ai_chat(token, question="二分查找的时间复杂度是多少？"):
    """测试 AI 知识问答"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "question": question,
        "use_rag": True
    }
    
    print("=== AI 知识问答测试 ===")
    print(f"问题: {question}")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/chat/",
            headers=headers,
            json=data,
            timeout=60  # 设置60秒超时
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"回答: {result.get('answer', '无回答')}")
            print(f"使用的 Token 数: {result.get('tokens_used', 0)}")
            print(f"剩余配额: {result.get('remaining_quota', 0)}")
            
            if 'sources' in result:
                print("\n参考来源:")
                for i, source in enumerate(result['sources'], 1):
                    print(f"  {i}. {source.get('title', '未知')}")
        else:
            print(f"错误: {response.text}")
    except requests.exceptions.Timeout:
        print("❌ 请求超时（超过60秒）")
        print("可能原因:")
        print("  1. Embedding 模型正在下载")
        print("  2. 网络连接 HuggingFace 失败")
        print("  3. 模型文件过大导致加载缓慢")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print()

def main():
    print("🚀 开始测试 AI 知识问答功能\n")
    
    # 1. 登录
    print("步骤1: 登录...")
    token = login()
    if not token:
        return
    
    print("✅ 登录成功\n")
    
    # 2. 创建知识库文档
    print("步骤2: 创建知识库文档...")
    if create_knowledge_doc(token):
        print("✅ 文档创建成功\n")
    else:
        print("❌ 文档创建失败\n")
        return
    
    # 3. 等待向量同步
    print("步骤3: 等待3秒让向量同步完成...")
    import time
    time.sleep(3)
    print("✅ 等待完成\n")
    
    # 4. 测试 AI 问答
    print("步骤4: 测试 AI 知识问答...")
    test_ai_chat(token)
    
    # 5. 测试其他问题
    print("步骤5: 测试其他问题...")
    test_ai_chat(token, "什么是二分查找？")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main()
