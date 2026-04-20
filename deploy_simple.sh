#!/bin/bash
# 简化版部署脚本 - 不依赖Git

set -e

echo "========================================="
echo "  ZJOJ 生产环境部署（简化版）"
echo "========================================="

PROJECT_DIR="/home/ubuntu/ZJOJ"
VENV_DIR="$PROJECT_DIR/.venv"

GREEN='\033[0;32m'
NC='\033[0m'

echo_step() {
    echo -e "${GREEN}[步骤 $1]${NC} $2"
}

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo "错误: 项目目录不存在"
    exit 1
fi

cd "$PROJECT_DIR"

# 步骤 1: 安装系统依赖
echo_step "1" "安装系统依赖..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip mysql-server nginx supervisor

# 步骤 2: 配置MySQL
echo_step "2" "配置MySQL..."
sudo systemctl start mysql
sudo systemctl enable mysql

sudo mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS zjoj_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'zjoj_user'@'localhost' IDENTIFIED BY 'ZjoJ@2026!Secure';
GRANT ALL PRIVILEGES ON zjoj_db.* TO 'zjoj_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# 步骤 3: 创建虚拟环境
echo_step "3" "创建Python虚拟环境..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 步骤 4: 配置Django
echo_step "4" "配置Django..."
mkdir -p /var/log/zjoj
mkdir -p staticfiles
mkdir -p media

export DJANGO_SETTINGS_MODULE=ZJOJ.settings_production
python manage.py collectstatic --noinput
python manage.py migrate

# 步骤 5: 配置Gunicorn
echo_step "5" "配置Gunicorn..."
cat > gunicorn_config.py <<EOF
bind = "127.0.0.1:8000"
workers = 3
timeout = 120
accesslog = "/var/log/zjoj/gunicorn_access.log"
errorlog = "/var/log/zjoj/gunicorn_error.log"
EOF

# 步骤 6: 配置Supervisor
echo_step "6" "配置Supervisor..."
cat > /etc/supervisor/conf.d/zjoj.conf <<EOF
[program:zjoj]
command=/home/ubuntu/ZJOJ/.venv/bin/gunicorn -c /home/ubuntu/ZJOJ/gunicorn_config.py ZJOJ.wsgi:application
directory=/home/ubuntu/ZJOJ
user=ubuntu
autostart=true
autorestart=true
environment=DJANGO_SETTINGS_MODULE="ZJOJ.settings_production"
stderr_logfile=/var/log/zjoj/supervisor_err.log
stdout_logfile=/var/log/zjoj/supervisor_out.log
EOF

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart zjoj

# 步骤 7: 配置Nginx
echo_step "7" "配置Nginx..."
cat > /etc/nginx/sites-available/zjoj <<EOF
server {
    listen 80;
    server_name 101.35.233.33;

    access_log /var/log/nginx/zjoj_access.log;
    error_log /var/log/nginx/zjoj_error.log;

    client_max_body_size 10M;

    location /static/ {
        alias /home/ubuntu/ZJOJ/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /home/ubuntu/ZJOJ/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/zjoj /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# 步骤 8: 配置防火墙
echo_step "8" "配置防火墙..."
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw --force enable

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
echo ""
