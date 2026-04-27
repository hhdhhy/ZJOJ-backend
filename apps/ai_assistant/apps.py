"""
AI助手应用配置
"""
from django.apps import AppConfig


class AIAssistantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_assistant'
    
    def ready(self):
        """
        应用启动时触发 ChromaDB 异步初始化
        避免多进程并发冲突
        """
        import os
        
        # 检查是否已经触发过（避免重复触发）
        if hasattr(self, '_init_triggered'):
            return
        
        try:
            print("=" * 60)
            print("准备异步初始化 ChromaDB...")
            print("=" * 60)
            
            # 延迟导入，确保 Celery 已就绪
            from celery import current_app
            
            # 检查 Celery 是否可用
            if not current_app:
                print("⚠️ Celery 未就绪，将在首次请求时初始化")
                return
            
            # 触发异步任务
            from apps.ai_assistant.tasks import init_chromadb_task
            
            # 延迟 5 秒执行，确保所有服务都已启动
            init_chromadb_task.apply_async(countdown=5)
            
            print("🔄 ChromaDB 初始化任务已提交到 Celery")
            print("   将在 5 秒后由 Celery worker 执行...")
            
            # 标记已触发
            self._init_triggered = True
            
        except Exception as e:
            print(f"⚠️ 触发异步初始化失败: {e}")
            print("   将在首次请求时重试...")
            # 不抛出异常，允许应用继续启动
