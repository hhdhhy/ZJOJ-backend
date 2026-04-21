#!/bin/bash
# ZJOJ Docker 备份脚本

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"

echo "📦 开始备份 ZJOJ..."

# 创建备份目录
mkdir -p "$BACKUP_PATH"

# 1. 备份数据库
echo "💾 备份数据库..."
docker compose exec -T db mysqldump -u zjoj_user -p${DB_PASSWORD:-ZJOJ@2024secure} ZJOJ > "$BACKUP_PATH/database.sql"
echo "✅ 数据库备份完成"

# 2. 备份媒体文件
echo "💾 备份媒体文件..."
docker compose run --rm web tar czf /tmp/media_backup.tar.gz media/ 2>/dev/null || true
docker compose cp web:/tmp/media_backup.tar.gz "$BACKUP_PATH/media.tar.gz" 2>/dev/null || echo "⚠️  媒体文件备份跳过（可能为空）"
echo "✅ 媒体文件备份完成"

# 3. 备份配置文件
echo "💾 备份配置文件..."
cp .env "$BACKUP_PATH/" 2>/dev/null || echo "⚠️  .env 文件不存在"
cp docker-compose.yml "$BACKUP_PATH/" 2>/dev/null || echo "⚠️  docker-compose.yml 不存在"
echo "✅ 配置文件备份完成"

# 4. 压缩备份
echo "📦 压缩备份文件..."
cd "$BACKUP_DIR"
tar czf "backup_$TIMESTAMP.tar.gz" "backup_$TIMESTAMP"
rm -rf "backup_$TIMESTAMP"
cd ..

echo ""
echo "🎉 备份完成！"
echo "📍 备份文件: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
echo "💡 恢复命令: bash deploy/docker-restore.sh $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
