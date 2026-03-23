# ZJOJ - 在线评测系统

<div align="center">

![Django](https://img.shields.io/badge/Django-6.0.3-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![MySQL](https://img.shields.io/badge/MySQL-5.7+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

**铸剑** **O**nline **J**udge - 专业编程竞赛评测平台

[文档](#文档) • [快速开始](#快速开始) • [功能特性](#功能特性) • [技术架构](#技术架构)

</div>

---

## 📖 项目简介

ZJOJ 是一个基于 Django 框架开发的在线评测（Online Judge）系统，旨在为编程爱好者提供专业、高效的代码评测服务。系统支持多种编程语言，提供实时评测、排名统计、比赛管理等功能。「铸剑」寓意着磨砺技术、铸造精品。

### 核心特性

- 🔐 **JWT 认证系统** - 安全高效的用户认证机制
- 👤 **自定义用户模型** - 灵活扩展的用户管理
- 🏆 **在线评测** - 支持多种编程语言的代码评测
- 📊 **实时排名** - 动态更新的排行榜系统
- 🎯 **比赛管理** - 完整的在线比赛功能
- 📝 **题目管理** - 便捷的题目创建和管理
- 🔒 **权限控制** - 细粒度的访问权限管理

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+
- Django 6.0.3

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd ZJOJ
```

#### 2. 安装依赖

```bash
pip install django djangorestframework django-cors-headers shortuuidfield pyjwt mysqlclient
```

#### 3. 配置数据库

创建 MySQL 数据库：

```sql
CREATE DATABASE ZJOJ CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `ZJOJ/settings.py` 中的数据库配置：

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "ZJOJ",
        "USER": "root",
        "PASSWORD": "your_password",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}
```

#### 4. 初始化数据库

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

#### 5. 运行开发服务器

```bash
python manage.py runserver
```

访问 http://localhost:8000/admin 进入管理后台

---

## 📚 文档

### 完整文档列表

| 文档 | 描述 | 路径 |
|------|------|------|
| 📘 **项目文档** | 项目概述、架构设计、核心模块说明 | [`docs/PROJECT_DOCUMENTATION.md`](docs/PROJECT_DOCUMENTATION.md) |
| 🔌 **API 文档** | 完整的 RESTful API 接口文档 | [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) |
| 🛠️ **开发指南** | 环境搭建、开发流程、代码规范 | [`docs/DEVELOPMENT_GUIDE.md`](docs/DEVELOPMENT_GUIDE.md) |
| 💾 **数据库设计** | 数据库表结构、ER 图、优化建议 | [`docs/DATABASE_DESIGN.md`](docs/DATABASE_DESIGN.md) |
| 🔐 **JWT 认证** | JWT 认证系统详细说明 | [`docs/JWT_AUTHENTICATION.md`](docs/JWT_AUTHENTICATION.md) |

### 快速导航

- **新手入门**: 先阅读 [开发指南](docs/DEVELOPMENT_GUIDE.md) 的环境搭建章节
- **API 使用**: 查看 [API 文档](docs/API_DOCUMENTATION.md) 了解接口调用方式
- **二次开发**: 参考 [项目文档](docs/PROJECT_DOCUMENTATION.md) 和 [开发指南](docs/DEVELOPMENT_GUIDE.md)
- **数据库设计**: 查阅 [数据库设计文档](docs/DATABASE_DESIGN.md) 了解数据结构

---

## 🏗️ 技术架构

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Django** | 6.0.3 | Web 应用框架 |
| **Django REST Framework** | Latest | RESTful API 开发 |
| **MySQL** | 5.7+ | 关系型数据库 |
| **PyJWT** | Latest | JWT 令牌认证 |
| **ShortUUIDField** | Latest | Short UUID 生成 |
| **django-cors-headers** | Latest | 跨域资源共享 |

### 系统架构图

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │ ◄────►  │  Django App  │ ◄────►  │   MySQL     │
│  (React/Vue)│  HTTP   │   (Backend)  │  ORM    │  Database   │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │    MYJWT     │
                       │  (Auth Module)│
                       └──────────────┘
```

### 项目结构

```
ZJOJ/
├── ZJOJ/                 # 项目配置目录
│   ├── settings.py       # 项目设置
│   ├── urls.py           # URL 路由配置
│   └── wsgi.py          # WSGI 配置
├── apps/                 # 应用目录
│   └── ojauth/          # 认证应用
│       ├── models.py     # 数据模型
│       ├── views.py      # 视图函数
│       └── serializers.py # 序列化器
├── MYJWT/                # JWT 认证模块
│   └── myjwt.py         # JWT 实现
├── docs/                 # 文档目录
│   ├── PROJECT_DOCUMENTATION.md
│   ├── API_DOCUMENTATION.md
│   ├── DEVELOPMENT_GUIDE.md
│   ├── DATABASE_DESIGN.md
│   └── JWT_AUTHENTICATION.md
└── manage.py            # Django 管理脚本
```

---

## 🎯 核心功能模块

### 1. 用户认证模块

- ✅ 用户注册与登录
- ✅ JWT Token 认证
- ✅ 密码加密存储
- ✅ 用户状态管理（激活/锁定）
- ✅ 权限分级（普通用户/管理员）

### 2. 题目管理模块（待实现）

- 📝 题目创建与编辑
- 📝 测试用例管理
- 📝 难度分级
- 📝 标签分类

### 3. 代码评测模块（待实现）

- ⚡ 多语言支持（C/C++/Java/Python 等）
- ⚡ 实时评测反馈
- ⚡ 执行时间与内存监控
- ⚡ 编译错误提示

### 4. 比赛系统模块（待实现）

- 🏆 在线比赛组织
- 🏆 实时排名更新
- 🏆 比赛数据统计
- 🏆 AC 自动机评测

### 5. 统计分析模块（待实现）

- 📊 个人能力雷达图
- 📊 题目通过率统计
- 📊 提交历史记录
- 📊 排行榜系统

---

## 📋 API 接口概览

### 认证相关

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/login/` | POST | 用户登录 |
| `/api/register/` | POST | 用户注册 |
| `/api/logout/` | POST | 用户登出 |
| `/api/user/profile/` | GET/PUT | 获取/更新用户信息 |
| `/api/password/change/` | POST | 修改密码 |
| `/api/password/reset/` | POST | 重置密码 |

### 题目相关（待实现）

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/problems/` | GET/POST | 获取题目列表/创建题目 |
| `/api/problems/{id}/` | GET/PUT/DELETE | 获取/更新/删除题目详情 |
| `/api/problems/{id}/submit/` | POST | 提交代码 |

### 提交记录相关（待实现）

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/submissions/` | GET/POST | 获取提交列表/提交代码 |
| `/api/submissions/{id}/` | GET | 获取提交详情 |

详细使用说明请查看：[API 文档](docs/API_DOCUMENTATION.md)

---

## 🔧 配置说明

### 关键配置项

```python
# ZJOJ/settings.py

# 调试模式
DEBUG = True

# 允许的主机
ALLOWED_HOSTS = []

# 数据库配置
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "ZJOJ",
        "USER": "root",
        "PASSWORD": "your_password",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}

