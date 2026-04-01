# ZJOJ 铸剑 - 在线评测系统

## 项目概述

ZJOJ（铸剑）是一个基于 Django 框架开发的在线评测（Online Judge）系统，提供用户认证、题目提交、代码评测等功能。「铸剑」寓意着磨砺技术、铸造精品。项目采用前后端分离架构，使用 RESTful API 进行数据交互。

## 技术栈

### 后端框架
- **Django 6.0.3** - 核心 Web 框架
- **Django REST Framework** - API 开发框架
- **django-cors-headers** - 跨域资源共享支持

### 数据库
- **MySQL** - 关系型数据库

### 认证系统
- **JWT (JSON Web Token)** - 基于令牌的身份认证
- **自定义用户模型 (OJUser)** - 扩展 Django 原生用户模型

### 其他依赖
- **shortuuidfield** - Short UUID 字段支持
- **PyJWT** - JWT 编解码库

## 项目结构

```
ZJOJ/
├── ZJOJ/                  # 项目配置目录
│   ├── __init__.py
│   ├── asgi.py           # ASGI 配置
│   ├── settings.py       # 项目设置
│   ├── urls.py           # 根 URL 配置
│   └── wsgi.py           # WSGI 配置
├── apps/                  # 应用目录
│   └── ojauth/           # 认证应用
│       ├── migrations/   # 数据库迁移
│       ├── __init__.py
│       ├── admin.py      # Django Admin 配置
│       ├── apps.py       # 应用配置
│       ├── models.py     # 数据模型
│       ├── seriallizers.py # DRF 序列化器
│       └── views.py      # 视图函数
├── MYJWT/                 # JWT 认证模块
│   ├── __init__.py
│   └── myjwt.py          # JWT 实现
├── templates/            # 模板文件
├── tests/                # 测试文件
│   └── tests.py
├── docs/                 # 文档目录
│   └── JWT_AUTHENTICATION.md
└── manage.py            # Django 管理脚本
```

## 核心功能模块

### 1. 用户认证模块 (ojauth) ✅

#### 用户模型 (OJUser)
继承自 `AbstractBaseUser` 和 `PermissionsMixin`，提供完整的用户认证功能。

**主要字段：**
- `uid` - Short UUID 主键
- `username` - 用户名（唯一，最多 150 字符）
- `realname` - 真实姓名（必填）
- `email` - 邮箱地址（唯一，用于登录）
- `telephone` - 电话号码（唯一）
- `is_staff` - 是否为工作人员
- `is_active` - 是否激活
- `status` - 用户状态（Active/Unactive/Locked）
- `date_joined` - 注册时间

**用户状态枚举 (UserStatusChoices)：**
- `ACTIVE = 1` - 已激活
- `UNACTIVE = 2` - 未激活
- `LOCKED = 3` - 锁定

**管理器方法：**
- `create_user()` - 创建普通用户
- `create_superuser()` - 创建超级用户
- `with_perm()` - 按权限查询用户

#### 登录视图 ✅
**路径**: `/api/login/`
**方法**: POST
**参数**: 
  - `username`: 用户名
  - `password`: 密码
**功能**: 验证用户凭据，更新最后登录时间，返回 JWT Token

**实现代码：**
```python
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()
            token = get_token(user)
            return Response({"token": token, "user": UerSerializer(user).data})
        return Response({"messages":"参数错误","errors":serializer.errors}, 
                       status=status.HTTP_400_BAD_REQUEST)
```

#### 登录序列化器
验证用户名和密码，检查用户状态，返回用户对象。

**验证规则：**
- 用户名长度：2-20 字符
- 密码长度：6-20 字符
- 检查用户是否存在
- 验证密码是否正确
- 检查用户是否被锁定

---

### 2. JWT 认证模块 (MYJWT) ✅

#### 令牌生成
```python
from MYJWT.myjwt import get_token
token = get_token(user)
```

**令牌特性：**
- 有效期：14 天
- 算法：HS256
- Payload: `{"userid": user.uid, "exp": 过期时间}`
- 签名密钥：Django SECRET_KEY

