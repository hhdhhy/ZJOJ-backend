# API 参考

> 🔌 ZJOJ RESTful API 完整接口文档

---

## 📋 目录

- [认证机制](#认证机制)
- [用户认证](#用户认证)
- [题目管理](#题目管理)
- [代码评测](#代码评测)
- [AI 助手](#ai-助手)
- [错误处理](#错误处理)

---

## 🔐 认证机制

### JWT Token 认证

所有需要认证的接口使用 JWT Token。

**请求头格式**:
```http
Authorization: jwt <token>
```

**获取 Token**:
通过登录接口 `/auth/login/` 获取。

**Token 有效期**: 24 小时

---

## 👤 用户认证

### 1. 用户登录

**端点**: `POST /auth/login/`

**请求体**:
```json
{
  "username": "john_doe",
  "password": "your_password"
}
```

**响应** (200):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "uid": "abc123",
    "username": "john_doe",
    "email": "john@example.com",
    "is_staff": false,
    "status": 1
  }
}
```

**错误响应** (400):
```json
{
  "messages": "参数错误",
  "errors": {
    "username": ["用户名不存在"]
  }
}
```

---

### 2. 获取用户信息

**端点**: `GET /api/user/profile/`

**认证**: 需要 JWT Token

**响应** (200):
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "uid": "abc123",
    "username": "john_doe",
    "realname": "John Doe",
    "email": "john@example.com",
    "telephone": "13800138000",
    "is_staff": false,
    "status": 1,
    "date_joined": "2026-04-16T10:00:00",
    "last_login": "2026-04-20T01:20:00"
  }
}
```

---

### 3. 更新用户信息

**端点**: `PUT /api/user/profile/`

**认证**: 需要 JWT Token

**请求体**:
```json
{
  "realname": "张三",
  "telephone": "13900139000"
}
```

**响应** (200):
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "uid": "abc123",
    "username": "john_doe",
    "realname": "张三",
    "telephone": "13900139000"
  }
}
```

**注意**: 只能更新 `realname` 和 `telephone` 字段。

---

## 📝 题目管理

### 1. 获取题目列表

**端点**: `GET /api/problems/`

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码（默认 1） |
| `page_size` | int | 每页数量（默认 20） |
| `difficulty` | string | 难度过滤 (EASY/MEDIUM/HARD) |
| `tag` | string | 标签过滤 |
| `search` | string | 搜索关键词 |

**响应** (200):
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/problems/?page=2",
  "previous": null,
  "results": [
    {
      "id": "A001",
      "title": "A+B Problem",
      "description": "计算 A + B",
      "difficulty": "EASY",
      "time_limit": 1000,
      "memory_limit": 256,
      "tags": ["模拟", "入门"],
      "solved_count": 1234,
      "submit_count": 5678
    }
  ]
}
```

---

### 2. 获取题目详情

**端点**: `GET /api/problems/{problem_id}/`

**响应** (200):
```json
{
  "id": "A001",
  "title": "A+B Problem",
  "description": "## 题目描述\n\n计算 A + B 的和...",
  "input_format": "两个整数 A 和 B",
  "output_format": "输出 A + B 的结果",
  "sample_input": "1 2",
  "sample_output": "3",
  "difficulty": "EASY",
  "time_limit": 1000,
  "memory_limit": 256,
  "tags": [
    {"name": "模拟", "slug": "simulation"},
    {"name": "入门", "slug": "intro"}
  ],
  "test_cases_count": 10,
  "solved_count": 1234,
  "submit_count": 5678,
  "acceptance_rate": 21.73
}
```

---

### 3. 创建题目

**端点**: `POST /api/problems/create/`

**认证**: 需要管理员权限

**请求体**:
```json
{
  "title": "New Problem",
  "description": "Problem description...",
  "input_format": "Input format...",
  "output_format": "Output format...",
  "sample_input": "1 2",
  "sample_output": "3",
  "difficulty": "MEDIUM",
  "time_limit": 1000,
  "memory_limit": 256,
  "tags": ["dp", "math"]
}
```

**响应** (201):
```json
{
  "code": 201,
  "message": "创建成功",
  "data": {
    "id": "A002",
    "title": "New Problem"
  }
}
```

---

### 4. 上传测试用例

**端点**: `POST /api/problems/{problem_id}/upload-testcases/`

**认证**: 需要管理员权限

**Content-Type**: `multipart/form-data`

**请求参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `file` | file | ZIP 文件 |

**ZIP 文件结构**:
```
testcases.zip
└── testdata/
    ├── 1.in
    ├── 1.out
    ├── 2.in
    └── 2.out
```

**响应** (200):
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "test_cases_count": 10
  }
}
```

---

### 5. 获取标签列表

**端点**: `GET /api/problems/tags/`

**响应** (200):
```json
{
  "count": 15,
  "results": [
    {"name": "动态规划", "slug": "dp", "problem_count": 50},
    {"name": "图论", "slug": "graph", "problem_count": 30},
    {"name": "数学", "slug": "math", "problem_count": 40}
  ]
}
```

---

## ⚡ 代码评测

### 1. 提交代码

**端点**: `POST /api/submissions/submit/`

**认证**: 需要 JWT Token

**请求体**:
```json
{
  "problem_id": "A001",
  "language": "cpp",
  "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}"
}
```

**支持的语言**:
- `cpp` - C++
- `c` - C
- `python` - Python 3
- `java` - Java

**响应** (201):
```json
{
  "submission_id": "sub_abc123",
  "status": "PENDING",
  "message": "提交成功，正在评测..."
}
```

**评测流程**:
1. 创建 Submission 记录（status=PENDING）
2. 同步调用评测系统
3. 执行所有测试点
4. 更新 Submission 状态
5. 返回最终结果

---

### 2. 获取提交列表

**端点**: `GET /api/submissions/`

**认证**: 需要 JWT Token

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码 |
| `problem_id` | string | 题目 ID 过滤 |
| `status` | string | 状态过滤 (AC/WA/TLE/...) |
| `language` | string | 语言过滤 |

**响应** (200):
```json
{
  "count": 50,
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": "sub_abc123",
      "problem": {
        "id": "A001",
        "title": "A+B Problem"
      },
      "user": {
        "uid": "user_xyz",
        "username": "john_doe"
      },
      "language": "cpp",
      "status": "ACCEPTED",
      "score": 100,
      "time_used": 12,
      "memory_used": 3200,
      "created_at": "2026-04-21T10:30:00"
    }
  ]
}
```

---

### 3. 获取提交详情

**端点**: `GET /api/submissions/{submission_id}/`

**认证**: 需要 JWT Token

**响应** (200):
```json
{
  "id": "sub_abc123",
  "problem": {
    "id": "A001",
    "title": "A+B Problem"
  },
  "user": {
    "uid": "user_xyz",
    "username": "john_doe"
  },
  "language": "cpp",
  "code": "#include <iostream>...",
  "status": "ACCEPTED",
  "score": 100,
  "time_used": 12,
  "memory_used": 3200,
  "test_cases": [
    {
      "id": 1,
      "status": "ACCEPTED",
      "score": 10,
      "time": 5,
      "memory": 3100,
      "stdout": "3\n"
    },
    {
      "id": 2,
      "status": "ACCEPTED",
      "score": 10,
      "time": 7,
      "memory": 3200,
      "stdout": "100\n"
    }
  ],
  "created_at": "2026-04-21T10:30:00",
  "judged_at": "2026-04-21T10:30:02"
}
```

**评测状态说明**:

| 状态 | 含义 |
|------|------|
| `PENDING` | 等待评测 |
| `JUDGING` | 评测中 |
| `ACCEPTED` | 答案正确 |
| `WRONG_ANSWER` | 答案错误 |
| `TIME_LIMIT_EXCEEDED` | 超时 |
| `MEMORY_LIMIT_EXCEEDED` | 超内存 |
| `RUNTIME_ERROR` | 运行时错误 |
| `COMPILATION_ERROR` | 编译错误 |
| `SYSTEM_ERROR` | 系统错误 |

---

## 🤖 AI 助手

### 1. AI 智能问答

**端点**: `POST /api/ai/chat/`

**认证**: 需要 JWT Token

**请求体**:
```json
{
  "question": "什么是动态规划？",
  "mode": "rag"  // rag 或 normal
}
```

**响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "answer": "动态规划是一种算法设计技术...",
    "sources": [
      {
        "title": "动态规划入门",
        "doc_type": "tutorial",
        "similarity": 0.95
      }
    ],
    "tokens_used": 150,
    "remaining_quota": 49
  }
}
```

