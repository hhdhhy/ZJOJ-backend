# AI 助手系统文档查漏补缺

## 📋 补充内容概述

本文档补充了 `docs/06-MODULES/ai-assistant.md` 中遗漏的重要功能和配置说明。

---

## 🔧 遗漏的核心功能

### 1. ChromaDB 异步初始化机制

**实现位置**：`apps/ai_assistant/apps.py` + `apps/ai_assistant/tasks.py`

**功能说明**：
为避免 Gunicorn 多进程并发初始化 ChromaDB 导致的表冲突问题，系统采用了 Celery 异步任务初始化机制。

**工作流程**：
```
Django 应用启动
    ↓
AppConfig.ready() 触发
    ↓
提交 Celery 异步任务（延迟5秒）
    ↓
Celery Worker 执行 init_chromadb_task
    ↓
初始化 RAG 引擎 + ChromaDB 连接
```

**关键代码**：
```python
# apps.py
class AIAssistantConfig(AppConfig):
    def ready(self):
        from apps.ai_assistant.tasks import init_chromadb_task
        init_chromadb_task.apply_async(countdown=5)  # 延迟5秒执行

# tasks.py
@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def init_chromadb_task(self):
    from apps.ai_assistant.rag_engine import get_rag_engine
    engine = get_rag_engine()  # 触发 ChromaDB 初始化
```

**配置要求**：
- 必须启动 Celery Worker 服务
- Redis 作为消息代理和结果后端
- Gunicorn 超时时间设置为 300 秒

---

### 2. 共享实例模式（单例模式）

**实现位置**：`apps/ai_assistant/vector_store.py` + `apps/ai_assistant/rag_engine.py`

**功能说明**：
为避免多进程重复初始化资源，系统实现了全局共享单例模式。

**实现方式**：
```python
# vector_store.py
_vector_store_instance = None

def get_vector_store(collection_name='knowledge_base'):
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore(collection_name)
    return _vector_store_instance

# rag_engine.py
_rag_engine_instance = None

def get_rag_engine():
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine()  # 使用共享的 VectorStore
    return _rag_engine_instance
```

**优势**：
- 节省内存（避免重复加载 Embedding 模型）
- 避免 ChromaDB 连接冲突
- 提高首次请求响应速度

---

### 3. Embedding 模型配置更新

**当前配置**：`shibing624/text2vec-base-chinese`

**配置位置**：`apps/ai_assistant/embedding_service.py`

**模型信息**：
- **模型名称**：`shibing624/text2vec-base-chinese`
- **向量维度**：768
- **支持语言**：中文优化
- **模型大小**：约 400MB
- **缓存路径**：`/home/zjoj/ai_data/embedding_models/`

**下载配置**：
```yaml
# docker-compose.yml
environment:
  - HF_ENDPOINT=https://hf-mirror.com  # 使用国内镜像加速
```

**自动检测机制**：
```python
# 优先检查本地缓存
modelscope_model_path = os.path.join(
    cache_dir, 
    'shibing624', 
    'text2vec-base-chinese'
)
if os.path.exists(modelscope_model_path):
    # 使用本地模型
else:
    # 从 hf-mirror 下载
```

---

### 4. 配额检查机制（AILimitChecker）

**实现位置**：`apps/ai_assistant/limits.py`

**核心功能**：

#### 4.1 每日配额检查
```python
@classmethod
def check_daily_quota(cls, user):
    """
    检查每日配额
    
    Returns:
        UserProfile 对象（配额充足时）
    
    Raises:
        Throttled: 配额已用完
    """
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # 检查是否需要重置
    today = timezone.now().date()
    if profile.last_reset_date != today:
        profile.used_today = 0
        profile.last_reset_date = today
        profile.save()
    
    # 检查配额
    if profile.used_today >= profile.daily_quota:
        raise Throttled(
            detail=f'今日配额已用完（{profile.daily_quota}次），明天重置',
            wait=None
        )
    
    return profile
```

#### 4.2 频率限制
```python
@classmethod
def check_rate_limit(cls, user):
    """
    60秒内最多10次请求
    """
    # 实现滑动窗口频率限制
```

#### 4.3 使用记录
```python
@classmethod
def increment_usage(cls, user):
    """增加今日使用次数"""
    profile = UserProfile.objects.get(user=user)
    profile.used_today += 1
    profile.save()

@classmethod
def trim_history(cls, user):
    """修剪历史记录，保留最新100条"""
    history_count = ChatHistory.objects.filter(user=user).count()
    if history_count > cls.MAX_HISTORY_PER_USER:
        # 删除最旧的记录
```

