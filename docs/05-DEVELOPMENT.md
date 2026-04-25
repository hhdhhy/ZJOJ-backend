# 开发指�?
> 🛠�?ZJOJ 项目开发规范和最佳实�?
---

## 快速开�?
### 环境要求

- **Python**: 3.8+
- **Django**: 6.0+
- **MySQL**: 8.0+
- **Docker**: 20.10+（推荐）

### 开发环境搭�?
#### 方式一：Docker（推荐）

```bash
git clone git@github.com:hhdhhy/ZJOJ-backend.git
cd ZJOJ-backend
./deploy/setup_env.sh
docker compose up -d
```

#### 方式二：本地开�?
```bash
# 1. 克隆项目
git clone git@github.com:hhdhhy/ZJOJ-backend.git
cd ZJOJ-backend

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置数据�?# 编辑 ZJOJ/settings.py 或创�?.env 文件

# 5. 数据迁移
python manage.py migrate

# 6. 创建管理�?python manage.py createsuperuser

# 7. 启动服务
python manage.py runserver
```

---

## 代码规范

### Python 代码风格

遵循 PEP 8 规范�?
```python
# �?好的命名
def get_user_profile(user_id: str) -> dict:
    """获取用户资料"""
    pass

# �?不好的命�?def getUser(u):
    pass
```

**要点**�?- 使用 snake_case 命名函数和变�?- 使用 PascalCase 命名�?- 添加类型注解
- 编写 docstring

### Django 最佳实�?
#### 1. 模型设计

```python
class Problem(models.Model):
    problem_id = models.CharField(primary_key=True, max_length=20)
    title = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'problem_problem'
        verbose_name = '题目'
        verbose_name_plural = '题目'
    
    def __str__(self):
        return f"{self.problem_id}: {self.title}"
```

#### 2. 视图设计

使用 DRF �?ViewSet�?
```python
from rest_framework import viewsets, permissions

class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tag__name=tag)
        return queryset
```

#### 3. 序列化器

```python
from rest_framework import serializers

class ProblemSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=Tag.objects.all()
    )
    
    class Meta:
        model = Problem
        fields = ['problem_id', 'title', 'description', 'tags']
```

---

## 项目结构

```
ZJOJ-backend/
├── apps/                  # 应用模块
�?  ├── ojauth/           # 用户认证
�?  ├── problem/          # 题目管理
�?  ├── submission/       # 提交记录
�?  └── ai_assistant/     # AI助手
├── ZJOJ/                 # 项目配置
�?  ├── settings.py       # 基础配置
�?  ├── urls.py           # URL路由
�?  └── wsgi.py           # WSGI入口
├── deploy/               # 部署脚本
├── docs/                 # 文档
├── manage.py             # Django管理命令
└── requirements.txt      # Python依赖
```

---

## API 开发规�?
### RESTful 设计

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/problems/ | 获取题目列表 |
| POST | /api/problems/ | 创建题目 |
| GET | /api/problems/{id}/ | 获取题目详情 |
| PUT | /api/problems/{id}/ | 更新题目 |
| DELETE | /api/problems/{id}/ | 删除题目 |

### 响应格式

**成功响应**�?```json
{
  "count": 100,
  "next": "http://api.example.com/problems/?page=2",
  "previous": null,
  "results": [...]
}
```

**错误响应**�?```json
{
  "error": "验证失败",
  "details": {
    "title": ["此字段必�?]
  }
}
```

### 权限控制

```python
from rest_framework.permissions import IsAuthenticated

class SubmissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # 需要登�?```

#### 角色权限控制

```python
from Middleware.PermissionCheck import coach_required, student_required

class ClassView(APIView):
    @coach_required  # 仅教练可访问
    def post(self, request):
        pass
```

详见：[权限系统文档](06-MODULES/permission-system.md)

公开接口需显式豁免�?
```python
from rest_framework.permissions import AllowAny

class LoginView(APIView):
    permission_classes = [AllowAny]  # 无需登录
```

---

## 测试

### 单元测试

```python
from django.test import TestCase
from apps.problem.models import Problem

class ProblemTestCase(TestCase):
    def setUp(self):
        Problem.objects.create(
            problem_id='P1001',
            title='Test Problem',
            time_limit=1000,
            memory_limit=256
        )
    
    def test_problem_creation(self):
        problem = Problem.objects.get(problem_id='P1001')
        self.assertEqual(problem.title, 'Test Problem')
```

运行测试�?```bash
python manage.py test
```

---

## Git 工作�?
### 分支策略

- `main` - 主分支（生产环境�?- `develop` - 开发分�?- `feature/*` - 功能分支
- `hotfix/*` - 紧急修�?
### 提交规范

```bash
# 格式�?type>: <subject>

# 示例
git commit -m "feat: add problem search feature"
git commit -m "fix: resolve login timeout issue"
git commit -m "docs: update API documentation"
```

**Type 类型**�?- `feat`: 新功�?- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具�?
---

## 调试技�?
### Django Debug Toolbar

安装�?```bash
pip install django-debug-toolbar
```

配置 `settings.py`�?```python
INSTALLED_APPS = [
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']
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
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

---

## 性能优化

### 数据库查询优�?
```python
# �?N+1 查询问题
problems = Problem.objects.all()
for p in problems:
    print(p.creator.username)  # 每次循环都查询数据库

# �?使用 select_related
problems = Problem.objects.select_related('creator').all()
for p in problems:
    print(p.creator.username)  # 只查询一�?```

### 缓存

```python
from django.core.cache import cache

def get_problem_list():
    cache_key = 'problem_list'
    data = cache.get(cache_key)
    if not data:
        data = list(Problem.objects.all())
        cache.set(cache_key, data, 300)  # 缓存5分钟
    return data
```

---

## 常见问题

### 1. 数据库连接失�?
```bash
# 检�?MySQL 是否运行
sudo systemctl status mysql

# 测试连接
mysql -u root -p
```

### 2. 迁移冲突

```bash
# 重置迁移
python manage.py migrate --fake zero
python manage.py makemigrations
python manage.py migrate
```

### 3. 静态文�?404

```bash
python manage.py collectstatic
```

---

## 相关文档

- [API 参考](04-API_REFERENCE.md)
- [数据库设计](07-DATABASE.md)
- [部署指南](03-DEPLOYMENT.md)
