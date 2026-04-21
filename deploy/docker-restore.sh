#!/bin/bash
# ZJOJ Docker 恢复脚本

set -e

if [ -z "$1" ]; then
    echo "❌ 请指定备份文件路径"
    echo "用法: bash deploy/docker-restore.sh <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "🔄 开始恢复 ZJOJ..."
echo "📦 备份文件: $BACKUP_FILE"

# 解压备份
TEMP_DIR=$(mktemp -d)
tar xzf "$BACKUP_FILE" -C "$TEMP_DIR"
BACKUP_PATH="$TEMP_DIR/backup_*"

# 1. 恢复配置文件
echo "📝 恢复配置文件..."
if [ -f "$BACKUP_PATH/.env" ]; then
    cp "$BACKUP_PATH/.env" ./.env
    echo "✅ .env 已恢复"
fi

# 2. 启动服务
echo "🚀 启动服务..."
docker compose up -d
sleep 10

# 3. 恢复数据库
echo "💾 恢复数据库..."
if [ -f "$BACKUP_PATH/database.sql" ]; then
    docker compose exec -T db mysql -u zjoj_user -p${DB_PASSWORD:-ZJOJ@2024secure} ZJOJ < "$BACKUP_PATH/database.sql"
    echo "✅ 数据库已恢复"
else
    echo "⚠️  数据库备份文件不存在，跳过"
fi

# 4. 恢复媒体文件
echo "💾 恢复媒体文件..."
if [ -f "$BACKUP_PATH/media.tar.gz" ]; then
    docker compose cp "$BACKUP_PATH/media.tar.gz" web:/tmp/media_restore.tar.gz
    docker compose exec web tar xzf /tmp/media_restore.tar.gz
    docker compose exec web rm /tmp/media_restore.tar.gz
    echo "✅ 媒体文件已恢复"
else
    echo "⚠️  媒体文件备份不存在，跳过"
fi

# 清理临时文件
rm -rf "$TEMP_DIR"

# 重启服务
echo "🔄 重启服务..."
docker compose restart

echo ""
echo "🎉 恢复完成！"
echo "📍 访问地址: http://localhost"
