#!/bin/bash
# ZJOJ 管理员账户创建脚本
# 用法: ./create_admin.sh [username] [password] [email]

set -e

# 默认值
ADMIN_USERNAME=${1:-admin}
ADMIN_PASSWORD=${2:-admin123}
ADMIN_EMAIL=${3:-admin@zjoj.com}

echo "========================================="
echo "ZJOJ 管理员账户创建"
echo "========================================="
echo "用户名: $ADMIN_USERNAME"
echo "邮箱: $ADMIN_EMAIL"
echo "========================================="

# 检查 Docker Compose 是否运行
if ! docker compose ps 2>/dev/null | grep -q "web"; then
    echo "❌ 错误: Docker 服务未运行，请先启动服务"
    echo "   运行: docker compose up -d"
    exit 1
fi

# 创建管理员账户
echo ""
echo "正在创建管理员账户..."
docker compose exec -T web python manage.py shell <<EOF
from apps.ojauth.models import OJUser

# 检查用户是否已存在
if OJUser.objects.filter(username='$ADMIN_USERNAME').exists():
    print(f"⚠️  用户 '$ADMIN_USERNAME' 已存在")
    user = OJUser.objects.get(username='$ADMIN_USERNAME')
    user.set_password('$ADMIN_PASSWORD')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"✅ 已更新用户 '$ADMIN_USERNAME' 的密码和权限")
else:
    # 创建新用户
    user = OJUser.objects.create_superuser(
        username='$ADMIN_USERNAME',
        email='$ADMIN_EMAIL',
        password='$ADMIN_PASSWORD'
    )
    print(f"✅ 成功创建管理员账户: $ADMIN_USERNAME")

print(f"\\n登录信息:")
print(f"  用户名: {user.username}")
print(f"  密码: $ADMIN_PASSWORD")
print(f"  邮箱: {user.email}")
print(f"\\n访问地址:")
print(f"  Admin后台: http://101.35.233.33/admin/")
print(f"  API登录: POST http://101.35.233.33/api/login/")
EOF

echo ""
echo "========================================="
echo "完成！"
echo "========================================="
