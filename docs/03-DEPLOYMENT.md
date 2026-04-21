# 部署指南

> 📦 ZJOJ 生产环境部署完整流程

---

## 📋 目录

- [部署方式选择](#部署方式选择)
- [Docker 部署（推荐）](#docker-部署推荐)
- [传统部署](#传统部署)
- [部署架构](#部署架构)
- [系统要求](#系统要求)
- [快速部署](#快速部署)
- [详细步骤](#详细步骤)
- [进程管理](#进程管理)
- [监控与日志](#监控与日志)
- [常见问题](#常见问题)

---

## 🎯 部署方式选择

ZJOJ 提供两种部署方式：

### 方式一：Docker Compose 部署（⭐ 推荐）

**优点**：
- ✅ 一键部署，5分钟完成
- ✅ 环境隔离，无依赖冲突
- ✅ 易于维护和升级
- ✅ 自动管理数据库和静态文件

**适用场景**：
- 快速部署测试环境
- 生产环境（推荐）
- 不熟悉 Linux 系统管理的用户

**快速开始**：
```bash
git clone git@github.com:hhdhhy/ZJOJ-backend.git
cd ZJOJ-backend
./deploy/setup_env.sh
docker compose up -d
./deploy/create_admin.sh admin YourPassword admin@example.com
```

详细文档：[deploy/README.md](../deploy/README.md)

---

### 方式二：传统手动部署

**优点**：
- ✅ 完全控制每个组件
- ✅ 可定制化程度高
- ✅ 适合学习和理解系统架构

**缺点**：
- ❌ 配置复杂，耗时长
- ❌ 需要手动管理依赖
- ❌ 维护成本高

**适用场景**：
- 学习系统架构
- 特殊定制需求
- 已有成熟运维体系

**快速开始**：见下方[详细步骤](#详细步骤)

---

> 💡 **建议**：大多数场景推荐使用 Docker 部署，简单高效且易于维护。

---

## 🏗️ 部署架构

```
                    ┌─────────────┐
                    │   Client    │
                    │  (Browser)  │
                    └──────┬──────┘
                           │ HTTPS
                    ┌──────▼──────┐
                    │   Nginx     │
                    │  (Reverse   │
                    │   Proxy)    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
     ┌────────▼────┐ ┌────▼─────┐ ┌───▼────────┐
     │  Gunicorn   │ │ go-judge │ │  ChromaDB  │
     │  (Django)   │ │Sandbox   │ │ (Vector DB)│
     └────────┬────┘ └────┬─────┘ └────────────┘
              │            │
     ┌────────▼────────────▼────────┐
     │         MySQL 5.7+           │
     │      (Primary Database)      │
     └──────────────────────────────┘
```

### 组件说明

| 组件 | 用途 | 端口 |
|------|------|------|
| **Nginx** | 反向代理、静态文件、SSL | 8000/8443 |
| **Gunicorn** | WSGI 服务器，运行 Django | 8000 (内部) |
| **MySQL** | 主数据库 | 3306 (仅内部) |

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
| **Python** | 3.8 - 3.11 |
| **MySQL** | 5.7+ / 8.0+ |
| **Nginx** | 1.18+ |
| **Node.js** | 16+ (go-judge 依赖) |

---

## 🚀 快速部署

### Ubuntu 20.04 一键部署

```bash
#!/bin/bash
set -e

echo "🚀 开始部署 ZJOJ..."

# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装依赖
sudo apt install -y python3.10 python3.10-venv python3-pip mysql-server nginx git nodejs npm

# 3. 克隆项目
cd /opt
sudo git clone https://github.com/your-repo/ZJOJ.git zjoj
cd zjoj

# 4. 创建虚拟环境
python3.10 -m venv .venv
source .venv/bin/activate

# 5. 安装 Python 依赖
pip install --upgrade pip
pip install django djangorestframework gunicorn mysqlclient requests

# 6. 安装 go-judge
sudo su -c 'LANG=zh . <(curl https://hydro.ac/setup.sh) --judge'

# 7. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 8. 初始化数据库
python manage.py migrate
python manage.py createsuperuser

# 9. 收集静态文件
python manage.py collectstatic --noinput

# 10. 启动服务
sudo systemctl start zjoj
sudo systemctl enable zjoj

echo "✅ 部署完成！"
echo "访问: http://your-server-ip"
```

---

## 📝 详细步骤

### 1. 服务器准备

#### 1.1 更新系统

```bash
# Ubuntu
sudo apt update && sudo apt upgrade -y

# CentOS
sudo yum update -y
```

#### 1.2 创建专用用户

```bash
sudo useradd -m -s /bin/bash zjoj
sudo usermod -aG sudo zjoj  # Ubuntu
su - zjoj
```

---

### 2. 安装依赖

#### 2.1 安装 Python

```bash
# Ubuntu
sudo apt install -y python3.10 python3.10-venv python3.10-dev

# 验证
python3.10 --version
```

#### 2.2 安装 MySQL

```bash
# Ubuntu
sudo apt install -y mysql-server

# 启动并设置开机自启
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation
```

#### 2.3 安装 Nginx

```bash
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 2.4 安装 Node.js (go-judge 依赖)

```bash
# 使用 NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 验证
node --version
npm --version
```

---

### 3. 配置数据库

#### 3.1 创建数据库

```bash
mysql -u root -p
```

```sql
CREATE DATABASE zjoj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'zjoj_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON zjoj.* TO 'zjoj_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3.2 配置 Django

编辑 `ZJOJ/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zjoj',
        'USER': 'zjoj_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```

---

### 4. 部署 Django 应用

#### 4.1 克隆项目

```bash
cd /opt
sudo git clone https://github.com/your-repo/ZJOJ.git zjoj
sudo chown -R zjoj:zjoj zjoj
cd zjoj
```

#### 4.2 创建虚拟环境

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

#### 4.3 安装依赖

```bash
pip install --upgrade pip
pip install django djangorestframework gunicorn mysqlclient requests
pip install sentence-transformers chromadb openai modelscope  # AI 功能
```

#### 4.4 配置环境变量

```bash
cp .env.example .env
nano .env
```

关键配置：
```env
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_NAME=zjoj
DB_USER=zjoj_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

HYDRO_JUDGE_URL=http://localhost:5050
```

#### 4.5 初始化数据库

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

### 5. 安装 go-judge

```bash
# 使用 Hydro OJ 官方脚本
sudo su -c 'LANG=zh . <(curl https://hydro.ac/setup.sh) --judge'

# 检查服务状态
sudo pm2 status | grep hydro-sandbox

# 测试 API
curl -s http://localhost:5050/run -X POST \
  -H 'Content-Type: application/json' \
  -d '{"cmd":[{"args":["/bin/echo","Hello"]}]}' | python3 -m json.tool
```

---

### 6. 配置 Nginx

创建配置文件 `/etc/nginx/sites-available/zjoj`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # 静态文件
    location /static/ {
        alias /opt/zjoj/staticfiles/;
        expires 30d;
    }

    # 媒体文件
    location /media/ {
        alias /opt/zjoj/media/;
        expires 30d;
    }

    # Django 应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/zjoj /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### 7. 配置 Gunicorn

创建 systemd 服务文件 `/etc/systemd/system/zjoj.service`:

```ini
[Unit]
Description=ZJOJ Gunicorn Service
After=network.target mysql.service

[Service]
User=zjoj
Group=zjoj
WorkingDirectory=/opt/zjoj
Environment="PATH=/opt/zjoj/.venv/bin"
ExecStart=/opt/zjoj/.venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    ZJOJ.wsgi:application

Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start zjoj
sudo systemctl enable zjoj
sudo systemctl status zjoj
```

---

### 8. 配置 HTTPS (Let's Encrypt)

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期测试
sudo certbot renew --dry-run
```

---

## 🔧 进程管理

### 查看服务状态

```bash
# Django (Gunicorn)
sudo systemctl status zjoj

# go-judge
sudo pm2 status | grep hydro-sandbox

# Nginx
sudo systemctl status nginx

# MySQL
sudo systemctl status mysql
```

### 重启服务

```bash
# 重启 Django
sudo systemctl restart zjoj

# 重启 go-judge
sudo pm2 restart hydro-sandbox

# 重启 Nginx
sudo systemctl restart nginx
```

### 查看日志

```bash
# Django 日志
sudo journalctl -u zjoj -f

# go-judge 日志
sudo pm2 logs hydro-sandbox

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 📊 监控与日志

### 系统监控

```bash
# CPU 和内存
htop

# 磁盘使用
df -h

# 网络连接
ss -tulpn | grep :8000
ss -tulpn | grep :5050
```

### 应用监控

```python
# Django Debug Toolbar (仅开发环境)
INSTALLED_APPS = [
    'debug_toolbar',
]
```

### 日志配置

`ZJOJ/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/zjoj/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## 🔄 备份策略

### 数据库备份

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

mysqldump -u root -p zjoj > $BACKUP_DIR/zjoj_$DATE.sql

# 保留最近 7 天的备份
find $BACKUP_DIR -name "zjoj_*.sql" -mtime +7 -delete
```

### 定时备份

```bash
# crontab -e
0 2 * * * /opt/zjoj/backup.sh
```

---

## ⚡ 性能优化

### Gunicorn 优化

```ini
--workers 3              # CPU 核心数 * 2 + 1
--threads 2              # 每个 worker 的线程数
--worker-class gthread   # 使用线程 worker
--keep-alive 5           # Keep-Alive 超时
```

### MySQL 优化

`/etc/mysql/mysql.conf.d/mysqld.cnf`:

```ini
[mysqld]
innodb_buffer_pool_size = 1G
max_connections = 200
query_cache_size = 64M
```

### Nginx 优化

```nginx
worker_processes auto;
worker_connections 1024;

gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

---

## 🐛 常见问题

### Q1: Gunicorn 启动失败

**检查日志**:
```bash
sudo journalctl -u zjoj -n 50
```

**常见原因**:
- 端口被占用
- 权限问题
- 依赖未安装

---

### Q2: go-judge 无法访问

**检查服务**:
```bash
sudo pm2 status | grep hydro-sandbox
sudo pm2 logs hydro-sandbox
```

**重启服务**:
```bash
sudo pm2 restart hydro-sandbox
```

---

### Q3: 502 Bad Gateway

**原因**: Gunicorn 未运行或 Nginx 配置错误

**解决**:
```bash
# 检查 Gunicorn
sudo systemctl status zjoj

# 检查 Nginx 配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

---

### Q4: 数据库连接失败

**检查**:
```bash
# MySQL 是否运行
sudo systemctl status mysql

# 用户权限
mysql -u zjoj_user -p -h localhost zjoj

# 防火墙
sudo ufw status
```

---

### Q5: 静态文件 404

**解决**:
```bash
# 重新收集静态文件
python manage.py collectstatic --noinput

# 检查 Nginx 配置
ls -la /opt/zjoj/staticfiles/
```

---

## 📞 获取帮助

遇到问题？

1. 📖 查看[完整文档](README.md)
2. 🔍 搜索 Issue
3. 💬 加入社区
4. 📝 提交新 Issue

---

<div align="center">

**继续阅读 →** [API 参考](04-API_REFERENCE.md)

</div>
