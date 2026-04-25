#!/bin/bash
# go-judge 安装脚本 - Ubuntu/Debian

set -e

echo "========================================="
echo "  安装 go-judge 评测沙箱"
echo "========================================="

# 1. 检查系统要求
echo ""
echo "[1/5] 检查系统环境..."
if [ "$(uname)" != "Linux" ]; then
    echo "❌ 错误: go-judge 只能在 Linux 系统上运行"
    exit 1
fi

# 2. 安装依赖
echo ""
echo "[2/5] 安装系统依赖..."
apt-get update
apt-get install -y \
    curl \
    wget \
    build-essential \
    golang-go \
    nodejs \
    npm \
    libseccomp-dev \
    pkg-config

# 3. 下载并安装 go-judge
echo ""
echo "[3/5] 安装 go-judge..."

# 方法1: 使用 Hydro OJ 官方脚本（推荐）
echo "使用 Hydro OJ 官方安装脚本..."
curl -sSL https://hydro.ac/setup.sh | bash -s -- --judge --no-caddy

# 4. 配置 go-judge
echo ""
echo "[4/5] 配置 go-judge..."

# 创建 systemd 服务文件（如果不存在）
if [ ! -f /etc/systemd/system/go-judge.service ]; then
    cat > /etc/systemd/system/go-judge.service << 'EOF'
[Unit]
Description=go-judge Code Execution Sandbox
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/hydro/judge
ExecStart=/usr/bin/env node dist/index.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
fi

# 5. 启动服务
echo ""
echo "[5/5] 启动 go-judge 服务..."
systemctl enable go-judge
systemctl restart go-judge

# 等待服务启动
sleep 3

# 验证服务
echo ""
echo "验证服务状态..."
if systemctl is-active --quiet go-judge; then
    echo "✅ go-judge 服务运行正常"
    
    # 测试 API
    echo ""
    echo "测试 API 连接..."
    RESPONSE=$(curl -s http://localhost:5050/run -X POST \
        -H 'Content-Type: application/json' \
        -d '{"cmd":[{"args":["/bin/echo","Hello World"]}]}' 2>&1)
    
    if echo "$RESPONSE" | grep -q "stdout"; then
        echo "✅ API 测试成功"
        echo "响应: $RESPONSE"
    else
        echo "⚠️  API 测试失败: $RESPONSE"
    fi
else
    echo "❌ go-judge 服务启动失败"
    echo "查看日志: journalctl -u go-judge -n 50"
    exit 1
fi

echo ""
echo "========================================="
echo "  ✅ 安装完成！"
echo "========================================="
echo ""
echo "服务信息:"
echo "  - 地址: http://localhost:5050"
echo "  - 状态: $(systemctl is-active go-judge)"
echo ""
echo "常用命令:"
echo "  查看状态: systemctl status go-judge"
echo "  查看日志: journalctl -u go-judge -f"
echo "  重启服务: systemctl restart go-judge"
echo ""