**配额限制**:
- 每日限额：50 次
- 频率限制：60秒内最多 10 次

---

### 2. 获取对话历史

**端点**: `GET /api/ai/history/`

**认证**: 需要 JWT Token

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码 |
| `page_size` | int | 每页数量（默认 20） |

**响应** (200):
```json
{
  "count": 30,
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": 1,
      "question": "什么是动态规划？",
      "answer": "动态规划是一种...",
      "sources": [...],
      "tokens_used": 150,
      "created_at": "2026-04-21T10:00:00"
    }
  ]
}
```

---

### 3. 获取使用情况

**端点**: `GET /api/ai/usage/`

**认证**: 需要 JWT Token

**响应** (200):
```json
{
  "code": 200,
  "data": {
    "daily_quota": 50,
    "used_today": 5,
    "remaining": 45,
    "total_questions": 120,
    "max_history": 100,
    "history_count": 30
  }
}
```

---

### 4. 清空对话历史

**端点**: `DELETE /api/ai/history/clear/`

**认证**: 需要 JWT Token

**响应** (200):
```json
{
  "code": 200,
  "message": "历史已清空"
}
```

---

## ❌ 错误处理

### 通用错误格式

```json
{
  "code": 400,
  "message": "错误描述",
  "errors": {
    "field_name": ["错误详情"]
  }
}
```

