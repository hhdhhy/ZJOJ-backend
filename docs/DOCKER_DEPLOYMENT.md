# Docker 部署指南

> 🐳 ZJOJ Docker Compose 生产环境部署完整流程

---

## 📋 目录

- [快速开始](#快速开始)
- [系统要求](#系统要求)
- [部署步骤](#部署步骤)
- [配置说明](#配置说明)
- [常用命令](#常用命令)
- [故障排查](#故障排查)
- [性能优化](#性能优化)

---

## 🚀 快速开始

### 一键部署（推荐）

```bash
# 1. 克隆代码
git clone git@github.com:hhdhhy/ZJOJ-backend.git
cd ZJOJ-backend

# 2. 配置环境变量（交互式）
./deploy/setup_env.sh

# 3. 启动服务
docker compose up -d

# 4. 创建管理员
./deploy/create_admin.sh admin YourPassword admin@example.com

# 5. 配置 AI API Key（可选）
./deploy/setup_ai_api.sh

# 完成！访问 http://your-server-ip:8000/admin/
```

---

## 💻 系统要求

### 硬件要求

| 配置项 | 最低配置 | 推荐配置 |
|--------|---------|---------|
| **CPU** | 2核 | 4核+ |
| **内存** | 4GB | 8GB+ |
| **磁盘** | 20GB | 50GB+ SSD |
| **网络** | 1Mbps | 10Mbps+ |

### 软件要求

| 软件 | 版本 |
|------|------|
| **操作系统** | Ubuntu 20.04+ / CentOS 7+ |
| **Docker** | 20.10+ |
| **Docker Compose** | 2.0+ |

---

## 📝 部署步骤

### 1. 安装 Docker 和 Docker Compose

#### Ubuntu 20.04+

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER

# 重新登录使权限生效
exit
# 重新 SSH 登录

# 验证安装
docker --version
docker compose version
```

#### CentOS 7+

```bash
# 安装 Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

### 2. 克隆项目代码

```bash
# 使用 SSH（推荐，需要配置 SSH Key）
git clone git@github.com:hhdhhy/ZJOJ-backend.git
cd ZJOJ-backend

# 或使用 HTTPS
git clone https://github.com/hhdhhy/ZJOJ-backend.git
cd ZJOJ-backend

# 切换到最新分支
git checkout feature/ai-assistant-step1
```

### 3. 配置环境变量

#### 方式一：交互式配置（推荐）

```bash
./deploy/setup_env.sh
```

按照提示输入配置信息，大部分参数有默认值，直接回车即可。

#### 方式二：手动配置

```bash
cp .env.example .env
nano .env
```

编辑 `.env` 文件：

```bash
# 数据库配置
DB_NAME=ZJOJ
DB_USER=zjoj_user
DB_PASSWORD=your_secure_password
DB_ROOT_PASSWORD=root_secure_password
DB_HOST=db
DB_PORT=3306

# DeepSeek API（可选）
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Django 配置
DJANGO_SECRET_KEY=change-this-to-a-random-string
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=*
```

### 4. 启动服务

```bash
# 构建并启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f web
```

首次启动会自动：
- ✅ 拉取 Docker 镜像
- ✅ 构建应用镜像
- ✅ 初始化数据库
- ✅ 执行数据迁移
- ✅ 收集静态文件

### 5. 创建管理员账户

```bash
# 使用默认密码
./deploy/create_admin.sh

# 自定义密码
./deploy/create_admin.sh admin YourPassword admin@example.com
```

### 6. 配置 AI API Key（可选）

```bash
./deploy/setup_ai_api.sh
```

选择 AI 提供商并输入 API Key。

### 7. 配置云服务器安全组

在阿里云/腾讯云控制台开放端口：

- **8000** - HTTP API
- **8443** - HTTPS API（可选）

---

## ⚙️ 配置说明

### 服务架构

```
┌─────────────────────────────────────┐
│         Docker Compose              │
│                                     │
│  ┌──────────┐  ┌────────────────┐  │
│  │  Nginx   │──│    Gunicorn    │  │
│  │ :8000    │  │   (Django)     │  │
│  └──────────┘  └───────┬────────┘  │
│                        │            │
│               ┌────────▼────────┐  │
│               │     MySQL       │  │
│               │      :3306      │  │
│               └─────────────────┘  │
└─────────────────────────────────────┘
```

### 端口映射

| 容器内端口 | 宿主机端口 | 用途 |
|-----------|-----------|------|
| 80 | 8000 | HTTP API |
| 443 | 8443 | HTTPS API |
| 3306 | 不暴露 | MySQL（仅内部访问） |

### 数据卷

| 数据卷 | 用途 | 位置 |
|-------|------|------|
| `mysql_data` | MySQL 数据 | `/var/lib/docker/volumes/` |
| `static_volume` | 静态文件 | `/home/zjoj/staticfiles` |
| `media_volume` | 媒体文件 | `/home/zjoj/media` |

---

## 🔧 常用命令

### 服务管理

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 重新构建并启动
docker compose up -d --build

# 查看服务状态
docker compose ps

# 查看资源使用
docker stats
```

### 日志查看

```bash
# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f web
docker compose logs -f db
docker compose logs -f nginx

# 查看最近 100 行日志
docker compose logs --tail=100 web
```

### 进入容器

```bash
# 进入 Web 容器
docker compose exec web bash

# 进入数据库容器
docker compose exec db mysql -uzjoj_user -p

# 执行 Django 命令
docker compose exec web python manage.py shell
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
```

### 数据库管理

```bash
# 备份数据库
docker compose exec db mysqldump -uzjoj_user -p ZJOJ > backup.sql

# 恢复数据库
docker compose exec -T db mysql -uzjoj_user -p ZJOJ < backup.sql

# 使用脚本备份
./deploy/docker-backup.sh backup_$(date +%Y%m%d).tar.gz

# 使用脚本恢复
./deploy/docker-restore.sh backup_20260422.tar.gz
```

### 更新部署

```bash
# 拉取最新代码
git pull origin feature/ai-assistant-step1

# 重新构建并启动
docker compose up -d --build

# 查看日志确认
docker compose logs -f web
```

---

## 🆘 故障排查

### 1. 服务无法启动

```bash
# 查看详细日志
docker compose logs web

# 检查端口占用
sudo ss -tlnp | grep ':8000'

# 重新启动
docker compose down
docker compose up -d
```

### 2. 数据库连接失败

```bash
# 检查数据库是否运行
docker compose ps db

# 查看数据库日志
docker compose logs db

# 测试连接
docker compose exec web python -c "from django.db import connection; print(connection.ensure_connection())"
```

### 3. 端口被占用

```bash
# 查找占用端口的进程
sudo ss -tlnp | grep ':8000'

# 停止占用端口的服务
sudo kill -9 <PID>

# 或修改 docker-compose.yml 中的端口映射
```

### 4. 权限问题

```bash
# 确保当前用户在 docker 组
groups

# 如果没有，添加用户
sudo usermod -aG docker $USER

# 重新登录
exit
```

### 5. 磁盘空间不足

```bash
# 检查磁盘使用
df -h

# 清理未使用的 Docker 资源
docker system prune -a

# 清理日志
docker compose logs --tail=0
```

---

## ⚡ 性能优化

### 1. Gunicorn 配置

当前配置（已优化）：
- Workers: 4
- Worker Class: gevent（异步）
- Threads: 2
- Keep-alive: 5秒

如需调整，编辑 `docker-compose.yml`：

```yaml
command: >
  sh -c "python manage.py migrate &&
         python manage.py collectstatic --noinput &&
         gunicorn --workers 4 --worker-class gevent --threads 2 --bind 0.0.0.0:8000 --timeout 120 --keep-alive 5 ZJOJ.wsgi:application"
```

### 2. MySQL 优化

编辑 `docker-compose.yml` 中的 MySQL 配置：

```yaml
db:
  command: >
    --max-connections=200
    --innodb-buffer-pool-size=1G
    --query-cache-size=64M
```

### 3. Nginx 优化

启用 Gzip 压缩（已在 `deploy/nginx.conf` 中配置）：

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### 4. 缓存策略

- 启用 Redis 缓存（需额外配置）
- 使用 CDN 加速静态文件
- 浏览器缓存静态资源

---

## 🔒 安全建议

### 1. 修改默认密码

```bash
# 修改数据库密码
./deploy/setup_env.sh

# 修改管理员密码
./deploy/create_admin.sh admin NewSecurePassword admin@example.com
```

### 2. 启用 HTTPS

```bash
# 使用 Let's Encrypt 免费证书
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# 配置 Nginx SSL
# 编辑 deploy/nginx.conf 添加 SSL 配置
```

### 3. 限制访问

在 `docker-compose.yml` 中限制允许的 IP：

```yaml
environment:
  DJANGO_ALLOWED_HOSTS: your-domain.com,www.your-domain.com
```

### 4. 定期备份

```bash
# 设置定时备份（crontab）
0 2 * * * cd /path/to/ZJOJ-backend && ./deploy/docker-backup.sh backup_$(date +\%Y\%m\%d).tar.gz
```

---

## 📊 监控

### 1. 容器监控

```bash
# 实时查看资源使用
docker stats

# 查看详细信息
docker inspect zjoj-web
```

### 2. 应用监控

```bash
# 查看 Django 日志
docker compose logs -f web

# 查看错误日志
docker compose logs web | grep ERROR
```

### 3. 数据库监控

```bash
# 查看连接数
docker compose exec db mysql -e "SHOW STATUS LIKE 'Threads_connected';"

# 查看慢查询
docker compose exec db mysql -e "SHOW VARIABLES LIKE 'slow_query_log';"
```

---

## 📞 技术支持

如有问题，请：

1. 查看日志：`docker compose logs -f web`
2. 检查文档：[deploy/README.md](../deploy/README.md)
3. 提交 Issue：https://github.com/hhdhhy/ZJOJ-backend/issues

---

## 🎯 下一步

- [API 参考文档](./04-API_REFERENCE.md)
- [开发指南](./DEVELOPMENT_GUIDE.md)
- [数据库设计](./DATABASE_DESIGN.md)
- [AI 助手指南](./AI_ASSISTANT_GUIDE.md)
