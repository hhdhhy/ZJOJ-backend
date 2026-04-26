# ZJOJ 项目技术文档总览

## 📖 文档说明

本文档集详细描述了 ZJOJ（铸剑在线评测系统）的完整技术实现，包括系统架构、核心模块、数据库设计、API接口等内容。适用于开发者理解项目结构、进行二次开发或系统集成。

---

## 📚 文档目录

### 基础文档

1. **[快速开始](01-GETTING_STARTED.md)** - 环境搭建与快速上手
2. **[系统架构](02-ARCHITECTURE.md)** - 整体架构设计与技术选型
3. **[部署指南](03-DEPLOYMENT.md)** - Docker 部署与服务器配置
4. **[API 参考](04-API_REFERENCE.md)** - 完整的 REST API 文档
5. **[开发指南](05-DEVELOPMENT.md)** - 开发规范与最佳实践

### 核心模块文档

6. **模块详解** ([06-MODULES/](06-MODULES/))
   - [用户认证模块](06-MODULES/auth.md) - JWT 认证与权限管理
   - [题目管理模块](06-MODULES/problem.md) - 题目的 CRUD 操作
   - [评测系统模块](06-MODULES/judge.md) - go-judge 集成与代码评测
   - [AI 助手模块](06-MODULES/ai-assistant.md) - RAG 架构与智能问答
   - [权限系统模块](06-MODULES/permission-system.md) - 角色与权限控制

### 专项文档

7. **[数据库设计](07-DATABASE.md)** - 数据模型与表结构设计
8. **[数据库详细设计](DATABASE_DETAILED.md)** - 完整的数据库 schema、索引、优化策略
9. **[评测系统详解](JUDGE_SYSTEM.md)** - go-judge 沙箱集成指南
10. **[评测系统详细实现](JUDGE_SYSTEM_DETAILED.md)** - 评测流程、代码编译、结果判定详解
11. **[AI 助手详细实现](AI_ASSISTANT_DETAILED.md)** - RAG 架构、向量检索、DeepSeek 集成
12. **[部署与运维详解](DEPLOYMENT_DETAILED.md)** - 生产环境部署、监控、故障排查
13. **[go-judge 文档](GOJUDGE_DOCUMENTATION.md)** - go-judge 官方文档总结
14. **[Docker 部署详解](DOCKER_DEPLOYMENT.md)** - 容器化部署最佳实践

---

## 🏗️ 项目概览

### 项目名称
ZJOJ (铸剑在线评测系统)

### 技术栈

**后端框架**:
- Python 3.10+
- Django 6.0.3
- Django REST Framework 3.15.2

**数据库**:
- MySQL 8.0 (主数据库)
- ChromaDB (向量数据库，用于 AI 助手)

**消息队列**:
- Redis 7.x (Celery Broker + Cache)
- Celery 5.4.0 (异步任务队列)

**代码评测**:
- go-judge v1.11.4 (hydro-sandbox)
- 支持语言: C, C++, Python, Java

**AI 能力**:
- DeepSeek API (大语言模型)
- text2vec-base-chinese (文本嵌入模型)
- RAG 架构 (检索增强生成)

**部署**:
- Docker + Docker Compose
- Nginx (反向代理)
- PM2 (进程管理)

---

## 📁 项目结构

