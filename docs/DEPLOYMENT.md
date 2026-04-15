# ZJOJ 铸剑 - 生产环境部署指南

> **版本**: v1.0.0  
> **最后更新**: 2026年4月16日  
> **适用系统**: Linux (Ubuntu 20.04+/CentOS 7+) / Windows Server

---

## 📋 目录

- [部署架构](#部署架构)
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [详细部署步骤](#详细部署步骤)
  - [1. 服务器准备](#1-服务器准备)
  - [2. 安装依赖](#2-安装依赖)
  - [3. 配置数据库](#3-配置数据库)
  - [4. 部署Django应用](#4-部署django应用)
  - [5. 配置Web服务器](#5-配置web服务器)
  - [6. 配置Celery](#6-配置celery)
  - [7. 配置AI助手](#7-配置ai助手)
  - [8. 配置HTTPS](#8-配置https)
- [进程管理](#进程管理)
- [监控与日志](#监控与日志)
- [备份策略](#备份策略)
- [性能优化](#性能优化)
- [故障排查](#故障排查)

---

## 部署架构

### 标准部署架构

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
     │  Gunicorn   │ │  Celery  │ │  ChromaDB  │
     │  (Django)   │ │ Worker   │ │ (Vector DB)│
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
| **Nginx** | 反向代理、静态文件服务、SSL终止 | 80/443 |
| **Gunicorn** | WSGI HTTP服务器，运行Django应用 | 8000 (内部) |
| **Celery Worker** | 异步任务处理（代码评测） | - |
| **MySQL** | 主数据库 | 3306 |
| **ChromaDB** | 向量数据库（AI助手） | 内部调用 |
| **Redis** (可选) | Celery Broker + Cache | 6379 |

---

## 系统要求

### 硬件要求

| 配置项 | 最低配置 | 推荐配置 | 说明 |
|--------|---------|---------|------|
| **CPU** | 2核 | 4核+ | Celery评测需要多核 |
| **内存** | 4GB | 8GB+ | AI模型需要约400MB |
| **磁盘** | 20GB | 50GB+ SSD | 数据库+日志+AI模型 |
| **网络** | 1Mbps | 10Mbps+ | API响应速度 |

### 软件要求

| 软件 | 版本 | 说明 |
|------|------|------|
| **操作系统** | Ubuntu 20.04+ / CentOS 7+ | 推荐Ubuntu |
| **Python** | 3.8 - 3.11 | 推荐3.10 |
| **MySQL** | 5.7+ / 8.0+ | 推荐8.0 |
| **Nginx** | 1.18+ | 反向代理 |
| **Redis** | 6.0+ | 可选，用于Celery和缓存 |
| **Git** | 2.0+ | 代码管理 |

---

## 快速开始

### Ubuntu 20.04 一键部署脚本

```bash
#!/bin/bash
# deploy.sh - ZJOJ 快速部署脚本

set -e

echo "🚀 开始部署 ZJOJ..."

# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装依赖
sudo apt install -y python3.10 python3.10-venv python3-pip mysql-server nginx git

# 3. 克隆项目
cd /opt
sudo git clone https://github.com/hhdhhy/ZJOJ-backend.git zjoj
cd zjoj

# 4. 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate

# 5. 安装Python依赖
pip install --upgrade pip
pip install django==6.0.3 djangorestframework celery gunicorn mysqlclient
pip install sentence-transformers chromadb openai modelscope

# 6. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置正确的配置

# 7. 初始化数据库
python manage.py migrate
python manage.py createsuperuser

# 8. 收集静态文件
python manage.py collectstatic --noinput

# 9. 启动服务
sudo systemctl start zjoj
sudo systemctl start zjoj-celery
sudo systemctl enable zjoj
sudo systemctl enable zjoj-celery

echo "✅ 部署完成！"
echo "访问: http://your-server-ip"
echo "Admin: http://your-server-ip/admin"
```

---

## 详细部署步骤

### 1. 服务器准备

#### 1.1 更新系统

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt upgrade -y
```

**CentOS/RHEL:**
```bash
sudo yum update -y
```

#### 1.2 安装基础工具

```bash
# Ubuntu
sudo apt install -y git curl wget vim build-essential

# CentOS
sudo yum install -y git curl wget vim gcc gcc-c++ make
```

#### 1.3 创建专用用户

```bash
sudo useradd -m -s /bin/bash zjoj
sudo usermod -aG sudo zjoj  # Ubuntu
# 或
sudo usermod -aG wheel zjoj  # CentOS

su - zjoj
```

---

### 2. 安装依赖

#### 2.1 安装Python 3.10

**Ubuntu:**
```bash
sudo apt install -y python3.10 python3.10-venv python3.10-dev
```

**CentOS:**
```bash
sudo yum install -y python3.10 python3.10-devel
```

#### 2.2 安装MySQL

**Ubuntu:**
```bash
sudo apt install -y mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
sudo mysql_secure_installation
```

**CentOS:**
```bash
sudo yum install -y mysql-server
sudo systemctl start mysqld
sudo systemctl enable mysqld
sudo mysql_secure_installation
```

#### 2.3 安装Nginx

```bash
# Ubuntu
sudo apt install -y nginx

# CentOS
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 2.4 安装Redis（可选但推荐）

```bash
# Ubuntu
sudo apt install -y redis-server
sudo systemctl start redis
sudo systemctl enable redis

# CentOS
sudo yum install -y redis
sudo systemctl start redis
sudo systemctl enable redis
```

---

### 3. 配置数据库

#### 3.1 创建数据库和用户

```bash
mysql -u root -p
```

```sql
-- 创建数据库
CREATE DATABASE zjoj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建专用用户
CREATE USER 'zjoj'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';

-- 授权
GRANT ALL PRIVILEGES ON zjoj.* TO 'zjoj'@'localhost';
FLUSH PRIVILEGES;

EXIT;
```

#### 3.2 优化MySQL配置

编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf` (Ubuntu) 或 `/etc/my.cnf` (CentOS):

```ini
[mysqld]
# 字符集
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 连接数
max_connections = 200

# 查询缓存（MySQL 5.7）
query_cache_type = 1
query_cache_size = 64M

# InnoDB优化
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2

# 慢查询日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
```

重启MySQL：
```bash
sudo systemctl restart mysql
```

---

### 4. 部署Django应用

#### 4.1 克隆项目

```bash
cd /opt
sudo git clone https://github.com/hhdhhy/ZJOJ-backend.git zjoj
sudo chown -R zjoj:zjoj zjoj
cd zjoj
```

#### 4.2 创建虚拟环境

```bash
python3.10 -m venv venv
source venv/bin/activate
```

#### 4.3 安装Python依赖

**创建 requirements.txt:**

```txt
# Core
django==6.0.3
djangorestframework==3.14.0
django-cors-headers==4.3.0
gunicorn==21.2.0

# Database
mysqlclient==2.2.0

# Authentication
PyJWT==2.8.0
shortuuidfield==0.3.0

# Celery
celery==5.3.6
sqlalchemy==2.0.23

# AI Assistant
sentence-transformers==2.2.2
chromadb==0.4.22
openai==1.6.1
modelscope==1.11.0

# Utilities
python-dotenv==1.0.0
```

**安装依赖：**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4.4 配置环境变量

**创建 `.env` 文件：**

```bash
cp .env.example .env
nano .env
```

**.env 配置示例：**

```ini
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

# Database
DATABASE_NAME=zjoj
DATABASE_USER=zjoj
DATABASE_PASSWORD=YourStrongPassword123!
DATABASE_HOST=localhost
DATABASE_PORT=3306

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Celery (使用Redis)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# HydroJudge
HYDRO_JUDGE_URL=http://localhost:5050
HYDRO_JUDGE_TIMEOUT=30

# AI Assistant
EMBEDDING_CACHE_DIR=/opt/zjoj_data/ai_models
CHROMA_DB_PATH=/opt/zjoj_data/chroma_db
DEEPSEEK_API_KEY=sk-your-api-key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Static Files
STATIC_ROOT=/opt/zjoj_data/static
MEDIA_ROOT=/opt/zjoj_data/media
```

**注意**: 生成安全的SECRET_KEY：
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 4.5 修改settings.py读取环境变量

在项目根目录创建 `ZJOJ/config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Django Settings
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_ALL_ORIGINS = False

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

# AI Assistant
EMBEDDING_CACHE_DIR = os.getenv('EMBEDDING_CACHE_DIR', '/opt/zjoj_data/ai_models')
CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', '/opt/zjoj_data/chroma_db')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')

# Static Files
STATIC_ROOT = os.getenv('STATIC_ROOT', '/opt/zjoj_data/static')
MEDIA_ROOT = os.getenv('MEDIA_ROOT', '/opt/zjoj_data/media')
```

在 `settings.py` 末尾添加：
```python
# 加载生产环境配置
try:
    from ZJOJ.config import *
except ImportError:
    pass
```

#### 4.6 创建数据目录

```bash
sudo mkdir -p /opt/zjoj_data/{ai_models,chroma_db,static,media,logs}
sudo chown -R zjoj:zjoj /opt/zjoj_data
```

#### 4.7 数据库迁移

```bash
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

#### 4.8 创建超级用户

```bash
python manage.py createsuperuser
```

按提示输入：
- 用户名（必填）
- 邮箱
- 密码

#### 4.9 收集静态文件

```bash
python manage.py collectstatic --noinput
```

#### 4.10 初始化AI助手（可选）

```bash
# 添加知识库文档
python tests/add_knowledge_base.py

# 同步到向量数据库
python tests/sync_knowledge_to_vector.py
```

**注意**: 首次运行会自动下载Embedding模型（约390MB），请耐心等待。

---

### 5. 配置Web服务器

#### 5.1 配置Gunicorn

**创建 `gunicorn_config.py`:**

```python
# Gunicorn配置文件
import multiprocessing

# 服务器套接字绑定
bind = "127.0.0.1:8000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作进程类型
worker_class = "sync"

# 单个工作进程的最大连接数
worker_connections = 1000

# 超时时间（秒）
timeout = 120

# 保持连接数
keepalive = 5

# 进程命名
proc_name = "zjoj"

# PID文件
pidfile = "/opt/zjoj_data/gunicorn.pid"

# 日志配置
accesslog = "/opt/zjoj_data/logs/gunicorn_access.log"
errorlog = "/opt/zjoj_data/logs/gunicorn_error.log"
loglevel = "info"

# 预加载应用
preload_app = True

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50
```

#### 5.2 配置Nginx

**创建 `/etc/nginx/sites-available/zjoj`:**

```nginx
upstream zjoj_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # 日志
    access_log /opt/zjoj_data/logs/nginx_access.log;
    error_log /opt/zjoj_data/logs/nginx_error.log;

    # 客户端最大上传大小
    client_max_body_size 10M;

    # 静态文件
    location /static/ {
        alias /opt/zjoj_data/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 媒体文件
    location /media/ {
        alias /opt/zjoj_data/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Django应用
    location / {
        proxy_pass http://zjoj_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # 健康检查
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

**启用站点：**

```bash
sudo ln -s /etc/nginx/sites-available/zjoj /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

---

### 6. 配置Celery

#### 6.1 创建systemd服务文件

**创建 `/etc/systemd/system/zjoj-celery.service`:**

```ini
[Unit]
Description=ZJOJ Celery Worker
After=network.target mysql.service redis.service
Wants=mysql.service redis.service

[Service]
Type=simple
User=zjoj
Group=zjoj
WorkingDirectory=/opt/zjoj
Environment="PATH=/opt/zjoj/venv/bin"
ExecStart=/opt/zjoj/venv/bin/celery -A ZJOJ worker --loglevel=info --concurrency=4
Restart=on-failure
RestartSec=10

# 日志
StandardOutput=append:/opt/zjoj_data/logs/celery_worker.log
StandardError=append:/opt/zjoj_data/logs/celery_worker_error.log

# 资源限制
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

#### 6.2 创建Celery Beat服务（定时任务，可选）

**创建 `/etc/systemd/system/zjoj-celerybeat.service`:**

```ini
[Unit]
Description=ZJOJ Celery Beat
After=network.target mysql.service redis.service

[Service]
Type=simple
User=zjoj
Group=zjoj
WorkingDirectory=/opt/zjoj
Environment="PATH=/opt/zjoj/venv/bin"
ExecStart=/opt/zjoj/venv/bin/celery -A ZJOJ beat --loglevel=info
Restart=on-failure
RestartSec=10

StandardOutput=append:/opt/zjoj_data/logs/celery_beat.log
StandardError=append:/opt/zjoj_data/logs/celery_beat_error.log

[Install]
WantedBy=multi-user.target
```

---

### 7. 配置AI助手

#### 7.1 创建Django systemd服务

**创建 `/etc/systemd/system/zjoj.service`:**

```ini
[Unit]
Description=ZJOJ Django Application
After=network.target mysql.service redis.service
Wants=mysql.service redis.service

[Service]
Type=notify
User=zjoj
Group=zjoj
WorkingDirectory=/opt/zjoj
Environment="PATH=/opt/zjoj/venv/bin"
ExecStart=/opt/zjoj/venv/bin/gunicorn -c gunicorn_config.py ZJOJ.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=10

# 日志
StandardOutput=append:/opt/zjoj_data/logs/gunicorn_stdout.log
StandardError=append:/opt/zjoj_data/logs/gunicorn_stderr.log

# 资源限制
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

#### 7.2 启动服务

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start zjoj
sudo systemctl start zjoj-celery

# 设置开机自启
sudo systemctl enable zjoj
sudo systemctl enable zjoj-celery

# 查看状态
sudo systemctl status zjoj
sudo systemctl status zjoj-celery
```

---

### 8. 配置HTTPS

#### 8.1 使用Let's Encrypt（免费）

**安装Certbot：**

```bash
# Ubuntu
sudo apt install -y certbot python3-certbot-nginx

# CentOS
sudo yum install -y certbot python3-certbot-nginx
```

**获取证书：**

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

按照提示操作，Certbot会自动配置Nginx并启用HTTPS。

**自动续期：**

```bash
# 测试续期
sudo certbot renew --dry-run

# 添加定时任务
sudo crontab -e
# 添加以下行（每月1号凌晨2点检查续期）
0 2 1 * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

#### 8.2 手动配置SSL（已有证书）

编辑Nginx配置，添加SSL部分：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # ... 其他配置同上
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 进程管理

### 常用命令

```bash
# 查看服务状态
sudo systemctl status zjoj
sudo systemctl status zjoj-celery

# 重启服务
sudo systemctl restart zjoj
sudo systemctl restart zjoj-celery

# 停止服务
sudo systemctl stop zjoj
sudo systemctl stop zjoj-celery

# 查看日志
sudo journalctl -u zjoj -f
sudo journalctl -u zjoj-celery -f

# 查看实时日志
tail -f /opt/zjoj_data/logs/gunicorn_error.log
tail -f /opt/zjoj_data/logs/celery_worker.log
```

### 手动管理Gunicorn

```bash
# 启动
cd /opt/zjoj
source venv/bin/activate
gunicorn -c gunicorn_config.py ZJOJ.wsgi:application

# 优雅重启（不中断服务）
kill -HUP $(cat /opt/zjoj_data/gunicorn.pid)

# 停止
kill $(cat /opt/zjoj_data/gunicorn.pid)
```

---

## 监控与日志

### 日志文件位置

| 日志类型 | 路径 | 说明 |
|---------|------|------|
| Nginx访问日志 | `/opt/zjoj_data/logs/nginx_access.log` | HTTP请求日志 |
| Nginx错误日志 | `/opt/zjoj_data/logs/nginx_error.log` | Nginx错误 |
| Gunicorn访问日志 | `/opt/zjoj_data/logs/gunicorn_access.log` | Django请求日志 |
| Gunicorn错误日志 | `/opt/zjoj_data/logs/gunicorn_error.log` | Django错误 |
| Celery Worker日志 | `/opt/zjoj_data/logs/celery_worker.log` | 异步任务日志 |
| Celery错误日志 | `/opt/zjoj_data/logs/celery_worker_error.log` | 任务错误 |

### 日志轮转配置

**创建 `/etc/logrotate.d/zjoj`:**

```
/opt/zjoj_data/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 zjoj zjoj
    sharedscripts
    postrotate
        systemctl reload zjoj > /dev/null 2>&1 || true
    endscript
}
```

### 监控工具

#### 1. 使用htop监控系统资源

```bash
sudo apt install -y htop
htop
```

#### 2. 监控MySQL

```bash
# 查看当前连接
mysql -u root -p -e "SHOW PROCESSLIST;"

# 查看慢查询
mysql -u root -p -e "SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;"
```

#### 3. 监控Celery

```bash
# 查看活跃任务
celery -A ZJOJ inspect active

# 查看注册的任务
celery -A ZJOJ inspect registered

# 查看统计信息
celery -A ZJOJ inspect stats
```

#### 4. 使用Prometheus + Grafana（高级）

安装exporter：
```bash
# Django metrics
pip install django-prometheus

# 在settings.py中添加
INSTALLED_APPS = [
    'django_prometheus',
    # ...
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... 其他中间件
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

---

## 备份策略

### 1. 数据库备份

**创建备份脚本 `/opt/zjoj/backup_db.sh`:**

```bash
#!/bin/bash
BACKUP_DIR="/opt/zjoj_data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="zjoj"
DB_USER="zjoj"
DB_PASS="YourStrongPassword123!"

mkdir -p $BACKUP_DIR

# 全量备份
mysqldump -u $DB_USER -p$DB_PASS \
    --single-transaction \
    --routines \
    --triggers \
    $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# 删除30天前的备份
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Database backup completed: db_backup_$DATE.sql.gz"
```

**设置权限并添加到crontab：**

```bash
chmod +x /opt/zjoj/backup_db.sh

# 每天凌晨3点备份
crontab -e
0 3 * * * /opt/zjoj/backup_db.sh >> /opt/zjoj_data/logs/backup.log 2>&1
```

### 2. 媒体文件备份

```bash
#!/bin/bash
BACKUP_DIR="/opt/zjoj_data/backups"
DATE=$(date +%Y%m%d_%H%M%S)

tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /opt/zjoj_data/media/

# 删除30天前的备份
find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +30 -delete

echo "Media backup completed: media_backup_$DATE.tar.gz"
```

### 3. 完整备份脚本

**创建 `/opt/zjoj/backup_all.sh`:**

```bash
#!/bin/bash
set -e

BACKUP_DIR="/opt/zjoj_data/backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "Starting full backup at $(date)"

# 1. 数据库备份
/opt/zjoj/backup_db.sh

# 2. 媒体文件备份
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /opt/zjoj_data/media/

# 3. 代码备份
tar -czf $BACKUP_DIR/code_backup_$DATE.tar.gz /opt/zjoj --exclude='venv' --exclude='__pycache__'

# 4. 清理旧备份
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Full backup completed at $(date)"
```

### 4. 远程备份（可选）

```bash
# 使用rsync备份到远程服务器
rsync -avz /opt/zjoj_data/backups/ user@backup-server:/backup/zjoj/

# 或使用AWS S3
aws s3 sync /opt/zjoj_data/backups/ s3://your-bucket/zjoj-backups/
```

---

## 性能优化

### 1. Gunicorn优化

根据服务器配置调整 `gunicorn_config.py`:

```python
# CPU密集型任务
workers = multiprocessing.cpu_count() * 2 + 1

# I/O密集型任务
workers = multiprocessing.cpu_count() * 4 + 1

# 每个worker的线程数（如果使用gthread）
threads = 2
```

### 2. MySQL优化

编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`:

```ini
[mysqld]
# 根据内存大小调整
innodb_buffer_pool_size = 2G          # 50-70% of RAM
innodb_log_file_size = 512M
innodb_flush_method = O_DIRECT

# 连接池
max_connections = 500
thread_cache_size = 64

# 查询优化
query_cache_type = 1
query_cache_size = 128M
tmp_table_size = 64M
max_heap_table_size = 64M
```

### 3. Redis缓存配置

在Django settings中添加：

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 缓存热门数据
CACHE_TTL = 60 * 15  # 15分钟
```

### 4. Nginx优化

```nginx
# 启用gzip压缩
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

#  worker进程数
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}
```

### 5. 数据库索引优化

确保关键查询有索引：

```sql
-- 提交记录查询优化
ALTER TABLE submission ADD INDEX idx_user_problem (user_id, problem_id);
ALTER TABLE submission ADD INDEX idx_status_time (status, submit_time);

-- 题目查询优化
ALTER TABLE problem_problem ADD FULLTEXT INDEX ft_title_desc (title, description(500));
```

---

## 故障排查

### 常见问题及解决方案

#### Q1: 502 Bad Gateway

**可能原因：**
- Gunicorn未启动
- Gunicorn崩溃
- Nginx配置错误

**解决方案：**
```bash
# 检查Gunicorn状态
sudo systemctl status zjoj

# 查看Gunicorn日志
tail -f /opt/zjoj_data/logs/gunicorn_error.log

# 重启Gunicorn
sudo systemctl restart zjoj

# 检查Nginx配置
sudo nginx -t
sudo systemctl restart nginx
```

#### Q2: 数据库连接失败

**检查项：**
```bash
# 1. MySQL是否运行
sudo systemctl status mysql

# 2. 测试连接
mysql -u zjoj -p -h localhost zjoj

# 3. 检查防火墙
sudo ufw status

# 4. 查看MySQL错误日志
sudo tail -f /var/log/mysql/error.log
```

#### Q3: Celery任务不执行

**解决方案：**
```bash
# 1. 检查Celery状态
sudo systemctl status zjoj-celery

# 2. 查看Celery日志
tail -f /opt/zjoj_data/logs/celery_worker.log

# 3. 检查Broker连接
celery -A ZJOJ inspect ping

# 4. 重启Celery
sudo systemctl restart zjoj-celery

# 5. 检查任务队列
celery -A ZJOJ inspect active
```

#### Q4: 静态文件404

**解决方案：**
```bash
# 1. 重新收集静态文件
source venv/bin/activate
python manage.py collectstatic --noinput

# 2. 检查文件权限
sudo chown -R www-data:www-data /opt/zjoj_data/static

# 3. 检查Nginx配置
sudo nginx -t
sudo systemctl reload nginx
```

#### Q5: ChromaDB hnsw索引错误

**解决方案：**
```bash
# 1. 停止Django
sudo systemctl stop zjoj

# 2. 删除损坏的数据库
rm -rf /opt/zjoj_data/chroma_db/*

# 3. 重启Django
sudo systemctl start zjoj

# 4. 重新同步知识库
source venv/bin/activate
python tests/sync_knowledge_to_vector.py
```

#### Q6: 内存不足

**监控内存使用：**
```bash
free -h
htop
```

**解决方案：**
```bash
# 1. 减少Gunicorn workers
# 编辑 gunicorn_config.py
workers = 2  # 降低worker数量

# 2. 增加swap空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 3. 优化MySQL内存使用
# 减少 innodb_buffer_pool_size
```

#### Q7: AI助手API调用失败

**检查项：**
```bash
# 1. 检查API密钥
echo $DEEPSEEK_API_KEY

# 2. 测试API连接
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Hello"}]}'

# 3. 查看Django日志
tail -f /opt/zjoj_data/logs/gunicorn_error.log | grep -i "ai\|llm\|deepseek"
```

### 调试技巧

#### 1. 启用Django Debug模式（临时）

```python
# .env
DEBUG=True

# 重启服务
sudo systemctl restart zjoj
```

**注意**: 生产环境不要长期开启DEBUG！

#### 2. 查看实时日志

```bash
# 同时监控多个日志
tail -f /opt/zjoj_data/logs/*.log
```

#### 3. 数据库查询分析

```python
# Django shell
python manage.py shell

from django.db import connection
from django.conf import settings

# 启用查询日志
settings.DEBUG = True

# 执行查询
from apps.problem.models import Problem
list(Problem.objects.all())

# 查看执行的SQL
for query in connection.queries:
    print(query['sql'])
    print(f"Time: {query['time']}s")
```

#### 4. 性能分析

```bash
# 安装django-debug-toolbar
pip install django-debug-toolbar

# 在settings.py中配置
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ['127.0.0.1', 'your-server-ip']
```

---

## 附录

### A. 完整的systemd服务文件清单

1. `/etc/systemd/system/zjoj.service` - Django应用
2. `/etc/systemd/system/zjoj-celery.service` - Celery Worker
3. `/etc/systemd/system/zjoj-celerybeat.service` - Celery Beat（可选）

### B. 防火墙配置

```bash
# Ubuntu (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### C. 安全加固建议

1. **禁用root SSH登录**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # 设置 PermitRootLogin no
   sudo systemctl restart sshd
   ```

2. **配置fail2ban**
   ```bash
   sudo apt install -y fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

3. **定期更新系统**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **使用强密码**
   - 数据库密码
   - Django SECRET_KEY
   - API密钥

5. **启用HTTPS**
   - 使用Let's Encrypt免费证书
   - 强制HTTP重定向到HTTPS

### D. 监控告警（可选）

使用以下工具实现监控告警：

- **Prometheus + Grafana** - 系统指标监控
- **Sentry** - 错误追踪
- **New Relic** - 应用性能监控
- **Datadog** - 全栈监控

---

<div align="center">

**Made with ❤️ by 铸剑团队**

[返回顶部](#zjoJ-铸剑---生产环境部署指南)

</div>
