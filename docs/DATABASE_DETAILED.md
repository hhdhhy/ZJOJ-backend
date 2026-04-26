# 数据库设计详细文档

## 📋 概述

本文档详细描述 ZJOJ 系统的数据库设计，包括数据模型、表结构、字段说明、关系图等。

**数据库**: MySQL 8.0  
**ORM**: Django ORM  
**字符集**: utf8mb4  

---

## 🗺️ ER 图

```
┌──────────────┐       ┌────────────────┐       ┌──────────────┐
│    User      │       │   Problem      │       │ Submission   │
├──────────────┤       ├────────────────┤       ├──────────────┤
│ id (PK)      │───┐   │ id (PK)        │   ┌──▶│ id (PK)      │
│ username     │   └──▶│ title          │   │   │ user_id (FK) │
│ email        │       │ description    │   │   │ problem_id(FK)│
│ password     │       │ difficulty     │   │   │ code         │
│ telephone    │       │ time_limit     │   │   │ language     │
│ is_staff     │       │ memory_limit   │   │   │ status       │
│ is_active    │       │ test_cases     │   │   │ result       │
│ created_at   │       │ created_at     │   │   │ score        │
└──────────────┘       └────────────────┘   │   │ exec_time    │
                                            │   │ memory_usage │
┌──────────────┐       ┌────────────────┐   │   └──────────────┘
│ TestCase     │       │ TestCaseResult │   │
├──────────────┤       ├────────────────┤   │
│ id (PK)      │   ┌──▶│ id (PK)        │   │
│ problem_id(FK)│───┘  │ submission_   │◀──┘
│ input_data   │       │   id (FK)      │
│ output_data  │       │ test_case_id   │
│ score        │       │ status         │
└──────────────┘       │ score          │
                       │ exec_time      │
┌──────────────┐       │ memory_usage   │
│ AIChatHistory│       └────────────────┘
├──────────────┤
│ id (PK)      │
│ user_id (FK) │
│ question     │
│ answer       │
│ contexts     │
│ created_at   │
└──────────────┘
```

---

## 📊 数据表详解

### 1. 用户表 (ojauth_ojuser)

**用途**: 存储用户基本信息和认证数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 用户 ID |
| username | VARCHAR(150) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(254) | UNIQUE, NOT NULL | 邮箱 |
| password | VARCHAR(128) | NOT NULL | 密码 (PBKDF2 加密) |
| telephone | VARCHAR(20) | UNIQUE, NOT NULL | 手机号 |
| nickname | VARCHAR(100) | NULL | 昵称 |
| avatar | VARCHAR(500) | NULL | 头像 URL |
| bio | TEXT | NULL | 个人简介 |
| is_staff | BOOLEAN | DEFAULT FALSE | 是否为管理员 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| date_joined | DATETIME | DEFAULT NOW() | 注册时间 |
| last_login | DATETIME | NULL | 最后登录时间 |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE: `username`, `email`, `telephone`

**示例数据**:
```sql
INSERT INTO ojauth_ojuser (username, email, password, telephone, is_staff) 
VALUES (
    'admin',
    'admin@zjoj.com',
    'pbkdf2_sha256$...',
    '13800138000',
    TRUE
);
```

---

### 2. 题目表 (problem_problem)

**用途**: 存储编程题目的基本信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 题目 ID |
| title | VARCHAR(200) | NOT NULL | 题目标题 |
| description | TEXT | NOT NULL | 题目描述 (Markdown) |
| input_format | TEXT | NULL | 输入格式说明 |
| output_format | TEXT | NULL | 输出格式说明 |
| sample_input | TEXT | NULL | 样例输入 |
| sample_output | TEXT | NULL | 样例输出 |
| hint | TEXT | NULL | 提示 |
| source | VARCHAR(200) | NULL | 来源 (如 "NOIP 2023") |
| difficulty | VARCHAR(20) | DEFAULT 'medium' | 难度 (easy/medium/hard) |
| time_limit | INT | DEFAULT 1000 | 时间限制 (毫秒) |
| memory_limit | INT | DEFAULT 256 | 内存限制 (MB) |
| test_cases_file | VARCHAR(500) | NOT NULL | 测试用例 ZIP 文件路径 |
| tags | JSON | NULL | 标签 (如 ["动态规划", "图论"]) |
| is_public | BOOLEAN | DEFAULT TRUE | 是否公开 |
| created_by_id | INT | FOREIGN KEY → ojauth_ojuser.id | 创建者 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | DEFAULT NOW() ON UPDATE | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- INDEX: `difficulty`, `is_public`, `created_at`
- FOREIGN KEY: `created_by_id`