```
ZJOJ/
├── apps/                      # Django 应用模块
│   ├── ojauth/               # 用户认证模块
│   │   ├── models.py         # 用户模型
│   │   ├── views.py          # 认证视图
│   │   ├── serializers.py    # 序列化器
│   │   └── urls.py           # URL 路由
│   ├── problem/              # 题目管理模块
│   │   ├── models.py         # 题目、提交、测试用例模型
│   │   ├── views.py          # 题目 CRUD 视图
│   │   └── serializers.py    # 序列化器
│   ├── judge/                # 评测系统模块
│   │   ├── adapter.py        # go-judge 适配器
│   │   ├── tasks.py          # Celery 异步评测任务
│   │   ├── task_processor.py # 任务处理器
│   │   └── gojudge_client.py # go-judge 客户端
│   └── ai_assistant/         # AI 助手模块
│       ├── rag_service.py    # RAG 服务
│       ├── embedding_model.py # 文本嵌入模型
│       └── views.py          # AI 问答视图
├── MYJWT/                     # JWT 认证模块
│   └── myjwt.py              # JWT 工具类
├── Middleware/                # 中间件
│   └── LoginCheck.py         # 登录检查中间件
├── deploy/                    # 部署配置
│   ├── docker-compose.yml    # Docker Compose 配置
│   ├── Dockerfile.gojudge    # go-judge 自定义镜像
│   └── gojudge-mount.yaml    # go-judge 挂载配置
├── docs/                      # 项目文档
├── scripts/                   # 脚本文件
├── tests/                     # 测试脚本
├── manage.py                  # Django 管理脚本
└── ZJOJ/                      # Django 项目配置
    ├── settings.py           # 项目设置
    ├── urls.py               # 根 URL 配置
    └── wsgi.py               # WSGI 入口
```

---

## 🔑 核心功能

### 1. 用户系统
- 用户注册与登录
- JWT Token 认证
- 密码加密存储 (PBKDF2)
- 用户信息管理

### 2. 题目管理
- 题目 CRUD 操作
- 题目标签分类
- 难度等级设置
- 测试用例管理 (ZIP 格式)

### 3. 代码评测
- 多语言支持 (C/C++/Python/Java)
- 自动编译与执行
- 资源限制 (时间、内存、进程数)
- 多测试点评分
- 实时评测结果反馈

### 4. AI 助手
- 智能编程问答
- 代码错误诊断
- 解题思路提示
- 基于 RAG 的知识检索

### 5. 权限管理
- 角色-based 权限控制
- 管理员/教师/学生三级权限
- 题目可见性控制
- 提交记录查看权限

---

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Docker & Docker Compose
- MySQL 8.0+
- Redis 7.x

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/ZJOJ.git
cd ZJOJ

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写数据库密码等配置

# 3. 启动服务
docker compose up -d

# 4. 初始化数据库
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

# 5. 访问系统
# Web 界面: http://localhost:8000
# API 文档: http://localhost:8000/api/docs/
```

---

## 📊 系统架构图

```
┌─────────────────────────────────────────────┐
│              Client (Browser/Mobile)         │
└────────────────┬────────────────────────────┘
                 │ HTTPS
┌────────────────▼────────────────────────────┐
│              Nginx (Reverse Proxy)           │
└────────────────┬────────────────────────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼────┐ ┌────▼────┐ ┌───▼────┐
│  Web    │ │  Celery │ │ go-    │
│ Server  │ │ Worker  │ │ judge  │
│(Django) │ │         │ │        │
└────┬────┘ └────┬────┘ └───┬────┘
     │           │           │
     │      ┌────▼────┐      │
     │      │  Redis  │      │
     │      │(Broker) │      │
     │      └─────────┘      │
     │                       │
     └───────────┬───────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼────┐ ┌────▼────┐ ┌───▼────┐
│  MySQL  │ │ChromaDB │ │ File   │
│         │ │         │ │ System │
└─────────┘ └─────────┘ └────────┘
```

---

## 🔗 相关文档

- [go-judge 官方文档](https://docs.goj.ac/cn/)
- [Django 官方文档](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery 官方文档](https://docs.celeryq.dev/)
- [DeepSeek API 文档](https://platform.deepseek.com/)

---

## 📝 更新日志

### v1.0.0 (2026-04-27)
- ✅ 完成基础用户系统
- ✅ 实现题目管理功能
- ✅ 集成 go-judge 评测系统
- ✅ 实现 AI 助手模块
- ✅ 完成 Docker 部署配置
- ✅ 编写完整技术文档

---

## 👥 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](../LICENSE) 文件。

---

## 📧 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues: https://github.com/your-repo/ZJOJ/issues
- Email: your-email@example.com

---

**最后更新**: 2026-04-27
