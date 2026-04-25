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

### 1. 用户注册

**端点**: `POST /api/register/`

**请求体**:
```json
{
  "username": "new_user",
  "password": "secure_password",
  "email": "user@example.com",
  "realname": "张三",
  "telephone": "13800138000"
}
```

**响应** (201):
```json
{
  "code": 201,
  "message": "注册成功",
  "data": {
    "uid": "abc123",
    "username": "new_user",
    "email": "user@example.com"
  }
}
```

---

### 2. 用户登录

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

### 3. 获取用户信息

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

### 4. 更新用户信息

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

### 5. 修改密码

**端点**: `POST /api/password/change/`

**认证**: 需要 JWT Token

**请求体**:
```json
{
  "old_password": "old_password",
  "new_password": "new_secure_password"
}
```

**响应** (200):
```json
{
  "code": 200,
  "message": "密码修改成功"
}
```

**错误响应**:
- `400 Bad Request` - 旧密码错误

---

### 6. 重置密码

**端点**: `POST /api/password/reset/`

**请求体**:
```json
{
  "email": "user@example.com"
}
```

**响应** (200):
```json
{
  "code": 200,
  "message": "重置密码邮件已发送"
}
```

**说明**: 系统会向指定邮箱发送密码重置链接。

---

### 7. 获取班级列表

**端点**: `GET /api/classes/`

**认证**: 需要 JWT Token

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| page | int | 页码（默认 1） |
| page_size | int | 每页数量（默认 20） |

