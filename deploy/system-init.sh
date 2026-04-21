#!/bin/bash
# Ubuntu 系统初始化脚本
# 适用于全新安装的 Ubuntu 20.04/22.04/24.04

set -e

echo "========================================="
echo "  Ubuntu 系统初始化脚本"
echo "========================================="
echo ""

# 1. 更新系统
echo "[1/8] 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装基础工具
echo "[2/8] 安装基础工具..."
sudo apt install -y \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    net-tools \
    unzip \
    zip \
    build-essential \
    software-properties-common

# 3. 配置防火墙
echo "[3/8] 配置防火墙..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw --force enable

# 4. 配置时区
echo "[4/8] 配置时区..."
sudo timedatectl set-timezone Asia/Shanghai

# 5. 禁用 Swap（可选，Docker 推荐）
echo "[5/8] 优化系统配置..."
sudo swapoff -a || true
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# 6. 配置内核参数
cat << EOF | sudo tee /etc/sysctl.d/99-docker.conf > /dev/null
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF
sudo sysctl --system

# 7. 创建部署目录
echo "[6/8] 创建项目目录..."
mkdir -p ~/projects
cd ~/projects

# 8. 克隆项目
echo "[7/8] 克隆 ZJOJ 项目..."
if [ ! -d "ZJOJ-backend" ]; then
    git clone git@github.com:hhdhhy/ZJOJ-backend.git
fi
cd ZJOJ-backend

# 9. 配置 Git SSH（如果还没配置）
echo "[8/8] 检查 Git 配置..."
if ! git config user.name &>/dev/null; then
    echo "请配置 Git 用户信息："
    read -p "用户名: " git_name
    read -p "邮箱: " git_email
    git config --global user.name "$git_name"
    git config --global user.email "$git_email"
fi

# 生成 SSH Key（如果不存在）
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "生成 SSH Key..."
    ssh-keygen -t rsa -b 4096 -C "$git_email" -f ~/.ssh/id_rsa -N ""
    echo ""
    echo "⚠️  请将以下公钥添加到 GitHub："
    echo "========================================="
    cat ~/.ssh/id_rsa.pub
    echo "========================================="
    echo ""
    read -p "添加完成后按回车继续..."
fi

# 测试 GitHub 连接
echo "测试 GitHub 连接..."
ssh -T git@github.com || echo "⚠️  GitHub 连接测试失败，请检查 SSH Key"

echo ""
echo "========================================="
echo "  ✅ 系统初始化完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. cd ~/projects/ZJOJ-backend"
echo "2. chmod +x deploy/docker-deploy.sh"
echo "3. ./deploy/docker-deploy.sh"
echo ""
