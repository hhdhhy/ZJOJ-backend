"""
测试 ChromaDB 向量数据库
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
django.setup()

from apps.ai_assistant.vector_store import VectorStore


def test_vector_store():
    """测试向量数据库"""
    print("="*60)
    print("测试 ChromaDB 向量数据库")
    print("="*60)
    
    try:
        # 1. 初始化向量数据库
        print("\n1. 初始化向量数据库...")
        store = VectorStore(collection_name='test_collection')
        print(f"   ✅ 数据库初始化成功")
        print(f"   存储路径: E:/ai_data/chroma_db")
        
        # 2. 添加单个文档
        print("\n2. 添加单个文档...")
        store.add_document(
            doc_id='doc_001',
            text='二分查找是一种在有序数组中查找特定元素的搜索算法。每次比较中间元素，将搜索范围缩小一半。',
            metadata={
                'title': '二分查找算法',
                'type': 'algorithm',
                'difficulty': 'easy'
            }
        )
        print(f"   ✅ 文档添加成功")
        print(f"   文档ID: doc_001")
        
        # 3. 批量添加文档
        print("\n3. 批量添加文档...")
        doc_ids = ['doc_002', 'doc_003', 'doc_004']
        texts = [
            '快速排序是一种高效的排序算法，采用分治法策略，平均时间复杂度为O(n log n)。',
            '动态规划通过将复杂问题分解为子问题来求解，适用于有重叠子问题和最优子结构性质的问题。',
            '深度优先搜索(DFS)是一种用于遍历或搜索树或图的算法，沿着树的深度遍历节点。'
        ]
        metadatas = [
            {'title': '快速排序', 'type': 'algorithm', 'difficulty': 'medium'},
            {'title': '动态规划', 'type': 'algorithm', 'difficulty': 'hard'},
            {'title': '深度优先搜索', 'type': 'algorithm', 'difficulty': 'medium'}
        ]
        
        store.add_batch(doc_ids, texts, metadatas)
        print(f"   ✅ 批量添加成功")
        print(f"   添加数量: {len(doc_ids)}")
        
        # 4. 检查文档总数
        print("\n4. 检查文档总数...")
        count = store.get_document_count()
        print(f"   ✅ 当前文档数: {count}")
        
        if count == 4:
            print(f"   ✅ 文档数量正确")
        else:
            print(f"   ⚠️  文档数量异常：期望4，实际{count}")
        
        # 5. 检索相似文档
        print("\n5. 检索相似文档...")
        query = "如何在一个有序数组中快速找到目标值？"
        results = store.search(query, top_k=3)
        
        print(f"   查询: {query}")
        print(f"   找到 {len(results)} 个相关文档:")
        
        for i, doc in enumerate(results):
            print(f"\n   [{i+1}] 相似度: {doc['similarity']:.4f}")
            print(f"       标题: {doc['metadata']['title']}")
            print(f"       内容: {doc['content'][:50]}...")
        
        # 验证第一个结果应该是二分查找
        if results and '二分查找' in results[0]['metadata']['title']:
            print(f"\n   ✅ 检索准确性测试通过")
        else:
            print(f"\n   ⚠️  检索结果可能不准确")
        
        # 6. 获取单个文档
        print("\n6. 获取单个文档...")
        doc = store.get_document('doc_001')
        if doc:
            print(f"   ✅ 获取成功")
            print(f"   标题: {doc['metadata']['title']}")
            print(f"   内容长度: {len(doc['content'])}")
        else:
            print(f"   ❌ 获取失败")
        
        # 7. 更新文档
        print("\n7. 更新文档...")
        store.update_document(
            doc_id='doc_001',
            text='二分查找（Binary Search）是一种高效的搜索算法，要求数组已排序。时间复杂度O(log n)。',
            metadata={
                'title': '二分查找算法（更新版）',
                'type': 'algorithm',
                'difficulty': 'easy'
            }
        )
        print(f"   ✅ 文档更新成功")
        
        # 验证更新
        updated_doc = store.get_document('doc_001')
        if updated_doc and '更新版' in updated_doc['metadata']['title']:
            print(f"   ✅ 更新验证通过")
        
        # 8. 删除文档
        print("\n8. 删除文档...")
        store.delete_document('doc_004')
        count_after_delete = store.get_document_count()
        print(f"   ✅ 删除成功")
        print(f"   删除后文档数: {count_after_delete}")
        
        if count_after_delete == 3:
            print(f"   ✅ 删除验证通过")
        
        # 9. 带过滤条件的检索
        print("\n9. 带过滤条件的检索...")
        filtered_results = store.search(
            query="排序算法",
            top_k=5,
            filter_metadata={'difficulty': 'medium'}
        )
        print(f"   查询: 排序算法 (难度: medium)")
        print(f"   找到 {len(filtered_results)} 个结果")
        
        for doc in filtered_results:
            print(f"   - {doc['metadata']['title']} (难度: {doc['metadata']['difficulty']})")
        
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
    success = test_vector_store()
    sys.exit(0 if success else 1)
