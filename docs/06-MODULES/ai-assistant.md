# AI助手系统使用指南

## 📋 目录

- [系统概述](#系统概述)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [API接口](#api接口)
- [使用示例](#使用示例)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [新增功能](#新增功能-v110)

---

## 系统概述

AI助手是一个基于RAG（检索增强生成）技术的智能问答系统，专为算法学习和编程辅助设计。系统采用**本地Embedding + 云端LLM**的混合部署架构，既保证了数据隐私和响应速度，又降低了运营成本。

### 核心功能

#### 基础功能
- ✅ **智能问答**：基于知识库的精准回答
- ✅ **引用溯源**：每个回答都标注信息来源
- ✅ **对话历史**：自动保存和管理对话记录
- ✅ **配额管理**：每日使用限制和频率控制
- ✅ **多模式支持**：RAG模式和简单对话模式

#### v1.1.0 新增功能
- ✅ **学情分析报告**：学生个性化报告 + 教练班级共性分析
- ✅ **错误解决方案推送**：判题失败后自动推送相关解决方案
- ✅ **API调用优化**：24小时缓存 + 指数退避重试机制
- ✅ **知识库增强**：支持错误解决方案类型、关联题目

---

## 技术架构

### 架构图

```
用户请求 → Django API → RAG引擎 → 向量检索(ChromaDB) → LLM生成(DeepSeek)
                     ↓
                  Embedding模型(本地text2vec)
```

### 技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| Web框架 | Django 6.0 + DRF | RESTful API服务 |
| 身份认证 | JWT (自定义) | Token-based认证 |
| Embedding模型 | text2vec-base-chinese | 本地部署，390MB |
| 向量数据库 | ChromaDB | 持久化存储到E盘 |
| LLM API | DeepSeek (deepseek-chat) | 云端调用，按量付费 |
| 相似度算法 | 余弦相似度 | HNSW索引加速 |

### 数据存储

- **Embedding模型**：`E:/ai_models/cache/damo/nlp_corom_sentence-embedding_chinese-base`
- **向量数据库**：`E:/ai_data/chroma_db`
- **关系型数据**：MySQL（知识库、用户配置、对话历史）

---

## 快速开始

### 1. 环境准备

确保已安装以下依赖：

```bash
pip install sentence-transformers chromadb openai
```

### 2. 启动服务

```bash
# 启动Django开发服务器
python manage.py runserver 8000
```

### 3. 登录获取Token

```bash
curl -X POST http://127.0.0.1:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test_ai", "password": "TestPass123"}'
```

响应示例：
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "uid": "BxeWkhbZf2nWiznoay37Zr",
    "username": "test_ai",
    "email": "test_ai@example.com"
  }
}
```

### 4. 发起AI问答

```bash
curl -X POST http://127.0.0.1:8000/api/ai/chat/ \
  -H "Authorization: jwt eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是二分查找算法？",
    "use_rag": true,
    "top_k": 3
  }'
