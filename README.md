# ZJOJ - 在线评测系统

<div align="center">

![Django](https://img.shields.io/badge/Django-6.0.4-green.svg)
![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

**铸剑** **O**nline **J**udge - 专业编程竞赛评测平台

[Docker 部署](#-docker-部署) • [快速开始](#-快速开始) • [功能特性](#-功能特性)

</div>

---

## 📖 项目简介

ZJOJ 是一个基于 Django 框架开发的在线评测（Online Judge）系统，采用 Docker 容器化部署，提供专业、高效的代码评测服务。

### 核心特性

#### 基础功能
- 🔐 **JWT 认证系统** - 安全高效的用户认证机制
- 👤 **自定义用户模型** - 灵活扩展的用户管理
- 🏆 **在线评测** - 基于 go-judge 的异步代码评测
- 📊 **实时排名** - 动态更新的排行榜系统
- 📝 **题目管理** - 便捷的题目创建和管理
- 🔒 **权限控制** - 细粒度的访问权限管理
- 🐳 **Docker 部署** - 一键部署，环境一致

#### AI 增强功能 (v1.1.0)
- 🤖 **AI智能问答** - 基于RAG的智能编程助手（DeepSeek）
- 📈 **学情分析报告** - 学生个性化 + 教练班级共性分析
- 💡 **错误解决方案推送** - 判题失败后自动推送相关建议
- ⚡ **API调用优化** - 24小时缓存 + 指数退避重试机制
- 🎯 **知识库增强** - 支持错误解决方案、关联题目

---

## 🚀 Docker 部署

### 前置要求

- Docker (>= 20.10)
- Docker Compose (>= 2.0)

### 一键部署

```bash
# 1. 克隆项目
git clone git@github.com:hhdhhy/ZJOJ-backend.git
cd ZJOJ-backend

# 2. 运行部署脚本
chmod +x deploy/docker-deploy.sh
./deploy/docker-deploy.sh

# 3. 创建管理员账户
docker compose exec web python manage.py createsuperuser
```

### 常用命令

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 备份数据
bash deploy/docker-backup.sh

# 恢复数据
bash deploy/docker-restore.sh backups/backup_xxx.tar.gz
```

详细文档请查看：
- 📘 [Docker 部署完整指南](docs/03-DEPLOYMENT.md)
- 📋 [快速上手指南](DOCKER_QUICKSTART.md)

---

## 🏗️ 技术架构

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Django** | 6.0.4 | Web 应用框架 |
| **Django REST Framework** | 3.17.1 | RESTful API 开发 |
| **MySQL** | 8.0 | 关系型数据库 |
| **Gunicorn** | 25.3.0 | WSGI HTTP 服务器 |
| **Nginx** | Alpine | 反向代理 |
| **PyJWT** | 2.12.1 | JWT 令牌认证 |
| **go-judge** | 1.11.4 | 代码评测沙箱 |
| **ChromaDB** | 0.6.3 | 向量数据库 |
| **Sentence-Transformers** | 3.3.1 | 文本嵌入模型 |
| **DeepSeek API** | deepseek-chat | LLM云端服务 |

### 系统架构

```
┌─────────────┐
│   Nginx     │ :80 (HTTP)
│  (Container)│
└──────┬──────┘
       │
       │ Proxy Pass
       │
┌──────▼──────┐
│   Django    │ :8000 (Internal)
│  (Gunicorn) │
└──────┬──────┘
       │
       │ MySQL Connection
       │
┌──────▼──────┐
│   MySQL     │ :3306 (Internal)
│  (Database) │
└─────────────┘
```

---

## 📋 API 接口概览

### 认证相关

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/login/` | POST | 用户登录 |
| `/api/register/` | POST | 用户注册 |
| `/api/logout/` | POST | 用户登出 |
| `/api/user/profile/` | GET/PUT | 获取/更新用户信息 |

### 题目相关

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/problems/` | GET/POST | 获取题目列表/创建题目 |
| `/api/problems/{id}/` | GET/PUT/DELETE | 获取/更新/删除题目详情 |
| `/api/submissions/submit/` | POST | 提交代码评测 |

详细 API 文档：[API 参考](docs/04-API_REFERENCE.md)

---

## 📁 项目结构

```
ZJOJ/
├── apps/                 # 应用目录
│   ├── ojauth/          # 用户认证模块
│   ├── problem/         # 题目管理模块
│   └── judge/           # 代码评测模块
├── deploy/              # 部署相关文件
│   ├── docker-deploy.sh    # Docker 部署脚本
│   ├── docker-backup.sh    # 备份脚本
│   ├── docker-restore.sh   # 恢复脚本
│   ├── system-init.sh      # 系统初始化脚本
│   └── nginx.conf          # Nginx 配置
├── docs/                # 文档目录
├── docker-compose.yml   # Docker 编排配置
├── Dockerfile           # Django 镜像构建
├── requirements.txt     # Python 依赖
└── manage.py           # Django 管理脚本
```

---

## 🧪 开发

### 本地开发（不使用 Docker）

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 4. 运行开发服务器
python manage.py runserver
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 📞 联系方式

- 项目主页：https://github.com/hhdhhy/ZJOJ-backend
- 问题反馈：[Issues 页面](https://github.com/hhdhhy/ZJOJ-backend/issues)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star 支持一下！⭐**

Made with ❤️ by 铸剑团队

[返回顶部](#zjoj---在线评测系统)

</div>
