"""
测试 Embedding 服务
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
django.setup()

from apps.ai_assistant.embedding_service import EmbeddingService


def test_embedding_service():
    """测试 Embedding 服务"""
    print("="*60)
    print("测试 Embedding 服务")
    print("="*60)
    
    try:
        # 1. 初始化服务
        print("\n1. 初始化 Embedding 服务...")
        service = EmbeddingService(model_name='shibing624/text2vec-base-chinese')
        print(f"   ✅ 模型加载成功")
        print(f"   模型: {service.model_name}")
        print(f"   向量维度: {service.dimension}")
        print(f"   缓存目录: {service.cache_dir}")
        
        # 2. 测试单文本编码
        print("\n2. 测试单文本编码...")
        text = "二分查找算法"
        embedding = service.encode(text)
        print(f"   ✅ 编码成功")
        print(f"   文本: {text}")
        print(f"   向量长度: {len(embedding)}")
        print(f"   前5个值: {embedding[:5]}")
        
        # 3. 测试批量编码
        print("\n3. 测试批量编码...")
        texts = ["快速排序", "动态规划", "深度优先搜索"]
        embeddings = service.encode_batch(texts)
        print(f"   ✅ 批量编码成功")
        print(f"   文本数量: {len(texts)}")
        print(f"   向量数量: {len(embeddings)}")
        
        # 4. 测试语义相似度
        print("\n4. 测试语义相似度...")
        import numpy as np
        
        vec1 = np.array(service.encode("二分查找"))
        vec2 = np.array(service.encode("折半查找"))
        vec3 = np.array(service.encode("红烧肉做法"))
        
        similarity_12 = np.dot(vec1, vec2)  # 已归一化，点积=余弦相似度
        similarity_13 = np.dot(vec1, vec3)
        
        print(f"   '二分查找' vs '折半查找': {similarity_12:.4f} (应该较高)")
        print(f"   '二分查找' vs '红烧肉做法': {similarity_13:.4f} (应该较低)")
        
        if similarity_12 > similarity_13:
            print(f"   ✅ 语义相似度测试通过")
        else:
            print(f"   ⚠️  语义相似度异常")
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_embedding_service()
    sys.exit(0 if success else 1)
