# 教练/学生权限体系

> 👥 ZJOJ 用户角色与班级管理系统

---

## 概述

ZJOJ 实现了完整的教练/学生权限体系，支持：
- ✅ 用户角色管理（学生/教练/管理员）
- ✅ 班级管理功能
- ✅ 权限隔离与数据安全
- ✅ 个人信息维护

---

## 用户角色

### 角色类型

| 角色 | 值 | 说明 |
|------|-----|------|
| 学生 | 1 | 普通用户，可以提交代码、查看题目 |
| 教练 | 2 | 可以创建班级、管理学生 |
| 管理员 | 3 | 系统管理员，拥有所有权限 |

### 用户模型字段

```python
class OJUser(AbstractBaseUser, PermissionsMixin):
    uid = CharField(primary_key=True)        # Short UUID
    username = CharField()                    # 用户名
    email = EmailField(unique=True)          # 邮箱（登录账号）
    telephone = CharField(unique=True)       # 手机号
    realname = CharField()                    # 真实姓名
    role = IntegerField()                     # 角色（1-学生, 2-教练, 3-管理员）
    avatar = URLField(blank=True)            # 头像URL
    bio = TextField(blank=True)              # 个人简介
    status = IntegerField()                   # 状态（1-激活, 2-未激活, 3-锁定）
    is_active = BooleanField()                # 是否激活
    is_staff = BooleanField()                 # 是否为工作人员
    date_joined = DateTimeField()             # 注册时间
```

### 角色判断方法

```python
user.is_student()   # 是否为学生
user.is_coach()     # 是否为教练
user.is_admin_user() # 是否为管理员
```

---

## 班级管理系统

### Class 模型

```python
class Class(models.Model):
    name = CharField(max_length=100, unique=True)  # 班级名称（唯一）
    coach = ForeignKey(OJUser, null=True)          # 班主任/教练
    description = TextField(blank=True)            # 班级描述
    create_time = DateTimeField(auto_now_add=True) # 创建时间
```

### ClassMember 模型

```python
class ClassMember(models.Model):
    class_obj = ForeignKey(Class)     # 班级
    user = ForeignKey(OJUser)         # 学生
    join_time = DateTimeField(auto_now_add=True)  # 加入时间
```

---

## API 接口

### 用户认证

#### 注册
```
POST /api/register/
Content-Type: application/json

{
  "username": "student01",
  "email": "student@example.com",
  "telephone": "13800001001",
  "realname": "张三",
  "password": "password123",
  "password_confirm": "password123",
  "role": 1  // 1-学生, 2-教练
}
```

#### 登录
```
POST /api/login/
Content-Type: application/json

{
  "username": "student01",
  "password": "password123"
}

响应:
{
  "token": "eyJhbGci...",
  "user": {
    "uid": "...",
    "username": "student01",
    "role": 1,
    ...
  }
}
```

### 用户信息

#### 获取个人信息
```
GET /api/user/profile/
Authorization: Bearer <token>
```

#### 更新个人信息
```
PUT /api/user/profile/
Authorization: Bearer <token>
Content-Type: application/json

{
  "realname": "李四",
  "telephone": "13800001002",
  "avatar": "https://example.com/avatar.jpg",
  "bio": "热爱编程"
}
```

#### 修改密码
```
POST /api/password/change/
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "oldpass",
  "new_password": "newpass"
}
```

### 班级管理

#### 班级列表
```
GET /api/classes/
Authorization: Bearer <token>

// 教练：返回自己管理的班级
// 学生：返回自己加入的班级
```

#### 创建班级（仅教练）
```
POST /api/classes/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "高一竞赛班",
  "description": "信息学竞赛培训"
}
```

#### 班级详情
```
GET /api/classes/{id}/
Authorization: Bearer <token>

响应:
{
  "id": 1,
  "name": "高一竞赛班",
  "coach": "李老师",
  "description": "信息学竞赛培训",
  "create_time": "2026-04-24T00:00:00Z",
  "members": [
    {
      "uid": "...",
      "username": "student01",
      "realname": "张三",
      "join_time": "2026-04-24T00:00:00Z"
    }
  ]
}
```

#### 添加成员（仅教练）
```
POST /api/classes/{id}/members/
Authorization: Bearer <token>
Content-Type: application/json

{
  "username": "student01"
}
```

#### 移除成员（仅教练）
```
DELETE /api/classes/{id}/members/
Authorization: Bearer <token>
Content-Type: application/json

{
  "username": "student01"
}
```

---

## 权限控制

### 权限装饰器

```python
from Middleware.PermissionCheck import coach_required, student_required

class MyView(APIView):
    @coach_required
    def post(self, request):
        # 只有教练可以访问
        pass
```

### 权限混入类

```python
from Middleware.PermissionCheck import CoachPermissionMixin

class MyClassView(CoachPermissionMixin, APIView):
    def post(self, request):
        self.check_coach_permission(request.user)
        # 教练专属逻辑
        pass
```

---

## 使用示例

### 1. 注册并登录

```bash
# 注册学生
curl -X POST http://101.35.233.33:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student01",
    "email": "student@test.com",
    "telephone": "13800001001",
    "realname": "张三",
    "password": "student123",
    "password_confirm": "student123",
    "role": 1
  }'

# 登录获取 Token
curl -X POST http://101.35.233.33:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "student01", "password": "student123"}'
```

### 2. 教练创建班级

```bash
# 教练登录
COACH_TOKEN=$(curl -s -X POST http://101.35.233.33:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "coach01", "password": "coach123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

# 创建班级
curl -X POST http://101.35.233.33:8000/api/classes/ \
  -H "Authorization: Bearer $COACH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "竞赛班",
    "description": "信息学竞赛培训"
  }'
```

### 3. 添加学生到班级

```bash
CLASS_ID=1
curl -X POST http://101.35.233.33:8000/api/classes/$CLASS_ID/members/ \
  -H "Authorization: Bearer $COACH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "student01"}'
```

---

## 数据安全

### 1. 密码安全
- ✅ 使用 Django PBKDF2 加密存储
- ✅ 密码不在 API 响应中返回

### 2. 权限隔离
- ✅ 教练只能管理自己的班级
- ✅ 学生只能查看自己的信息
- ✅ 敏感操作需要相应权限

### 3. 数据验证
- ✅ 用户名、邮箱、手机号唯一性
- ✅ 输入数据格式验证
- ✅ 防止 SQL 注入（Django ORM）

---

## 相关文件

- 模型：`apps/ojauth/models.py`
- 序列化器：`apps/ojauth/serializers.py`
- 视图：`apps/ojauth/views.py`
- URL：`apps/ojauth/urls.py`
- 权限中间件：`Middleware/PermissionCheck.py`
- Admin：`apps/ojauth/admin.py`