**示例数据**:
```sql
INSERT INTO problem_problem (
    title, description, difficulty, time_limit, memory_limit,
    test_cases_file, is_public, created_by_id
) VALUES (
    'A+B Problem',
    '计算两个整数的和...',
    'easy',
    1000,
    256,
    '/media/test_cases/1.zip',
    TRUE,
    1
);
```

---

### 3. 提交记录表 (problem_submission)

**用途**: 存储用户的代码提交记录和评测结果

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 提交 ID |
| user_id | INT | FOREIGN KEY → ojauth_ojuser.id | 用户 ID |
| problem_id | INT | FOREIGN KEY → problem_problem.id | 题目 ID |
| code | TEXT | NOT NULL | 提交的代码 |
| language | VARCHAR(20) | NOT NULL | 编程语言 (cpp/c/python/java) |
| status | VARCHAR(20) | DEFAULT 'PENDING' | 状态 (见下方枚举) |
| result | VARCHAR(20) | NULL | 最终结果 (AC/WA/TLE/...) |
| score | INT | DEFAULT 0 | 得分 (0-100) |
| execution_time | INT | NULL | 最大运行时间 (ms) |
| memory_usage | INT | NULL | 最大内存使用 (KB) |
| error_message | TEXT | NULL | 错误信息 (编译错误等) |
| submitted_at | DATETIME | DEFAULT NOW() | 提交时间 |
| judged_at | DATETIME | NULL | 评测完成时间 |

**状态枚举**:
- `PENDING`: 等待评测
- `JUDGING`: 正在评测
- `COMPLETED`: 评测完成
- `ERROR`: 评测出错

**结果枚举**:
- `AC`: Accepted (答案正确)
- `WA`: Wrong Answer (答案错误)
- `TLE`: Time Limit Exceeded (超时)
- `MLE`: Memory Limit Exceeded (超内存)
- `RE`: Runtime Error (运行时错误)
- `CE`: Compilation Error (编译错误)
- `OLE`: Output Limit Exceeded (输出超限)
- `SE`: System Error (系统错误)

**索引**:
- PRIMARY KEY: `id`
- INDEX: `user_id`, `problem_id`, `status`, `result`, `submitted_at`
- FOREIGN KEY: `user_id`, `problem_id`

**示例数据**:
```sql
INSERT INTO problem_submission (
    user_id, problem_id, code, language, status, result, score,
    execution_time, memory_usage, submitted_at
) VALUES (
    1,
    1,
    '#include<iostream>\nusing namespace std;\nint main(){...}',
    'cpp',
    'COMPLETED',
    'AC',
    100,
    45,
    3584,
    '2026-04-27 10:30:00'
);
```

---

### 4. 测试点结果表 (problem_testcaseresult)

**用途**: 存储每个测试点的详细评测结果

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 结果 ID |
| submission_id | INT | FOREIGN KEY → problem_submission.id | 提交 ID |
| test_case_id | INT | NOT NULL | 测试点 ID (从 1 开始) |
| status | VARCHAR(20) | NOT NULL | 该测试点状态 (AC/WA/...) |
| score | INT | DEFAULT 0 | 该测试点得分 |
| execution_time | INT | NULL | 运行时间 (ms) |
| memory_usage | INT | NULL | 内存使用 (KB) |
| stdout | TEXT | NULL | 程序输出 |
| stderr | TEXT | NULL | 错误输出 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

**索引**:
- PRIMARY KEY: `id`
- INDEX: `submission_id`
- FOREIGN KEY: `submission_id`

**示例数据**:
```sql
INSERT INTO problem_testcaseresult (
    submission_id, test_case_id, status, score,
    execution_time, memory_usage, stdout
) VALUES (
    1,
    1,
    'AC',
    10,
    12,
    3200,
    '8\n'
);
```

---

### 5. AI 聊天历史表 (ai_assistant_aichathistory)

**用途**: 存储用户与 AI 助手的对话历史

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 记录 ID |
| user_id | INT | FOREIGN KEY → ojauth_ojuser.id | 用户 ID |
| question | TEXT | NOT NULL | 用户问题 |
| answer | TEXT | NOT NULL | AI 回答 |
| contexts | JSON | NULL | 检索到的上下文 (Top-K 文档) |
| sources | JSON | NULL | 来源列表 |
| tokens_used | INT | NULL | 消耗的 Token 数 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

**索引**:
- PRIMARY KEY: `id`
- INDEX: `user_id`, `created_at`
- FOREIGN KEY: `user_id`

**示例数据**:
```sql
INSERT INTO ai_assistant_aichathistory (
    user_id, question, answer, contexts, sources, tokens_used
) VALUES (
    1,
    '如何使用 go-judge 编译 C++ 代码？',
    '使用 go-judge 编译 C++ 代码需要以下步骤...',
    '[{"content": "...", "score": 0.92}]',
    '["JUDGE_SYSTEM.md"]',
    1500
);
```

