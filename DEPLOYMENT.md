# ZJOJ 生产环境部署文档

## 📋 目录

- [系统要求](#系统要求)
- [服务器准备](#服务器准备)
- [快速部署](#快速部署)
- [评测系统配置](#评测系统配置)
- [详细配置说明](#详细配置说明)
- [服务管理](#服务管理)
- [故障排查](#故障排查)
- [安全加固](#安全加固)

---

## 系统要求

### 硬件要求
- **CPU**: 2核心及以上（推荐4核心）
- **内存**: 4GB及以上（推荐8GB）
- **磁盘**: 50GB可用空间
- **网络**: 公网IP地址

### 软件要求
- **操作系统**: Ubuntu 20.04/22.04 LTS
- **Python**: 3.10+
- **MySQL**: 8.0+
- **Nginx**: 1.18+
- **Supervisor**: 4.2+

---

## 服务器准备

### 1. 安装系统依赖

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y python3 python3-pip python3-venv \
    mysql-server nginx supervisor git curl wget \
    pkg-config libmysqlclient-dev build-essential
```

### 2. 配置 MySQL 数据库

```bash
# 启动 MySQL 并设置开机自启
sudo systemctl start mysql
sudo systemctl enable mysql

# 初始化 MySQL 安全配置
sudo mysql_secure_installation

# 登录 MySQL 创建数据库和用户
sudo mysql -u root -p
```

在 MySQL 中执行：

```sql
-- 创建数据库
CREATE DATABASE zjoj_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建专用用户
CREATE USER 'zjoj_user'@'localhost' IDENTIFIED BY 'ZjoJ@2026!Secure';

-- 授权
GRANT ALL PRIVILEGES ON zjoj_db.* TO 'zjoj_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. 创建必要的目录

```bash
# 创建日志目录
sudo mkdir -p /var/log/zjoj
sudo chown ubuntu:ubuntu /var/log/zjoj

# 创建运行时目录
sudo mkdir -p /var/run/zjoj
sudo chown ubuntu:ubuntu /var/run/zjoj

# 创建数据目录（可选，用于存储AI模型等）
sudo mkdir -p /home/ubuntu/ai_models/cache
sudo mkdir -p /home/ubuntu/ai_data/chroma_db
```

---

## 快速部署

### 方法一：使用 GitHub（推荐）

#### 1. 配置 SSH Key

```bash
# 生成 SSH Key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 查看公钥并添加到 GitHub
cat ~/.ssh/id_ed25519.pub

# 测试连接
ssh -T git@github.com
```

#### 2. 克隆代码

```bash
cd /home/ubuntu
git clone git@github.com:hhdhhy/ZJOJ-backend.git ZJOJ
cd ZJOJ

# 切换到目标分支
git checkout feature/ai-assistant-step1
```

#### 3. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

**注意**：如果遇到依赖冲突，可能需要手动调整版本：

```bash
# 降级 numpy（兼容 chromadb）
pip install 'numpy<2.0'

# 升级 sentence-transformers
pip install sentence-transformers==2.7.0

# 确保 mysqlclient 版本正确
pip install mysqlclient==2.2.4
```

#### 4. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑配置文件
nano .env
```

关键配置项：

```env
# Django 配置
DJANGO_SETTINGS_MODULE=ZJOJ.settings_production
SECRET_KEY=your-secret-key-here

# 数据库配置
DB_NAME=zjoj_db
DB_USER=zjoj_user
DB_PASSWORD=ZjoJ@2026!Secure
DB_HOST=localhost
DB_PORT=3306

# AI 服务配置（如需要）
OPENAI_API_KEY=your-openai-key
MODELSCOPE_TOKEN=your-modelscope-token
```

#### 5. 数据库迁移

```bash
# 执行数据库迁移
DJANGO_SETTINGS_MODULE=ZJOJ.settings_production python manage.py migrate

# 收集静态文件
DJANGO_SETTINGS_MODULE=ZJOJ.settings_production python manage.py collectstatic --noinput

# 创建超级用户（可选）
DJANGO_SETTINGS_MODULE=ZJOJ.settings_production python manage.py createsuperuser
```

#### 6. 配置 Gunicorn

创建 `gunicorn_config.py`：

```python
import multiprocessing

bind = '127.0.0.1:8000'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5
proc_name = 'zjoj'
pidfile = '/var/run/zjoj/gunicorn.pid'
accesslog = '/var/log/zjoj/gunicorn_access.log'
errorlog = '/var/log/zjoj/gunicorn_error.log'
loglevel = 'info'
preload_app = True
max_requests = 1000
max_requests_jitter = 50
```

#### 7. 配置 Supervisor

创建 `/etc/supervisor/conf.d/zjoj.conf`：

```ini
[program:zjoj]
command=/home/ubuntu/ZJOJ/.venv/bin/gunicorn -c /home/ubuntu/ZJOJ/gunicorn_config.py ZJOJ.wsgi:application
directory=/home/ubuntu/ZJOJ
environment=DJANGO_SETTINGS_MODULE="ZJOJ.settings_production"
user=ubuntu
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stdout_logfile=/var/log/zjoj/supervisor_stdout.log
stderr_logfile=/var/log/zjoj/supervisor_stderr.log
```

重新加载 Supervisor：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start zjoj
```

#### 8. 配置 Nginx

创建 `/etc/nginx/sites-available/zjoj`：

```nginx
server {
    listen 80;
    server_name 101.35.233.33;  # 替换为你的域名或IP

    # 静态文件
    location /static/ {
        alias /home/ubuntu/ZJOJ/staticfiles/;
        expires 30d;
    }

    # 媒体文件
    location /media/ {
        alias /home/ubuntu/ZJOJ/media/;
        expires 30d;
    }

    # 反向代理到 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # 超时设置
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

启用配置：

```bash
# 创建符号链接
sudo ln -sf /etc/nginx/sites-available/zjoj /etc/nginx/sites-enabled/zjoj

# 删除默认配置
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

---

## 评测系统配置

ZJOJ 使用 HydroJudge 作为代码评测引擎。以下是两种配置方案：

### 方案一：使用 Docker 部署（推荐）

这是最简单的方式，适合生产环境。

#### 1. 安装 Docker

```bash
# 安装 Docker
sudo apt update
sudo apt install -y docker.io docker-compose

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 将 ubuntu 用户加入 docker 组
sudo usermod -aG docker ubuntu
```

#### 2. 运行 go-judge 沙箱

```bash
# 拉取镜像并运行
docker run -d \
  --name go-judge \
  --privileged \
  -p 5050:5050 \
  --restart=always \
  criyle/go-judge:latest

# 检查是否运行成功
docker ps | grep go-judge
```

#### 3. 验证服务

```bash
# 测试 API
curl http://localhost:5050/run \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": [
      {
        "args": ["echo", "Hello World"]
      }
    ]
  }'
```

应该返回类似：
```json
{"run":[{"status":"Accepted","exitStatus":0,"time":0.001,"memory":1024}]}
```

### 方案二：手动编译安装

适合需要自定义配置的环境。

#### 1. 下载 go-judge

```bash
# 下载最新版本
cd /tmp
wget https://github.com/criyle/go-judge/releases/latest/download/go-judge-init_linux_amd64
chmod +x go-judge-init_linux_amd64
sudo mv go-judge-init_linux_amd64 /usr/local/bin/go-judge
```

#### 2. 创建配置文件

```bash
# 创建配置目录
sudo mkdir -p /etc/go-judge
sudo mkdir -p /var/lib/go-judge

# 创建配置文件
cat > /etc/go-judge/config.yaml << 'EOF'
# go-judge 配置
http_addr: "0.0.0.0:5050"
tmp_dir: "/tmp/go-judge"
cgroup_parent: "go-judge"
enable_cgroup: true
enable_seccomp: true
max_process_count: 64
max_memory_limit: 1073741824  # 1GB
max_time_limit: 60000  # 60s
EOF
```

#### 3. 配置 Supervisor 管理

创建 `/etc/supervisor/conf.d/go-judge.conf`：

```ini
[program:go-judge]
command=/usr/local/bin/go-judge --config /etc/go-judge/config.yaml
directory=/var/lib/go-judge
user=root
autostart=true
autorestart=true
stdout_logfile=/var/log/go-judge.log
stderr_logfile=/var/log/go-judge-error.log
```

启动服务：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start go-judge
```

### 配置 Django 连接评测服务

在 `ZJOJ/settings_production.py` 中确认配置：

```python
# HydroJudge 配置
HYDRO_JUDGE_URL = 'http://localhost:5050'  # go-judge 服务地址
HYDRO_JUDGE_TIMEOUT = 30  # 超时时间（秒）
```

### 测试评测功能

#### 1. 创建测试题目

登录 Django Admin (`http://your-server/admin/`)，创建一个测试题目：

- 题目ID: TEST001
- 标题: A+B Problem
- 时间限制: 1000ms
- 内存限制: 256MB

#### 2. 上传测试数据

创建测试数据 ZIP 文件 (`testcases.zip`)：

```
testdata/
  ├── 1.in    # 输入: 1 2
  ├── 1.out   # 输出: 3
  ├── 2.in    # 输入: 100 200
  └── 2.out   # 输出: 300
```

通过 Django Admin 上传到题目。

#### 3. 提交代码测试

```bash
# 使用 curl 测试
curl -X POST http://localhost/api/submissions/submit/ \
  -H "Authorization: jwt YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_id": "TEST001",
    "language": "cpp",
    "code": "#include <iostream>\nusing namespace std;\nint main() { int a, b; cin >> a >> b; cout << a + b << endl; return 0; }"
  }'
```

#### 4. 查看评测结果

```bash
# 获取提交详情
curl http://localhost/api/submissions/SUBMISSION_ID/ \
  -H "Authorization: jwt YOUR_TOKEN"
```

### 常见问题

#### 1. go-judge 无法启动

```bash
# 检查日志
sudo tail -f /var/log/go-judge-error.log

# 检查端口占用
sudo lsof -i :5050

# 重启服务
sudo supervisorctl restart go-judge
```

#### 2. 评测超时

- 检查题目时间限制是否合理
- 检查服务器负载
- 查看 go-judge 日志

#### 3. 权限问题

go-judge 需要 root 权限来创建 cgroup 和命名空间：

```bash
# 确保以 root 运行
sudo supervisorctl status go-judge
```

### 性能优化

#### 1. 调整并发数

在 go-judge 配置中调整：

```yaml
# 根据 CPU 核心数调整
max_concurrent_runs: 4  # 默认值
```

#### 2. 资源限制

```yaml
# 限制单个评测的最大资源
max_memory_limit: 2147483648  # 2GB
max_time_limit: 120000  # 120s
max_process_count: 128
```

#### 3. 缓存优化

Django 会自动缓存热门题目的测试数据，无需额外配置。

---

## 详细配置说明

### 生产环境配置文件

`ZJOJ/settings_production.py` 关键配置：

```python
import os

# 安全设置
DEBUG = False
ALLOWED_HOSTS = ['101.35.233.33', 'localhost', '127.0.0.1']

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zjoj_db',
        'USER': 'zjoj_user',
        'PASSWORD': 'ZjoJ@2026!Secure',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# 静态文件
STATIC_ROOT = '/home/ubuntu/ZJOJ/staticfiles'
MEDIA_ROOT = '/home/ubuntu/ZJOJ/media'

# AI 模型缓存路径
EMBEDDING_CACHE_DIR = '/home/ubuntu/ai_models/cache'
CHROMA_DB_PATH = '/home/ubuntu/ai_data/chroma_db'

# 日志配置
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

### Gunicorn 性能调优

根据服务器配置调整 `gunicorn_config.py`：

```python
# CPU密集型任务
workers = multiprocessing.cpu_count() * 2 + 1

# IO密集型任务
workers = multiprocessing.cpu_count() * 4 + 1

# 单个工作进程的最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50  # 随机抖动，避免所有进程同时重启
```

### Nginx 优化配置

在 `/etc/nginx/nginx.conf` 的 `http` 块中添加：

```nginx
http {
    # 上传文件大小限制
    client_max_body_size 100M;
    
    # 启用 gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 1000;
    
    # 连接优化
    keepalive_timeout 65;
    worker_connections 1024;
}
```

---

## 服务管理

### Supervisor 常用命令

```bash
# 查看所有服务状态
sudo supervisorctl status

# 启动服务
sudo supervisorctl start zjoj

# 停止服务
sudo supervisorctl stop zjoj

# 重启服务
sudo supervisorctl restart zjoj

# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 查看实时日志
sudo tail -f /var/log/zjoj/supervisor_stdout.log
sudo tail -f /var/log/zjoj/supervisor_stderr.log
```

### Nginx 常用命令

```bash
# 检查配置
sudo nginx -t

# 重新加载配置（不中断服务）
sudo systemctl reload nginx

# 重启 Nginx
sudo systemctl restart nginx

# 查看状态
sudo systemctl status nginx

# 查看访问日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Gunicorn 监控

```bash
# 查看 Gunicorn 进程
ps aux | grep gunicorn

# 查看工作进程数量
ps aux | grep gunicorn | grep -v grep | wc -l

# 查看监听端口
sudo netstat -tlnp | grep 8000

# 查看错误日志
tail -f /var/log/zjoj/gunicorn_error.log

# 查看访问日志
tail -f /var/log/zjoj/gunicorn_access.log
```

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

```bash
# 检查 Supervisor 日志
sudo tail -50 /var/log/zjoj/supervisor_stderr.log

# 检查 Gunicorn 日志
sudo tail -50 /var/log/zjoj/gunicorn_error.log

# 检查 Django 日志
sudo tail -50 /var/log/zjoj/django.log
```

#### 2. 数据库连接失败

```bash
# 测试数据库连接
mysql -u zjoj_user -p zjoj_db

# 检查 MySQL 状态
sudo systemctl status mysql

# 查看 MySQL 错误日志
sudo tail -50 /var/log/mysql/error.log
```

#### 3. 权限问题

```bash
# 修复文件所有权
sudo chown -R ubuntu:ubuntu /home/ubuntu/ZJOJ
sudo chown -R ubuntu:ubuntu /var/log/zjoj
sudo chown -R ubuntu:ubuntu /var/run/zjoj

# 修复文件权限
chmod 755 /home/ubuntu/ZJOJ
chmod 644 /home/ubuntu/ZJOJ/gunicorn_config.py
```

#### 4. 端口被占用

```bash
# 查看端口占用
sudo lsof -i :8000
sudo lsof -i :80

# 杀死占用进程
sudo kill -9 <PID>
```

#### 5. 静态文件 404

```bash
# 重新收集静态文件
cd /home/ubuntu/ZJOJ
source .venv/bin/activate
DJANGO_SETTINGS_MODULE=ZJOJ.settings_production python manage.py collectstatic --noinput

# 检查 Nginx 配置
sudo nginx -t
sudo systemctl reload nginx
```

### 性能问题排查

```bash
# 查看系统负载
top
htop

# 查看内存使用
free -h

# 查看磁盘使用
df -h

# 查看网络连接
sudo netstat -an | grep ESTABLISHED | wc -l

# 查看慢查询
sudo tail -100 /var/log/zjoj/gunicorn_access.log | awk '{print $NF}' | sort | uniq -c | sort -rn
```

---

## 安全加固

### 1. 防火墙配置

```bash
# 启用 UFW 防火墙
sudo ufw enable

# 允许 SSH
sudo ufw allow 22/tcp

# 允许 HTTP
sudo ufw allow 80/tcp

# 允许 HTTPS（如果配置了SSL）
sudo ufw allow 443/tcp

# 查看状态
sudo ufw status
```

### 2. 配置 SSL/TLS（推荐）

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

### 3. 数据库安全

```sql
-- 限制数据库用户只能本地访问
DROP USER 'zjoj_user'@'%';
CREATE USER 'zjoj_user'@'localhost' IDENTIFIED BY 'strong-password';

-- 最小化权限
GRANT SELECT, INSERT, UPDATE, DELETE ON zjoj_db.* TO 'zjoj_user'@'localhost';
```

### 4. Django 安全设置

在 `settings_production.py` 中：

```python
# 强制 HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# XSS 保护
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# 点击劫持保护
X_FRAME_OPTIONS = 'DENY'
```

### 5. 定期备份

创建备份脚本 `/home/ubuntu/backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u zjoj_user -p'ZjoJ@2026!Secure' zjoj_db > $BACKUP_DIR/db_$DATE.sql

# 备份媒体文件
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/ubuntu/ZJOJ/media/

# 保留最近7天的备份
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

设置定时任务：

```bash
# 编辑 crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /home/ubuntu/backup.sh >> /var/log/zjoj/backup.log 2>&1
```

---

## 监控与告警

### 1. 系统监控

安装监控工具：

```bash
# 安装 htop
sudo apt install htop

# 安装 net-tools
sudo apt install net-tools

# 安装 logrotate（日志轮转）
sudo apt install logrotate
```

### 2. 日志轮转配置

创建 `/etc/logrotate.d/zjoj`：

```
/var/log/zjoj/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0644 ubuntu ubuntu
    postrotate
        sudo supervisorctl restart zjoj > /dev/null 2>&1 || true
    endscript
}
```

### 3. 健康检查脚本

创建 `/home/ubuntu/health_check.sh`：

```bash
#!/bin/bash

# 检查 Gunicorn
if ! sudo supervisorctl status zjoj | grep -q "RUNNING"; then
    echo "ERROR: Gunicorn is not running"
    sudo supervisorctl restart zjoj
    exit 1
fi

# 检查 Nginx
if ! sudo systemctl is-active --quiet nginx; then
    echo "ERROR: Nginx is not running"
    sudo systemctl restart nginx
    exit 1
fi

# 检查 API 响应
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/problems/)
if [ "$HTTP_CODE" != "401" ] && [ "$HTTP_CODE" != "200" ]; then
    echo "ERROR: API returned HTTP $HTTP_CODE"
    exit 1
fi

echo "Health check passed"
exit 0
```

设置定时检查：

```bash
# 每5分钟检查一次
*/5 * * * * /home/ubuntu/health_check.sh >> /var/log/zjoj/health_check.log 2>&1
```

---

## 更新与维护

### 代码更新流程

```bash
# 1. 进入项目目录
cd /home/ubuntu/ZJOJ

# 2. 拉取最新代码
git pull origin feature/ai-assistant-step1

# 3. 激活虚拟环境
source .venv/bin/activate

# 4. 安装新依赖（如果有）
pip install -r requirements.txt

# 5. 执行数据库迁移
DJANGO_SETTINGS_MODULE=ZJOJ.settings_production python manage.py migrate

# 6. 收集静态文件
DJANGO_SETTINGS_MODULE=ZJOJ.settings_production python manage.py collectstatic --noinput

# 7. 重启服务
sudo supervisorctl restart zjoj
```

### 依赖更新

```bash
# 查看过时的包
pip list --outdated

# 更新特定包
pip install package_name --upgrade

# 更新所有包（谨慎操作）
pip install --upgrade -r requirements.txt
```

---

## 附录

### A. 有用的命令速查

```bash
# 服务管理
sudo supervisorctl status          # 查看服务状态
sudo supervisorctl restart zjoj    # 重启服务
sudo systemctl restart nginx       # 重启 Nginx

# 日志查看
tail -f /var/log/zjoj/gunicorn_error.log   # Gunicorn 错误日志
tail -f /var/log/zjoj/django.log           # Django 日志
tail -f /var/log/nginx/access.log          # Nginx 访问日志

# 数据库
mysql -u zjoj_user -p zjoj_db      # 登录数据库
mysqldump -u zjoj_user -p zjoj_db > backup.sql  # 备份数据库

# 性能监控
top                                # 系统资源监控
htop                               # 增强版 top
df -h                              # 磁盘使用
free -h                            # 内存使用
```

### B. 文件结构

```
/home/ubuntu/ZJOJ/
├── .venv/                      # Python 虚拟环境
├── apps/                       # Django 应用
├── ZJOJ/                       # 项目配置
│   ├── settings.py
│   ├── settings_production.py  # 生产环境配置
│   ├── urls.py
│   └── wsgi.py
├── staticfiles/                # 收集的静态文件
├── media/                      # 用户上传文件
├── gunicorn_config.py          # Gunicorn 配置
├── manage.py                   # Django 管理脚本
└── requirements.txt            # Python 依赖

/var/log/zjoj/
├── django.log                  # Django 日志
├── gunicorn_access.log         # Gunicorn 访问日志
├── gunicorn_error.log          # Gunicorn 错误日志
├── supervisor_stdout.log       # Supervisor 标准输出
└── supervisor_stderr.log       # Supervisor 错误输出
```

### C. 联系方式与支持

- **GitHub**: https://github.com/hhdhhy/ZJOJ-backend
- **问题反馈**: 提交 Issue 到 GitHub
- **文档更新**: 欢迎提交 PR 改进文档

---

**最后更新时间**: 2026-04-21  
**部署版本**: feature/ai-assistant-step1  
**服务器**: 101.35.233.33 (Ubuntu)