**配置常量**：
```python
MAX_HISTORY_PER_USER = 100  # 历史对话上限
DAILY_QUOTA = 50            # 每日配额（次）
RATE_LIMIT_WINDOW = 60      # 频率限制窗口（秒）
RATE_LIMIT_MAX = 10         # 窗口内最大请求数
```

**使用示例**：
```python
# 检查配额（捕获异常）
try:
    profile = AILimitChecker.check_daily_quota(user)
except Throttled as e:
    return Response({'error': str(e.detail)}, status=429)

# 记录使用
AILimitChecker.increment_usage(user)

# 修剪历史
AILimitChecker.trim_history(user)
```

---

### 5. 错误解决方案推送详细流程

**实现位置**：`apps/ai_assistant/error_pusher.py`

**完整工作流程**：

```
用户提交代码
    ↓
判题系统评测（RE/WA/TLE/MLE/CE）
    ↓
前端调用 API
    ↓
GET /api/ai/error-solution/{submission_id}/
    ↓
ErrorSolutionView 处理请求
    ↓
1. 检查配额（AILimitChecker）
2. 调用 ErrorSolutionPusher.push_on_judge_failure()
3. 构建查询关键词（题目ID + 错误类型）
4. RAG 引擎检索知识库（doc_type='error_solution'）
5. 去重并返回最多3个解决方案
    ↓
扣减配额
    ↓
返回 JSON 响应
```

**智能查询构建**：
```python
query_keywords = [
    f"{submission.problem.problem_id} {submission.result}",  # "A001 RE"
    f"{submission.problem.title} {submission.get_result_display()}",  # "A+B问题 运行时错误"
    submission.result,  # "RE"
]
```

**知识库文档要求**：
- `doc_type` 必须为 `error_solution`
- `error_type` 应设置为对应错误类型（WA/TLE/MLE/RE/CE）
- `content` 应包含详细的错误原因和解决方法

---

### 6. 向量数据库同步机制

**实现位置**：`apps/ai_assistant/views.py` (KnowledgeBaseView)

**同步策略**：异步线程同步

#### 6.1 创建文档时同步
```python
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

#### 6.2 更新文档时同步
```python
def put(self, request, kb_id):
    doc = serializer.save()
    
    # 异步更新向量数据库
    def update_vector():
        engine.vector_store.update_document(
            doc_id=doc.vector_id,
            text=doc.content,
            metadata={...}
        )
```

#### 6.3 删除文档时同步
```python
def delete(self, request, kb_id):
    vector_id = doc.vector_id
    doc.delete()
    
    # 异步从向量数据库删除
    def delete_from_vector():
        engine.vector_store.delete_document(doc_id=vector_id)
```

**注意事项**：
- 使用守护线程（daemon=True），不阻塞主请求
- 失败时仅打印警告，不影响数据库操作
- 生产环境建议使用 Celery 异步任务

---

## 📊 数据模型补充

### KnowledgeBase 模型完整字段

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
    error_type = models.CharField(max_length=50, blank=True, default='')  # WA/TLE/MLE/RE/CE
    source = models.CharField(max_length=500, blank=True)
    vector_id = models.CharField(max_length=100, unique=True)  # UUID
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'doc_type', 'error_type'],
                name='unique_knowledge_doc'  # 防止重复文档
            )
        ]
```

**关键字段说明**：
- `vector_id`: 向量数据库中的唯一标识（UUID格式）
- `error_type`: 错误类型，仅当 `doc_type='error_solution'` 时使用
- `problem`: 关联的题目，可用于题目特定的解决方案
- `tags`: 多对多标签，支持按标签搜索

---

## 🔌 API 接口补充

### 1. 知识库管理完整 CRUD

#### 1.1 创建文档（幂等性检查）
```bash
POST /api/ai/knowledge/
```

**幂等性机制**：
- 检查 `title + doc_type + error_type` 是否已存在
- 如果存在，返回 200 和现有文档（而非 409 冲突）
- 避免重复添加相同文档

#### 1.2 更新文档
```bash
PUT /api/ai/knowledge/<kb_id>/
```

**支持部分更新**：
- 使用 `partial=True`
- 只更新提供的字段
- 自动同步到向量数据库

