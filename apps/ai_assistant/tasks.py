"""
ChromaDB 初始化任务
在应用启动后异步初始化向量数据库，避免多进程并发冲突
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def init_chromadb_task(self):
    """
    异步初始化 ChromaDB
    
    这个任务会在 Django 应用启动后由 Celery worker 执行
    确保只有一个进程初始化 ChromaDB，避免表冲突
    """
    try:
        logger.info("=" * 60)
        logger.info("开始异步初始化 ChromaDB...")
        logger.info("=" * 60)
        
        # 导入 RAG 引擎（触发 ChromaDB 初始化）
        from apps.ai_assistant.rag_engine import get_rag_engine
        
        # 获取共享的 RAG 引擎实例
        engine = get_rag_engine()
        
        logger.info("✅ ChromaDB 初始化成功！")
        logger.info(f"   - Embedding 模型: {engine.vector_store.embedding_service.model_name}")
        logger.info(f"   - 向量维度: {engine.vector_store.embedding_service.dimension}")
        logger.info(f"   - ChromaDB 集合: {engine.vector_store.collection.name}")
        logger.info(f"   - 当前文档数: {engine.vector_store.get_document_count()}")
        logger.info("=" * 60)
        
        return {
            'status': 'success',
            'message': 'ChromaDB 初始化成功',
            'document_count': engine.vector_store.get_document_count()
        }
        
    except Exception as e:
        logger.error(f"❌ ChromaDB 初始化失败: {e}")
        logger.exception("详细错误信息:")
        
        # 重试
        raise self.retry(exc=e)


@shared_task
def check_chromadb_health():
    """
    检查 ChromaDB 健康状态
    """
    try:
        from apps.ai_assistant.rag_engine import get_rag_engine
        
        engine = get_rag_engine()
        doc_count = engine.vector_store.get_document_count()
        
        return {
            'status': 'healthy',
            'document_count': doc_count,
            'collection_name': engine.vector_store.collection.name
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }
