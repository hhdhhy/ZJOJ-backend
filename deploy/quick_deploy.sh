#!/bin/bash
# ZJOJ 快速部署脚本（Ubuntu 20.04+）
# 用法: sudo ./quick_deploy.sh

set -e

echo "🚀 开始部署 ZJOJ..."
echo "================================"

# 检查是否以root运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用sudo运行此脚本"
    exit 1
fi

# 配置变量
PROJECT_DIR="/opt/zjoj"
DATA_DIR="/opt/zjoj_data"
DB_NAME="zjoj"
DB_USER="zjoj"
DB_PASS=""

# 生成随机密码
generate_password() {
    openssl rand -base64 32 | tr -dc 'a-zA-Z0-9!@#$%^&*' | head -c 20
}

echo ""
echo "📋 请提供以下信息："
echo ""
read -p "数据库密码 (留空自动生成): " DB_PASS
if [ -z "$DB_PASS" ]; then
    DB_PASS=$(generate_password)
    echo "✅ 已生成随机密码: $DB_PASS"
fi

read -p "域名 (如 example.com，留空使用localhost): " DOMAIN
if [ -z "$DOMAIN" ]; then
    DOMAIN="localhost"
fi

echo ""
echo "🔧 开始安装..."

# 1. 更新系统
echo ""
echo "📦 步骤 1/10: 更新系统..."
apt update && apt upgrade -y

# 2. 安装依赖
echo ""
echo "📦 步骤 2/10: 安装系统依赖..."
apt install -y python3.10 python3.10-venv python3-pip mysql-server nginx git curl wget vim build-essential

# 3. 启动服务
echo ""
echo "🚀 步骤 3/10: 启动基础服务..."
systemctl start mysql
systemctl enable mysql
systemctl start nginx
systemctl enable nginx

# 4. 克隆项目
echo ""
echo "📥 步骤 4/10: 克隆项目..."
if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  项目目录已存在，跳过克隆"
else
    git clone https://github.com/hhdhhy/ZJOJ-backend.git $PROJECT_DIR
fi

cd $PROJECT_DIR

# 5. 创建虚拟环境
echo ""
echo "🐍 步骤 5/10: 创建Python虚拟环境..."
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# 6. 安装Python依赖
echo ""
echo "📦 步骤 6/10: 安装Python依赖..."
pip install -r requirements.txt

# 7. 配置数据库
echo ""
echo "🗄️  步骤 7/10: 配置MySQL数据库..."
mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

# 8. 创建配置文件
echo ""
echo "⚙️  步骤 8/10: 创建配置文件..."

# 生成SECRET_KEY
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# 创建.env文件
cat > .env <<EOF
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$DOMAIN,localhost,127.0.0.1
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASS
DATABASE_HOST=localhost
DATABASE_PORT=3306
CORS_ALLOWED_ORIGINS=https://$DOMAIN
CELERY_BROKER_URL=sqla+sqlite:///$PROJECT_DIR/celerybroker.db
CELERY_RESULT_BACKEND=db+sqlite:///$PROJECT_DIR/celeryresults.db
HYDRO_JUDGE_URL=http://localhost:5050
HYDRO_JUDGE_TIMEOUT=30
EMBEDDING_CACHE_DIR=$DATA_DIR/ai_models
CHROMA_DB_PATH=$DATA_DIR/chroma_db
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
STATIC_ROOT=$DATA_DIR/static
MEDIA_ROOT=$DATA_DIR/media
EOF

echo "✅ .env 文件已创建"

# 9. 初始化应用
echo ""
echo "🔧 步骤 9/10: 初始化Django应用..."

# 创建数据目录
mkdir -p $DATA_DIR/{ai_models,chroma_db,static,media,logs,backups}
chown -R www-data:www-data $DATA_DIR

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

echo ""
echo "👤 创建超级用户..."
python manage.py createsuperuser

# 10. 配置systemd服务
echo ""
echo "🔧 步骤 10/10: 配置系统服务..."

# 复制服务文件
cp deploy/zjoj.service /etc/systemd/system/
cp deploy/zjoj-celery.service /etc/systemd/system/

# 重载systemd
systemctl daemon-reload

# 启动服务
systemctl start zjoj
systemctl start zjoj-celery
systemctl enable zjoj
systemctl enable zjoj-celery

# 完成
echo ""
echo "================================"
echo "✅ 部署完成！"
echo "================================"
echo ""
echo "📊 服务状态:"
systemctl status zjoj --no-pager -l
echo ""
systemctl status zjoj-celery --no-pager -l
echo ""
echo "🌐 访问地址:"
echo "   http://$DOMAIN"
echo "   http://$DOMAIN/admin"
echo ""
echo "📝 重要信息:"
echo "   数据库密码: $DB_PASS"
echo "   项目目录: $PROJECT_DIR"
echo "   数据目录: $DATA_DIR"
echo ""
echo "💡 常用命令:"
echo "   查看日志: journalctl -u zjoj -f"
echo "   重启服务: systemctl restart zjoj"
echo "   备份数据库: $PROJECT_DIR/deploy/backup_db.sh"
echo ""
echo "⚠️  请妥善保管数据库密码和.env文件！"
echo ""