#### JWT 认证类
`JWTAuthentication` 继承自 `BaseAuthentication`

**认证流程：**
1. 从请求头获取 `Authorization: jwt <token>`
2. 解码并验证 JWT 令牌
3. 提取 userid 查询用户
4. 验证用户状态
5. 返回用户对象

**错误处理：**
- 令牌过期
- 签名无效
- 格式错误
- 用户不存在
- 用户非活跃

**使用示例：**
```python
from rest_framework.authentication import BaseAuthentication
from MYJWT.myjwt import JWTAuthentication

class ProtectedView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        # request.user 已认证
        return Response({"user": request.user.username})
```

## 数据库配置

### MySQL 连接
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "ZJOJ",
        "USER": "root",
        "PASSWORD": "******",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}
```

## 项目设置

### 关键配置项
- `DEBUG = True` - 调试模式
- `LANGUAGE_CODE = "zh-hans"` - 简体中文
- `TIME_ZONE = "UTC"` - 时区
- `USE_TZ = False` - 不使用时区
- `CORS_ALLOW_ALL_ORIGINS = True` - 允许所有跨域
- `AUTH_USER_MODEL = "ojauth.OJUser"` - 自定义用户模型

### 已安装应用
- `django.contrib.admin`
- `django.contrib.auth`
- `django.contrib.contenttypes`
- `django.contrib.sessions`
- `django.contrib.messages`
- `django.contrib.staticfiles`
- `rest_framework`
- `corsheaders`
- `apps.ojauth`

### 中间件
- SecurityMiddleware
- SessionMiddleware
- CorsMiddleware
- CommonMiddleware
- AuthenticationMiddleware
- MessageMiddleware
- XFrameOptionsMiddleware

## API 接口

### 已实现接口 ✅
1. **用户登录**: `POST /api/login/`
   - 验证用户名密码
   - 返回 JWT Token 和用户信息
   - 更新最后登录时间

### 待实现接口 ⏳
1. **用户注册**: `POST /api/register/`
2. **用户登出**: `POST /api/logout/`
3. **密码重置**: `POST /api/password/reset/`
4. **用户信息**: `GET/PUT /api/user/profile/`

## 安全性

### CSRF 保护
当前已关闭 CSRF 保护（开发环境），生产环境需启用。

### 密码验证
- 用户属性相似性检查
- 最小长度验证
- 常见密码检查
- 纯数字密码检查

### JWT 安全
- 使用 Django SECRET_KEY 签名
- 令牌有效期限制
- 签名验证
- 用户状态检查

## 开发指南

### 安装依赖
```bash
pip install django djangorestframework django-cors-headers shortuuidfield pyjwt mysqlclient
```

### 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

### 创建超级用户
```bash
python manage.py createsuperuser
```

### 运行开发服务器
```bash
python manage.py runserver
```

### 运行测试
```bash
python manage.py test
```

## 部署建议

### 生产环境配置
1. 设置 `DEBUG = False`
2. 配置 `ALLOWED_HOSTS`
3. 更换安全的 `SECRET_KEY`
4. 启用 CSRF 保护
5. 配置 HTTPS
6. 使用环境变量管理敏感信息

### 静态文件
```bash
python manage.py collectstatic
```

### WSGI 服务器
推荐使用 Gunicorn 或 uWSGI 作为 WSGI 服务器，配合 Nginx 反向代理。

## 测试说明

### 测试文件
- `tests/tests.py` - 主测试文件

### 测试注意事项
- 测试使用独立数据库，不影响生产数据
- 运行测试前确保数据库连接正常
- 测试覆盖认证流程和 JWT 功能

## 常见问题

### 1. 模型未安装错误
确保在 `settings.py` 的 `INSTALLED_APPS` 中正确注册应用。

### 2. JWT 密钥长度
HMAC 密钥应至少 32 字节，满足 RFC 7518 安全要求。

### 3. 自定义用户模型
必须在首次迁移前设置 `AUTH_USER_MODEL`，之后不能修改。

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

[请添加许可证信息]

## 联系方式

[请添加联系方式]

---

*最后更新：2026 年 3 月 24 日*
