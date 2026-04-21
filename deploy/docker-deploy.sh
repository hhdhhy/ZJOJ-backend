#!/bin/bash
# ZJOJ Docker 一键部署脚本
# 适用于全新 Ubuntu 系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${BLUE}[STEP]${NC} $1"
}

echo -e "${BLUE}"
echo "======================================="
echo "  ZJOJ Docker 一键部署脚本"
echo "======================================="
echo -e "${NC}"

# 检查是否为 root 用户
if [ "$EUID" -eq 0 ]; then
    log_error "请不要使用 root 用户运行此脚本"
    exit 1
fi

# 1. 安装 Docker
log_step "1/6 安装 Docker..."
if ! command -v docker &> /dev/null; then
    log_info "正在安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    log_info "Docker 安装完成，需要重新登录才能生效"
else
    log_info "Docker 已安装: $(docker --version)"
fi

# 2. 安装 Docker Compose
log_step "2/6 安装 Docker Compose..."
if ! command -v docker compose &> /dev/null; then
    log_info "正在安装 Docker Compose..."
    DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
    mkdir -p $DOCKER_CONFIG/cli-plugins
    curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
    chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
    log_info "Docker Compose 安装完成"
else
    log_info "Docker Compose 已安装: $(docker compose version)"
fi

# 3. 配置项目
cd "$(dirname "$0")/.."

log_step "3/6 配置环境变量..."
if [ ! -f .env ]; then
    log_info "创建 .env 配置文件..."
    cat > .env << 'EOF'
# ==================== 数据库配置 ====================
DB_PASSWORD=ZJOJ@2024secure
DB_ROOT_PASSWORD=root_secure_password_2024

# ==================== DeepSeek API 配置（可选）====================
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com

# ==================== Django 配置 ====================
DJANGO_SECRET_KEY=change-this-to-a-random-string
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=*
EOF
    
    log_warn "请编辑 .env 文件修改密码和配置！"
    log_info "使用命令: nano .env 或 vim .env"
    read -p "按回车继续..." 
else
    log_info ".env 文件已存在"
fi

# 4. 构建镜像
log_step "4/6 构建 Docker 镜像..."
docker compose build

# 5. 启动服务
log_step "5/6 启动服务..."
docker compose up -d

# 6. 等待并检查
log_step "6/6 检查服务状态..."
log_info "等待服务启动（30秒）..."
sleep 30

# 显示服务状态
echo ""
log_info "服务状态："
docker compose ps

# 检查健康状态
if docker compose ps web | grep -q "Up"; then
    echo ""
    log_info "✅ Web 服务运行正常"
else
    echo ""
    log_warn "⚠️  Web 服务可能未正常启动，查看日志："
    log_warn "   docker compose logs web"
fi

if docker compose ps db | grep -q "healthy"; then
    log_info "✅ 数据库运行正常"
else
    log_warn "⚠️  数据库可能未就绪，查看日志："
    log_warn "   docker compose logs db"
fi

# 创建超级用户提示
echo ""
log_info "创建管理员账户："
log_info "docker compose exec web python manage.py createsuperuser"

# 显示访问信息
echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  🎉 部署完成！${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo "📍 访问地址:"
echo "   - 网站: http://$(curl -s ifconfig.me)"
echo "   - Admin: http://$(curl -s ifconfig.me)/admin"
echo ""
echo "📝 常用命令:"
echo "   查看日志:     docker compose logs -f"
echo "   停止服务:     docker compose down"
echo "   重启服务:     docker compose restart"
echo "   进入容器:     docker compose exec web bash"
echo "   数据库备份:   docker compose exec db mysqldump -u zjoj_user -p ZJOJ > backup.sql"
echo ""
echo "🔧 配置文件:"
echo "   - 环境变量: .env"
echo "   - Nginx:    deploy/nginx.conf"
echo "   - 主配置:   docker-compose.yml"
echo ""

