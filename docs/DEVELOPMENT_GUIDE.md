# ZJOJ 开发指南

## 目录

1. [环境搭建](#环境搭建)
2. [项目配置](#项目配置)
3. [开发流程](#开发流程)
4. [代码规范](#代码规范)
5. [测试指南](#测试指南)
6. [部署指南](#部署指南)
7. [常见问题](#常见问题)

---

## 环境搭建

### 系统要求

- **Python**: 3.8+
- **Django**: 6.0.3
- **MySQL**: 5.7+ 或 8.0+
- **操作系统**: Windows/Linux/macOS

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd ZJOJ
```

#### 2. 创建虚拟环境

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install django==6.0.3 djangorestframework django-cors-headers shortuuidfield pyjwt mysqlclient
```

或使用 requirements.txt（如已创建）:
```bash
pip install -r requirements.txt
```

#### 4. 配置数据库

创建 MySQL 数据库：
```sql
CREATE DATABASE ZJOJ CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `ZJOJ/settings.py` 中的数据库配置：
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "ZJOJ",
        "USER": "root",
        "PASSWORD": "your_password",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}
```

#### 5. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. 创建超级用户

```bash
python manage.py createsuperuser
```

按提示输入：
- 用户名
- 邮箱
- 密码

#### 7. 运行开发服务器

```bash
python manage.py runserver
```

访问：
- 开发服务器：http://localhost:8000
- Django Admin: http://localhost:8000/admin

---

## 项目配置

### 环境变量管理

建议使用环境变量管理敏感信息，创建 `.env` 文件：

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_NAME=ZJOJ
DATABASE_USER=root
DATABASE_PASSWORD=your-password
ALLOWED_HOSTS=localhost,127.0.0.1
```

在 `settings.py` 中读取：
```python
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv('DATABASE_NAME'),
        "USER": os.getenv('DATABASE_USER'),
        "PASSWORD": os.getenv('DATABASE_PASSWORD'),
        # ...
    }
}
```

### 关键配置项说明

#### DEBUG 模式
```python
DEBUG = True  # 开发环境开启
DEBUG = False  # 生产环境必须关闭
```

#### CORS 配置
```python
# 开发环境：允许所有跨域
CORS_ALLOW_ALL_ORIGINS = True

# 生产环境：指定允许的源
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://www.example.com",
]
```

#### 自定义用户模型
```python
AUTH_USER_MODEL = "ojauth.OJUser"
```
⚠️ **重要**: 此配置必须在首次迁移前设置，之后不能修改！

---

## 开发流程

### 1. 创建新应用

```bash
python manage.py startapp appname
```

将新应用添加到 `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    "apps.appname",
]
```

### 2. 创建模型

在 `models.py` 中定义模型：
```python
from django.db import models

class Problem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'problem'
    
    def __str__(self):
        return self.title
```

### 3. 创建迁移并应用

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 创建序列化器

在 `serializers.py` 中创建：
```python
from rest_framework import serializers
from .models import Problem

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = '__all__'
```

### 5. 创建视图

在 `views.py` 中创建：
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Problem
from .serializers import ProblemSerializer

class ProblemList(APIView):
    def get(self, request):
        problems = Problem.objects.all()
        serializer = ProblemSerializer(problems, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ProblemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
```

### 6. 配置 URL

在项目 `urls.py` 中添加路由：
```python
from django.urls import path
from apps.problem import views

urlpatterns = [
    path('api/problems/', views.ProblemList.as_view()),
]
```

### 7. 测试接口

使用 Postman、curl 或编写单元测试进行测试。

---

## 代码规范

### Python 风格指南

遵循 PEP 8 编码规范：

#### 命名规范
```python
# 变量和函数：小写 + 下划线
def get_user_info():
    user_name = "john"
    return user_name

# 类：大驼峰
class UserInfo:
    pass

# 常量：全大写 + 下划线
MAX_LOGIN_ATTEMPTS = 5
```

#### 缩进
- 使用 4 个空格，不要用 Tab
- 保持一致的缩进风格

#### 行长度
- 每行不超过 79 个字符
- 长表达式使用括号换行

#### 导入顺序
```python
# 1. 标准库
import os
import sys

# 2. 第三方库
import jwt
from rest_framework import serializers

# 3. 本地应用
from apps.ojauth.models import OJUser
from MYJWT.myjwt import get_token
```

### Django 最佳实践

#### 模型层
- 使用 `objects` 管理器封装常用查询
- 添加 `__str__` 方法
- 在 `Meta` 类中定义 `db_table`
- 使用合适的数据类型和字段约束

#### 视图层
- 优先使用 DRF 的通用视图和视图集
- 保持视图函数简洁，业务逻辑放在服务层
- 使用序列化器验证数据
- 统一错误处理

#### 序列化器
- 明确指定 `fields` 或使用 `__all__`
- 使用验证器验证数据
- 自定义验证逻辑写在 `validate()` 方法

### 注释规范

```python
class JWTAuthentication(BaseAuthentication):
    """
    JWT 认证类
    
    用于验证 JWT Token 并获取用户对象
    """
    
    def authenticate(self, request):
        """
        认证请求
        
        Args:
            request: DRF 请求对象
            
        Returns:
            tuple: (user, auth) 或 None
            
        Raises:
            AuthenticationFailed: 当 Token 无效或过期时
        """
        pass
```

---

## 测试指南

### 运行测试

```bash
python manage.py test
```

运行特定应用的测试：
```bash
python manage.py test apps.ojauth
```

运行特定测试类：
```bash
python manage.py test apps.ojauth.tests.LoginTestCase
```

### 编写单元测试

#### 测试模型
```python
from django.test import TestCase
from apps.ojauth.models import OJUser

class OJUserTestCase(TestCase):
    def setUp(self):
        self.user = OJUser.objects.create_user(
            username='testuser',
            realname='Test User',
            email='test@example.com',
            password='password123'
        )
    
    def test_user_creation(self):
        """测试用户创建"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('password123'))
    
    def test_user_status(self):
        """测试用户状态"""
        from apps.ojauth.models import UserStatusChoices
        self.assertEqual(self.user.status, UserStatusChoices.UNACTIVE)
```

#### 测试视图
```python
from rest_framework.test import APITestCase
from rest_framework import status

class LoginViewTestCase(APITestCase):
    def setUp(self):
        self.user = OJUser.objects.create_user(
            username='testuser',
            realname='Test User',
            email='test@example.com',
            password='password123'
        )
    
    def test_login_success(self):
        """测试登录成功"""
        url = '/api/login/'
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_login_wrong_password(self):
        """测试密码错误"""
        url = '/api/login/'
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('密码错误', str(response.data))
```

#### 测试 JWT 认证
```python
from MYJWT.myjwt import get_token

class JWTTestCase(APITestCase):
    def setUp(self):
        self.user = OJUser.objects.create_user(
            username='testuser',
            realname='Test User',
            email='test@example.com',
            password='password123'
        )
        self.token = get_token(self.user)
    
    def test_authenticated_access(self):
        """测试认证访问"""
        url = '/api/user/profile/'
        self.client.credentials(HTTP_AUTHORIZATION=f'jwt {self.token}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_unauthenticated_access(self):
        """测试未认证访问"""
        url = '/api/user/profile/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

### 测试注意事项

⚠️ **测试数据库安全**
- Django 测试使用独立的测试数据库，不会影响生产数据
- 测试结束后会自动清理测试数据库
- 可放心运行测试

---

## 部署指南

### 生产环境准备

#### 1. 关闭 DEBUG 模式
```python
DEBUG = False
```

#### 2. 配置 ALLOWED_HOSTS
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'server-ip']
```

#### 3. 更换 SECRET_KEY
```python
SECRET_KEY = os.getenv('SECRET_KEY')  # 使用环境变量
# 生成新密钥：python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

#### 4. 启用 CSRF 保护
取消注释 CSRF 中间件：
```python
MIDDLEWARE = [
    # ...
    "django.middleware.csrf.CsrfViewMiddleware",
    # ...
]
```

#### 5. 配置生产数据库
- 使用强密码
- 创建专用数据库用户
- 限制数据库用户权限

#### 6. 静态文件收集
```bash
python manage.py collectstatic --noinput
```

配置 Nginx 提供静态文件服务：
```nginx
location /static/ {
    alias /path/to/staticfiles/;
}
```

### 使用 Gunicorn 部署

#### 安装 Gunicorn
```bash
pip install gunicorn
```

#### 启动 Gunicorn
```bash
gunicorn ZJOJ.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

#### 使用 systemd 管理（Linux）

创建服务文件 `/etc/systemd/system/zjoj.service`:
```ini
[Unit]
Description=ZJOJ Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/ZJOJ
ExecStart=/path/to/venv/bin/gunicorn ZJOJ.wsgi:application --bind unix:/run/zjoj.sock --workers 3

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl start zjoj
sudo systemctl enable zjoj
```

### 使用 Nginx 反向代理

配置 Nginx:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://unix:/run/zjoj.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }
}
```

### 使用 Docker 部署

创建 `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "ZJOJ.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

构建和运行：
```bash
docker build -t zjoj .
docker run -p 8000:8000 zjoj
```

---

## 常见问题

### Q1: 模型未安装错误

**错误信息：**
```
LookupError: Model class apps.ojauth.models.OJUser doesn't exist!
```

**解决方案：**
1. 检查 `INSTALLED_APPS` 是否正确配置
2. 确保应用路径正确：`"apps.ojauth"`
3. 重启开发服务器

### Q2: 迁移冲突

**问题：** 多个开发者创建了相同的迁移编号

**解决方案：**
```bash
# 合并迁移
python manage.py makemigrations --merge
```

### Q3: 自定义用户模型迁移问题

**错误：**
```
You're trying to add a non-nullable field 'X' to Y without a default.
```

**解决方案：**
```bash
# 删除有问题的迁移文件
# 重新创建迁移
python manage.py makemigrations
```

### Q4: JWT Token 验证失败

**可能原因：**
- SECRET_KEY 不一致
- Token 已过期
- Token 格式错误

**解决方案：**
1. 检查 SECRET_KEY 是否一致
2. 重新登录获取新 Token
3. 检查 Authorization 头格式：`jwt <token>`

### Q5: CORS 错误

**错误信息：**
```
Access to XMLHttpRequest at '...' from origin '...' has been blocked by CORS policy
```

**解决方案：**
```python
# 开发环境
CORS_ALLOW_ALL_ORIGINS = True

# 生产环境
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]
```

### Q6: 数据库连接失败

**检查项：**
1. MySQL 服务是否运行
2. 数据库名称、用户名、密码是否正确
3. 主机和端口配置是否正确
4. 防火墙设置

**解决方案：**
```bash
# 测试 MySQL 连接
mysql -u root -p -h 127.0.0.1 -P 3306
```

### Q7: 静态文件 404

**解决方案：**
1. 运行 `python manage.py collectstatic`
2. 检查 `STATIC_URL` 和 `STATIC_ROOT` 配置
3. 配置 Web 服务器（Nginx/Apache）提供静态文件

---

## 性能优化建议

### 数据库优化
- 为常用查询字段添加索引
- 使用 `select_related` 和 `prefetch_related` 减少查询次数
- 避免 N+1 查询问题

### 缓存
```python
from django.core.cache import cache

# 设置缓存
cache.set('key', 'value', timeout=300)

# 获取缓存
value = cache.get('key')
```

### 异步任务
对于耗时操作（如发送邮件），建议使用 Celery 等异步任务队列。

---

## 调试技巧

### Django Debug Toolbar
安装：
```bash
pip install django-debug-toolbar
```

配置：
```python
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### 日志配置
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

---

*最后更新：2026 年 3 月 24 日*
