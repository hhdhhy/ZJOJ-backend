#!/bin/bash
# ZJOJ 数据库备份脚本
# 用法: ./backup_db.sh

set -e

# 配置
BACKUP_DIR="/opt/zjoj_data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="zjoj"
DB_USER="zjoj"
DB_PASS="YourStrongPassword123!"  # 建议从环境变量读取
RETENTION_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

echo "📦 开始数据库备份..."
echo "时间: $(date)"
echo "数据库: $DB_NAME"

# 全量备份
mysqldump -u $DB_USER -p$DB_PASS \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# 检查备份是否成功
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h $BACKUP_DIR/db_backup_$DATE.sql.gz | cut -f1)
    echo "✅ 备份成功！"
    echo "文件大小: $BACKUP_SIZE"
    echo "文件位置: $BACKUP_DIR/db_backup_$DATE.sql.gz"
else
    echo "❌ 备份失败！"
    exit 1
fi

# 删除旧备份
echo "🗑️  清理${RETENTION_DAYS}天前的备份..."
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "✨ 备份完成！"
