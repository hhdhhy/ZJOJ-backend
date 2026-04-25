#!/usr/bin/env python3
"""
同步知识库到向量数据库
将所有 MySQL 中的知识库文档同步到 ChromaDB
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
django.setup()

from apps.ai_assistant.models import KnowledgeBase
from apps.ai_assistant.rag_engine import RAGEngine


def sync_knowledge_base_to_vector():
    """同步所有知识库文档到向量数据库"""
    
    print("=" * 60)
    print("开始同步知识库到向量数据库...")
    print("=" * 60)
    
    # 获取所有启用的知识库文档
    docs = KnowledgeBase.objects.filter(is_active=True)
    total = docs.count()
    
    print(f"\n找到 {total} 个启用的知识库文档\n")
    
    if total == 0:
        print("⚠️ 没有需要同步的文档")
        return
    
    engine = RAGEngine()
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for doc in docs:
        try:
            # 检查是否已存在
            existing = engine.vector_store.get_document(doc.vector_id)
            if existing:
                print(f"⊘ 跳过（已存在）: {doc.title}")
                skipped_count += 1
                continue
            
            # 添加到向量数据库
            engine.vector_store.add_document(
                doc_id=doc.vector_id,
                text=doc.content,
                metadata={
                    'title': doc.title,
                    'type': doc.doc_type,
                    'doc_id': doc.id,
                    'error_type': doc.error_type or '',
                    'source': doc.source or '',
                }
            )
            
            print(f"✓ 同步成功: {doc.title}")
            success_count += 1
            
        except Exception as e:
            print(f"✗ 同步失败: {doc.title} - {str(e)}")
            failed_count += 1
    
    print("\n" + "=" * 60)
    print("同步完成！")
    print(f"  成功: {success_count} 个")
    print(f"  跳过: {skipped_count} 个")
    print(f"  失败: {failed_count} 个")
    print(f"  总计: {total} 个")
    print("=" * 60)
    
    # 显示向量数据库统计
    vector_count = engine.vector_store.get_document_count()
    print(f"\n向量数据库中文档总数: {vector_count}")


if __name__ == '__main__':
    sync_knowledge_base_to_vector()