---

## 🔗 表关系说明

### 一对多关系

1. **User → Submission**
   - 一个用户可以有多次提交
   - `Submission.user_id` → `OJUser.id`

2. **Problem → Submission**
   - 一个题目可以被多次提交
   - `Submission.problem_id` → `Problem.id`

3. **Problem → TestCase**
   - 一个题目有多个测试点
   - `TestCase.problem_id` → `Problem.id`

4. **Submission → TestCaseResult**
   - 一次提交有多个测试点结果
   - `TestCaseResult.submission_id` → `Submission.id`

5. **User → AIChatHistory**
   - 一个用户可以有多次 AI 对话
   - `AIChatHistory.user_id` → `OJUser.id`

---

## 📈 性能优化

### 1. 索引策略

```sql
-- 常用查询的复合索引
CREATE INDEX idx_submission_user_problem ON problem_submission(user_id, problem_id);
CREATE INDEX idx_submission_status_result ON problem_submission(status, result);
CREATE INDEX idx_submission_submitted_at ON problem_submission(submitted_at DESC);

-- AI 聊天历史的查询索引
CREATE INDEX idx_ai_chat_user_created ON ai_assistant_aichathistory(user_id, created_at DESC);
```

### 2. 分区策略 (大数据量时)

```sql
-- 按月份对提交记录分区
ALTER TABLE problem_submission PARTITION BY RANGE (YEAR(submitted_at) * 100 + MONTH(submitted_at)) (
    PARTITION p202601 VALUES LESS THAN (202602),
    PARTITION p202602 VALUES LESS THAN (202603),
    ...
);
```

### 3. 缓存策略

```python
# Redis 缓存热门题目
cache.set(f"problem:{problem_id}", problem_data, timeout=3600)

# 缓存用户最近提交
cache.set(f"user:{user_id}:recent_submissions", submissions, timeout=300)
```

---

## 🔍 常用查询示例

### 1. 获取用户的 AC 率

```sql
SELECT 
    COUNT(CASE WHEN result = 'AC' THEN 1 END) * 100.0 / COUNT(*) as ac_rate
FROM problem_submission
WHERE user_id = 1 AND status = 'COMPLETED';
```

### 2. 获取题目的通过率

```sql
SELECT 
    p.title,
    COUNT(CASE WHEN s.result = 'AC' THEN 1 END) * 100.0 / COUNT(*) as pass_rate
FROM problem_problem p
LEFT JOIN problem_submission s ON p.id = s.problem_id
WHERE s.status = 'COMPLETED'
GROUP BY p.id;
```

### 3. 获取用户的最近 10 次提交

```sql
SELECT 
    s.id,
    p.title,
    s.language,
    s.result,
    s.score,
    s.execution_time,
    s.submitted_at
FROM problem_submission s
JOIN problem_problem p ON s.problem_id = p.id
WHERE s.user_id = 1
ORDER BY s.submitted_at DESC
LIMIT 10;
```

### 4. 统计各难度的题目数量

```sql
SELECT 
    difficulty,
    COUNT(*) as count
FROM problem_problem
WHERE is_public = TRUE
GROUP BY difficulty;
```

---

## 🛠️ 数据库迁移

### Django Migration 示例

```python
# apps/problem/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('ojauth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('difficulty', models.CharField(default='medium', max_length=20)),
                ('time_limit', models.IntegerField(default=1000)),
                ('memory_limit', models.IntegerField(default=256)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ojauth.ojuser')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.TextField()),
                ('language', models.CharField(max_length=20)),
                ('status', models.CharField(default='PENDING', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ojauth.ojuser')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problem.problem')),
            ],
        ),
    ]
```

### 执行迁移

```bash
# 生成迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 查看迁移状态
python manage.py showmigrations
```

---

## 📊 数据备份

### 1. mysqldump 备份

```bash
# 完整备份
mysqldump -u root -p zjoj_db > backup_$(date +%Y%m%d).sql

# 仅备份结构
mysqldump -u root -p --no-data zjoj_db > schema_backup.sql

# 仅备份数据
mysqldump -u root -p --no-create-info zjoj_db > data_backup.sql
```

### 2. 恢复数据

```bash
mysql -u root -p zjoj_db < backup_20260427.sql
```

### 3. 定时备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="zjoj_db"
DB_USER="root"
DB_PASS="your_password"

mkdir -p $BACKUP_DIR

mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# 保留最近 7 天的备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

---

## 🔗 相关文档

- [Django Models](../apps/problem/models.py)
- [API 参考](04-API_REFERENCE.md)
- [部署指南](03-DEPLOYMENT.md)

---

**最后更新**: 2026-04-27