# 自定义用户模型
AUTH_USER_MODEL = "ojauth.OJUser"

# CORS 配置
CORS_ALLOW_ALL_ORIGINS = True
```

更多配置项请参考：[开发指南](docs/DEVELOPMENT_GUIDE.md)

---

## 🧪 测试

### 运行测试

```bash
python manage.py test
```

### 运行特定应用的测试

```bash
python manage.py test apps.ojauth
```

---

## 📦 部署

### 生产环境部署

#### 1. 关闭 DEBUG 模式

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
```

#### 2. 收集静态文件

```bash
python manage.py collectstatic --noinput
```

#### 3. 使用 Gunicorn 运行

```bash
gunicorn ZJOJ.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

#### 4. Nginx 反向代理

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }
}
```

详细部署教程请查看：[开发指南 - 部署指南](docs/DEVELOPMENT_GUIDE.md#部署指南)

---

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 如何贡献

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发环境搭建

详见：[开发指南](docs/DEVELOPMENT_GUIDE.md)

---

## ❓ 常见问题

### Q: 如何创建超级用户？

```bash
python manage.py createsuperuser
```

### Q: 数据库迁移失败怎么办？

1. 检查数据库连接配置
2. 确保数据库已创建
3. 删除迁移记录重新生成

### Q: JWT Token 如何使用？

在请求头中添加：
```
Authorization: jwt <your_token>
```

更多问题请查看：[开发指南 - 常见问题](docs/DEVELOPMENT_GUIDE.md#常见问题)

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 👥 开发团队

- 创始人：[您的名字]
- 核心开发者：[团队成员名字]

---

## 📞 联系方式

- 邮箱：your.email@example.com
- 项目主页：[项目链接]
- 问题反馈：[Issues 页面]

---

## 🙏 致谢

感谢以下开源项目：

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PyJWT](https://pyjwt.readthedocs.io/)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star 支持一下！⭐**

Made with ❤️ by 铸剑团队

[返回顶部](#zjoJ---在线评测系统)

</div>
