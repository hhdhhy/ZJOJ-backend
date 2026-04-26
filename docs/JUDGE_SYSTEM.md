# 评测系统集成指南

## 📋 概述

ZJOJ 使用 **go-judge (hydro-sandbox)** 作为代码执行沙箱，通过 Python 适配器实现完整的评测功能。

### 技术栈

- **沙箱**: go-judge v1.11.4 (hydro-sandbox)
- **适配器**: Python JudgeAdapter
- **通信**: HTTP REST API
- **语言支持**: C, C++, Python, Java

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────┐
│      ZJOJ (Django Backend)          │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Submission View             │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │  HydroJudgeClient            │  │
│  │  - 读取测试用例 ZIP          │  │
│  │  - 提取输入/输出数据         │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼──────────────────┐   │
│  │  JudgeAdapter (Python)     │   │
│  │  - 遍历测试点              │   │
│  │  - 构建 go-judge 请求      │   │
│  │  - 比较输出                │   │
│  │  - 计算分数                │   │
│  └──────────┬──────────────────┘   │
└─────────────┼──────────────────────┘
              │ HTTP POST /run
┌─────────────▼──────────────────────┐
│  go-judge (hydro-sandbox)          │
│  localhost:5050                    │
│                                    │
│  - 编译代码                        │
│  - 沙箱执行                        │
│  - 资源限制 (CPU/内存/进程)        │
│  - 捕获 stdout/stderr              │
└────────────────────────────────────┘
```

---

## 📦 核心组件

### 1. go-judge (hydro-sandbox)

**服务信息**:
- **端口**: 5050
- **进程管理**: PM2 (`hydro-sandbox`)
- **配置文件**: `/root/.hydro/mount.yaml`
- **状态**: ✅ 运行中

**功能**:
- 安全的代码执行环境
- 资源限制（时间、内存、进程数）
- 文件系统隔离
- 支持多种编程语言

**API 端点**:
```
POST http://localhost:5050/run
Content-Type: application/json

{
  "cmd": [{
    "args": ["/bin/bash", "-c", "g++ -o main main.cpp && ./main"],
    "env": ["PATH=/usr/bin:/bin"],
    "files": [
      {"content": "输入数据"},
      {"name": "stdout", "max": 10485760},
      {"name": "stderr", "max": 10485760}
    ],
    "cpuLimit": 1000000000,      // 1秒 (纳秒)
    "memoryLimit": 268435456,    // 256MB (字节)
    "procLimit": 50,
    "copyIn": {
      "main.cpp": {"content": "源代码"}
    },
    "copyOut": ["stdout", "stderr"]
  }]
}
```

### 2. JudgeAdapter (Python)

**文件**: `apps/judge/adapter.py`

**功能**:
- 封装 go-judge 的复杂调用逻辑
- 多测试点自动遍历
- 输出比较（规范化空白字符）
- 状态判断和评分

**主要方法**:

```python
class JudgeAdapter:
    def judge(code, language, test_cases, time_limit, memory_limit):
        """
        执行评测
        
        Args:
            code: 源代码字符串
            language: 编程语言 (cpp/c/python/java)
            test_cases: [{'input': '...', 'output': '...'}]
            time_limit: 时间限制 (ms)
            memory_limit: 内存限制 (MB)
        
        Returns:
            {
                'status': 'success',
                'result': 'AC/WA/TLE/MLE/RE/CE',
                'score': 总分 (0-100),
                'time': 最大运行时间 (ms),
                'memory': 最大内存使用 (KB),
                'test_cases': [...]
            }
        """
```

**输出比较规则**:

```python
def _compare_output(self, actual, expected):
    """
    规范化空白字符后比较
    
    规则:
    1. 去除首尾空白
    2. 将所有连续空白替换为单个空格
    3. 比较规范化后的字符串
    
    示例:
    - "1  2\n3" == "1 2 3"  ✅
    - "hello   world" == "hello world"  ✅
    """
```

### 3. HydroJudgeClient (Django)

**文件**: `apps/judge/hydro_client.py`

**功能**:
- 与 Django 模型集成
- 读取测试用例 ZIP 文件
- 调用 JudgeAdapter
- 返回标准化结果

**使用示例**:

```python
from apps.judge.hydro_client import HydroJudgeClient

# 创建客户端
client = HydroJudgeClient()

# 执行评测
result = client.judge(submission)

# 结果格式
{
    'status': 'success',
    'result': 'AC',
    'score': 100,
    'time': 45,
    'memory': 3584,
    'test_cases': [
        {
            'id': 1,
            'status': 'AC',
            'score': 10,
            'time': 12,
            'memory': 3200,
            'stdout': '8\n'
        },
        ...
    ]
}
```

---

## 🔧 配置说明

### go-judge 配置

**关键参数** (`adapter.py`):

```python
payload = {
    'cmd': [{
        'cpuLimit': time_limit * 1000000,      # ms -> ns
        'memoryLimit': memory_limit * 1024 * 1024,  # MB -> bytes
        'procLimit': 50,  # 进程数限制（C/C++编译需要）
        ...
    }]
}
```

**为什么 procLimit=50?**
- C/C++ 编译时 g++ 会创建多个子进程
- procLimit=1 会导致 "fork: Resource temporarily unavailable"
- 50 是安全值，足够编译使用

### 测试用例格式

**ZIP 文件结构**:
```
testcases.zip
└── testdata/
    ├── 1.in
    ├── 1.out
    ├── 2.in
    ├── 2.out
    └── ...
