"""
AI助手应用配置
"""
from django.apps import AppConfig


class AIAssistantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_assistant'
    
    def ready(self):
        """
        应用启动时预加载 RAG 引擎
        避免首次请求时的长时间等待
        """
        import os
        
        # 只在主进程中预加载（避免在 manage.py 命令中加载）
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        try:
            print("=" * 60)
            print("预加载 AI 助手 RAG 引擎...")
            print("=" * 60)
            
            # 导入并初始化 RAG 引擎（触发模型加载）
            from apps.ai_assistant.rag_engine import get_rag_engine
            
            # 异步加载，不阻塞应用启动
            import threading
            
            def load_rag_engine():
                try:
                    engine = get_rag_engine()
                    print("✅ RAG 引擎预加载完成！")
                    print(f"   - Embedding 模型: {engine.embedding_model.model_name}")
                    print(f"   - 向量维度: {engine.embedding_model.dimension}")
                    print(f"   - ChromaDB 集合: {engine.collection.name}")
                except Exception as e:
                    print(f"⚠️ RAG 引擎预加载失败: {e}")
                    print("   将在首次请求时重试...")
            
            # 在后台线程中加载
            thread = threading.Thread(target=load_rag_engine, daemon=True)
            thread.start()
            print("🔄 RAG 引擎正在后台加载...")
            
        except Exception as e:
            print(f"⚠️ 预加载初始化失败: {e}")
            # 不抛出异常，允许应用继续启动
