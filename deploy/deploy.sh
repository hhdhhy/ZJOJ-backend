#!/bin/bash
# deploy.sh - ZJOJ 自动化部署脚本

set -e

echo "🚀 开始部署 ZJOJ..."

# 1. 拉取最新代码（强制重置）
echo "📥 拉取最新代码..."
cd /home/ubuntu/ZJOJ
git fetch origin
git reset --hard origin/feature/ai-assistant-step1

# 2. 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 3. 安装依赖
echo "📦 安装依赖..."
pip install --upgrade pip
pip install django djangorestframework gunicorn mysqlclient requests django-shortuuidfield pyjwt django-cors-headers python-dotenv

# 4. 数据库迁移
echo "🗄️  执行数据库迁移..."
python manage.py migrate

# 5. 收集静态文件
echo "📁 收集静态文件..."
python manage.py collectstatic --noinput

# 6. 重启服务
echo "🔄 重启服务..."
sudo systemctl restart zjoj

# 7. 检查服务状态
echo "✅ 检查服务状态..."
sleep 2
sudo systemctl status zjoj --no-pager -l | head -10

echo ""
echo "🎉 部署完成！"
echo "📍 访问地址: http://101.35.233.33"
echo "🔐 Admin: http://101.35.233.33/admin"
