# 数据库设计

> 🗄️ ZJOJ 数据库核心设计概览

---

## 数据库环境

- **类型**: MySQL 8.0
- **字符集**: utf8mb4
- **引擎**: InnoDB
- **用户模型**: 自定义 OJUser (uid 为主键)

---

## 核心数据表

### 1. 用户模块

#### ojauth_ojuser（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| uid | VARCHAR(255) | Short UUID 主键 |
| username | VARCHAR(150) | 用户名（唯一） |
| email | VARCHAR(254) | 邮箱（登录账号，唯一） |
| password | VARCHAR(128) | 密码哈希 |
| is_superuser | TINYINT | 是否超级用户 |
| is_staff | TINYINT | 是否工作人员 |
| status | INT | 状态：1-激活, 2-未激活, 3-锁定 |

**特点**：
- 使用 Short UUID 避免信息泄露
- 邮箱作为登录账号
- PBKDF2 加密存储密码

---

### 2. 题目模块

#### problem_problem（题目表）

| 字段 | 类型 | 说明 |
|------|------|------|
| problem_id | VARCHAR(20) | 题目编号（主键，如 P1001） |
| title | VARCHAR(100) | 题目标题 |
| description | LONGTEXT | 题目描述（Markdown） |
| time_limit | INT | 时间限制（毫秒） |
| memory_limit | INT | 内存限制（MB） |
| creator_id | VARCHAR(255) | 创建者（外键，SET NULL） |

#### problem_tag（标签表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 自增主键 |
| name | VARCHAR(50) | 标签名（唯一） |

**关系**：Problem ↔ Tag（多对多）

---

### 3. 提交记录模块

#### submission（提交表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 自增主键 |
| problem_id | VARCHAR(20) | 题目（外键） |
| user_id | VARCHAR(255) | 用户（外键） |
| language | VARCHAR(20) | 编程语言（cpp/c/java/python3） |
| code | LONGTEXT | 提交的代码 |
| code_length | INT | 代码长度（字节） |
| status | INT | 评测状态（0-4） |
| result | VARCHAR(10) | 评测结果（AC/WA/TLE等） |
| score | INT | 得分 |
| execution_time | INT | 运行时间（毫秒） |
| memory_usage | INT | 内存使用（KB） |
| submit_time | DATETIME | 提交时间 |
| judge_time | DATETIME | 评测时间 |

**评测状态**：
- 0: 等待评测
- 1: 评测中
- 2: 已完成
- 3: 编译错误
- 4: 系统错误

**评测结果**：
- AC: Accepted（通过）
- WA: Wrong Answer（答案错误）
- TLE: Time Limit Exceeded（超时）
- MLE: Memory Limit Exceeded（超内存）
- RE: Runtime Error（运行错误）
- CE: Compilation Error（编译错误）
- SE: System Error（系统错误）

#### test_case_result（测试点结果表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 自增主键 |
| submission_id | BIGINT | 提交记录（外键） |
| test_case_id | INT | 测试用例ID |
| status | VARCHAR(10) | 测试点状态（AC/WA/TLE/MLE/RE） |
| execution_time | INT | 用时（毫秒） |
| memory_usage | INT | 内存（KB） |
| score | INT | 该测试点得分 |
| message | TEXT | 详细信息 |

---

### 4. AI 助手模块

#### ai_assistant_knowledgebase（知识库）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 自增主键 |
| title | VARCHAR(200) | 文档标题 |
| content | LONGTEXT | 文档内容 |
| embedding | JSON | 向量嵌入 |
| problem_id | VARCHAR(20) | 关联题目（可选） |

#### ai_assistant_chathistory（对话历史）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 自增主键 |
| user_id | VARCHAR(255) | 用户（外键） |
| messages | JSON | 对话消息列表 |
| created_at | DATETIME | 创建时间 |

#### ai_assistant_userprofile（用户AI配置）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 自增主键 |
| user_id | VARCHAR(255) | 用户（一对一） |
| api_key | VARCHAR(255) | 用户自定义 API Key |
| model | VARCHAR(50) | 偏好模型 |

#### ai_assistant_ratelimit（频率限制）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 自增主键 |
| user_id | VARCHAR(255) | 用户（外键） |
| request_count | INT | 今日请求次数 |
| last_request | DATETIME | 最后请求时间 |

---

## ER 关系图

```
┌──────────────┐       ┌─────────────────┐
│  OJUser      │       │   Problem       │
│──────────────│       │─────────────────│
│ uid (PK)     │◄──────│ creator_id (FK) │
│ username     │       │ problem_id (PK) │
│ email        │       │ title           │
│ password     │       │ description     │
└──────┬───────┘       └────────┬────────┘
       │                        │
       │                        │
       │              ┌─────────▼────────┐
       │              │   Submission     │
       │              │──────────────────│
       │              │ id (PK)          │
       │              │ user_id (FK)     │
       │              │ problem_id (FK)  │
       │              │ result           │
       │              │ code             │
       │              └────────┬─────────┘
       │                       │
       │              ┌────────▼──────────────┐
       │              │ TestCaseResult        │
       │              │───────────────────────│
       │              │ submission_id (FK)    │
       │              │ test_case_id          │
       │              │ result                │
       │              └───────────────────────┘
       │
       │              ┌──────────────────────┐
       │              │ ChatHistory          │
       │              │──────────────────────│
       │              │ user_id (FK)         │
       │              │ messages (JSON)      │
       │              └──────────────────────┘
```

---

## 索引优化建议

### 必建索引

1. **用户表**：username, email, telephone（唯一索引）
2. **题目表**：problem_id（主键）
3. **提交表**：user_id, problem_id, submit_time（联合查询优化）
4. **测试点结果**：submission_id（外键查询）

### 性能优化

1. **分页查询**：在 submit_time 上建立索引
2. **标签筛选**：problem_tag 中间表建立联合索引
3. **搜索功能**：考虑使用全文索引或 Elasticsearch

---

## 注意事项

1. **外键约束**：creator_id 使用 SET NULL，删除用户时保留题目
2. **大字段**：description、code、content 使用 LONGTEXT
3. **JSON 字段**：messages、embedding 使用 JSON 类型（MySQL 5.7+）
4. **时间戳**：使用 DATETIME(6) 支持微秒精度

---

## 相关文件

- 用户模型：`apps/ojauth/models.py`
- 题目模型：`apps/problem/models.py`
- 提交模型：`apps/problem/models.py`（Submission, TestCaseResult）
- AI 模型：`apps/ai_assistant/models.py`
