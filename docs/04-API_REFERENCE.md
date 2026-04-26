# ZJOJ API 参考文档

> **版本**: v1.2.0  
> **Base URL**: `/api/`  
> **认证方式**: JWT Bearer Token  
> **数据格式**: JSON

---

## 📋 目录

- [认证机制](#认证机制)
- [用户认证模块](#用户认证模块)
- [班级管理模块](#班级管理模块)
- [题目管理模块](#题目管理模块)
- [测试用例管理](#测试用例管理)
- [代码提交与评测](#代码提交与评测)
- [AI 助手模块](#ai-助手模块)
- [错误码说明](#错误码说明)
- [使用示例](#使用示例)

---

## 🔐 认证机制

### JWT Token 认证

所有需要认证的接口必须在请求头中携带 JWT Token。

**请求头格式**:
```
Authorization: Bearer <token>
```

或（兼容旧格式）:
```
Authorization: jwt <token>
```

**Token 获取**: 通过登录接口 `/api/login/` 获取  
**Token 有效期**: 14 天  
**Token 算法**: HS256

**Token Payload 结构**:
```json
{
  "userid": "用户UID",
  "exp": 过期时间戳
}
```

---

## 👤 用户认证模块

### 1. 用户登录

**接口**: `POST /api/login/`  
**认证**: 无需认证  
**描述**: 用户登录并获取 JWT Token

**请求体**:
```json
{
  "username": "coach",
  "password": "coach123"
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，2-20字符 |
| password | string | 是 | 密码，6-20字符 |

**成功响应** (200):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "uid": "RD96qaV3qss6SU67GrHP3s",
    "username": "coach",
    "email": "coach@zjoj.com",
    "realname": "Coach",
    "telephone": "13800000001",
    "role": 2,
    "is_staff": true,
    "status": 2,
    "avatar": "",
    "bio": "",
    "is_active": true,
    "date_joined": "2026-04-26T06:53:15.116262",
    "last_login": "2026-04-26T06:55:30.057898"
  }
}
```

**错误响应** (400):
```json
{
  "detail": "用户名不存在",
  "errors": {
    "username": ["用户名不存在"]
  }
}
```

**可能的错误**:
- `用户名不存在` - 用户名未注册
- `密码错误` - 密码不正确
- `用户已锁定` - 账户已被锁定
- `请传入用户名以及密码` - 参数缺失

---

### 2. 用户注册

**接口**: `POST /api/register/`  
**认证**: 无需认证  
**描述**: 新用户注册

**请求体**:
```json
{
  "username": "student01",
  "email": "student@example.com",
  "telephone": "13800001001",
  "realname": "张三",
  "password": "password123",
  "password_confirm": "password123",
  "role": 1
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，2-20字符，必须唯一 |
| email | string | 是 | 邮箱地址，必须唯一 |
| telephone | string | 是 | 手机号，必须唯一 |
| realname | string | 是 | 真实姓名 |
| password | string | 是 | 密码，6-20字符 |
| password_confirm | string | 是 | 确认密码，必须与password一致 |
| role | integer | 否 | 角色：1=学生，2=教练，默认为1 |

**成功响应** (201):
```json
{
  "code": 201,
  "message": "注册成功",
  "data": {
    "uid": "RD96qaV3qss6SU67GrHP3s",
    "username": "student01",
    "email": "student@example.com",
    "role": "学生"
  }
}
```

**错误响应** (400):
```json
{
  "code": 400,
  "message": "注册失败",
  "errors": {
    "username": ["用户名已存在"],
    "email": ["邮箱已被注册"],
    "telephone": ["手机号已被注册"],
    "password_confirm": ["两次密码不一致"]
  }
}
```

---

### 3. 获取用户信息

**接口**: `GET /api/user/profile/`  
**认证**: 需要认证  
**描述**: 获取当前登录用户的详细信息

**响应** (200):
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "uid": "RD96qaV3qss6SU67GrHP3s",
    "username": "coach",
    "email": "coach@zjoj.com",
    "telephone": "13800000001",
    "realname": "Coach",
    "role": 2,
    "role_name": "教练",
    "status": 2,
    "status_name": "正常",
    "avatar": "",
    "bio": "",
    "date_joined": "2026-04-26T06:53:15.116262"
  }
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| uid | string | 用户唯一标识（短UUID） |
| username | string | 用户名 |
| email | string | 邮箱 |
| telephone | string | 手机号 |
| realname | string | 真实姓名 |
| role | integer | 角色ID：1=学生，2=教练 |
| role_name | string | 角色名称 |
| status | integer | 状态ID |
| status_name | string | 状态名称 |
| avatar | string | 头像URL |
| bio | string | 个人简介 |
| date_joined | datetime | 注册时间 |

---

### 4. 更新用户信息

**接口**: `PUT /api/user/profile/`  
**认证**: 需要认证  
**描述**: 更新当前用户的信息

**请求体** (所有字段可选):
```json
{
  "realname": "李四",
  "telephone": "13800001002",
  "avatar": "https://example.com/avatar.jpg",
  "bio": "热爱编程的学生"
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| realname | string | 否 | 真实姓名 |
| telephone | string | 否 | 手机号 |
| avatar | string | 否 | 头像URL |
| bio | string | 否 | 个人简介 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "uid": "RD96qaV3qss6SU67GrHP3s",
    "username": "coach",
    "email": "coach@zjoj.com",
    "telephone": "13800001002",
    "realname": "李四",
    "role": 2,
    "role_name": "教练",
    "status": 2,
    "status_name": "正常",
    "avatar": "https://example.com/avatar.jpg",
    "bio": "热爱编程的学生",
    "date_joined": "2026-04-26T06:53:15.116262"
  }
}
```

**注意**: uid、username、email、date_joined 字段不可修改

---

### 5. 修改密码

**接口**: `POST /api/password/change/`  
**认证**: 需要认证  
**描述**: 修改当前用户密码

**请求体**:
```json
{
  "old_password": "oldpass123",
  "new_password": "newpass456"
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 原密码 |
| new_password | string | 是 | 新密码，6-20字符 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "密码修改成功"
}
```

**错误响应**:
```json
{
  "code": 400,
  "message": "原密码错误"
}
```

**可能的错误**:
- `请提供原密码和新密码` - 参数缺失
- `原密码错误` - 原密码不正确
- `新密码长度必须在6-20字符之间` - 新密码长度不符合要求

---

### 6. 重置密码

**接口**: `POST /api/password/reset/`  
**认证**: 无需认证  
**描述**: 发送密码重置邮件（功能待实现）

**请求体**:
```json
{
  "email": "user@example.com"
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 是 | 注册邮箱 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "如果该邮箱已注册，重置链接将发送到您的邮箱"
}
```

**注意**: 
- 为防止邮箱枚举攻击，无论邮箱是否存在都返回相同消息
- 当前为占位实现，邮件发送功能待开发

---

## 🏫 班级管理模块

### 7. 获取班级列表

**接口**: `GET /api/classes/`  
**认证**: 需要认证  
**描述**: 获取用户相关的班级列表

**权限说明**:
- 教练/管理员：返回自己管理的班级
- 学生：返回自己加入的班级

**响应** (200):
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "高一竞赛班",
      "coach": "李老师",
      "description": "信息学竞赛培训",
      "member_count": 30,
      "create_time": "2026-04-24T00:00:00Z"
    },
    {
      "id": 2,
      "name": "高二提高班",
      "coach": "王老师",
      "description": "算法提高训练",
      "member_count": 25,
      "create_time": "2026-04-25T00:00:00Z"
    }
  ]
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 班级ID |
| name | string | 班级名称 |
| coach | string | 教练用户名 |
| description | string | 班级描述 |
| member_count | integer | 成员数量 |
| create_time | datetime | 创建时间 |

---

### 8. 创建班级

**接口**: `POST /api/classes/`  
**认证**: 需要认证（仅教练/管理员）  
**描述**: 创建新班级

**请求体**:
```json
{
  "name": "高一竞赛班",
  "description": "信息学竞赛培训"
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 班级名称，不能为空 |
| description | string | 否 | 班级描述，默认为空 |

**成功响应** (201):
```json
{
  "code": 201,
  "message": "班级创建成功",
  "data": {
    "id": 1,
    "name": "高一竞赛班"
  }
}
```

**错误响应**:
```json
{
  "code": 403,
  "message": "只有教练可以创建班级"
}
```

**可能的错误**:
- `只有教练可以创建班级` - 权限不足
- `班级名称不能为空` - name字段为空
- `该班级已存在` - 班级名称已存在

---

### 9. 获取班级详情

**接口**: `GET /api/classes/{class_id}/`  
**认证**: 需要认证  
**描述**: 获取指定班级的详细信息和成员列表

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| class_id | integer | 班级ID |

**权限说明**: 只有班主任、班级成员或管理员可以查看

**响应** (200):
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "name": "高一竞赛班",
    "coach": "李老师",
    "description": "信息学竞赛培训",
    "create_time": "2026-04-24T00:00:00Z",
    "members": [
      {
        "uid": "RD96qaV3qss6SU67GrHP3s",
        "username": "student01",
        "realname": "张三",
        "join_time": "2026-04-24T10:00:00Z"
      },
      {
        "uid": "abc123def456",
        "username": "student02",
        "realname": "李四",
        "join_time": "2026-04-24T11:00:00Z"
      }
    ]
  }
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 班级ID |
| name | string | 班级名称 |
| coach | string | 教练用户名 |
| description | string | 班级描述 |
| create_time | datetime | 创建时间 |
| members | array | 成员列表 |
| members[].uid | string | 用户UID |
| members[].username | string | 用户名 |
| members[].realname | string | 真实姓名 |
| members[].join_time | datetime | 加入时间 |

**错误响应**:
```json
{
  "code": 404,
  "message": "班级不存在"
}
```

---

### 10. 添加班级成员

**接口**: `POST /api/classes/{class_id}/members/`  
**认证**: 需要认证（仅班主任/管理员）  
**描述**: 将学生添加到班级

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| class_id | integer | 班级ID |

**请求体**:
```json
{
  "username": "student01"
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 要添加的学生用户名 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "添加成功"
}
```

**错误响应**:
```json
{
  "code": 403,
  "message": "只有班主任可以添加成员"
}
```

**可能的错误**:
- `只有班主任可以添加成员` - 权限不足
- `班级不存在` - 班级ID无效
- `请提供用户名` - username字段为空
- `用户不存在` - 用户名不存在
- `只能添加学生` - 目标用户不是学生角色
- `该学生已在班级中` - 重复添加

---

### 11. 移除班级成员

**接口**: `DELETE /api/classes/{class_id}/members/`  
**认证**: 需要认证（仅班主任/管理员）  
**描述**: 从班级中移除学生

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| class_id | integer | 班级ID |

**请求体**:
```json
{
  "username": "student01"
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 要移除的学生用户名 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "移除成功"
}
```

**错误响应**:
```json
{
  "code": 403,
  "message": "只有班主任可以移除成员"
}
```

**可能的错误**:
- `只有班主任可以移除成员` - 权限不足
- `班级不存在` - 班级ID无效
- `请提供用户名` - username字段为空
- `用户不存在` - 用户名不存在
- `该学生不在班级中` - 学生不属于该班级

---

## 📝 题目管理模块

### 12. 获取题目列表

**接口**: `GET /api/problems/`  
**认证**: 需要认证  
**描述**: 获取题目列表，支持搜索和过滤

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 否 | 按标题搜索（模糊匹配） |
| tag_id | integer | 否 | 按标签ID过滤 |
| creator | string | 否 | 按创建者用户名过滤 |
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20 |

**响应** (200):
```json
{
  "count": 100,
  "next": "http://example.com/api/problems/?page=2",
  "previous": null,
  "results": [
    {
      "problem_id": "A001",
      "title": "A+B Problem",
      "time_limit": 1000,
      "memory_limit": 256,
      "tags": [
        {"id": 1, "name": "入门"},
        {"id": 2, "name": "模拟"}
      ],
      "upload_time": "2026-04-20T10:00:00Z",
      "update_time": "2026-04-20T10:00:00Z",
      "creator_name": "coach"
    }
  ]
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| problem_id | string | 题目编号 |
| title | string | 题目标题 |
| time_limit | integer | 时间限制（毫秒） |
| memory_limit | integer | 内存限制（MB） |
| tags | array | 标签列表 |
| upload_time | datetime | 上传时间 |
| update_time | datetime | 更新时间 |
| creator_name | string | 创建者用户名 |

---

### 13. 创建题目

**接口**: `POST /api/problems/create/`  
**认证**: 需要认证  
**描述**: 创建新题目

**请求体**:
```json
{
  "problem_id": "A001",
  "title": "A+B Problem",
  "description": "计算两个整数的和",
  "time_limit": 1000,
  "memory_limit": 256,
  "tag_ids": [1, 2]
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| problem_id | string | 是 | 题目编号，必须唯一 |
| title | string | 是 | 题目标题 |
| description | string | 是 | 题目描述 |
| time_limit | integer | 是 | 时间限制（毫秒），必须>0 |
| memory_limit | integer | 是 | 内存限制（MB），必须>0 |
| tag_ids | array | 否 | 标签ID列表 |

**成功响应** (201):
```json
{
  "message": "题目创建成功",
  "data": {
    "problem_id": "A001",
    "title": "A+B Problem",
    "description": "计算两个整数的和",
    "time_limit": 1000,
    "memory_limit": 256,
    "tags": [
      {"id": 1, "name": "入门"},
      {"id": 2, "name": "模拟"}
    ],
    "upload_time": "2026-04-26T06:00:00Z",
    "update_time": "2026-04-26T06:00:00Z",
    "creator_name": "coach"
  }
}
```

**错误响应**:
```json
{
  "message": "创建失败",
  "errors": {
    "problem_id": ["该题目编号已存在"],
    "time_limit": ["时间限制必须大于0"],
    "memory_limit": ["内存限制必须大于0"],
    "tag_ids": ["部分标签不存在"]
  }
}
```

---

### 14. 获取题目详情

**接口**: `GET /api/problems/{problem_id}/`  
**认证**: 需要认证  
**描述**: 获取指定题目的详细信息

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| problem_id | string | 题目编号 |

**响应** (200):
```json
{
  "problem_id": "A001",
  "title": "A+B Problem",
  "description": "计算两个整数的和\n\n输入两个整数a和b，输出它们的和。",
  "time_limit": 1000,
  "memory_limit": 256,
  "tags": [
    {"id": 1, "name": "入门"},
    {"id": 2, "name": "模拟"}
  ],
  "upload_time": "2026-04-20T10:00:00Z",
  "update_time": "2026-04-20T10:00:00Z",
  "creator_name": "coach"
}
```

**注意**: 此接口不包含测试用例内容

---

### 15. 更新题目（完整更新）

**接口**: `PUT /api/problems/{problem_id}/`  
**认证**: 需要认证（仅创建者）  
**描述**: 完整更新题目信息

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| problem_id | string | 题目编号 |

**请求体**: 需要提供所有字段（同创建题目）

**权限**: 只有题目创建者可以修改

**成功响应** (200):
```json
{
  "message": "题目更新成功",
  "data": {
    "problem_id": "A001",
    "title": "A+B Problem (Updated)",
    ...
  }
}
```

**错误响应**:
```json
{
  "message": "无权限修改此题目"
}
```

---

### 16. 更新题目（部分更新）

**接口**: `PATCH /api/problems/{problem_id}/`  
**认证**: 需要认证（仅创建者）  
**描述**: 部分更新题目信息

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| problem_id | string | 题目编号 |

**请求体**: 只需提供要更新的字段

**示例**:
```json
{
  "title": "新标题",
  "time_limit": 2000
}
```

---

### 17. 删除题目

**接口**: `DELETE /api/problems/{problem_id}/`  
**认证**: 需要认证（仅创建者）  
**描述**: 删除题目

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| problem_id | string | 题目编号 |

**成功响应** (204):
```json
{
  "message": "题目删除成功"
}
```

**注意**: 删除题目会同时删除相关的测试用例和提交记录

---

### 18. 获取标签列表

**接口**: `GET /api/problems/tags/`  
**认证**: 需要认证  
**描述**: 获取所有标签

**响应** (200):
```json
[
  {"id": 1, "name": "入门"},
  {"id": 2, "name": "模拟"},
  {"id": 3, "name": "动态规划"},
  {"id": 4, "name": "图论"},
  {"id": 5, "name": "数据结构"}
]
```

---

### 19. 创建标签

**接口**: `POST /api/problems/tags/create/`  
**认证**: 需要认证  
**描述**: 创建新标签

**请求体**:
```json
{
  "name": "贪心算法"
}
```

**成功响应** (201):
```json
{
  "message": "标签创建成功",
  "data": {
    "id": 6,
    "name": "贪心算法"
  }
}
```

**错误响应**:
```json
{
  "message": "该标签已存在"
}
```

---

## 🧪 测试用例管理

### 20. 上传测试用例

**接口**: `POST /api/problems/{problem_id}/testcases/upload/`  
**认证**: 需要认证（仅教练/管理员）  
**描述**: 上传题目测试用例（Hydro格式ZIP文件）

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| problem_id | string | 题目编号 |

**Content-Type**: `multipart/form-data`

**表单数据**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | ZIP格式的测试用例文件 |

**ZIP文件结构** (Hydro格式):
```
testcases.zip
├── problem.yaml          # 题目配置文件
└── testdata/
    ├── 1.in              # 测试点1输入
    ├── 1.out             # 测试点1输出
    ├── 2.in
    ├── 2.out
    └── ...
```

**problem.yaml 示例**:
```yaml
name: A+B Problem
time_limit: 1000
memory_limit: 256
testcases:
  - input: 1.in
    output: 1.out
  - input: 2.in
    output: 2.out
```

**成功响应** (200):
```json
{
  "message": "测试用例上传成功",
  "count": 10
}
```

**处理流程**:
1. 验证ZIP文件格式
2. 解压并验证文件结构
3. 自动转换为系统内部格式
4. 保存到文件系统
5. 更新数据库记录

**错误响应**:
```json
{
  "message": "上传失败",
  "error": "无效的ZIP文件格式"
}
```

---

### 21. 获取测试用例列表

**接口**: `GET /api/problems/{problem_id}/testcases/`  
**认证**: 需要认证  
**描述**: 获取题目的测试用例列表

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| problem_id | string | 题目编号 |

**响应** (200):
```json
{
  "count": 10,
  "testcases": [
    {
      "id": 1,
      "name": "1.in",
      "size": 1024,
      "upload_time": "2026-04-24T10:00:00Z"
    },
    {
      "id": 2,
      "name": "2.in",
      "size": 2048,
      "upload_time": "2026-04-24T10:00:00Z"
    }
  ]
}
```

**注意**: 出于安全考虑，不返回测试用例的实际内容

---

### 22. 删除测试用例

**接口**: `DELETE /api/problems/{problem_id}/testcases/delete/`  
**认证**: 需要认证（仅教练/管理员）  
**描述**: 批量删除测试用例

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| problem_id | string | 题目编号 |

**请求体**:
```json
{
  "testcase_ids": [1, 2, 3]
}
```

**成功响应** (200):
```json
{
  "message": "删除成功",
  "deleted_count": 3
}
```

---

## 💻 代码提交与评测

### 23. 提交代码

**接口**: `POST /api/submissions/submit/`  
**认证**: 需要认证  
**描述**: 提交代码进行自动评测

**请求体**:
```json
{
  "problem_id": "A001",
  "language": "cpp",
  "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}"
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| problem_id | string | 是 | 题目编号 |
| language | string | 是 | 编程语言 |
| code | string | 是 | 代码内容 |

**支持的编程语言**:
| 语言标识 | 说明 |
|----------|------|
| cpp | C++ |
| c | C |
| java | Java |
| python3 | Python 3 |
| python2 | Python 2 |

**代码限制**:
- 最大长度: 64KB (65536字节)
- 不能为空

**成功响应** (201):
```json
{
  "message": "提交成功，正在评测",
  "submission_id": 24,
  "status": "等待评测"
}
```

**评测流程**:
1. 验证提交参数
2. 创建提交记录（状态：等待评测）
3. 异步调用评测任务（Celery）
4. go-judge 执行代码评测
5. 更新提交结果

**错误响应**:
```json
{
  "message": "提交失败",
  "errors": {
    "problem": ["题目不存在"],
    "language": ["不支持的编程语言: xxx"],
    "code": ["代码不能为空"]
  }
}
```

---

### 24. 获取提交列表

**接口**: `GET /api/submissions/`  
**认证**: 需要认证  
**描述**: 获取提交记录列表

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| problem_id | string | 否 | 按题目编号过滤 |
| user_id | integer | 否 | 按用户ID过滤 |
| result | string | 否 | 按评测结果过滤 |
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20 |

**权限说明**:
- 普通用户：只能查看自己的提交
- 管理员/教练：可以查看所有提交

**评测结果类型**:
| 结果 | 说明 |
|------|------|
| AC | Accepted - 答案正确 |
| WA | Wrong Answer - 答案错误 |
| TLE | Time Limit Exceeded - 超时 |
| MLE | Memory Limit Exceeded - 超内存 |
| RE | Runtime Error - 运行错误 |
| CE | Compilation Error - 编译错误 |
| PENDING | Pending - 等待评测 |

**响应** (200):
```json
{
  "count": 50,
  "next": "http://example.com/api/submissions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 24,
      "problem_id": "A001",
      "problem_title": "A+B Problem",
      "username": "student01",
      "language": "cpp",
      "language_display": "C++",
      "status": 1,
      "status_display": "已评测",
      "result": "AC",
      "result_display": "答案正确",
      "score": 100,
      "execution_time": 12,
      "memory_usage": 3200,
      "submit_time": "2026-04-26T06:27:28Z"
    }
  ]
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 提交ID |
| problem_id | string | 题目编号 |
| problem_title | string | 题目标题 |
| username | string | 提交者用户名 |
| language | string | 编程语言标识 |
| language_display | string | 编程语言显示名称 |
| status | integer | 状态ID |
| status_display | string | 状态显示名称 |
| result | string | 评测结果 |
| result_display | string | 评测结果显示名称 |
| score | integer | 得分（0-100） |
| execution_time | integer | 执行时间（毫秒） |
| memory_usage | integer | 内存使用（KB） |
| submit_time | datetime | 提交时间 |

---

### 25. 获取提交详情

**接口**: `GET /api/submissions/{submission_id}/`  
**认证**: 需要认证  
**描述**: 获取指定提交的详细信息（包含代码和测试点结果）

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| submission_id | integer | 提交ID |

**权限说明**:
- 普通用户：只能查看自己的提交
- 管理员/教练：可以查看所有提交

**响应** (200):
```json
{
  "id": 24,
  "problem_id": "A001",
  "problem_title": "A+B Problem",
  "username": "student01",
  "language": "cpp",
  "language_display": "C++",
  "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}",
  "code_length": 128,
  "status": 1,
  "status_display": "已评测",
  "result": "AC",
  "result_display": "答案正确",
  "score": 100,
  "execution_time": 12,
  "memory_usage": 3200,
  "submit_time": "2026-04-26T06:27:28Z",
  "judge_time": "2026-04-26T06:27:29Z",
  "test_case_results": [
    {
      "test_case_id": 1,
      "status": "AC",
      "execution_time": 5,
      "memory_usage": 3100,
      "score": 10,
      "message": ""
    },
    {
      "test_case_id": 2,
      "status": "AC",
      "execution_time": 7,
      "memory_usage": 3200,
      "score": 10,
      "message": ""
    }
  ]
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 提交的代码 |
| code_length | integer | 代码长度（字节） |
| judge_time | datetime | 评测时间 |
| test_case_results | array | 测试点结果列表 |
| test_case_results[].test_case_id | integer | 测试点ID |
| test_case_results[].status | string | 测试点结果 |
| test_case_results[].execution_time | integer | 执行时间（毫秒） |
| test_case_results[].memory_usage | integer | 内存使用（KB） |
| test_case_results[].score | integer | 得分 |
| test_case_results[].message | string | 错误信息（如果有） |

**错误响应**:
```json
{
  "message": "无权限查看此提交"
}
```

---

## 🤖 AI 助手模块

### 26. AI 智能问答

**接口**: `POST /api/chat/`  
**认证**: 需要认证  
**描述**: 向AI助手提问，支持RAG增强检索

**请求体**:
```json
{
  "question": "如何实现快速排序算法？",
  "top_k": 5,
  "use_rag": true
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | 是 | 问题内容 |
| top_k | integer | 否 | 返回相关知识数量，默认5 |
| use_rag | boolean | 否 | 是否使用RAG检索，默认true |

**响应** (200):
```json
{
  "answer": "快速排序是一种高效的排序算法，采用分治策略。基本步骤：\n1. 选择一个基准元素\n2. 将数组分为两部分\n3. 递归排序两部分\n\n示例代码：\n```python\ndef quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)\n```",
  "sources": [
    {
      "doc_id": 1,
      "title": "排序算法详解",
      "similarity": 0.95,
      "content": "快速排序..."
    },
    {
      "doc_id": 5,
      "title": "算法复杂度分析",
      "similarity": 0.82,
      "content": "..."
    }
  ],
  "tokens_used": 150,
  "remaining_quota": 49,
  "chat_id": 123
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| answer | string | AI回答内容 |
| sources | array | 参考的知识库文档（仅RAG模式） |
| sources[].doc_id | integer | 文档ID |
| sources[].title | string | 文档标题 |
| sources[].similarity | float | 相似度（0-1） |
| sources[].content | string | 文档内容片段 |
| tokens_used | integer | 消耗的Token数 |
| remaining_quota | integer | 剩余每日配额 |
| chat_id | integer | 对话记录ID |

**使用限制**:
- 每日配额：50次问答
- 频率限制：防止滥用
- 配额在每天00:00重置

**错误响应** (429):
```json
{
  "error": "已达到每日使用限额"
}
```

---

### 27. 获取对话历史列表

**接口**: `GET /api/history/`  
**认证**: 需要认证  
**描述**: 获取当前用户的对话历史列表

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | integer | 否 | 返回数量，默认50 |
| offset | integer | 否 | 偏移量，默认0 |

**响应** (200):
```json
[
  {
    "id": 123,
    "question": "如何实现快速排序？",
    "answer": "快速排序是一种...",
    "created_at": "2026-04-26T06:30:00Z",
    "tokens_used": 150
  },
  {
    "id": 122,
    "question": "什么是动态规划？",
    "answer": "动态规划是一种...",
    "created_at": "2026-04-26T06:25:00Z",
    "tokens_used": 200
  }
]
```

---

### 28. 获取单条对话详情

**接口**: `GET /api/history/{chat_id}/`  
**认证**: 需要认证  
**描述**: 获取指定对话的详细信息

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| chat_id | integer | 对话ID |

**响应** (200):
```json
{
  "id": 123,
  "question": "如何实现快速排序？",
  "answer": "快速排序是一种...",
  "sources": [...],
  "created_at": "2026-04-26T06:30:00Z",
  "tokens_used": 150
}
```

**错误响应** (404):
```json
{
  "error": "聊天记录不存在或无权访问"
}
```

---

### 29. 清空对话历史

**接口**: `DELETE /api/history/clear/`  
**认证**: 需要认证  
**描述**: 清空当前用户的所有对话历史

**响应** (200):
```json
{
  "message": "已清空 25 条对话记录"
}
```

---

### 30. 获取使用情况统计

**接口**: `GET /api/usage/`  
**认证**: 需要认证  
**描述**: 获取AI助手的当前使用情况

**响应** (200):
```json
{
  "daily_quota": 50,
  "used_today": 10,
  "remaining": 40,
  "max_history": 100,
  "history_count": 25,
  "reset_time": "明天 00:00"
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| daily_quota | integer | 每日配额 |
| used_today | integer | 今日已用次数 |
| remaining | integer | 剩余次数 |
| max_history | integer | 最大历史记录数 |
| history_count | integer | 当前历史记录数 |
| reset_time | string | 配额重置时间 |

---

### 31. 获取知识库列表

**接口**: `GET /api/knowledge/`  
**认证**: 需要认证  
**描述**: 获取知识库文档列表

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| doc_type | string | 否 | 文档类型过滤 |
| error_type | string | 否 | 错误类型过滤 |
| is_active | boolean | 否 | 是否激活 |
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |

**响应** (200):
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "title": "常见编译错误及解决",
      "doc_type": "error_solution",
      "error_type": "Compilation Error",
      "content_preview": "编译错误通常由语法错误引起...",
      "is_active": true,
      "created_at": "2026-04-20T10:00:00Z"
    }
  ]
}
```

---

### 32. 获取知识库详情

**接口**: `GET /api/knowledge/{kb_id}/`  
**认证**: 需要认证  
**描述**: 获取知识库文档的完整内容

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| kb_id | integer | 文档ID |

**响应** (200):
```json
{
  "id": 1,
  "title": "常见编译错误及解决",
  "doc_type": "error_solution",
  "error_type": "Compilation Error",
  "content": "完整的文档内容...",
  "is_active": true,
  "created_at": "2026-04-20T10:00:00Z",
  "updated_at": "2026-04-20T10:00:00Z"
}
```

---

### 33. 获取学生学情报告

**接口**: `GET /api/report/student/`  
**认证**: 需要认证（仅学生）  
**描述**: 获取当前学生的个性化学情报告

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| days | integer | 否 | 统计天数，默认7 |

**权限**: 只有学生角色可以查看自己的报告

**响应** (200):
```json
{
  "report_type": "学生个性化学情报告",
  "period": "2026-04-19 至 2026-04-26",
  "summary": "本周共提交15次，AC率80%，表现优秀！",
  "statistics": {
    "total_submissions": 15,
    "accepted": 12,
    "ac_rate": 0.8,
    "avg_execution_time": 25,
    "avg_memory_usage": 3500,
    "best_score": 100,
    "worst_score": 60
  },
  "problem_stats": {
    "easy": {"total": 5, "accepted": 5},
    "medium": {"total": 7, "accepted": 5},
    "hard": {"total": 3, "accepted": 2}
  },
  "weak_points": [
    "动态规划",
    "图论算法"
  ],
  "recommendations": [
    "建议加强动态规划练习，推荐练习题：DP001, DP002",
    "注意内存优化，某些题目内存使用偏高",
    "继续保持良好状态！"
  ],
  "generated_at": "2026-04-26T06:00:00Z"
}
```

**错误响应** (403):
```json
{
  "error": "只有学生可以查看学情报告"
}
```

---

### 34. 获取班级学情报告

**接口**: `GET /api/report/class/{class_id}/`  
**认证**: 需要认证（仅教练/管理员）  
**描述**: 获取班级整体学情报告

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| class_id | integer | 班级ID |

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| days | integer | 否 | 统计天数，默认7 |

**权限**: 只有教练或管理员可以查看

**响应** (200):
```json
{
  "report_type": "班级学情报告",
  "class_name": "高一竞赛班",
  "period": "2026-04-19 至 2026-04-26",
  "summary": "班级整体表现良好，平均AC率75%",
  "statistics": {
    "total_students": 30,
    "active_students": 25,
    "total_submissions": 450,
    "avg_ac_rate": 0.75,
    "avg_score": 78
  },
  "student_rankings": [
    {
      "username": "student01",
      "realname": "张三",
      "submissions": 20,
      "ac_rate": 0.9,
      "avg_score": 92
    }
  ],
  "generated_at": "2026-04-26T06:00:00Z"
}
```

---

### 35. 获取错误解决方案

**接口**: `GET /api/error-solution/{submission_id}/`  
**认证**: 需要认证  
**描述**: 根据提交错误获取智能解决方案

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| submission_id | integer | 提交ID |

**响应** (200):
```json
{
  "submission_id": 24,
  "solutions": [
    {
      "error_type": "Runtime Error",
      "solution": "检测到运行时错误，可能原因：\n1. 数组越界访问\n2. 空指针引用\n3. 除零错误\n\n建议检查：\n- 数组边界条件\n- 指针初始化\n- 除法运算的分母",
      "related_docs": [
        {
          "id": 5,
          "title": "常见运行时错误及解决",
          "url": "/api/knowledge/5/"
        },
        {
          "id": 8,
          "title": "调试技巧指南",
          "url": "/api/knowledge/8/"
        }
      ]
    }
  ],
  "count": 1,
  "remaining_quota": 45
}
```

**功能说明**:
- 分析提交代码的错误类型
- 从知识库检索相关解决方案
- 提供针对性的修复建议
- 返回相关文档链接

---

## ⚠️ 错误码说明

### HTTP 状态码

| 状态码 | 名称 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或Token无效 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 429 | Too Many Requests | 请求频率超限 |
| 500 | Internal Server Error | 服务器内部错误 |

### 业务错误码

| code | 说明 |
|------|------|
| 200 | 操作成功 |
| 201 | 创建成功 |
| 400 | 请求失败（参数错误、验证失败等） |
| 403 | 权限不足 |
| 404 | 资源不存在 |

### 常见错误消息

| 错误消息 | 原因 | 解决方法 |
|----------|------|----------|
| 用户名不存在 | 登录时用户名未注册 | 检查用户名或先注册 |
| 密码错误 | 登录时密码不正确 | 检查密码或使用重置功能 |
| 用户已锁定 | 账户被锁定 | 联系管理员解锁 |
| 用户名已存在 | 注册时用户名重复 | 使用其他用户名 |
| 邮箱已被注册 | 注册时邮箱重复 | 使用其他邮箱或找回密码 |
| 手机号已被注册 | 注册时手机号重复 | 使用其他手机号 |
| 两次密码不一致 | 注册时密码确认不匹配 | 确保两次输入一致 |
| 只有教练可以创建班级 | 权限不足 | 使用教练账号登录 |
| 班级不存在 | 班级ID无效 | 检查班级ID |
| 题目不存在 | 题目编号无效 | 检查题目编号 |
| 无权限修改此题目 | 非题目创建者 | 使用创建者账号 |
| 不支持的编程语言 | 语言标识错误 | 使用支持的语言：cpp, c, java, python3, python2 |
| 代码不能为空 | 提交时代码为空 | 填写代码内容 |
| 代码长度不能超过64KB | 代码过长 | 精简代码 |
| 已达到每日使用限额 | AI配额用完 | 等待第二天重置 |
| 聊天记录不存在或无权访问 | 对话ID无效或不属于当前用户 | 检查对话ID |

---

## 💡 使用示例

### Python 示例

```python
import requests
import json

BASE_URL = "http://your-domain.com/api"

# ==================== 1. 登录获取Token ====================
login_response = requests.post(f"{BASE_URL}/login/", json={
    "username": "coach",
    "password": "coach123"
})

if login_response.status_code == 200:
    token = login_response.json()["token"]
    print(f"登录成功，Token: {token}")
else:
    print(f"登录失败: {login_response.json()}")
    exit(1)

# ==================== 2. 设置通用Headers ====================
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# ==================== 3. 获取用户信息 ====================
user_response = requests.get(f"{BASE_URL}/user/profile/", headers=headers)
print("用户信息:", user_response.json())

# ==================== 4. 获取题目列表 ====================
problems_response = requests.get(
    f"{BASE_URL}/problems/",
    headers=headers,
    params={"page": 1, "page_size": 10}
)
print("题目列表:", problems_response.json())

# ==================== 5. 获取题目详情 ====================
problem_response = requests.get(
    f"{BASE_URL}/problems/A001/",
    headers=headers
)
print("题目详情:", problem_response.json())

# ==================== 6. 提交代码 ====================
submit_response = requests.post(
    f"{BASE_URL}/submissions/submit/",
    headers=headers,
    json={
        "problem_id": "A001",
        "language": "cpp",
        "code": """#include <iostream>
using namespace std;
int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}"""
    }
)
print("提交结果:", submit_response.json())

if submit_response.status_code == 201:
    submission_id = submit_response.json()["submission_id"]
    
    # ==================== 7. 查询提交详情 ====================
    import time
    time.sleep(2)  # 等待评测完成
    
    detail_response = requests.get(
        f"{BASE_URL}/submissions/{submission_id}/",
        headers=headers
    )
    print("提交详情:", detail_response.json())

# ==================== 8. AI问答 ====================
chat_response = requests.post(
    f"{BASE_URL}/chat/",
    headers=headers,
    json={
        "question": "如何实现快速排序？",
        "top_k": 3,
        "use_rag": True
    }
)
print("AI回答:", chat_response.json())

# ==================== 9. 获取使用情况 ====================
usage_response = requests.get(f"{BASE_URL}/usage/", headers=headers)
print("使用情况:", usage_response.json())

# ==================== 10. 获取学情报告 ====================
report_response = requests.get(
    f"{BASE_URL}/report/student/",
    headers=headers,
    params={"days": 7}
)
print("学情报告:", report_response.json())
```

### cURL 示例

```bash
# 设置变量
BASE_URL="http://your-domain.com/api"
TOKEN="your_jwt_token_here"

# ==================== 1. 登录 ====================
curl -X POST ${BASE_URL}/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "coach",
    "password": "coach123"
  }'

# ==================== 2. 获取用户信息 ====================
curl -X GET ${BASE_URL}/user/profile/ \
  -H "Authorization: Bearer ${TOKEN}"

# ==================== 3. 获取题目列表 ====================
curl -X GET "${BASE_URL}/problems/?page=1&page_size=10" \
  -H "Authorization: Bearer ${TOKEN}"

# ==================== 4. 获取题目详情 ====================
curl -X GET ${BASE_URL}/problems/A001/ \
  -H "Authorization: Bearer ${TOKEN}"

# ==================== 5. 提交代码 ====================
curl -X POST ${BASE_URL}/submissions/submit/ \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_id": "A001",
    "language": "cpp",
    "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}"
  }'

# ==================== 6. 查询提交详情 ====================
curl -X GET ${BASE_URL}/submissions/24/ \
  -H "Authorization: Bearer ${TOKEN}"

# ==================== 7. AI问答 ====================
curl -X POST ${BASE_URL}/chat/ \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "如何实现快速排序？",
    "top_k": 3,
    "use_rag": true
  }'

# ==================== 8. 获取使用情况 ====================
curl -X GET ${BASE_URL}/usage/ \
  -H "Authorization: Bearer ${TOKEN}"

# ==================== 9. 获取班级列表 ====================
curl -X GET ${BASE_URL}/classes/ \
  -H "Authorization: Bearer ${TOKEN}"

# ==================== 10. 上传测试用例 ====================
curl -X POST ${BASE_URL}/problems/A001/testcases/upload/ \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file=@testcases.zip"
```

### JavaScript 示例

```javascript
const BASE_URL = 'http://your-domain.com/api';
let token = '';

// ==================== 1. 登录 ====================
async function login() {
  const response = await fetch(`${BASE_URL}/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: 'coach',
      password: 'coach123'
    })
  });
  
  const data = await response.json();
  token = data.token;
  console.log('登录成功', data);
}

// ==================== 2. 获取题目列表 ====================
async function getProblems(page = 1, pageSize = 10) {
  const response = await fetch(
    `${BASE_URL}/problems/?page=${page}&page_size=${pageSize}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  const data = await response.json();
  console.log('题目列表', data);
  return data;
}

// ==================== 3. 提交代码 ====================
async function submitCode(problemId, language, code) {
  const response = await fetch(`${BASE_URL}/submissions/submit/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      problem_id: problemId,
      language: language,
      code: code
    })
  });
  
  const data = await response.json();
  console.log('提交结果', data);
  return data;
}

// ==================== 4. AI问答 ====================
async function askAI(question, topK = 5, useRAG = true) {
  const response = await fetch(`${BASE_URL}/chat/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      question: question,
      top_k: topK,
      use_rag: useRAG
    })
  });
  
  const data = await response.json();
  console.log('AI回答', data);
  return data;
}

// 使用示例
(async () => {
  await login();
  await getProblems();
  await submitCode('A001', 'cpp', '#include <iostream>\n...');
  await askAI('如何实现快速排序？');
})();
```

---

## 📌 注意事项

### 1. 认证相关
- Token 有效期为 14 天，过期后需要重新登录
- 支持 `Bearer` 和 `jwt` 两种 Authorization header 格式
- Token 丢失或泄露请立即重新登录获取新Token

### 2. 速率限制
- AI 问答：每日 50 次配额，次日 00:00 重置
- 其他接口：暂无明确限制，但请避免恶意高频请求

### 3. 文件大小限制
- 测试用例 ZIP 文件：不超过 10MB
- 提交代码：不超过 64KB (65536字节)

### 4. 时间/内存单位
- 时间限制：毫秒 (ms)
- 内存限制：MB
- 执行时间：毫秒 (ms)
- 内存使用：KB

### 5. 权限说明
- 学生：只能查看和操作自己的数据
- 教练：可以管理班级、创建题目、查看学生数据
- 管理员：拥有所有权限

### 6. 数据格式
- 所有日期时间使用 ISO 8601 格式：`YYYY-MM-DDTHH:MM:SS.ssssss`
- 所有请求和响应均为 JSON 格式
- 文件上传使用 multipart/form-data 格式

### 7. 分页说明
- 默认每页 20 条记录
- 响应中包含 `count`、`next`、`previous` 字段
- 通过 `page` 和 `page_size` 参数控制分页

---

## 🔗 相关资源

- [项目 GitHub](https://github.com/your-repo/ZJOJ)
- [go-judge 文档](https://github.com/criyle/go-judge)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT 标准](https://jwt.io/)

---

<div align="center">

**ZJOJ 铸剑在线评测系统**

Made with ❤️ by 铸剑团队

</div>