```

**存储位置**: `media/problems/{problem_id}/testcases.zip`

---

## 🚀 部署指南

### 1. 安装 go-judge

```bash
# 使用 Hydro OJ 官方脚本安装评测机组件
sudo su -c 'LANG=zh . <(curl https://hydro.ac/setup.sh) --judge'

# 检查服务状态
sudo pm2 status | grep hydro-sandbox
```

### 2. 验证 go-judge

```bash
# 测试简单命令
curl -s http://localhost:5050/run -X POST \
  -H 'Content-Type: application/json' \
  -d '{"cmd":[{"args":["/bin/echo","Hello"]}]}' | python3 -m json.tool

# 预期输出
{
  "status": "Accepted",
  "exitStatus": 0,
  "files": {
    "stdout": "Hello\n"
  }
}
```

### 3. 部署 ZJOJ

```bash
# 上传代码到服务器
scp apps/judge/adapter.py ubuntu@101.35.233.33:/home/ubuntu/ZJOJ/apps/judge/
scp apps/judge/hydro_client.py ubuntu@101.35.233.33:/home/ubuntu/ZJOJ/apps/judge/

# 重启 Django 服务
ssh ubuntu@101.35.233.33 "sudo systemctl restart zjoj"
```

### 4. 测试评测功能

```python
# 在 Django shell 中测试
python manage.py shell

>>> from apps.judge.hydro_client import HydroJudgeClient
>>> from apps.problem.models import Problem, Submission
>>> 
>>> # 获取一个提交
>>> submission = Submission.objects.first()
>>> 
>>> # 执行评测
>>> client = HydroJudgeClient()
>>> result = client.judge(submission)
>>> print(result)
```

---

## 📊 评测状态说明

| 状态码 | 含义 | 说明 |
|--------|------|------|
| AC | Accepted | 答案正确 |
| WA | Wrong Answer | 答案错误 |
| TLE | Time Limit Exceeded | 超时 |
| MLE | Memory Limit Exceeded | 超内存 |
| RE | Runtime Error | 运行时错误 |
| CE | Compilation Error | 编译错误 |
| SE | System Error | 系统错误 |

**状态优先级**: SE > CE > RE > TLE > MLE > WA > AC

最终结果取所有测试点中最差的状态。

---

## 🐛 常见问题

### 1. go-judge 返回 "Time Limit Exceeded" 但 exitStatus=0

**原因**: cgroup v1 内存限制问题  
**解决**: 已在 adapter.py 中自行判断时间和内存，不依赖 go-judge 的 status 字段

### 2. C++ 编译失败 "fork: Resource temporarily unavailable"

**原因**: procLimit 设置太小  
**解决**: 已设置为 50，确保编译时有足够的进程数

### 3. 输出比较过于严格

**原因**: 学生输出有多余空格或换行  
**解决**: adapter.py 使用规范化空白字符比较，已处理此问题

### 4. 测试用例文件找不到

**检查**:
```bash
# 确认 ZIP 文件存在
ls -la /home/ubuntu/ZJOJ/media/problems/A001/testcases.zip

# 确认解压后的结构
unzip -l /home/ubuntu/ZJOJ/media/problems/A001/testcases.zip
```

---

## 🔒 安全考虑

### go-judge 安全措施

1. **文件系统隔离**: 使用 chroot + mount namespace
2. **资源限制**: CPU、内存、进程数严格限制
3. **网络禁用**: 沙箱内无法访问网络
4. **用户权限**: 以非 root 用户运行 (uid: 1536)

### ZJOJ 安全措施

1. **代码审查**: 提交前可进行代码审查
2. **频率限制**: 防止恶意提交
3. **日志记录**: 所有评测操作都有日志

---

## 📈 性能优化建议

1. **缓存编译结果**: 相同代码不需要重复编译
2. **并行评测**: 多个测试点可以并行执行
3. **异步处理**: 使用 Celery 异步评测（可选）
4. **监控指标**: 记录评测耗时，优化瓶颈

---

## 🔗 相关文档

- [API 文档](API_DOCUMENTATION.md) - 评测相关 API
- [数据库设计](DATABASE_DESIGN.md) - Submission 模型
- [部署指南](DEPLOYMENT.md) - 完整部署流程
- [开发指南](DEVELOPMENT_GUIDE.md) - 开发规范

---

## 📝 更新日志

**2026-04-21**: 
- ✅ 完成 go-judge 集成
- ✅ 实现 Python JudgeAdapter
- ✅ 支持多测试点评测
- ✅ 实现规范化空白字符比较
- ❌ 废弃 hydrojudge HTTP adapter 方案