### HTTP 状态码

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证（Token 无效或缺失） |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 频率限制 |
| 500 | 服务器内部错误 |

### 常见错误

#### 1. 认证失败 (401)

```json
{
  "detail": "未提供身份验证凭据"
}
```

**解决**: 在请求头中添加 `Authorization: jwt <token>`

---

#### 2. 权限不足 (403)

```json
{
  "detail": "您没有执行此操作的权限"
}
```

**解决**: 检查用户角色和权限

---

#### 3. 频率限制 (429)

```json
{
  "code": 429,
  "message": "请求过于频繁，请稍后再试"
}
```

**解决**: 等待 60 秒后重试

---

#### 4. 资源不存在 (404)

```json
{
  "code": 404,
  "message": "题目不存在"
}
```

---

## 📝 示例代码

### Python 示例

```python
import requests

# 登录获取 Token
response = requests.post('http://localhost:8000/auth/login/', json={
    'username': 'admin',
    'password': 'password'
})
token = response.json()['token']

# 设置认证头
headers = {
    'Authorization': f'jwt {token}',
    'Content-Type': 'application/json'
}

# 获取题目列表
response = requests.get('http://localhost:8000/api/problems/', headers=headers)
print(response.json())

# 提交代码
response = requests.post('http://localhost:8000/api/submissions/submit/', 
    headers=headers,
    json={
        'problem_id': 'A001',
        'language': 'cpp',
        'code': '#include <iostream>\n...'
    }
)
print(response.json())
```

### JavaScript 示例

```javascript
// 登录
const loginResponse = await fetch('http://localhost:8000/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'password'
  })
});
const { token } = await loginResponse.json();

// 获取题目列表
const problemsResponse = await fetch('http://localhost:8000/api/problems/', {
  headers: {
    'Authorization': `jwt ${token}`
  }
});
const problems = await problemsResponse.json();

// 提交代码
const submitResponse = await fetch('http://localhost:8000/api/submissions/submit/', {
  method: 'POST',
  headers: {
    'Authorization': `jwt ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    problem_id: 'A001',
    language: 'cpp',
    code: '#include <iostream>\n...'
  })
});
const result = await submitResponse.json();
```

---

## 🔗 相关文档

- [快速开始](01-GETTING_STARTED.md)
- [系统架构](02-ARCHITECTURE.md)
- [部署指南](03-DEPLOYMENT.md)
- [开发指南](05-DEVELOPMENT.md)

---

<div align="center">

**返回导航** → [README](README.md)

</div>