```

---

## API接口

### 1. AI智能问答

**接口地址**：`POST /api/ai/chat/`

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | 是 | 问题内容 |
| use_rag | boolean | 否 | 是否使用RAG模式，默认true |
| top_k | integer | 否 | 检索文档数量，默认5 |

**响应示例**：

```json
{
  "answer": "二分查找是一种在有序数组中查找特定元素的算法...",
  "tokens_used": 270,
  "remaining_quota": 47,
  "chat_id": 3,
  "sources": [
    {
      "id": "kb_abc123",
      "content": "二分查找（Binary Search）是一种...",
      "metadata": {
        "doc_id": 1,
        "title": "二分查找算法",
        "doc_type": "algorithm"
      },
      "similarity": 0.9822
    }
  ]
}
```

**错误响应**：

- `401 Unauthorized` - 未提供有效的JWT Token
- `400 Bad Request` - 请求参数验证失败
- `429 Too Many Requests` - 超过频率限制
- `500 Internal Server Error` - 服务器内部错误

---

### 2. 获取对话历史

**接口地址**：`GET /api/ai/history/?limit=50&offset=0`

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | integer | 否 | 每页数量，默认50 |
| offset | integer | 否 | 偏移量，默认0 |

**响应示例**：

```json
{
  "count": 10,
  "results": [
    {
      "id": 5,
      "question": "什么是二分查找算法？",
      "answer": "二分查找是一种...",
      "sources": [...],
      "tokens_used": 270,
      "created_at": "2026-04-16T00:05:58.123456"
    }
  ]
}
```

---

### 3. 使用情况统计

**接口地址**：`GET /api/ai/usage/`

**响应示例**：

```json
{
  "daily_quota": 50,
  "used_today": 3,
  "remaining": 47,
  "max_history": 100,
  "history_count": 10,
  "reset_time": "明天 00:00"
}
```

---

### 4. 清空对话历史

**接口地址**：`DELETE /api/ai/history/clear/`

**响应示例**：

```json
{
  "message": "已清空 10 条对话记录"
}
```

---

## 使用示例

### Python客户端示例

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. 登录
login_response = requests.post(f"{BASE_URL}/auth/login/", json={
    "username": "test_ai",
    "password": "TestPass123"
})
token = login_response.json()["token"]

headers = {
    "Authorization": f"jwt {token}",
    "Content-Type": "application/json"
}

# 2. RAG模式问答（推荐用于技术问题）
rag_response = requests.post(f"{BASE_URL}/api/ai/chat/", headers=headers, json={
    "question": "动态规划的核心思想是什么？",
    "use_rag": True,
    "top_k": 3
})
print(rag_response.json()["answer"])

# 3. 简单对话模式（适用于闲聊）
chat_response = requests.post(f"{BASE_URL}/api/ai/chat/", headers=headers, json={
    "question": "你好，请介绍一下自己",
    "use_rag": False
})
print(chat_response.json()["answer"])

# 4. 查看使用情况
usage_response = requests.get(f"{BASE_URL}/api/ai/usage/", headers=headers)
print(usage_response.json())
```

### JavaScript客户端示例

```javascript
const BASE_URL = "http://127.0.0.1:8000";

// 1. 登录
async function login() {
  const response = await fetch(`${BASE_URL}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'test_ai',
      password: 'TestPass123'
    })
  });
  const data = await response.json();
  return data.token;
}

