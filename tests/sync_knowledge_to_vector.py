"""
将知识库文档同步到向量数据库
"""
import os
import sys
import django

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
django.setup()

from apps.ai_assistant.models import KnowledgeBase
from apps.ai_assistant.vector_store import VectorStore
from apps.ai_assistant.embedding_service import EmbeddingService

print("=" * 60)
print("开始同步知识库到向量数据库")
print("=" * 60)

# 初始化服务
embedding_service = EmbeddingService()
vector_store = VectorStore()

# 获取所有活跃的文档
docs = KnowledgeBase.objects.filter(is_active=True)
print(f"\n找到 {docs.count()} 个活跃文档\n")

success_count = 0
error_count = 0

for doc in docs:
    try:
        print(f"处理: {doc.title}")
        
        # 检查是否已存在
        existing = vector_store.collection.get(ids=[doc.vector_id])
        if existing['ids']:
            print(f"  ⚠️  已存在，跳过")
            continue
        
        # 生成嵌入向量
        embedding = embedding_service.encode(doc.content)
        
        # 添加到向量数据库
        metadata = {
            'doc_id': doc.id,
            'title': doc.title,
            'doc_type': doc.doc_type,
            'source': doc.source or ''
        }
        
        vector_store.add_document(
            doc_id=doc.vector_id,
            text=doc.content,
            metadata=metadata
        )
        
        print(f"  ✅ 成功添加")
        success_count += 1
        
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        error_count += 1

print("\n" + "=" * 60)
print(f"同步完成！")
print(f"  成功: {success_count}")
print(f"  失败: {error_count}")
print(f"  总计: {docs.count()}")
print("=" * 60)
