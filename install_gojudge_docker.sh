#!/bin/bash
# go-judge Docker 安装脚本（推荐）

set -e

echo "========================================="
echo "  使用 Docker 安装 go-judge"
echo "========================================="

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装"
    exit 1
fi

echo ""
echo "[1/3] 拉取 go-judge 镜像..."
docker pull hydrooj/gojudge:latest

echo ""
echo "[2/3] 启动 go-judge 容器..."

# 停止旧容器（如果存在）
docker stop zjoj-gojudge 2>/dev/null || true
docker rm zjoj-gojudge 2>/dev/null || true

# 启动新容器
docker run -d \
  --name zjoj-gojudge \
  --restart always \
  --privileged \
  --network host \
  -v /tmp:/w \
  hydrooj/gojudge:latest

echo ""
echo "[3/3] 验证服务..."
sleep 3

# 测试 API
RESPONSE=$(curl -s http://localhost:5050/run -X POST \
  -H 'Content-Type: application/json' \
  -d '{"cmd":[{"args":["/bin/echo","Hello World"]}]}' 2>&1)

if echo "$RESPONSE" | grep -q "stdout"; then
    echo "✅ go-judge 启动成功！"
    echo ""
    echo "响应示例: $RESPONSE"
else
    echo "⚠️  服务可能还在启动中，请稍后测试"
    echo "查看日志: docker logs zjoj-gojudge"
fi

echo ""
echo "========================================="
echo "  ✅ 安装完成！"
echo "========================================="
echo ""
echo "服务信息:"
echo "  - 地址: http://localhost:5050"
echo "  - 容器名: zjoj-gojudge"
echo ""
echo "常用命令:"
echo "  查看状态: docker ps | grep gojudge"
echo "  查看日志: docker logs -f zjoj-gojudge"
echo "  重启服务: docker restart zjoj-gojudge"
echo "  停止服务: docker stop zjoj-gojudge"
echo ""
