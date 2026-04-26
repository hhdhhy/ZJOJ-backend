#!/bin/bash
# ZJOJ 环境变量配置脚本（交互式）
# 用法: ./setup_env.sh

set -e

echo "========================================="
echo "ZJOJ 环境变量配置向导"
echo "========================================="
echo ""

# 检查 .env 文件是否存在
if [ -f ".env" ]; then
    echo "⚠️  检测到已存在的 .env 文件"
    read -p "是否覆盖现有配置？(y/N): " OVERWRITE
    if [[ ! $OVERWRITE =~ ^[Yy]$ ]]; then
        echo "已取消配置"
        exit 0
    fi
fi

echo ""
echo "请配置以下参数（直接回车使用默认值）："
echo ""

# 数据库配置
echo "--- 数据库配置 ---"
read -p "数据库名称 [ZJOJ]: " DB_NAME
DB_NAME=${DB_NAME:-ZJOJ}

read -p "数据库用户名 [zjoj_user]: " DB_USER
DB_USER=${DB_USER:-zjoj_user}

read -sp "数据库密码 [ZJOJ@2024secure]: " DB_PASSWORD
echo ""
DB_PASSWORD=${DB_PASSWORD:-ZJOJ@2024secure}

read -sp "数据库 root 密码 [root_secure_password_2024]: " DB_ROOT_PASSWORD
echo ""
DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD:-root_secure_password_2024}

echo ""
echo "--- DeepSeek API 配置（可选）---"
read -p "DeepSeek API Key (留空则禁用AI功能): " DEEPSEEK_API_KEY
DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY:-}

if [ -n "$DEEPSEEK_API_KEY" ]; then
    read -p "DeepSeek 模型 [deepseek-chat]: " DEEPSEEK_MODEL
    DEEPSEEK_MODEL=${DEEPSEEK_MODEL:-deepseek-chat}
    
    read -p "DeepSeek API 基础URL [https://api.deepseek.com]: " DEEPSEEK_BASE_URL
    DEEPSEEK_BASE_URL=${DEEPSEEK_BASE_URL:-https://api.deepseek.com}
else
    DEEPSEEK_MODEL=""
    DEEPSEEK_BASE_URL=""
fi

echo ""
echo "--- Django 配置 ---"
read -p "Django Secret Key (建议修改为随机字符串) [change-this-to-a-random-string]: " DJANGO_SECRET_KEY
DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY:-change-this-to-a-random-string}

read -p "Django Debug 模式 [False]: " DJANGO_DEBUG
DJANGO_DEBUG=${DJANGO_DEBUG:-False}

read -p "允许的主机 [*]: " DJANGO_ALLOWED_HOSTS
DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS:-*}

echo ""
echo "========================================="
echo "配置预览"
echo "========================================="
echo "数据库名称: $DB_NAME"
echo "数据库用户: $DB_USER"
echo "数据库密码: ${DB_PASSWORD:0:3}***"
echo "DeepSeek API: ${DEEPSEEK_API_KEY:0:8}..."
echo "Django Debug: $DJANGO_DEBUG"
echo "========================================="
echo ""

read -p "确认写入配置？(y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "已取消配置"
    exit 0
fi

# 生成 .env 文件
cat > .env <<EOF
# ==================== 数据库配置 ====================
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_ROOT_PASSWORD=$DB_ROOT_PASSWORD
DB_HOST=db
DB_PORT=3306

# ==================== DeepSeek API 配置（可选）====================
DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY
DEEPSEEK_MODEL=$DEEPSEEK_MODEL
DEEPSEEK_BASE_URL=$DEEPSEEK_BASE_URL

# ==================== Django 配置 ====================
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
DJANGO_DEBUG=$DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS=$DJANGO_ALLOWED_HOSTS
EOF

echo ""
echo "✅ 配置文件已保存到 .env"
echo ""
echo "下一步操作："
echo "1. 启动服务: docker compose up -d"
echo "2. 创建管理员: ./deploy/create_admin.sh"
echo "3. 查看日志: docker compose logs -f web"
echo ""
echo "========================================="
