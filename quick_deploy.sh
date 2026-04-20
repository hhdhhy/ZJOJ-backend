#!/bin/bash
# 快速部署脚本 - 从本地上传代码到服务器并执行部署

SERVER_IP="101.35.233.33"
SERVER_USER="ubuntu"
SERVER_PASS="Liu2004hd"
PROJECT_NAME="ZJOJ"

echo "========================================="
echo "  ZJOJ 快速部署到云服务器"
echo "========================================="
echo ""
echo "服务器: $SERVER_USER@$SERVER_IP"
echo ""

# 检查是否安装了sshpass
if ! command -v sshpass &> /dev/null; then
    echo "正在安装 sshpass..."
    sudo apt install -y sshpass 2>/dev/null || brew install sshpass 2>/dev/null || {
        echo "错误: 无法安装 sshpass"
        echo "请手动安装或使用SSH密钥认证"
        exit 1
    }
fi

# 步骤 1: 提交当前更改
echo "[1/4] 提交本地更改..."
git add -A
git commit -m "deploy: 准备部署到生产环境" || echo "没有新的更改"

# 步骤 2: 推送代码（如果有远程仓库）
echo "[2/4] 推送代码到Git仓库..."
git push origin main 2>/dev/null || echo_warn "跳过Git推送（可能未配置远程仓库）"

# 步骤 3: 上传代码到服务器
echo "[3/4] 上传代码到服务器..."
sshpass -p "$SERVER_PASS" scp -r ./* $SERVER_USER@$SERVER_IP:/home/ubuntu/$PROJECT_NAME/

# 步骤 4: 在服务器上执行部署
echo "[4/4] 在服务器上执行部署脚本..."
sshpass -p "$SERVER_PASS" ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
    cd /home/ubuntu/ZJOJ
    chmod +x deploy.sh
    bash deploy.sh
ENDSSH

echo ""
echo "========================================="
echo "✓ 部署完成！"
echo "========================================="
echo ""
echo "访问地址: http://$SERVER_IP"
echo ""
