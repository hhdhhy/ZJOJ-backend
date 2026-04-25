# 评测系统模块

> �?基于 go-judge 的代码自动评测系�?
---

## 📋 概述

评测系统�?ZJOJ 的核心功能，负责�?- 编译和执行用户提交的代码
- 限制资源使用（时间、内存）
- 比较输出并评�?- 返回评测结果

**技术栈**: go-judge v1.11.4 + Python Adapter

---

## 🏗�?架构设计

```
┌─────────────────────────────────────�?�?     ZJOJ (Django Backend)          �?�?                                    �?�? ┌──────────────────────────────�? �?�? �? Submission View             �? �?�? └──────────┬───────────────────�? �?�?            �?                      �?�? ┌──────────▼───────────────────�? �?�? �? GoJudgeClient            �? �?�? �? - 读取测试用例 ZIP          �? �?�? �? - 提取输入/输出数据         �? �?�? └──────────┬───────────────────�? �?�?            �?                      �?�? ┌──────────▼──────────────────�?  �?�? �? JudgeAdapter (Python)     �?  �?�? �? - 遍历测试�?             �?  �?�? �? - 构建 go-judge 请求      �?  �?�? �? - 比较输出                �?  �?�? �? - 计算分数                �?  �?�? └──────────┬──────────────────�?  �?└─────────────┼──────────────────────�?              �?HTTP POST /run
┌─────────────▼──────────────────────�?�? go-judge (go-judge)          �?�? localhost:5050                    �?�?                                   �?�? - 编译代码                        �?�? - 沙箱执行                        �?�? - 资源限制 (CPU/内存/进程)        �?�? - 捕获 stdout/stderr              �?└────────────────────────────────────�?```

---

## 📦 核心组件

### 1. go-judge (go-judge)

**服务信息**:
- **端口**: 5050
- **进程管理**: PM2 (`go-judge`)
- **配置文件**: `/root/.hydro/mount.yaml`

**功能**:
- 安全的代码执行环境（chroot + namespace�?- 资源限制（cgroup�?- 支持多种编程语言
- 文件系统隔离

**API**:
```http
POST http://localhost:5050/run
Content-Type: application/json

{
  "cmd": [{
    "args": ["/bin/bash", "-c", "g++ -o main main.cpp && ./main"],
    "files": [
      {"content": "输入数据"},
      {"name": "stdout", "max": 10485760},
      {"name": "stderr", "max": 10485760}
    ],
    "cpuLimit": 1000000000,      // 1�?(纳秒)
    "memoryLimit": 268435456,    // 256MB (字节)
    "procLimit": 50,
    "copyIn": {
      "main.cpp": {"content": "源代�?}
    },
    "copyOut": ["stdout", "stderr"]
  }]
}
```

---

### 2. JudgeAdapter (Python)

**文件**: `apps/judge/adapter.py`

