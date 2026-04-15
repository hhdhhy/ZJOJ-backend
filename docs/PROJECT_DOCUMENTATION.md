# ZJOJ 铸剑 - 在线评测系统项目文档

> **最后更新**: 2026年4月16日  
> **版本**: v1.0.0  
> **状态**: 核心功能已完成，AI助手已集成

---

## 📋 目录

- [项目概述](#项目概述)
- [技术架构](#技术架构)
- [项目结构](#项目结构)
- [核心模块](#核心模块)
- [数据库设计](#数据库设计)
- [API接口](#api接口)
- [部署指南](#部署指南)
- [开发规范](#开发规范)
- [相关文档](#相关文档)

---

## 项目概述

ZJOJ（铸剑）是一个基于 Django 框架开发的在线评测（Online Judge）系统，提供用户认证、题目管理、代码评测、AI智能问答等功能。「铸剑」寓意着磨砺技术、铸造精品。

### 核心特性

- 🔐 **JWT认证系统** - 安全高效的用户认证机制
- 👤 **自定义用户模型** - 灵活扩展的用户管理
- 🏆 **在线评测** - 基于HydroJudge的异步代码评测
- 📊 **实时排名** - 动态更新的排行榜系统
- 📝 **题目管理** - 便捷的题目创建和管理
- 🤖 **AI助手** - RAG智能问答系统（本地Embedding + 云端LLM）
- 🔒 **权限控制** - 细粒度的访问权限管理

### 系统架构图

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │ ◄────►  │  Django App  │ ◄────►  │   MySQL     │
│  (React/Vue)│  HTTP   │   (Backend)  │  ORM    │  Database   │
└─────────────┘         └──────────────┘         └─────────────┘
                               │                        ▲
                               ▼                        │
                        ┌──────────────┐                │
                        │   Celery     │                │
                        │  (Async Task)│                │
                        └──────────────┘                │
                               │                        │
                               ▼                        │
                        ┌──────────────┐                │
                        │ HydroJudge   │────────────────┘
                        │  (Evaluator) │
                        └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   AI System  │
                        │  (RAG+LLM)   │
                        └──────────────┘
```

---

## 技术架构

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Django** | 6.0.3 | Web应用框架 |
| **Django REST Framework** | Latest | RESTful API开发 |
| **MySQL** | 5.7+ | 关系型数据库 |
| **Celery** | Latest | 异步任务队列 |
| **ChromaDB** | Latest | 向量数据库 |
| **PyJWT** | Latest | JWT令牌认证 |
| **shortuuidfield** | Latest | Short UUID生成 |
| **django-cors-headers** | Latest | 跨域资源共享 |

### AI技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| **Embedding模型** | text2vec-base-chinese | 本地部署，390MB |
| **向量数据库** | ChromaDB | 持久化存储到E盘 |
| **LLM API** | DeepSeek (deepseek-chat) | 云端调用，按量付费 |
| **相似度算法** | 余弦相似度 | HNSW索引加速 |

### 数据存储

- **关系型数据**: MySQL（用户、题目、提交记录等）
- **向量数据**: ChromaDB（知识库文档向量）
- **文件存储**: 本地文件系统（测试用例、媒体文件）
- **缓存**: SQLite（Celery broker/backend，开发环境）

---

## 项目结构

```
ZJOJ/
├── ZJOJ/                          # 项目配置目录
│   ├── settings.py                # 全局配置
│   ├── urls.py                    # URL路由配置
│   ├── wsgi.py                    # WSGI入口
│   └── asgi.py                    # ASGI入口
│
├── apps/                          # 应用模块目录
│   ├── ojauth/                    # 🔐 用户认证模块
│   │   ├── models.py             # OJUser自定义用户模型
│   │   ├── views.py              # 登录视图
│   │   ├── serializers.py        # 序列化器
│   │   └── urls.py               # /auth/login/
│   │
│   ├── problem/                   # 📝 题目管理模块
│   │   ├── models.py             # Problem、Tag模型
│   │   ├── views.py              # 题目CRUD视图
│   │   └── urls.py               # /api/problems/*
│   │
│   ├── judge/                     # ⚡ 代码评测模块
│   │   ├── tasks.py              # Celery异步评测任务
│   │   ├── hydro_client.py       # HydroJudge客户端
│   │   └── models.py             # Submission评测记录
│   │
│   └── ai_assistant/              # 🤖 AI助手模块
│       ├── models.py             # KnowledgeBase、ChatHistory等
│       ├── embedding_service.py  # Embedding服务
│       ├── vector_store.py       # ChromaDB向量数据库
│       ├── llm_client.py         # DeepSeek LLM客户端
│       ├── rag_engine.py         # RAG引擎
│       ├── limits.py             # 配额和频率限制
│       ├── views.py              # AI问答API视图
│       └── urls.py               # /api/ai/*
│
├── MYJWT/                         # 🔑 JWT认证模块
│   ├── myjwt.py                  # Token生成函数
│   └── authentication.py         # DRF JWT认证类
│
├── Middleware/                    # 🛡️ 中间件
│   └── LoginCheck.py             # 登录检查中间件
│
├── tests/                         # 🧪 测试脚本
│   ├── test_ai_assistant_full.py # AI助手完整测试
│   ├── test_rag_mode.py          # RAG模式专项测试
│   ├── add_knowledge_base.py     # 知识库初始化
│   └── sync_knowledge_to_vector.py # 向量库同步
│
├── docs/                          # 📚 文档
│   ├── PROJECT_DOCUMENTATION.md  # 本文档
│   ├── API_DOCUMENTATION.md      # API接口文档
│   ├── AI_ASSISTANT_GUIDE.md     # AI助手使用指南
│   ├── DATABASE_DESIGN.md        # 数据库设计
│   ├── DEVELOPMENT_GUIDE.md      # 开发指南
│   └── ...
│
├── manage.py                      # Django管理脚本
├── celerybroker.db                # Celery消息代理
└── celeryresults.db               # Celery结果存储
```

---

## 核心模块

### 1. 用户认证模块 (apps.ojauth) ✅

**功能**:
- 自定义用户模型 `OJUser`
- JWT Token认证
- 用户状态管理（激活/未激活/锁定）
- 权限分级（普通用户/管理员）

**数据模型**:
```python
OJUser:
  - uid (ShortUUID, 主键)
  - username (唯一)
  - realname, email (唯一), telephone (唯一)
  - password (加密)
  - status (ACTIVE/UNACTIVE/LOCKED)
  - is_staff, is_active
```

**API接口**:
- `POST /auth/login/` - 用户登录

**详细文档**: [JWT认证说明](JWT_AUTHENTICATION.md)

---

### 2. 题目管理模块 (apps.problem) ✅

**功能**:
- 题目CRUD操作
- 标签分类系统
- 难度分级（EASY/MEDIUM/HARD）
- 测试用例管理

**数据模型**:
```python
Problem:
  - id, title, description
  - difficulty, time_limit, memory_limit
  - tags (ManyToMany)
  
Tag:
  - name, slug
```

**API接口**:
- `GET /api/problems/` - 获取题目列表
- `POST /api/problems/create/` - 创建题目
- `GET /api/problems/<id>/` - 获取题目详情
- `GET /api/problems/tags/` - 获取标签列表

**详细文档**: [题目模块文档](PROBLEM_MODULE.md)

---

### 3. 代码评测模块 (apps.judge) ✅

**功能**:
- 基于HydroJudge的异步评测
- Celery任务队列管理
- 多语言支持（C/C++/Java/Python等）
- 实时评测结果反馈

**技术架构**:
```
用户提交 → Submission创建 → Celery异步任务 
         → HydroJudge评测 → 结果回写数据库
```

**数据模型**:
```python
Submission:
  - user (ForeignKey)
  - problem (ForeignKey)
  - code, language
  - status (PENDING/JUDGING/ACCEPTED/WA/TLE/MLE/RE)
  - score, time_used, memory_used
```

**API接口**:
- `POST /api/submissions/submit/` - 提交代码
- `GET /api/submissions/` - 获取提交列表
- `GET /api/submissions/<id>/` - 获取评测详情

**详细文档**: [HydroJudge集成文档](HYDRO_JUDGE_INTEGRATION.md)

---

### 4. AI助手模块 (apps.ai_assistant) ✅ **NEW**

**功能**:
- RAG智能问答（检索增强生成）
- 本地Embedding + 云端LLM混合部署
- 知识库管理和向量检索
- 对话历史和使用统计
- 配额和频率限制

**技术架构**:
```
用户提问 → Embedding编码 → ChromaDB向量检索 
         → 组装上下文 → DeepSeek LLM生成 → 返回答案+引用来源
```

**核心组件**:
- `EmbeddingService` - text2vec-base-chinese（390MB，E盘存储）
- `VectorStore` - ChromaDB持久化向量数据库
- `LLMClient` - DeepSeek API客户端
- `RAGEngine` - RAG问答引擎
- `AILimitChecker` - 配额和频率限制

**数据模型**:
```python
KnowledgeBase:
  - title, content, doc_type
  - vector_id (ChromaDB文档ID)
  
UserProfile:
  - daily_quota (50次/天)
  - used_today, max_history (100条)
  
ChatHistory:
  - user, question, answer
  - sources (JSON), tokens_used
```

**API接口**:
- `POST /api/ai/chat/` - AI智能问答
- `GET /api/ai/history/` - 获取对话历史
- `GET /api/ai/usage/` - 使用情况统计
- `DELETE /api/ai/history/clear/` - 清空历史

**性能指标**:
- 响应时间：10-30秒（RAG模式）
- 向量检索相似度：98%+
- 每日配额：50次
- 频率限制：60秒内最多10次

**详细文档**: [AI助手使用指南](AI_ASSISTANT_GUIDE.md)

---

## 数据库设计

### 主要数据表

1. **用户表** (`ojauth_ojuser`)
   - 用户基本信息、认证信息、状态管理

2. **题目表** (`problem_problem`)
   - 题目描述、难度、限制条件

3. **标签表** (`problem_tag`)
   - 题目标签分类

4. **提交记录表** (`judge_submission`)
   - 代码提交、评测结果、性能数据

5. **知识库文档表** (`ai_assistant_knowledgebase`)
   - AI助手的知识文档

6. **用户AI配置表** (`ai_assistant_userprofile`)
   - 每日配额、使用统计

7. **对话历史表** (`ai_assistant_chathistory`)
   - 用户与AI的对话记录

8. **频率限制表** (`ai_assistant_ratelimit`)
   - API调用频率控制

**详细文档**: [数据库设计文档](DATABASE_DESIGN.md)

---

## API接口

### 认证接口
- `POST /auth/login/` - 用户登录

### 题目接口
- `GET /api/problems/` - 获取题目列表
- `POST /api/problems/create/` - 创建题目
- `GET /api/problems/<id>/` - 获取题目详情
- `GET /api/problems/tags/` - 获取标签列表

### 评测接口
- `POST /api/submissions/submit/` - 提交代码
- `GET /api/submissions/` - 获取提交列表
- `GET /api/submissions/<id>/` - 获取评测详情

### AI助手接口
- `POST /api/ai/chat/` - AI智能问答
- `GET /api/ai/history/` - 获取对话历史
- `GET /api/ai/usage/` - 使用情况统计
- `DELETE /api/ai/history/clear/` - 清空历史

**详细文档**: [API接口文档](API_DOCUMENTATION.md)

---

## 部署指南

### 开发环境

```bash
# 1. 安装依赖
pip install django djangorestframework celery shortuuidfield pyjwt mysqlclient
pip install sentence-transformers chromadb openai modelscope

# 2. 配置数据库
# 修改 ZJOJ/settings.py 中的 DATABASES 配置

# 3. 初始化数据库
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# 4. 启动服务
python manage.py runserver 8000

# 5. 启动Celery Worker（代码评测需要）
celery -A ZJOJ worker --loglevel=info
```

### 生产环境

1. **关闭DEBUG模式**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   ```

2. **使用Gunicorn**
   ```bash
   gunicorn ZJOJ.wsgi:application --bind 0.0.0.0:8000 --workers 3
   ```

3. **Nginx反向代理**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
       }
   }
   ```

4. **Celery生产配置**
   - Broker: Redis/RabbitMQ
   - Backend: Redis/Database

**详细文档**: [开发指南](DEVELOPMENT_GUIDE.md)

---

## 开发规范

### 代码风格
- 遵循PEP 8 Python编码规范
- 使用类视图（CBV）而非函数视图
- DRF视图权限配置去重（使用全局默认权限）

### Git工作流
- 分步测试，每步完成后提交到Git分支
- 分支命名：`feature/xxx`, `bugfix/xxx`
- Commit信息清晰描述变更内容

### 数据存储
- 所有大数据文件存储到E盘（避开C盘）
- Embedding模型：`E:/ai_models/cache`
- 向量数据库：`E:/ai_data/chroma_db`

---

## 相关文档

| 文档 | 描述 | 路径 |
|------|------|------|
| 📘 **项目文档** | 项目概述、架构设计、核心模块 | [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) |
| 🔌 **API文档** | 完整的RESTful API接口文档 | [API_DOCUMENTATION.md](API_DOCUMENTATION.md) |
| 🤖 **AI助手指南** | AI助手系统详细使用说明 | [AI_ASSISTANT_GUIDE.md](AI_ASSISTANT_GUIDE.md) |
| 🛠️ **开发指南** | 环境搭建、开发流程、代码规范 | [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) |
| 💾 **数据库设计** | 数据库表结构、ER图、优化建议 | [DATABASE_DESIGN.md](DATABASE_DESIGN.md) |
| 🔐 **JWT认证** | JWT认证系统详细说明 | [JWT_AUTHENTICATION.md](JWT_AUTHENTICATION.md) |
| 📝 **题目模块** | 题目管理模块详细文档 | [PROBLEM_MODULE.md](PROBLEM_MODULE.md) |
| ⚡ **HydroJudge集成** | 代码评测系统集成说明 | [HYDRO_JUDGE_INTEGRATION.md](HYDRO_JUDGE_INTEGRATION.md) |

---

## 项目状态

| 模块 | 状态 | 完成度 |
|------|------|--------|
| 用户认证 | ✅ 完成 | 100% |
| 题目管理 | ✅ 完成 | 100% |
| 代码评测 | ✅ 完成 | 100% |
| AI助手 | ✅ 完成 | 100% |
| 比赛系统 | ⏸️ 待实现 | 0% |
| 统计分析 | ⏸️ 待实现 | 0% |

---

## 常见问题

### Q1: 如何创建超级用户？
```bash
python manage.py createsuperuser
```

### Q2: JWT Token如何使用？
在请求头中添加：
```
Authorization: jwt <your_token>
```

### Q3: ChromaDB出现hnsw索引错误？
删除旧数据库并重新同步：
```bash
python -c "import shutil; shutil.rmtree('E:/ai_data/chroma_db')"
python tests/sync_knowledge_to_vector.py
```

### Q4: Celery任务不执行？
确保Celery Worker正在运行：
```bash
celery -A ZJOJ worker --loglevel=info
```

---

<div align="center">

**Made with ❤️ by 铸剑团队**

[返回顶部](#zjoJ-铸剑---在线评测系统项目文档)

</div>
