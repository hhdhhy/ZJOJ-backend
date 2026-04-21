# ZJOJ 部署脚本说明

本目录包含 ZJOJ 项目的自动化部署脚本，帮助您快速完成服务器配置和应用部署。

## 📋 脚本列表

### 1. `setup_env.sh` - 环境变量配置向导（推荐首次使用）

**用途**: 交互式配置所有环境变量

**用法**:
```bash
cd ~/projects/ZJOJ-backend
./deploy/setup_env.sh
```

**功能**:
- ✅ 配置数据库连接信息
- ✅ 配置 DeepSeek API（可选）
- ✅ 生成 `.env` 文件
- ✅ 提供默认值，直接回车即可

---

### 2. `create_admin.sh` - 管理员账户创建

**用途**: 快速创建或更新管理员账户

**用法**:
```bash
# 使用默认值（admin/admin123）
./deploy/create_admin.sh

# 自定义参数
./deploy/create_admin.sh [用户名] [密码] [邮箱]

# 示例
./deploy/create_admin.sh myadmin MyPass@123 admin@example.com
```

**功能**:
- ✅ 自动检测 Docker 服务状态
- ✅ 创建新的管理员账户
- ✅ 如果用户已存在则更新密码
- ✅ 显示登录信息

---

### 3. `setup_ai_api.sh` - AI API Key 配置

**用途**: 交互式配置 AI 服务提供商的 API Key

**用法**:
```bash
./deploy/setup_ai_api.sh
```

**功能**:
- ✅ 支持 DeepSeek（推荐）
- ✅ 支持智谱 AI（Zhipu）
- ✅ 支持通义千问（Qwen）
- ✅ 安全输入 API Key（不显示在屏幕）
- ✅ 可选重启服务应用配置

**配置示例**:
```bash
$ ./deploy/setup_ai_api.sh

请选择 AI 服务提供商：
1. DeepSeek (推荐)
2. 智谱 AI (Zhipu)
3. 通义千问 (Qwen)
4. 跳过 AI 配置

请选择 [1-4]: 1

--- DeepSeek 配置 ---
请输入 DeepSeek API Key: sk-xxxxxxxxxxxxx
模型名称 [deepseek-chat]: deepseek-chat
API 基础URL [https://api.deepseek.com]: https://api.deepseek.com

✅ DeepSeek 配置完成
```

---

### 4. `quick-deploy.sh` - 快速部署脚本

**用途**: 一键完成代码拉取、环境配置和服务启动

**用法**:
```bash
./deploy/quick-deploy.sh
```

**功能**:
- ✅ 从 GitHub 拉取最新代码
- ✅ 检查并配置环境变量
- ✅ 构建 Docker 镜像
- ✅ 启动所有服务
- ✅ 创建管理员账户

---

### 4. `system-init.sh` - 系统初始化脚本

**用途**: 在新服务器上初始化系统环境

**用法**:
```bash
sudo ./deploy/system-init.sh
```

**功能**:
- ✅ 安装 Docker 和 Docker Compose
- ✅ 配置系统参数
- ✅ 创建必要目录
- ✅ 设置防火墙规则

---

### 5. `docker-backup.sh` - 数据备份脚本

**用途**: 备份数据库和重要数据

**用法**:
```bash
./deploy/docker-backup.sh [备份文件名]
```

**示例**:
```bash
./deploy/docker-backup.sh backup_20260422.tar.gz
```

---

### 6. `docker-restore.sh` - 数据恢复脚本

**用途**: 从备份文件恢复数据

**用法**:
```bash
./deploy/docker-restore.sh <备份文件>
```

**示例**:
```bash
./deploy/docker-restore.sh backup_20260422.tar.gz
```

---

## 🚀 快速开始（完整流程）

### 首次部署

```bash
# 1. 克隆代码
git clone git@github.com:hhdhhy/ZJOJ-backend.git
cd ZJOJ-backend

# 2. 配置环境变量（交互式）
./deploy/setup_env.sh

# 3. 启动服务
docker compose up -d

# 4. 创建管理员账户
./deploy/create_admin.sh admin YourPassword admin@example.com

# 5. 配置 AI API Key（可选）
./deploy/setup_ai_api.sh

# 6. 查看日志确认运行正常
docker compose logs -f web
```

### 更新部署

```bash
# 1. 拉取最新代码
git pull origin feature/ai-assistant-step1

# 2. 重新构建并启动
docker compose up -d --build

# 3. 查看日志
docker compose logs -f web
```

---

## 📝 配置文件说明

### 服务访问地址

部署完成后，可通过以下地址访问：

- **后端 API**: `http://101.35.233.33:8000/api/`
- **Admin 后台**: `http://101.35.233.33:8000/admin/`
- **API 文档**: `http://101.35.233.33:8000/api/docs/` (如果启用)

### `.env` 文件结构

```bash
# 数据库配置
DB_NAME=ZJOJ
DB_USER=zjoj_user
DB_PASSWORD=your_password
DB_ROOT_PASSWORD=root_password
DB_HOST=db
DB_PORT=3306

# DeepSeek API（可选）
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Django 配置
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=*
```

---

## 🔧 常用命令

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f web

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 进入容器
docker compose exec web bash

# 数据库迁移
docker compose exec web python manage.py migrate

# 收集静态文件
docker compose exec web python manage.py collectstatic --noinput
```

---

## ⚠️ 注意事项

1. **安全性**: 
   - 生产环境务必修改默认密码
   - 不要将 `.env` 文件提交到 Git
   - 定期备份数据库

2. **端口占用**:
   - 后端默认使用 8000 端口（避免与前端冲突）
   - HTTPS 使用 8443 端口
   - 确保在云服务器安全组中开放相应端口
   - 如有冲突，修改 `docker-compose.yml` 中的端口映射

3. **资源要求**:
   - 最低配置: 2GB RAM, 1 CPU
   - 推荐配置: 4GB RAM, 2 CPU
   - 磁盘空间: 至少 10GB

4. **网络问题**:
   - 首次构建需要下载依赖，可能需要较长时间
   - 如遇到网络超时，可配置国内镜像源

---

## 🆘 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker compose logs web

# 检查端口占用
sudo ss -tlnp | grep ':80'

# 重新启动
docker compose down && docker compose up -d
```

### 数据库连接失败

```bash
# 检查数据库是否运行
docker compose ps db

# 查看数据库日志
docker compose logs db

# 测试连接
docker compose exec web python -c "from django.db import connection; print(connection.ensure_connection())"
```

### 管理员无法登录

```bash
# 重置管理员密码
./deploy/create_admin.sh admin newpassword admin@example.com
```

---

## 📞 支持

如有问题，请提交 Issue 或联系开发团队。
