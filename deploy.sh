#!/bin/bash
# ZJOJ 生产环境部署脚本 - Ubuntu

set -e

echo "========================================="
echo "  ZJOJ 生产环境部署"
echo "========================================="

# 配置变量
PROJECT_DIR="/home/ubuntu/ZJOJ"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_DIR="/var/log/zjoj"
STATIC_ROOT="$PROJECT_DIR/staticfiles"
MEDIA_ROOT="$PROJECT_DIR/media"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_step() {
    echo -e "${GREEN}[步骤 $1]${NC} $2"
}

echo_warn() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

# ==================== 步骤 1: 更新系统 ====================
echo_step "1" "更新系统包..."
sudo apt update
sudo apt upgrade -y

# ==================== 步骤 2: 安装依赖 ====================
echo_step "2" "安装系统依赖..."
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    mysql-server \
    nginx \
    git \
    supervisor

# ==================== 步骤 3: 配置MySQL ====================
echo_step "3" "配置MySQL数据库..."
sudo systemctl start mysql
sudo systemctl enable mysql

# 创建数据库和用户
sudo mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS zjoj_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'zjoj_user'@'localhost' IDENTIFIED BY 'ZjoJ@2026!Secure';
GRANT ALL PRIVILEGES ON zjoj_db.* TO 'zjoj_user'@'localhost';
FLUSH PRIVILEGES;
EOF

echo_warn "MySQL用户: zjoj_user"
echo_warn "MySQL密码: ZjoJ@2026!Secure"
echo_warn "请记得修改 settings.py 中的数据库配置！"

# ==================== 步骤 4: 克隆/更新代码 ====================
echo_step "4" "获取项目代码..."
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    git pull origin main
else
    cd /home/ubuntu
    git clone <YOUR_GIT_REPO_URL> ZJOJ
    cd "$PROJECT_DIR"
fi

# ==================== 步骤 5: 创建虚拟环境 ====================
echo_step "5" "创建Python虚拟环境..."
python3.10 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# ==================== 步骤 6: 配置Django ====================
echo_step "6" "配置Django..."

# 创建必要的目录
mkdir -p $LOG_DIR
mkdir -p $STATIC_ROOT
mkdir -p $MEDIA_ROOT

# 生成SECRET_KEY（如果不存在）
if ! grep -q "SECRET_KEY" "$PROJECT_DIR/ZJOJ/settings.py"; then
    echo_warn "需要在 settings.py 中配置 SECRET_KEY"
fi

# 收集静态文件
export DJANGO_SETTINGS_MODULE=ZJOJ.settings_production
python manage.py collectstatic --noinput

# 运行数据库迁移
python manage.py migrate

# 创建超级用户（如果需要）
echo_warn "如需创建超级用户，请运行: python manage.py createsuperuser"

# ==================== 步骤 7: 配置Gunicorn ====================
echo_step "7" "配置Gunicorn..."

cat > $PROJECT_DIR/gunicorn_config.py <<EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
timeout = 120
accesslog = "/var/log/zjoj/gunicorn_access.log"
errorlog = "/var/log/zjoj/gunicorn_error.log"
EOF

# ==================== 步骤 8: 配置Supervisor ====================
echo_step "8" "配置Supervisor进程管理..."

cat > /etc/supervisor/conf.d/zjoj.conf <<EOF
[program:zjoj]
command=/home/ubuntu/ZJOJ/.venv/bin/gunicorn -c /home/ubuntu/ZJOJ/gunicorn_config.py ZJOJ.wsgi:application
directory=/home/ubuntu/ZJOJ
user=ubuntu
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
environment=DJANGO_SETTINGS_MODULE="ZJOJ.settings_production"
stderr_logfile=/var/log/zjoj/supervisor_err.log
stdout_logfile=/var/log/zjoj/supervisor_out.log
EOF

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart zjoj

# ==================== 步骤 9: 配置Nginx ====================
echo_step "9" "配置Nginx反向代理..."

cat > /etc/nginx/sites-available/zjoj <<EOF
server {
    listen 80;
    server_name 101.35.233.33;

    # 日志
    access_log /var/log/nginx/zjoj_access.log;
    error_log /var/log/nginx/zjoj_error.log;

    # 最大上传文件大小
    client_max_body_size 10M;

    # 静态文件
    location /static/ {
        alias /home/ubuntu/ZJOJ/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 媒体文件
    location /media/ {
        alias /home/ubuntu/ZJOJ/media/;
        expires 30d;
    }

    # 代理到Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# 启用站点
sudo ln -sf /etc/nginx/sites-available/zjoj /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

# ==================== 步骤 10: 配置防火墙 ====================
echo_step "10" "配置防火墙..."
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw --force enable

# ==================== 完成 ====================
echo ""
echo "========================================="
echo -e "${GREEN}✓ 部署完成！${NC}"
echo "========================================="
echo ""
echo "访问地址: http://101.35.233.33"
echo ""
echo "管理命令:"
echo "  查看状态: sudo supervisorctl status zjoj"
echo "  重启服务: sudo supervisorctl restart zjoj"
echo "  查看日志: tail -f /var/log/zjoj/gunicorn_error.log"
echo "  Nginx日志: tail -f /var/log/nginx/zjoj_error.log"
echo ""
echo_warn "重要: 请检查并修改以下配置:"
echo_warn "  1. ZJOJ/settings.py - DATABASES配置"
echo_warn "  2. ZJOJ/settings.py - ALLOWED_HOSTS 添加 '101.35.233.33'"
echo_warn "  3. ZJOJ/settings.py - DEBUG = False"
echo_warn "  4. 创建超级用户: python manage.py createsuperuser"
echo ""
