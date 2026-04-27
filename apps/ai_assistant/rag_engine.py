"""
RAG 检索增强生成引擎
结合向量检索和LLM生成答案
"""
from .vector_store import get_vector_store
from .llm_client import LLMClient
from .prompts import RAG_PROMPT

# 全局单例
_rag_engine_instance = None

def get_rag_engine():
    """
    获取共享的 RAGEngine 单例
    
    Returns:
        RAGEngine 实例
    """
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine()
    return _rag_engine_instance


class RAGEngine:
    """RAG 检索增强生成引擎"""
    
    def __init__(self):
        """初始化 RAG 引擎"""
        # 使用共享的 VectorStore 单例
        self.vector_store = get_vector_store()
        self.llm_client = LLMClient()
    
    def ask(self, question: str, top_k=5) -> dict:
        """
        智能问答
        
        Args:
            question: 用户问题
            top_k: 检索文档数量
        
        Returns:
            {
                'answer': '答案',
                'sources': [...],  # 引用来源
                'tokens_used': 123  # Token消耗
            }
        """
        # 1. 检索相关文档
        relevant_docs = self.vector_store.search(question, top_k=top_k)
        
        # 2. 组装上下文
        if relevant_docs:
            context = '\n\n'.join([
                f"【文档{i+1}】{doc['content']}" 
                for i, doc in enumerate(relevant_docs)
            ])
            
            # 3. 构建 Prompt
            messages = [
                {'role': 'system', 'content': RAG_PROMPT},
                {'role': 'user', 'content': f'问题：{question}\n\n相关知识：\n{context}'}
            ]
        else:
            # 没有相关知识，直接让LLM回答
            messages = [
                {'role': 'system', 'content': RAG_PROMPT},
                {'role': 'user', 'content': f'问题：{question}\n\n注意：知识库中没有相关内容，请根据你的知识回答。'}
            ]
        
        # 4. 调用 LLM 生成答案
        result = self.llm_client.chat(messages)
        
        # 5. 返回结果
        return {
            'answer': result['answer'],
            'sources': [
                {
                    'id': doc['id'],
                    'title': doc['metadata'].get('title', ''),
                    'type': doc['metadata'].get('type', ''),
                    'similarity': doc.get('similarity', 0)
                }
                for doc in relevant_docs
            ],
            'tokens_used': result['tokens_used']
        }
    
    def chat(self, question: str, history=None) -> dict:
        """
        简单对话（不使用RAG）
        
        Args:
            question: 用户问题
            history: 对话历史（可选）
        
        Returns:
            {
                'answer': '答案',
                'tokens_used': 123
            }
        """
        from .prompts import CHAT_SYSTEM_PROMPT
        
        messages = [{'role': 'system', 'content': CHAT_SYSTEM_PROMPT}]
        
        # 添加历史对话
        if history:
            messages.extend(history)
        
        messages.append({'role': 'user', 'content': question})
        
        result = self.llm_client.chat(messages)
        
        return {
            'answer': result['answer'],
            'tokens_used': result['tokens_used']
        }
    
    def search_knowledge_base(self, query: str, doc_type=None, top_k=5):
        """
        搜索知识库（支持按类型过滤）
        
        Args:
            query: 查询关键词
            doc_type: 文档类型过滤（algorithm/solution/error_solution等）
            top_k: 返回数量
        
        Returns:
            相关文档列表
        """
        results = self.vector_store.search(query, top_k=top_k * 2)  # 多检索一些用于过滤
        
        # 按类型过滤
        if doc_type:
            filtered = [
                doc for doc in results
                if doc.get('metadata', {}).get('type') == doc_type
            ]
        else:
            filtered = results
        
        # 格式化返回结果
        formatted_results = []
        for doc in filtered[:top_k]:
            formatted_results.append({
                'id': doc['id'],
                'title': doc['metadata'].get('title', ''),
                'content': doc['content'],
                'doc_type': doc['metadata'].get('type', ''),
                'score': doc.get('similarity', 0),
            })
        
        return formatted_results


# 测试代码
if __name__ == "__main__":
    import os
    import sys
    import django
    
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
    django.setup()
    
    print("="*60)
    print("测试 RAG 引擎")
    print("="*60)
    
    try:
        engine = RAGEngine()
        
        # 先添加一些测试数据
        print("\n1. 添加测试数据...")
        engine.vector_store.add_document(
            doc_id='test_001',
            text='二分查找是一种在有序数组中查找特定元素的算法。每次比较中间元素，如果目标值小于中间元素，则在左半部分继续查找；如果大于中间元素，则在右半部分继续查找。时间复杂度为O(log n)。',
            metadata={'title': '二分查找详解', 'type': 'algorithm'}
        )
        print(f"   ✅ 添加测试文档成功")
        
        # 测试 RAG 问答
        print("\n2. 测试 RAG 问答...")
        question = "二分查找的时间复杂度是多少？"
        result = engine.ask(question, top_k=3)
        
        print(f"   问题: {question}")
        print(f"   答案: {result['answer'][:100]}...")
        print(f"   Token消耗: {result['tokens_used']}")
        print(f"   引用来源数: {len(result['sources'])}")
        
        if result['sources']:
            print(f"   第一个来源: {result['sources'][0]['title']}")
        
        print("\n3. 测试简单对话...")
        chat_result = engine.chat("你好，请介绍一下自己")
        print(f"   答案: {chat_result['answer'][:100]}...")
        print(f"   Token消耗: {chat_result['tokens_used']}")
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)
        
        # 清理测试数据
        engine.vector_store.delete_document('test_001')
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