**职责**:
- 封装 go-judge 的复杂调用逻辑
- 多测试点自动遍历
- 输出比较（规范化空白字符�?- 状态判断和评分

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
                'time': 最大运行时�?(ms),
                'memory': 最大内存使�?(KB),
                'test_cases': [...]
            }
        """
    
    def _compare_output(actual, expected):
        """
        比较输出（规范化空白字符�?        
        规则:
        1. 去除首尾空白
        2. 将所有连续空白替换为单个空格
        3. 比较规范化后的字符串
        
        示例:
        - "1  2\n3" == "1 2 3"  �?        - "hello   world" == "hello world"  �?        """
```

**输出比较规则**:

| 实际输出 | 预期输出 | 结果 | 说明 |
|---------|---------|------|------|
| `"8\n"` | `"8"` | �?AC | 忽略末尾换行 |
| `"1  2"` | `"1 2"` | �?AC | 忽略多余空格 |
| `"1\n2\n3"` | `"1 2 3"` | �?AC | 换行视为空格 |
| `"8"` | `"9"` | �?WA | 答案错误 |

---

### 3. GoJudgeClient (Django)

**文件**: `apps/judge/gojudge_client.py`

**职责**:
- �?Django 模型集成
- 读取测试用例 ZIP 文件
- 调用 JudgeAdapter
- 返回标准化结�?
**使用示例**:

```python
from apps.judge.gojudge_client import GoJudgeClient

# 创建客户�?client = GoJudgeClient()

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

## 🔄 评测流程

### 完整流程�?
```
1. 用户提交代码
        �?2. 创建 Submission 记录 (status=PENDING)
        �?3. GoJudgeClient.judge(submission)
        �?4. 读取测试用例 ZIP 文件
        �?5. 解压到临时目�?        �?6. 遍历每个测试�?
   ├─ 读取 input/output 文件
   ├─ 调用 JudgeAdapter.judge()
   ├─ 构建 go-judge 请求
   ├─ 执行代码（沙箱）
   ├─ 捕获输出
   ├─ 比较输出
   └─ 记录结果
        �?7. 聚合所有测试点结果
        �?8. 更新 Submission (status=ACCEPTED/WA/...)
        �?9. 清理临时文件
        �?10. 返回结果给用�?```

### 代码示例

```python
# views.py
class SubmissionCreateView(APIView):
    def post(self, request):
        # 1. 验证请求
        serializer = SubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 2. 创建提交记录
        submission = serializer.save(user=request.user)
        
        # 3. 执行评测
        from apps.judge.gojudge_client import GoJudgeClient
        client = GoJudgeClient()
        result = client.judge(submission)
        
        # 4. 更新提交记录
        submission.status = result['result']
        submission.score = result['score']
        submission.time_used = result['time']
        submission.memory_used = result['memory']
        submission.save()
        
        # 5. 返回结果
        return Response({
            'submission_id': submission.id,
            'status': submission.status,
            'score': submission.score
        })
```

---

## 📊 评测状�?
| 状态码 | 含义 | 触发条件 |
|--------|------|----------|
| `AC` | Accepted | 所有测试点通过 |
| `WA` | Wrong Answer | 输出不匹�?|
| `TLE` | Time Limit Exceeded | 超过时间限制 |
| `MLE` | Memory Limit Exceeded | 超过内存限制 |
| `RE` | Runtime Error | 运行时错误（段错误、除零等�?|
| `CE` | Compilation Error | 编译失败 |
| `SE` | System Error | 系统错误（沙箱异常） |

**状态优先级**: SE > CE > RE > TLE > MLE > WA > AC

最终结果取所有测试点中最差的状态�?
---

## 🔧 配置说明

### go-judge 关键参数

```python
# adapter.py
payload = {
    'cmd': [{
        'cpuLimit': time_limit * 1000000,      # ms -> ns
        'memoryLimit': memory_limit * 1024 * 1024,  # MB -> bytes
        'procLimit': 50,  # 进程数限�?        ...
    }]
}
```

**为什�?procLimit=50?**
- C/C++ 编译�?g++ 会创建多个子进程
- procLimit=1 会导�?"fork: Resource temporarily unavailable"
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
# 使用 Hydro OJ 官方脚本
sudo su -c 'LANG=zh . <(curl https://hydro.ac/setup.sh) --judge'

# 检查服务状�?sudo pm2 status | grep go-judge
```

### 2. 验证 go-judge

```bash
curl -s http://localhost:5050/run -X POST \
  -H 'Content-Type: application/json' \
  -d '{"cmd":[{"args":["/bin/echo","Hello"]}]}' | python3 -m json.tool
```

预期输出�?```json
{
  "status": "Accepted",
  "exitStatus": 0,
  "files": {
    "stdout": "Hello\n"
  }
}
```

### 3. 测试评测功能

```python
# Django shell
python manage.py shell

>>> from apps.judge.gojudge_client import GoJudgeClient
>>> from apps.problem.models import Submission
>>> 
>>> submission = Submission.objects.first()
>>> client = GoJudgeClient()
>>> result = client.judge(submission)
>>> print(result)
```

---

## 🐛 常见问题

### Q1: go-judge 返回 "Time Limit Exceeded" �?exitStatus=0

**原因**: cgroup v1 内存限制问题  
**解决**: adapter.py 中自行判断时间和内存，不依赖 go-judge �?status 字段

### Q2: C++ 编译失败 "fork: Resource temporarily unavailable"

**原因**: procLimit 设置太小  
**解决**: 已设置为 50

### Q3: 输出比较过于严格

**原因**: 学生输出有多余空格或换行  
**解决**: adapter.py 使用规范化空白字符比�?
### Q4: 测试用例文件找不�?
**检�?*:
```bash
# 确认 ZIP 文件存在
ls -la /home/ubuntu/ZJOJ/media/problems/A001/testcases.zip

# 确认解压后的结构
unzip -l /home/ubuntu/ZJOJ/media/problems/A001/testcases.zip
```

---

## 🔒 安全考虑

### go-judge 安全措施

1. **文件系统隔离**: chroot + mount namespace
2. **资源限制**: CPU、内存、进程数严格限制
3. **网络禁用**: 沙箱内无法访问网�?4. **用户权限**: 以非 root 用户运行 (uid: 1536)

### ZJOJ 安全措施

1. **代码审查**: 提交前可进行代码审查
2. **频率限制**: 防止恶意提交
3. **日志记录**: 所有评测操作都有日�?
---

## 📈 性能优化建议

1. **缓存编译结果**: 相同代码不需要重复编�?2. **并行评测**: 多个测试点可以并行执�?3. **异步处理**: 使用 Celery 异步评测（可选）
4. **监控指标**: 记录评测耗时，优化瓶�?
---

## 🔗 相关文档

- [快速开始](../01-GETTING_STARTED.md)
- [系统架构](../02-ARCHITECTURE.md)
- [部署指南](../03-DEPLOYMENT.md)
- [API 参考](../04-API_REFERENCE.md)

---

<div align="center">

**返回模块列表** �?[README](../README.md)

</div>