#### 1.3 删除文档
```bash
DELETE /api/ai/knowledge/<kb_id>/
```

**级联删除**：
- 删除 MySQL 记录
- 异步删除 ChromaDB 向量

---

### 2. 配额管理 API 使用模式

**检查配额 + 记录使用的标准模式**：
```python
# 1. 检查配额
try:
    profile = AILimitChecker.check_daily_quota(user)
except Throttled as e:
    return Response({'error': str(e.detail)}, status=429)

# 2. 执行业务逻辑
result = do_something()

# 3. 记录使用
AILimitChecker.increment_usage(user)

# 4. 返回结果
remaining = profile.daily_quota - profile.used_today
return Response({
    'data': result,
    'remaining_quota': remaining
})
```

---

## ⚙️ 配置项补充

### 环境变量配置清单

```bash
# AI 服务配置
DEEPSEEK_API_KEY=sk-xxx              # DeepSeek API 密钥
HF_ENDPOINT=https://hf-mirror.com    # HuggingFace 镜像（国内加速）

# 路径配置
CHROMA_DB_PATH=/home/zjoj/ai_data/chroma_db
EMBEDDING_CACHE_DIR=/home/zjoj/ai_data/embedding_models

# Celery 配置
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Gunicorn 配置
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=300  # 增加到300秒，支持模型加载
```

---

## 🐛 已知问题和解决方案

### 1. ChromaDB 多进程表冲突

**问题**：Gunicorn 4个 worker 进程同时初始化 ChromaDB 导致表冲突

**错误信息**：
```
table embeddings_queue_config already exists
table maintenance_log already exists
```

**解决方案**：
- 使用 Celery 异步任务初始化（已实现）
- 或使用单进程模式（`--workers 1`）
- 或使用文件锁机制

### 2. Embedding 模型加载超时

**问题**：首次请求时模型加载需要 10-30 秒，可能超时

**解决方案**：
- 使用 Celery 预加载（已实现）
- 增加 Gunicorn 超时时间到 300 秒
- 模型缓存到本地，避免重复下载

### 3. 向量数据库同步失败

**问题**：异步线程同步失败时没有重试机制

**建议改进**：
- 使用 Celery 异步任务替代 threading
- 添加重试机制
- 记录同步失败日志

---

## 📝 最佳实践

### 1. 添加错误解决方案文档

```python
# 1. 创建文档
doc = KnowledgeBase.objects.create(
    title='RE 运行时错误解决方案',
    doc_type='error_solution',
    error_type='RE',
    content='''# RE (Runtime Error)

## 常见原因
1. 数组越界
2. 空指针/除零错误
3. 栈溢出
...
''',
    source='ZJOJ 知识库',
    is_active=True
)

# 2. 同步到向量数据库（自动）
# views.py 中的 post 方法会自动触发异步同步
```

### 2. 优化查询性能

```python
# 1. 使用 select_related 减少查询次数
submission = Submission.objects.select_related('problem').get(id=submission_id)

# 2. 使用 filter 在数据库层面过滤
queryset = KnowledgeBase.objects.filter(
    doc_type='error_solution',
    error_type='RE',
    is_active=True
)

# 3. 限制返回数量
solutions = solutions[:3]
```

### 3. 错误处理

```python
try:
    # 业务逻辑
except Throttled as e:
    # 配额限制
    return Response({'error': str(e.detail)}, status=429)
except Exception as e:
    # 其他错误
    return Response({'error': str(e)}, status=500)
```

---

## 🔄 版本更新建议

### 待实现功能

1. **流式响应**：支持 SSE (Server-Sent Events) 流式输出 AI 回答
2. **对话上下文**：支持多轮对话，保持上下文连贯
3. **缓存优化**：实现 Redis 缓存层，减少数据库查询
4. **监控告警**：添加 API 调用监控和异常告警
5. **批量导入**：支持从 Markdown/Word 批量导入知识库文档
6. **文档版本控制**：支持知识库文档的版本管理和回滚

---

## 📚 相关文档

- **主文档**：`docs/06-MODULES/ai-assistant.md`
- **API 参考**：`docs/04-API_REFERENCE.md`
- **数据库设计**：`docs/07-DATABASE.md`
- **部署指南**：`docs/03-DEPLOYMENT.md`

---

**文档版本**：v1.0  
**更新日期**：2026-04-27  
**维护者**：ZJOJ 开发团队
