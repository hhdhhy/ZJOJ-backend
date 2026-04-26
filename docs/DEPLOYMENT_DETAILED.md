# 部署与运维详细文档

## 📋 概述

本文档详细描述 ZJOJ 系统的部署流程、运维管理、监控告警、故障排查等内容。

---

## 🏗️ 部署架构

### 生产环境架构图

```
                    ┌─────────────────┐
                    │   Internet      │
                    └────────┬────────┘
                             │ HTTPS (443)
                    ┌────────▼────────┐
                    │   Nginx         │
                    │   (Load Balancer)│
                    └───┬─────┬───────┘
                        │     │
              ┌─────────▼─┐ ┌─▼──────────┐
              │ Web Node 1│ │ Web Node 2 │
              │ (Django)  │ │ (Django)   │
              └────────┬──┘ └──┬─────────┘
                       │       │
              ┌────────▼───────▼────────┐
              │   Redis Cluster         │
              │   (Celery Broker)       │
              └────────┬────────────────┘
                       │
              ┌────────▼────────────────┐
              │   MySQL Master-Slave    │
              │   - Master (Write)      │
              │   - Slave (Read)        │
              └─────────────────────────┘
                       
              ┌─────────────────────────┐
              │   go-judge (Sandbox)    │
              │   - Node 1              │
              │   - Node 2              │
              └─────────────────────────┘
                       
              ┌─────────────────────────┐
              │   Celery Workers        │
              │   - Worker 1            │
              │   - Worker 2            │
              └─────────────────────────┘
```

### 单机部署架构 (开发/测试环境)

```
┌──────────────────────────────────────┐
│         Docker Host                  │
│                                      │
│  ┌──────────┐ ┌──────────┐          │
│  │  Nginx   │ │  MySQL   │          │
│  └──────────┘ └──────────┘          │
│                                      │
│  ┌──────────┐ ┌──────────┐          │
│  │  Django  │ │  Redis   │          │
│  │  Web     │ │          │          │
│  └──────────┘ └──────────┘          │
│                                      │
│  ┌──────────┐ ┌──────────┐          │
│  │  Celery  │ │ go-judge │          │
│  │  Worker  │ │          │          │
│  └──────────┘ └──────────┘          │
└──────────────────────────────────────┘
```

---

## 🚀 部署流程

### 1. 服务器准备

#### 系统要求

- **操作系统**: Ubuntu 20.04+ / CentOS 8+
- **CPU**: 4核+ (推荐 8核)
- **内存**: 8GB+ (推荐 16GB)
- **磁盘**: 50GB+ SSD
- **网络**: 公网 IP，开放端口 80, 443

#### 安装依赖

```bash
# Ubuntu
sudo apt update
sudo apt install -y docker.io docker-compose git curl

# CentOS
sudo yum install -y docker docker-compose git curl

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
```

### 2. 克隆项目

```bash
cd /opt
git clone https://github.com/your-repo/ZJOJ.git
cd ZJOJ
```

### 3. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件
vim .env
```

**.env 文件内容**:

```bash
# Django 配置
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=zjoj.com,www.zjoj.com

# 数据库配置
DB_ENGINE=mysql
DB_HOST=mysql
DB_PORT=3306
DB_NAME=zjoj_db
DB_USER=zjoj_user
DB_PASSWORD=your-db-password

# Redis 配置
REDIS_URL=redis://redis:6379/0

# DeepSeek API
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx

# JWT 配置
JWT_SECRET_KEY=your-jwt-secret
JWT_EXPIRE_HOURS=24

# go-judge 配置
GO_JUDGE_URL=http://gojudge:5050
```

### 4. 启动服务

```bash
# 构建镜像
docker compose build

# 启动所有服务
docker compose up -d

# 查看运行状态
docker compose ps
```

### 5. 初始化数据库

```bash
# 执行迁移
docker compose exec web python manage.py migrate

# 创建超级用户
docker compose exec web python manage.py createsuperuser

# 收集静态文件
docker compose exec web python manage.py collectstatic --noinput

