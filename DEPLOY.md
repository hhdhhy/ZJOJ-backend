# ZJOJ Docker 部署指南

## 🚀 快速开始

### 全新系统（推荐）

```bash
# 1. 系统初始化
curl -fsSL https://raw.githubusercontent.com/hhdhhy/ZJOJ-backend/main/deploy/system-init.sh | bash

# 2. 进入项目目录
cd ~/projects/ZJOJ-backend

# 3. 一键部署
chmod +x deploy/docker-deploy.sh
./deploy/docker-deploy.sh

# 4. 创建管理员
docker compose exec web python manage.py createsuperuser
```

### 已有系统

```bash
# 1. 克隆项目
git clone git@github.com:hhdhhy/ZJOJ-backend.git
cd ZJOJ-backend

# 2. 运行部署脚本
chmod +x deploy/docker-deploy.sh
./deploy/docker-deploy.sh

# 3. 创建管理员
docker compose exec web python manage.py createsuperuser
```

## 📋 常用命令

```bash
# 服务管理
docker compose up -d          # 启动
docker compose down           # 停止
docker compose restart        # 重启
docker compose ps             # 状态
docker compose logs -f        # 日志

# 数据管理
bash deploy/docker-backup.sh                    # 备份
bash deploy/docker-restore.sh backups/xxx.tar.gz # 恢复

# 数据库操作
docker compose exec web python manage.py migrate      # 迁移
docker compose exec web python manage.py createsuperuser # 创建管理员
docker compose exec db mysql -u zjoj_user -p ZJOJ       # 数据库CLI
```

## 🔧 配置文件

| 文件 | 说明 |
|------|------|
| `.env` | 环境变量（密码、API Key） |
| `docker-compose.yml` | Docker 服务编排 |
| `Dockerfile` | Django 镜像构建 |
| `deploy/nginx.conf` | Nginx 配置 |

## 📊 架构

```
外部访问 (80端口)
    ↓
┌──────────┐
│  Nginx   │
└────┬─────┘
     ↓
┌──────────┐
│  Django  │ (8000端口)
└────┬─────┘
     ↓
┌──────────┐
│  MySQL   │
└──────────┘
```

## ⚠️ 注意事项

1. **首次启动**需要等待 30-60 秒（数据库初始化）
2. **修改 .env** 后需重启：`docker compose up -d`
3. **数据持久化**在 Docker Volumes 中，不要随意删除

## 📞 帮助

- 完整文档：查看 `docs/` 目录
- 问题反馈：https://github.com/hhdhhy/ZJOJ-backend/issues
