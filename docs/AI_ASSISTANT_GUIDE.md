# AI助手系统使用指南

## 📋 目录

- [系统概述](#系统概述)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [API接口](#api接口)
- [使用示例](#使用示例)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

---

## 系统概述

AI助手是一个基于RAG（检索增强生成）技术的智能问答系统，专为算法学习和编程辅助设计。系统采用**本地Embedding + 云端LLM**的混合部署架构，既保证了数据隐私和响应速度，又降低了运营成本。

### 核心功能

- ✅ **智能问答**：基于知识库的精准回答
- ✅ **引用溯源**：每个回答都标注信息来源
- ✅ **对话历史**：自动保存和管理对话记录
- ✅ **配额管理**：每日使用限制和频率控制
- ✅ **多模式支持**：RAG模式和简单对话模式

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

## 更新日志

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
