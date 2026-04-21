# Problem 模块

> 📝 题目管理模块 - 题目的增删改查和标签管理

---

## 数据模型

### Tag（标签）

用于对题目进行分类标记。

**关键字段：**
- `name` - 标签名（唯一）
- `create_time` - 创建时间

```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    create_time = models.DateTimeField(auto_now_add=True)
```

### Problem（题目）

存储题目的基本信息。

**关键字段：**
- `problem_id` - 题目编号（主键，如 P1001）
- `title` - 题目标题
- `description` - 题面描述（Markdown）
- `time_limit` - 时间限制（毫秒）
- `memory_limit` - 内存限制（MB）
- `tags` - 多对多关联标签
- `creator` - 创建者（外键）
- `upload_time` / `update_time` - 时间戳

```python
class Problem(models.Model):
    problem_id = models.CharField(primary_key=True, max_length=20)
    title = models.CharField(max_length=100)
    description = models.TextField()
    time_limit = models.PositiveIntegerField()
    memory_limit = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag, blank=True, related_name='problems')
    creator = models.ForeignKey(OJUser, on_delete=models.SET_NULL)
    upload_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
```

---

## API 接口

### 题目列表

```
GET /api/problems/
```

**查询参数：**
- `page` - 页码（默认 1）
- `page_size` - 每页数量（默认 10）
- `tag` - 按标签筛选
- `search` - 搜索标题

**响应示例：**
```json
{
  "count": 100,
  "results": [
    {
      "problem_id": "P1001",
      "title": "A+B Problem",
      "time_limit": 1000,
      "memory_limit": 256,
      "tags": ["入门", "模拟"]
    }
  ]
}
```

### 题目详情

```
GET /api/problems/{problem_id}/
```

### 创建题目

```
POST /api/problems/
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体：**
```json
{
  "problem_id": "P1002",
  "title": "两数之和",
  "description": "# 题目描述\n...",
  "time_limit": 1000,
  "memory_limit": 256,
  "tags": [1, 2]
}
```

### 更新题目

```
PUT /api/problems/{problem_id}/
PATCH /api/problems/{problem_id}/
```

### 删除题目

```
DELETE /api/problems/{problem_id}/
```

---

## 使用示例

### 创建题目

```python
from apps.problem.models import Problem, Tag
from apps.ojauth.models import OJUser

# 获取创建者
user = OJUser.objects.get(username='admin')

# 创建题目
problem = Problem.objects.create(
    problem_id='P1001',
    title='A+B Problem',
    description='# A+B Problem\n\n计算 A + B',
    time_limit=1000,
    memory_limit=256,
    creator=user
)

# 添加标签
tag = Tag.objects.get(name='入门')
problem.tags.add(tag)
```

### 查询题目

```python
# 查询所有题目
problems = Problem.objects.all()

# 按标签筛选
dp_problems = Problem.objects.filter(tags__name='动态规划')

# 搜索标题
results = Problem.objects.filter(title__contains='A+B')
```

---

## 注意事项

1. **题目编号唯一**：`problem_id` 是主键，不能重复
2. **Markdown 格式**：`description` 字段支持 Markdown
3. **权限控制**：创建/修改/删除需要登录认证
4. **测试用例**：测试数据通过文件系统存储，不在数据库中

---

## 相关文件

- 模型：`apps/problem/models.py`
- 序列化器：`apps/problem/serializers.py`
- 视图：`apps/problem/views.py`
- URL：`apps/problem/urls.py`
