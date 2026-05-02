# AI 助手系统详细实现 - 补充文档

> 本文档补充 `AI_ASSISTANT_DETAILED.md` 中遗漏的核心功能和实现细节。

---

## 📋 补充内容索引

1. [RAG 引擎实际实现（RAGEngine）](#1-rag-引擎实际实现ragengine)
2. [向量数据库管理器（VectorStore）](#2-向量数据库管理器vectorstore)
3. [LLM 客户端封装（LLMClient）](#3-llm-客户端封装llmclient)
4. [学情分析系统](#4-学情分析系统)
5. [错误解决方案推送系统](#5-错误解决方案推送系统)
6. [配额和限流管理](#6-配额和限流管理)
7. [知识库管理系统](#7-知识库管理系统)
8. [异步任务初始化](#8-异步任务初始化)
9. [API 调用优化](#9-api-调用优化)
10. [数据模型详细说明](#10-数据模型详细说明)

---

## 1. RAG 引擎实际实现（RAGEngine）

### 1.1 文件位置
`apps/ai_assistant/rag_engine.py`

### 1.2 完整类结构

```python
class RAGEngine:
    """RAG 检索增强生成引擎"""
    
    def __init__(self):
        """初始化 RAG 引擎"""
        self.vector_store = get_vector_store()  # 使用共享单例
        self.llm_client = LLMClient()
        self.embedding_model = self.vector_store.embedding_service
    
    def ask(self, question: str, top_k: int = 5) -> dict:
        """
        RAG 模式问答（检索 + 生成）
        
        Args:
            question: 用户问题
            top_k: 检索文档数量
        
        Returns:
            {
                'answer': str,          # AI 回答
                'sources': list,        # 引用来源
                'tokens_used': int      # 消耗的 token 数
            }
        """
    
    def chat(self, question: str) -> dict:
        """
        简单对话模式（不调用知识库）
        
        Args:
            question: 用户问题
        
        Returns:
            {
                'answer': str,
                'tokens_used': int
            }
        """
    
    def search_knowledge_base(self, query: str, doc_type=None, top_k=5) -> list:
        """
        搜索知识库（支持类型过滤）
        
        Args:
            query: 查询关键词
            doc_type: 文档类型过滤（algorithm/solution/error_solution等）
            top_k: 返回数量
        
        Returns:
            相关文档列表
        """
```

### 1.3 全局单例访问

```python
# 全局单例模式
_rag_engine_instance = None

def get_rag_engine():
    """获取共享的 RAGEngine 单例"""
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine()
    return _rag_engine_instance
```

**优势**：
- 避免重复加载 Embedding 模型（节省 ~2GB 内存）
- 避免 ChromaDB 连接冲突
- 提高首次请求响应速度

---

## 2. 向量数据库管理器（VectorStore）

### 2.1 文件位置
`apps/ai_assistant/vector_store.py`

### 2.2 完整功能

```python
class VectorStore:
    """ChromaDB 向量数据库"""
    
    def __init__(self, collection_name='knowledge_base'):
        """初始化向量数据库"""
        # 配置 ChromaDB 持久化路径
        persist_directory = getattr(settings, 'CHROMA_DB_PATH', 
                                    '/home/zjoj/ai_data/chroma_db')
        
        # 创建客户端（关闭遥测）
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 初始化 Embedding 服务
        self.embedding_service = EmbeddingService()
        
        # 获取或创建集合（余弦相似度）
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={'hnsw:space': 'cosine'}
        )
    
    def add_document(self, doc_id: str, text: str, metadata: dict):
        """添加文档到向量数据库"""
        embedding = self.embedding_service.encode(text)
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text]
        )
    
    def add_batch(self, doc_ids: list, texts: list, metadatas: list):
        """批量添加文档"""
        embeddings = self.embedding_service.encode_batch(texts)
        self.collection.add(
            ids=doc_ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )
    
    def search(self, query: str, top_k=5, filter_metadata=None) -> list:
        """
        检索相似文档
        
        Returns:
            [
                {
                    'id': str,
                    'content': str,
                    'metadata': dict,
                    'distance': float,
                    'similarity': float  # 1 - distance
                }
            ]
        """
    
    def delete_document(self, doc_id: str):
        """删除文档"""
    
    def delete_by_filter(self, filter_metadata: dict):
        """根据过滤条件删除文档"""
    
    def update_document(self, doc_id: str, text: str, metadata: dict):
        """更新文档"""
    
    def get_document_count(self) -> int:
        """获取文档总数"""
    
    def get_document(self, doc_id: str) -> dict:
        """获取单个文档"""
```

### 2.3 全局单例访问

```python
_vector_store_instance = None

def get_vector_store(collection_name='knowledge_base'):
    """获取共享的 VectorStore 单例"""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore(collection_name)
    return _vector_store_instance
```

---

## 3. LLM 客户端封装（LLMClient）

### 3.1 文件位置
`apps/ai_assistant/llm_client.py`

### 3.2 完整功能

```python
class LLMClient:
    """LLM API 客户端（支持 DeepSeek）"""
    
    def __init__(self):
        """初始化 LLM 客户端"""
        self.api_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
        self.model = getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat')
        self.base_url = getattr(settings, 'DEEPSEEK_BASE_URL', 
                               'https://api.deepseek.com')
        
        # 初始化 OpenAI 兼容客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(self, messages: list, temperature=0.7, max_tokens=2000) -> dict:
        """
        调用 LLM API
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度参数 (0-1)
            max_tokens: 最大 token 数
        
        Returns:
            {
                'content': str,         # AI 回答
                'tokens_used': int,     # 消耗的 token 数
                'model': str            # 使用的模型
            }
        """
    
    def generate_answer(self, question: str, context: str = '') -> dict:
        """
        生成回答（自动构建 prompt）
        
        Args:
            question: 用户问题
            context: 上下文信息（可选）
        
        Returns:
            {
                'content': str,
                'tokens_used': int
            }
        """
```

### 3.3 Prompt 模板

```python
RAG_PROMPT_TEMPLATE = """你是一个专业的编程竞赛助手。请根据以下上下文信息回答用户的问题。

上下文信息：
{context}

用户问题：{question}

回答要求：
1. 基于上下文信息回答问题
2. 如果上下文中没有相关信息，请说明你不知道
3. 回答要详细、准确、有条理
4. 使用 Markdown 格式

请回答："""

CHAT_PROMPT_TEMPLATE = """你是一个专业的编程竞赛助手。请回答用户的问题。

用户问题：{question}

请回答："""
```

---

## 4. 学情分析系统

### 4.1 文件位置
`apps/ai_assistant/learning_analytics.py`

### 4.2 核心功能

```python
class LearningAnalyticsService:
    """学情分析服务"""
    
    @classmethod
    def get_or_generate_student_report(cls, user, days=7) -> LearningReport:
        """
        获取或生成学生个性化学情报告
        
        Args:
            user: 用户对象
            days: 统计天数
        
        Returns:
            LearningReport 对象
        """
    
    @classmethod
    def get_or_generate_class_report(cls, class_obj, user, days=7) -> LearningReport:
        """
        获取或生成班级共性学情报告
        
        Args:
            class_obj: 班级对象
            user: 教练用户
            days: 统计天数
        
        Returns:
            LearningReport 对象
        """
    
    @classmethod
    def analyze_student_performance(cls, user, days=7) -> dict:
        """
        分析学生表现
        
        Returns:
            {
                'total_submissions': int,
                'ac_count': int,
                'wa_count': int,
                'tle_count': int,
                'mle_count': int,
                're_count': int,
                'ce_count': int,
                'ac_rate': float,
                'problem_solved': int,
                'difficulty_distribution': dict,
                'error_distribution': dict,
                'weak_areas': list  # 薄弱环节
            }
        """
    
    @classmethod
    def analyze_class_performance(cls, class_obj, days=7) -> dict:
        """
        分析班级表现
        
        Returns:
            {
                'total_students': int,
                'active_students': int,
                'total_submissions': int,
                'ac_rate': float,
                'common_difficult_problems': list,  # 共性难题
                'common_errors': list,  # 常见错误
                'progress_trend': dict  # 进度趋势
            }
        """
    
    @classmethod
    def generate_recommendations(cls, analysis_result, report_type) -> list:
        """
        生成学习建议
        
        Args:
            analysis_result: 分析结果
            report_type: 报告类型（student/class）
        
        Returns:
            建议列表
        """
```

### 4.3 API 接口

**学生报告**：`GET /api/ai/report/student/?days=7`

**班级报告**：`GET /api/ai/report/class/<int:class_id>/?days=7`

---

## 5. 错误解决方案推送系统

### 5.1 文件位置
`apps/ai_assistant/error_pusher.py`

### 5.2 核心功能

```python
class ErrorSolutionPusher:
    """错误解决方案推送器"""
    
    @staticmethod
    def push_on_judge_failure(submission_id) -> list:
        """
        在判题失败后推送解决方案
        
        Args:
            submission_id: 提交记录ID
        
        Returns:
            [
                {
                    'title': str,
                    'content': str,  # 前500字
                    'doc_type': str,
                    'relevance_score': float
                }
            ]
        """
        # 1. 获取提交记录
        submission = Submission.objects.get(id=submission_id)
        
        # 2. 只对非AC提交推送
        if submission.result == 'AC':
            return []
        
        # 3. 构建查询关键词
        query_keywords = [
            f"{submission.problem.problem_id} {submission.result}",
            f"{submission.problem.title} {submission.get_result_display()}",
            submission.result,
        ]
        
        # 4. 检索知识库（doc_type='error_solution'）
        engine = RAGEngine()
        solutions = []
        
        for query in query_keywords:
            result = engine.search_knowledge_base(
                query=query,
                doc_type='error_solution',
                top_k=3
            )
            
            for doc in result:
                solutions.append({
                    'title': doc['title'],
                    'content': doc['content'][:500],
                    'doc_type': doc['doc_type'],
                    'relevance_score': doc.get('score', 0),
                })
            
            if len(solutions) >= 3:
                break
        
        # 5. 去重并返回
        return unique_solutions[:3]
    
    @staticmethod
    def get_error_suggestions(problem_id, error_type, top_k=3) -> list:
        """
        获取特定题目和错误类型的建议
        
        Args:
            problem_id: 题目ID
            error_type: 错误类型（WA/TLE/MLE/RE/CE）
            top_k: 返回数量
        
        Returns:
            建议列表
        """
```

### 5.3 API 接口

**接口**：`GET /api/ai/error-solution/<int:submission_id>/`

**使用场景**：
- 学生提交代码后收到 WA/TLE/RE 等错误
- 前端调用此接口获取解决建议
- 帮助学生快速定位问题

---

## 6. 配额和限流管理

### 6.1 文件位置
`apps/ai_assistant/limits.py`

### 6.2 核心功能

```python
class AILimitChecker:
    """AI助手限制检查器"""
    
    # 配置常量
    MAX_HISTORY_PER_USER = 100  # 历史对话上限
    DAILY_QUOTA = 50            # 每日配额（次）
    RATE_LIMIT_WINDOW = 60      # 频率限制窗口（秒）
    RATE_LIMIT_MAX = 10         # 窗口内最大请求数
    
    @classmethod
    def check_daily_quota(cls, user) -> UserProfile:
        """
        检查每日配额
        
        Returns:
            UserProfile 对象（配额充足时）
        
        Raises:
            Throttled: 如果配额已用完
        """
    
    @classmethod
    def check_rate_limit(cls, user):
        """
        检查频率限制（60秒内最多10次）
        
        Raises:
            Throttled: 如果请求过于频繁
        """
    
    @classmethod
    def increment_usage(cls, user):
        """增加使用次数"""
    
    @classmethod
    def trim_history(cls, user):
        """修剪历史记录，保留最新的100条"""
```

### 6.3 使用模式

```python
# 标准配额检查模式
try:
    profile = AILimitChecker.check_daily_quota(user)
except Throttled as e:
    return Response({'error': str(e.detail)}, status=429)

# 执行业务逻辑
result = do_something()

# 记录使用
AILimitChecker.increment_usage(user)

# 修剪历史
AILimitChecker.trim_history(user)
```

---

## 7. 知识库管理系统

### 7.1 文件位置
`apps/ai_assistant/views.py` - `KnowledgeBaseView`

### 7.2 完整 CRUD 操作

```python
class KnowledgeBaseView(APIView):
    """知识库管理"""
    
    def get(self, request, kb_id=None):
        """
        获取知识库文档
        - 提供 kb_id：返回单个文档详情
        - 不提供 kb_id：返回文档列表（支持过滤）
        """
    
    def post(self, request):
        """创建知识库文档（仅教练或管理员）"""
        # 幂等性检查：title + doc_type + error_type
        # 异步同步到向量数据库
    
    def put(self, request, kb_id):
        """更新知识库文档（仅教练或管理员）"""
        # 异步更新向量数据库
    
    def delete(self, request, kb_id):
        """删除知识库文档（仅教练或管理员）"""
        # 异步从向量数据库删除
```

### 7.3 向量数据库同步机制

```python
# 创建时同步
def post(self, request):
    doc = serializer.save()
    
    # 异步同步到向量数据库
    import threading
    def sync_to_vector():
        engine = RAGEngine()
        engine.vector_store.add_document(
            doc_id=doc.vector_id,
            text=doc.content,
            metadata={...}
        )
    
    thread = threading.Thread(target=sync_to_vector)
    thread.daemon = True
    thread.start()
```

---

## 8. 异步任务初始化

### 8.1 文件位置
- `apps/ai_assistant/apps.py` - Django AppConfig
- `apps/ai_assistant/tasks.py` - Celery 任务

### 8.2 实现原理

**问题**：Gunicorn 多进程并发初始化 ChromaDB 导致表冲突

**解决方案**：使用 Celery 异步任务延迟初始化

```python
# apps.py
class AIAssistantConfig(AppConfig):
    def ready(self):
        # 应用启动时触发异步任务
        from apps.ai_assistant.tasks import init_chromadb_task
        init_chromadb_task.apply_async(countdown=5)  # 延迟5秒

# tasks.py
@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def init_chromadb_task(self):
    """异步初始化 ChromaDB"""
    from apps.ai_assistant.rag_engine import get_rag_engine
    engine = get_rag_engine()  # 触发初始化
```

### 8.3 配置要求

```yaml
# docker-compose.yml
environment:
  - HF_ENDPOINT=https://hf-mirror.com  # 国内镜像加速

command: >
  gunicorn --workers 4 --worker-class gevent --threads 2 
           --bind 0.0.0.0:8000 --timeout 300  # 增加超时时间
           ZJOJ.wsgi:application
```

---

## 9. API 调用优化

### 9.1 文件位置
`apps/ai_assistant/api_optimizer.py`

### 9.2 缓存机制

```python
class APICallOptimizer:
    """API 调用优化器"""
    
    @staticmethod
    def cached_api_call(func):
        """
        装饰器：缓存 API 调用结果（24小时）
        
        使用场景：相同问题的重复询问
        """
    
    @staticmethod
    def retry_on_failure(max_retries=3, delay=1, backoff=2):
        """
        装饰器：失败重试（指数退避）
        
        使用场景：网络不稳定时的 LLM API 调用
        """
```

### 9.3 缓存效果

- **缓存命中率**：30-50%
- **响应时间**：10-30秒 → <100ms
- **API 成本**：降低 30-50%

---

## 10. 数据模型详细说明

### 10.1 KnowledgeBase 模型

```python
class KnowledgeBase(models.Model):
    DOC_TYPE_CHOICES = [
        ('algorithm', '算法讲解'),
        ('solution', '题解'),
        ('template', '代码模板'),
        ('concept', '概念说明'),
        ('error_solution', '错误解决方案'),  # 新增
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)
    tags = models.ManyToManyField('problem.Tag', blank=True)
    problem = models.ForeignKey('problem.Problem', null=True, blank=True)
    error_type = models.CharField(max_length=50, blank=True, default='')
    source = models.CharField(max_length=500, blank=True)
    vector_id = models.CharField(max_length=100, unique=True)  # UUID
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'doc_type', 'error_type'],
                name='unique_knowledge_doc'  # 防止重复
            )
        ]
```

### 10.2 UserProfile 模型

```python
class UserProfile(models.Model):
    """用户AI助手配置"""
    user = models.OneToOneField(OJUser, on_delete=models.CASCADE)
    daily_quota = models.IntegerField(default=50)  # 每日配额
    used_today = models.IntegerField(default=0)   # 今日已用
    last_reset_date = models.DateField(auto_now_add=True)
    max_history = models.IntegerField(default=100)  # 最大历史记录
```

### 10.3 ChatHistory 模型

```python
class ChatHistory(models.Model):
    """对话历史"""
    user = models.ForeignKey(OJUser, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list)  # 引用来源
    model_used = models.CharField(max_length=50, default='glm-4')
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 10.4 LearningReport 模型

```python
class LearningReport(models.Model):
    """学情报告"""
    REPORT_TYPE_CHOICES = [
        ('student', '学生个性报告'),
        ('class', '班级共性报告'),
    ]
    
    user = models.ForeignKey(OJUser, on_delete=models.CASCADE)
    class_obj = models.ForeignKey('ojauth.Class', null=True, blank=True)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    summary = models.TextField()
    statistics = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)
    generated_at = models.DateTimeField(auto_now_add=True)
```

---

## 📊 完整 API 接口清单

### 基础功能

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| AI 问答 | POST | `/api/ai/chat/` | RAG 模式或简单对话 |
| 对话历史 | GET | `/api/ai/history/` | 获取历史列表 |
| 历史详情 | GET | `/api/ai/history/<id>/` | 获取单条记录 |
| 清空历史 | DELETE | `/api/ai/history/clear/` | 清空所有历史 |
| 使用情况 | GET | `/api/ai/usage/` | 查看配额使用 |

### 学情分析

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 学生报告 | GET | `/api/ai/report/student/` | 学生个性化报告 |
| 班级报告 | GET | `/api/ai/report/class/<id>/` | 班级共性报告 |

### 错误解决方案

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 错误方案 | GET | `/api/ai/error-solution/<id>/` | 获取错误解决方案 |

### 知识库管理

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 创建文档 | POST | `/api/ai/knowledge/` | 创建知识库文档 |
| 获取列表 | GET | `/api/ai/knowledge/` | 获取文档列表 |
| 获取详情 | GET | `/api/ai/knowledge/<id>/` | 获取单个文档 |
| 更新文档 | PUT | `/api/ai/knowledge/<id>/` | 更新文档 |
| 删除文档 | DELETE | `/api/ai/knowledge/<id>/` | 删除文档 |

---

## 🐛 已知问题和解决方案

### 1. ChromaDB 多进程表冲突

**错误**：`table embeddings_queue_config already exists`

**解决**：使用 Celery 异步任务初始化（已实现）

### 2. Embedding 模型加载超时

**问题**：首次请求时模型加载需要 10-30 秒

**解决**：
- Celery 预加载
- Gunicorn 超时时间 300 秒
- 模型本地缓存

### 3. 向量数据库同步失败

**问题**：异步线程同步失败无重试机制

**建议**：使用 Celery 异步任务替代 threading

---

## 📝 最佳实践

### 1. 添加错误解决方案文档

```python
doc = KnowledgeBase.objects.create(
    title='RE 运行时错误解决方案',
    doc_type='error_solution',
    error_type='RE',
    content='''# RE (Runtime Error)

## 常见原因
1. 数组越界
2. 空指针/除零错误
...
''',
    source='ZJOJ 知识库',
    is_active=True
)
```

### 2. 使用共享单例

```python
# 推荐：使用全局单例
from apps.ai_assistant.rag_engine import get_rag_engine

engine = get_rag_engine()
result = engine.ask(question)

# 不推荐：重复创建实例
engine = RAGEngine()  # 会重复加载模型
```

### 3. 配额检查标准模式

```python
try:
    profile = AILimitChecker.check_daily_quota(user)
except Throttled as e:
    return Response({'error': str(e.detail)}, status=429)

# 业务逻辑
result = do_something()

# 记录使用
AILimitChecker.increment_usage(user)
```

---

## 🔗 相关文档

- [AI 助手系统使用指南](06-MODULES/ai-assistant.md)
- [AI 助手系统补充文档](AI_ASSISTANT_SUPPLEMENT.md)
- [API 参考文档](04-API_REFERENCE.md)
- [数据库设计文档](07-DATABASE.md)

---

**文档版本**：v1.0  
**更新日期**：2026-04-27  
**维护者**：ZJOJ 开发团队