// 2. AI问答
async function askQuestion(token, question) {
  const response = await fetch(`${BASE_URL}/api/ai/chat/`, {
    method: 'POST',
    headers: {
      'Authorization': `jwt ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      question: question,
      use_rag: true,
      top_k: 3
    })
  });
  const data = await response.json();
  console.log('回答:', data.answer);
  console.log('引用来源:', data.sources);
  return data;
}

// 使用示例
(async () => {
  const token = await login();
  await askQuestion(token, '什么是快速排序？');
})();
```

---

## 配置说明

### 环境变量配置

在 `ZJOJ/settings.py` 中配置：

```python
# AI Assistant Configuration
EMBEDDING_CACHE_DIR = 'E:/ai_models/cache'  # Embedding模型缓存目录
CHROMA_DB_PATH = 'E:/ai_data/chroma_db'     # ChromaDB存储路径

# LLM API Configuration (DeepSeek)
DEEPSEEK_API_KEY = 'sk-9d8da1c7c07548ecb6986efe57f233b8'
DEEPSEEK_MODEL = 'deepseek-chat'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
```

### 限制配置

在 `apps/ai_assistant/limits.py` 中修改：

```python
class AILimitChecker:
    MAX_HISTORY_PER_USER = 100  # 历史对话上限
    DAILY_QUOTA = 50            # 每日配额（次）
    RATE_LIMIT_WINDOW = 60      # 频率限制窗口（秒）
    RATE_LIMIT_MAX = 10         # 窗口内最大请求数
```

---

## 常见问题

### Q1: RAG模式回答不准确怎么办？

**可能原因**：
1. 知识库中没有相关文档
2. 向量检索相似度阈值过低
3. 问题表述不够清晰

**解决方案**：
- 向知识库添加更多相关文档
- 调整`top_k`参数获取更多参考
- 优化问题描述，使用更专业的术语

### Q2: 如何向知识库添加新文档？

使用提供的脚本：

```bash
# 1. 编辑 tests/add_knowledge_base.py 添加文档
# 2. 运行脚本
python tests/add_knowledge_base.py

# 3. 同步到向量数据库
python tests/sync_knowledge_to_vector.py
```

### Q3: 响应速度慢怎么办？

**影响因素**：
- Embedding模型加载（首次约5秒）
- 向量检索（约0.1秒）
- LLM API调用（约5-30秒，取决于回答长度）

**优化建议**：
- 保持Django服务持续运行，避免重复加载模型
- 减少`top_k`值（如从5改为3）
- 使用更简洁的问题描述

### Q4: 遇到"Nothing found on disk"错误？

这是ChromaDB索引损坏导致的，解决方法：

```bash
# 1. 停止Django服务
# 2. 删除向量数据库
python -c "import shutil; shutil.rmtree('E:/ai_data/chroma_db')"

# 3. 重新同步知识库
python tests/sync_knowledge_to_vector.py

# 4. 重启Django服务
```

### Q5: 如何监控API使用情况？

查看用户使用情况：

```bash
curl -X GET http://127.0.0.1:8000/api/ai/usage/ \
  -H "Authorization: jwt YOUR_TOKEN"
```

或在数据库中直接查询：

```sql
-- 查看今日使用情况
SELECT user_id, used_today, daily_quota 
FROM ai_assistant_userprofile;

-- 查看对话历史统计
SELECT user_id, COUNT(*) as chat_count 
FROM ai_assistant_chathistory 
GROUP BY user_id;
```

---

## 性能指标

### 响应时间

| 操作 | 平均耗时 | 说明 |
|------|---------|------|
| 简单对话 | 5-10秒 | 仅调用LLM API |
| RAG问答 | 10-30秒 | Embedding + 检索 + LLM |
| 获取历史 | <100ms | 纯数据库查询 |
| 使用情况 | <50ms | 纯数据库查询 |

### 资源占用

| 资源 | 占用量 | 说明 |
|------|--------|------|
| 内存 | ~2GB | Embedding模型常驻 |
| 磁盘 | ~500MB | 模型+向量数据库 |
| API费用 | ~$0.001/次 | DeepSeek按token计费 |

---

## 新增功能 v1.1.0

### 1. 学情分析报告系统

#### 学生个性化学情报告

**接口地址**：`GET /api/ai/report/student/?days=7`

**功能说明**：
- 统计指定时间段内的提交情况
- 计算AC率、题目难度分布
- AI生成个性化学习建议
- 识别薄弱环节和改进方向

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| days | integer | 否 | 统计天数，默认7天 |

**响应示例**：

```json
{
  "report_type": "学生个性报告",
  "period": "2026-04-17 至 2026-04-24",
  "summary": "本周你共提交了15次代码，通过率为60%。你在动态规划问题上表现较好，但在图论算法上需要加强...",
  "statistics": {
    "total_submissions": 15,
    "ac_count": 9,
    "wa_count": 4,
    "tle_count": 2,
    "ac_rate": 60.0,
    "problem_difficulty": {
      "easy": 5,
      "medium": 8,
      "hard": 2
    }
  },
  "recommendations": [
    "建议多练习图论相关题目，特别是最短路径算法",
    "注意时间复杂度优化，避免TLE",
    "可以尝试挑战更高难度的题目"
  ],
  "generated_at": "2026-04-24T01:30:00"
}
```

**权限要求**：仅学生角色可访问

---

#### 教练班级共性报告

**接口地址**：`GET /api/ai/report/class/{class_id}/?days=7`

**功能说明**：
- 统计整个班级的学习情况
- 识别共性难题（通过率<50%）
- 生成教学建议
- 分析班级整体进度

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| class_id | integer | 是 | 班级ID（URL路径参数） |
| days | integer | 否 | 统计天数，默认7天 |

**响应示例**：

```json
{
  "report_type": "班级共性报告",
  "class_name": "AI测试班",
  "period": "2026-04-17 至 2026-04-24",
  "summary": "本周班级整体表现良好，平均通过率为65%。大部分学生在基础算法上掌握较好，但在动态规划和图论方面存在困难...",
  "statistics": {
    "total_students": 30,
    "active_students": 25,
    "total_submissions": 450,
    "ac_count": 293,
    "ac_rate": 65.1,
    "common_difficult_problems": [
      {
        "problem_id": "P1001",
        "title": "最短路径",
        "attempt_count": 45,
        "ac_rate": 35.6
      }
    ]
  },
  "recommendations": [
    "建议下周重点讲解动态规划的状态转移方程设计",
    "可以组织一次图论算法的专题训练",
    "对于通过率低于40%的题目，建议增加习题课"
  ],
  "generated_at": "2026-04-24T01:30:00"
}
```

**权限要求**：仅教练或管理员可访问该班级的报告

---

### 2. 错误解决方案推送

**接口地址**：`GET /api/ai/error-solution/{submission_id}/`

**功能说明**：
- 判题失败后自动检索相关错误解决方案
- 基于错误类型（WA/TLE/MLE/RE/CE）智能匹配
- 结合题目信息提供针对性建议
- 最多返回3个最相关的解决方案

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| submission_id | integer | 是 | 提交记录ID（URL路径参数） |

**响应示例**：

```json
{
  "submission_id": 123,
  "solutions": [
    {
      "id": "kb_err_001",
      "title": "WA常见原因及解决方法",
      "content": "答案错误(WA)通常由以下原因导致：1.边界条件处理不当...",
      "doc_type": "error_solution",
      "error_type": "WA",
      "score": 0.92
    },
    {
      "id": "kb_err_002",
      "title": "二分查找边界陷阱",
      "content": "在实现二分查找时，常见的边界错误包括...",
      "doc_type": "error_solution",
      "error_type": "WA",
      "score": 0.87
    }
  ],
  "count": 2
}
```

**使用场景**：
- 学生提交代码后收到WA/TLE等错误
- 前端调用此接口获取解决建议
- 帮助学生快速定位问题

---

### 3. API调用优化

#### 结果缓存机制

**特性**：
- 24小时有效期
- 基于MD5哈希的缓存键
- 自动过期清理
- 显著降低API调用成本

**实现位置**：`apps/ai_assistant/api_optimizer.py`

**使用示例**：

```python
from apps.ai_assistant.api_optimizer import cached_api_call

@cached_api_call
def call_llm_api(prompt, temperature=0.7):
    """LLM API调用会自动缓存结果"""
    # ... API调用逻辑
    return response
```

**缓存效果**：
- 相同问题的重复询问直接返回缓存结果
- 减少约30-50%的API调用次数
- 响应速度从10-30秒降至<100ms

---

#### 网络异常重试机制

**特性**：
- 指数退避策略（1s → 2s → 4s）
- 最多重试3次
- 自动处理超时和连接错误
- 提高系统稳定性

**使用示例**：

```python
from apps.ai_assistant.api_optimizer import retry_on_failure

@retry_on_failure(max_retries=3, delay=1, backoff=2)
def unstable_api_call():
    """不稳定的API调用会自动重试"""
    # ... 可能失败的API调用
    return result
```

---

### 4. 知识库增强

#### 新增字段

**KnowledgeBase模型扩展**：

```python
class KnowledgeBase(models.Model):
    # 原有字段...
    
    # 新增字段
    doc_type = models.CharField(
        choices=[
            ('algorithm', '算法讲解'),
            ('solution', '题解'),
            ('template', '代码模板'),
            ('concept', '概念说明'),
            ('error_solution', '错误解决方案'),  # 新增
        ]
    )
    problem = models.ForeignKey('problem.Problem', ...)  # 关联题目
    error_type = models.CharField(  # 错误类型
        max_length=50,
        choices=[('WA', 'WA'), ('TLE', 'TLE'), ...]
    )
```

#### 按类型搜索

**RAG引擎增强**：

```python
engine = RAGEngine()

# 只搜索错误解决方案
solutions = engine.search_knowledge_base(
    query="二分查找 WA",
    doc_type='error_solution',
    top_k=3
)

# 搜索所有类型
docs = engine.search_knowledge_base(
    query="动态规划",
    top_k=5
)
```

---

### 5. Docker构建优化

#### 镜像加速配置

**Dockerfile优化**：
- ✅ 使用阿里云Debian镜像源
- ✅ 使用清华PyPI镜像源
- ✅ 下载速度提升5-10倍

**修改前**：
```dockerfile
RUN apt-get update && apt-get install -y gcc ...
RUN pip install -r requirements.txt
```

**修改后**：
```dockerfile
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y gcc ...
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**性能提升**：
- 系统包安装：~40s → ~5s
- Python依赖安装：~5分钟 → ~30s
- 总体构建时间减少约80%

---

### 6. 认证头格式说明

**重要提示**：本项目使用自定义JWT认证，认证头格式为：

```
Authorization: jwt <token>
```

**不是标准的Bearer格式！**

**正确示例**：
```bash
curl -X GET http://101.35.233.33:8000/api/user/profile/ \
  -H "Authorization: jwt eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**错误示例**（会返回401）：
```bash
curl -X GET http://101.35.233.33:8000/api/user/profile/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 7. 部署注意事项

#### 代码更新流程

由于项目使用Docker镜像部署，代码更新后必须重新构建镜像：

```bash
# 1. 拉取最新代码
git pull origin feature/ai-assistant-step1

# 2. 重新构建镜像
docker compose build web

# 3. 重启服务
docker compose up -d

# 4. 验证服务状态
docker compose ps
```

**常见问题**：如果只执行`git pull`而不重新构建，容器内仍然是旧代码，会导致404错误。

#### 依赖管理

新增Python依赖后，必须更新`requirements.txt`并重新构建：

```bash
# 添加新依赖到 requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# 提交并推送
git add requirements.txt
git commit -m "Add: new-package dependency"
git push

# 服务器上重新构建
docker compose build web
docker compose up -d
```

---

## 更新日志

### v1.1.0 (2026-04-24)

**新增功能**：
- ✅ 学情分析报告系统（学生个性化 + 教练班级共性）
- ✅ 错误解决方案自动推送
- ✅ API调用优化（24小时缓存 + 指数退避重试）
- ✅ 知识库增强（支持error_solution类型、关联题目）

**性能优化**：
- ✅ Docker构建速度提升80%（使用国内镜像源）
- ✅ 相同问题响应时间从10-30秒降至<100ms（缓存命中）
- ✅ API调用成本降低30-50%

**Bug修复**：
- ✅ 修复URL路由404问题（启用AI助手路由）
- ✅ 修复认证头格式问题（使用jwt而非Bearer）
- ✅ 添加缺失的AI依赖（chromadb, sentence-transformers, torch）

**配置变更**：
- ✅ DeepSeek API密钥已配置
- ✅ 认证中间件正常工作
- ✅ 所有API端点可访问

---

### v1.0.0 (2026-04-16)

- ✅ 完成基础RAG问答系统
- ✅ 实现知识库管理
- ✅ 集成DeepSeek API
- ✅ 添加配额和频率限制
- ✅ 完成端到端测试

---

## 技术支持

如有问题，请联系开发团队或提交Issue到GitHub仓库。

**项目地址**：https://github.com/hhdhhy/ZJOJ-backend  
**分支**：`feature/ai-assistant-step1`