# 加载初始数据 (可选)
docker compose exec web python manage.py loaddata initial_data.json
```

### 6. 配置 Nginx (反向代理)

**nginx.conf**:

```nginx
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name zjoj.com www.zjoj.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name zjoj.com www.zjoj.com;
    
    # SSL 证书
    ssl_certificate /etc/nginx/ssl/zjoj.com.crt;
    ssl_certificate_key /etc/nginx/ssl/zjoj.com.key;
    
    # 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 日志
    access_log /var/log/nginx/zjoj_access.log;
    error_log /var/log/nginx/zjoj_error.log;
    
    # 前端静态文件
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
    }
    
    # 媒体文件
    location /media/ {
        alias /app/media/;
        expires 30d;
    }
    
    # Django API
    location /api/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket (如果需要)
    location /ws/ {
        proxy_pass http://django;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 7. 配置 HTTPS (Let's Encrypt)

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d zjoj.com -d www.zjoj.com

# 自动续期
sudo crontab -e
# 添加: 0 0 1 * * certbot renew --quiet
```

---

## 📊 监控与告警

### 1. 服务健康检查

```bash
#!/bin/bash
# health_check.sh

SERVICES=("web" "celery" "gojudge" "mysql" "redis")

for service in "${SERVICES[@]}"; do
    if docker compose ps $service | grep -q "Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service is DOWN"
        # 发送告警通知
        curl -X POST https://hooks.slack.com/services/YOUR_WEBHOOK \
             -d '{"text":"🚨 '$service' is down!"}'
    fi
done
```

### 2. Prometheus + Grafana 监控

**docker-compose.yml 添加**:

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
```

**prometheus.yml**:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'django'
    static_configs:
      - targets: ['web:8000']
  
  - job_name: 'gojudge'
    static_configs:
      - targets: ['gojudge:5050']
```

### 3. 日志收集 (ELK Stack)

```yaml
services:
  elasticsearch:
    image: elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
  
  logstash:
    image: logstash:7.17.0
    volumes:
      - ./monitoring/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  
  kibana:
    image: kibana:7.17.0
    ports:
      - "5601:5601"
```

---

## 🔧 运维管理

### 1. 常用命令

```bash
# 查看所有容器状态
docker compose ps

# 查看服务日志
docker compose logs -f web
docker compose logs -f celery
docker compose logs -f gojudge

# 重启服务
docker compose restart web
docker compose restart celery

# 进入容器
docker compose exec web bash
docker compose exec mysql mysql -u root -p

# 查看资源使用
docker stats

# 清理未使用的资源
docker system prune -a
```

### 2. 备份策略

#### 数据库备份

```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_CONTAINER="zjoj-mysql"
DB_NAME="zjoj_db"
DB_USER="root"
DB_PASS="your-password"

mkdir -p $BACKUP_DIR

# 备份数据库
docker exec $DB_CONTAINER mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 保留最近 7 天
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Database backup completed: db_$DATE.sql.gz"
```

#### 定时备份

```bash
# crontab -e
# 每天凌晨 2 点备份
0 2 * * * /opt/ZJOJ/scripts/backup_db.sh >> /var/log/backup.log 2>&1
```

### 3. 更新部署

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker compose build

# 3. 停止旧服务
docker compose down

# 4. 启动新服务
docker compose up -d

# 5. 执行迁移
docker compose exec web python manage.py migrate

# 6. 重启 Celery Worker
docker compose restart celery
```

---

## 🐛 故障排查

### 1. Web 服务无法访问

**检查步骤**:

```bash
# 1. 检查容器是否运行
docker compose ps web

# 2. 查看日志
docker compose logs web | tail -50

# 3. 检查端口占用
netstat -tlnp | grep 8000

# 4. 测试内部连接
docker compose exec web curl http://localhost:8000/api/health/

# 5. 检查 Nginx 配置
nginx -t
systemctl status nginx
```

**常见原因**:
- 容器未启动
- 端口冲突
- 数据库连接失败
- 环境变量配置错误

### 2. Celery Worker 不处理任务

**检查步骤**:

```bash
# 1. 检查 Celery 状态
docker compose logs celery | tail -50

# 2. 检查 Redis 连接
docker compose exec redis redis-cli ping

# 3. 查看队列长度
docker compose exec redis redis-cli llen celery

# 4. 重启 Celery
docker compose restart celery
```

**常见原因**:
- Redis 连接失败
- 任务序列化错误
- Worker 进程崩溃

### 3. go-judge 评测失败

**检查步骤**:

```bash
# 1. 检查 go-judge 状态
docker compose ps gojudge

# 2. 查看日志
docker compose logs gojudge | tail -50

# 3. 测试 API
curl http://localhost:5050/version

# 4. 检查 cgroup 权限
docker exec gojudge ls -la /sys/fs/cgroup/memory/gojudge/
```

**常见原因**:
- cgroup 权限不足
- 编译器缺失
- 内存限制过小

### 4. 数据库连接失败

**检查步骤**:

```bash
# 1. 检查 MySQL 状态
docker compose ps mysql

# 2. 查看日志
docker compose logs mysql | tail -50

# 3. 测试连接
docker compose exec mysql mysql -u root -p

# 4. 检查磁盘空间
df -h
```

**常见原因**:
- 磁盘空间不足
- 最大连接数达到上限
- 密码错误

---

## 📈 性能优化

### 1. Django 优化

```python
# settings.py

# 启用缓存
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 数据库连接池
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'CONN_MAX_AGE': 600,  # 连接保持 10 分钟
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Gzip 压缩
MIDDLEWARE += [
    'django.middleware.gzip.GZipMiddleware',
]
```

### 2. MySQL 优化

```ini
# my.cnf

[mysqld]
# 连接数
max_connections = 500

# 缓存
innodb_buffer_pool_size = 4G
query_cache_size = 256M

# 日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
```

### 3. Redis 优化

```bash
# redis.conf

maxmemory 2gb
maxmemory-policy allkeys-lru

# 持久化
save 900 1
save 300 10
save 60 10000
```

---

## 🔒 安全加固

### 1. 防火墙配置

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# 禁止其他端口
sudo ufw default deny incoming
```

### 2. Fail2Ban 防护

```bash
# 安装
sudo apt install fail2ban

# 配置
cat > /etc/fail2ban/jail.local << EOF
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

sudo systemctl restart fail2ban
```

### 3. Docker 安全

```yaml
# docker-compose.yml
services:
  web:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /run
```

---

## 📝 维护清单

### 每日检查

- [ ] 检查服务运行状态
- [ ] 查看错误日志
- [ ] 监控系统资源 (CPU/内存/磁盘)
- [ ] 检查备份是否成功

### 每周检查

- [ ] 清理过期日志
- [ ] 检查数据库慢查询
- [ ] 更新安全补丁
- [ ] 审查访问日志

### 每月检查

- [ ] 完整数据备份测试
- [ ] 性能分析报告
- [ ] 安全漏洞扫描
- [ ] 容量规划评估

---

## 🔗 相关文档

- [Docker 部署详解](DOCKER_DEPLOYMENT.md)
- [快速开始](01-GETTING_STARTED.md)
- [系统架构](02-ARCHITECTURE.md)

---

**最后更新**: 2026-04-27