**响应** (200):
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "算法竞赛班",
      "coach": {
        "uid": "coach123",
        "username": "coach_zhang",
        "realname": "张老师"
      },
      "member_count": 30,
      "created_at": "2026-04-01T10:00:00"
    }
  ]
}
```

---

### 8. 获取班级详情

**端点**: `GET /api/classes/<int:class_id>/`

**认证**: 需要 JWT Token

**响应** (200):
```json
{
  "id": 1,
  "name": "算法竞赛班",
  "description": "专注于算法竞赛训练的班级",
  "coach": {
    "uid": "coach123",
    "username": "coach_zhang",
    "realname": "张老师"
  },
  "member_count": 30,
  "created_at": "2026-04-01T10:00:00"
}
```

---

### 9. 班级管理成员

**端点**: `GET/POST /api/classes/<int:class_id>/members/`

**认证**: 需要 JWT Token
**权限**: GET - 所有成员可查看；POST - 仅教练可添加

#### 9.1 获取成员列表

**请求**: `GET /api/classes/1/members/`

**响应** (200):
```json
{
  "count": 30,
  "results": [
    {
      "user": {
        "uid": "student1",
        "username": "john_doe",
        "realname": "张三"
      },
      "role": "student",
      "joined_at": "2026-04-01T10:00:00"
    }
  ]
}
```

#### 9.2 添加成员

**请求**: `POST /api/classes/1/members/`

**请求体**:
```json
{
  "user_id": "student_uid",
  "role": "student"  // student 或 coach
}
```

**响应** (201):
```json
{
  "code": 201,
  "message": "成员添加成功"
}
```

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

### 4. 创建标签

**端点**: `POST /api/problems/tags/create/`

**认证**: 需要管理员权限

**请求体**:
```json
{
  "name": "动态规划",
  "slug": "dp"
}
```

**响应** (201):
```json
{
  "code": 201,
  "message": "创建成功",
  "data": {
    "name": "动态规划",
    "slug": "dp",
    "problem_count": 0
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

### 7. 获取测试用例列表

**端点**: `GET /api/problems/<str:problem_id>/testcases/`

**认证**: 需要 JWT Token

**响应** (200):
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "input_file": "1.in",
      "output_file": "1.out",
      "is_sample": true,
      "created_at": "2026-04-16T10:00:00"
    }
  ]
}
```

---

### 8. 上传测试用例

**端点**: `POST /api/problems/<str:problem_id>/testcases/upload/`

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

### 9. 删除测试用例

**端点**: `DELETE /api/problems/<str:problem_id>/testcases/delete/`

**认证**: 需要管理员权限

**请求体**:
```json
{
  "testcase_ids": [1, 2, 3]
}
```

**响应** (200):
```json
{
  "code": 200,
  "message": "删除成功",
  "data": {
    "deleted_count": 3
  }
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
  "use_rag": true,  // 是否使用 RAG 模式，默认 true
  "top_k": 5        // 检索文档数量，默认 5
}
```

**响应** (200):
```json
{
  "answer": "动态规划是一种算法设计技术...",
  "sources": [
    {
      "id": "kb_abc123",
      "title": "动态规划入门",
      "type": "algorithm",
      "similarity": 0.95
    }
  ],
  "tokens_used": 150,
  "remaining_quota": 49,
  "chat_id": 1
}
```

**配额限制**:
- 每日限额：50 次
- 频率限制：60秒内最多 10 次

---

### 2. 获取对话历史列表

**端点**: `GET /api/ai/history/?limit=50&offset=0`

**认证**: 需要 JWT Token

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `limit` | int | 每页数量（默认 50） |
| `offset` | int | 偏移量（默认 0） |

**响应** (200):
```json
{
  "count": 30,
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

### 3. 获取单条对话详情

**端点**: `GET /api/ai/history/<int:chat_id>/`

**认证**: 需要 JWT Token

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `chat_id` | int | 聊天记录 ID |

**响应** (200):
```json
{
  "id": 1,
  "question": "什么是动态规划？",
  "answer": "动态规划是一种算法设计技术...",
  "sources": [
    {
      "id": "kb_abc123",
      "title": "动态规划基础",
      "type": "algorithm",
      "similarity": 0.95
    }
  ],
  "created_at": "2026-04-23T18:59:14.240903",
  "tokens_used": 1751
}
```

**错误响应**:
- `404 Not Found` - 聊天记录不存在或无权访问

---

### 4. 清空对话历史

**端点**: `DELETE /api/ai/history/clear/`

**认证**: 需要 JWT Token

**响应** (200):
```json
{
  "message": "已清空 30 条对话记录"
}
```

---

### 5. 使用情况统计

**端点**: `GET /api/ai/usage/`

**认证**: 需要 JWT Token

**响应** (200):
```json
{
  "daily_quota": 50,
  "used_today": 5,
  "remaining": 45,
  "max_history": 100,
  "history_count": 30,
  "reset_time": "明天 00:00"
}
```

---

### 6. 知识库管理

#### 6.1 获取知识库列表

**端点**: `GET /api/ai/knowledge/?page=1&page_size=20&doc_type=algorithm`

**认证**: 需要 JWT Token

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码（默认 1） |
| `page_size` | int | 每页数量（默认 20） |
| `doc_type` | string | 按类型过滤 |
| `error_type` | string | 按错误类型过滤 |
| `is_active` | boolean | 按激活状态过滤 |

**响应** (200):
```json
{
  "count": 7,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 1,
      "title": "动态规划基础教程",
      "content": "动态规划是一种算法思想...",
      "doc_type": "algorithm",
      "tags": [1, 2, 3],
      "problem": null,
      "error_type": "",
      "source": "",
      "vector_id": "kb_1776971398541",
      "is_active": true,
      "created_at": "2026-04-23T19:09:58.541541",
      "updated_at": "2026-04-23T19:09:58.541566"
    }
  ]
}
```

---

#### 6.2 创建知识库文档

**端点**: `POST /api/ai/knowledge/`

**认证**: 需要 JWT Token
**权限**: 仅教练或管理员

**请求体**:
```json
{
  "title": "动态规划基础教程",
  "content": "动态规划是一种算法思想，用于解决具有最优子结构和重叠子问题性质的问题。",
  "doc_type": "algorithm",
  "tag_names": ["DP", "算法", "动态规划"],
  "problem": null,
  "error_type": "",
  "source": "",
  "is_active": true
}
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 文档标题 |
| content | string | 是 | 文档内容（支持 Markdown） |
| doc_type | string | 是 | 文档类型：algorithm/solution/template/concept/error_solution |
| tag_names | array | 否 | 标签名称列表 |
| problem | integer | 否 | 关联的题目 ID |
| error_type | string | 否 | 错误类型（WA/TLE/MLE/RE/CE） |
| source | string | 否 | 来源说明 |
| is_active | boolean | 否 | 是否启用，默认 true |

**响应** (201):
```json
{
  "message": "知识库文档创建成功",
  "data": {
    "id": 1,
    "title": "动态规划基础教程",
    "content": "动态规划是一种算法思想...",
    "doc_type": "algorithm",
    "tags": [1, 2, 3],
    "vector_id": "kb_1776971398541",
    "is_active": true,
    "created_at": "2026-04-23T19:09:58.541541",
    "updated_at": "2026-04-23T19:09:58.541566"
  }
}
```

**注意**: 创建成功后会自动同步到向量数据库。

---

#### 6.3 获取知识库详情

**端点**: `GET /api/ai/knowledge/<int:kb_id>/`

**认证**: 需要 JWT Token

**响应** (200): 同创建接口的 data 字段

---

#### 6.4 更新知识库文档

**端点**: `PUT /api/ai/knowledge/<int:kb_id>/`

**认证**: 需要 JWT Token
**权限**: 仅教练或管理员

**请求体** (部分更新):
```json
{
  "title": "动态规划基础教程（已更新）",
  "tag_names": ["DP", "算法", "动态规划", "进阶"]
}
```

**响应** (200):
```json
{
  "message": "知识库文档更新成功",
  "data": {
    "id": 1,
    "title": "动态规划基础教程（已更新）",
    ...
  }
}
```

**注意**: 更新成功后会自动同步到向量数据库。

---

#### 6.5 删除知识库文档

**端点**: `DELETE /api/ai/knowledge/<int:kb_id>/`

**认证**: 需要 JWT Token
**权限**: 仅教练或管理员

**响应** (200):
```json
{
  "message": "知识库文档删除成功"
}
```

**注意**: 删除成功后会自动从向量数据库中删除。

---

### 7. 学情分析报告

#### 7.1 学生个性化学情报告

**端点**: `GET /api/ai/report/student/?days=7`

**认证**: 需要 JWT Token
**权限**: 仅学生可查看自己的报告

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| days | int | 统计天数（默认 7） |

**响应** (200):
```json
{
  "report_type": "学生个性报告",
  "period": "2026-04-16 至 2026-04-23",
  "summary": "本周你完成了 15 道题目，正确率 73%...",
  "statistics": {
    "total_submissions": 20,
    "accepted_count": 15,
    "acceptance_rate": 0.75,
    "problem_solved": 12,
    "error_distribution": {
      "WA": 3,
      "TLE": 1,
      "RE": 1
    }
  },
  "recommendations": [
    "建议加强动态规划练习",
    "注意边界条件处理"
  ],
  "generated_at": "2026-04-23T19:00:00"
}
```

**错误响应**:
- `403 Forbidden` - 非学生用户无权访问

---

#### 7.2 班级共性学情报告

**端点**: `GET /api/ai/report/class/<int:class_id>/?days=7`

**认证**: 需要 JWT Token
**权限**: 仅该班级的教练或管理员

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| class_id | int | 班级 ID |

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| days | int | 统计天数（默认 7） |

**响应** (200):
```json
{
  "report_type": "班级共性报告",
  "class_name": "算法竞赛班",
  "period": "2026-04-16 至 2026-04-23",
  "summary": "本周班级整体表现良好，平均正确率 68%...",
  "statistics": {
    "total_students": 30,
    "active_students": 25,
    "total_submissions": 450,
    "acceptance_rate": 0.68,
    "common_errors": [
      {
        "error_type": "WA",
        "count": 80,
        "percentage": 0.40
      }
    ]
  },
  "recommendations": [
    "建议组织动态规划专题讲解",
    "重点关注时间复杂度优化"
  ],
  "generated_at": "2026-04-23T19:00:00"
}
```

**错误响应**:
- `403 Forbidden` - 无权查看此班级报告
- `404 Not Found` - 班级不存在

---

### 8. 错误解决方案

**端点**: `GET /api/ai/error-solution/<int:submission_id>/`

**认证**: 需要 JWT Token

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| submission_id | int | 提交记录 ID |

**功能说明**: 当学生提交代码判题失败时，系统自动根据错误类型从知识库中检索相关解决方案。

**限流说明**: 
- ⚠️ **与 AI 智能问答共用每日配额**（50 次/天）
- 每次调用消耗 1 次配额，但不消耗 LLM token
- 频率限制：60秒内最多 10 次

**响应** (200):
```json
{
  "submission_id": 123,
  "solutions": [
    {
      "title": "WA（答案错误）常见原因",
      "content": "WA 的常见原因包括：1. 边界条件处理不当...",
      "doc_type": "error_solution",
      "relevance_score": 0.85
    }
  ],
  "count": 1,
  "remaining_quota": 49
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| submission_id | int | 提交记录 ID |
| solutions | array | 解决方案列表（最多 3 个） |
| count | int | 解决方案数量 |
| remaining_quota | int | ⭐ 剩余配额次数 |

**错误响应** (429 - 配额超限):
```json
{
  "error": "今日配额已用完 (50/50)",
  "remaining": 0,
  "reset_time": "明天 00:00"
}
```

**使用场景**: 学生提交后收到 WA/TLE 等错误时，调用此接口获取针对性的解决方案。

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

```
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

```
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
