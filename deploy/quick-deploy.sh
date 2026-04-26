#!/bin/bash
# 一键部署脚本 - 在服务器上执行

set -e

echo "========================================="
echo "  ZJOJ Docker 一键部署"
echo "========================================="

# 1. 更新系统
echo "[1/5] 更新系统..."
sudo apt update && sudo apt upgrade -y

# 2. 安装 Docker
echo "[2/5] 安装 Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "✅ Docker 安装完成"
else
    echo "✅ Docker 已安装"
fi

# 3. 克隆项目
echo "[3/5] 克隆项目..."
cd ~
if [ ! -d "projects/ZJOJ-backend" ]; then
    mkdir -p projects
    cd projects
    git clone git@github.com:hhdhhy/ZJOJ-backend.git
else
    echo "✅ 项目已存在"
fi

cd ~/projects/ZJOJ-backend

# 4. 运行部署脚本
echo "[4/5] 运行 Docker 部署..."
chmod +x deploy/docker-deploy.sh
./deploy/docker-deploy.sh

# 5. 创建管理员提示
echo ""
echo "[5/5] 创建管理员账户..."
echo "请执行以下命令创建管理员："
echo "docker compose exec web python manage.py createsuperuser"
echo ""
echo "========================================="
echo "  🎉 部署完成！"
echo "========================================="
echo "访问地址: http://$(curl -s ifconfig.me)"
