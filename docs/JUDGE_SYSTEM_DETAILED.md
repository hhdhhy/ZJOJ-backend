# 评测系统详细实现文档

## 📋 概述

本文档详细描述 ZJOJ 评测系统的完整实现，包括 go-judge 集成、代码编译、沙箱执行、结果判定等核心流程。

---

## 🏗️ 系统架构

### 整体流程图

```
用户提交代码
    ↓
Submission 视图接收请求
    ↓
创建 Submission 记录 (状态: PENDING)
    ↓
触发 Celery 异步任务
    ↓
Celery Worker 执行 judge_task
    ↓
读取题目测试用例 (ZIP 文件)
    ↓
调用 JudgeAdapter.judge()
    ↓
┌─────────────────────────────┐
│  遍历每个测试点              │
│  ┌───────────────────────┐  │
│  │ 1. 编译代码 (如需)     │  │
│  │ 2. 运行代码            │  │
│  │ 3. 捕获输出            │  │
│  │ 4. 比较结果            │  │
│  │ 5. 记录状态            │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
    ↓
计算总分和最终结果
    ↓
更新 Submission 记录
    ↓
返回评测结果给用户
```

### 组件交互图

```
┌──────────────────────────────────────────┐
│         Django Web Server                │
│                                          │
│  ┌──────────────┐    ┌────────────────┐ │
│  │ Submission   │───▶│ Celery Task    │ │
│  │ View         │    │ (judge_task)   │ │
│  └──────────────┘    └───────┬────────┘ │
└──────────────────────────────┼──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Celery Worker     │
                    │                     │
                    │  ┌───────────────┐  │
                    │  │ HydroJudge   │  │
                    │  │ Client       │  │
                    │  └───────┬───────┘  │
                    │          │          │
                    │  ┌───────▼───────┐  │
                    │  │ JudgeAdapter │  │
                    │  └───────┬───────┘  │
                    └──────────┼──────────┘
                               │ HTTP POST /run
                    ┌──────────▼──────────┐
                    │   go-judge          │
                    │   (localhost:5050)  │
                    │                     │
                    │  - 编译代码          │
                    │  - 沙箱执行          │
                    │  - 资源限制          │
                    └─────────────────────┘
```

---

## 🔧 核心组件详解

### 1. JudgeAdapter (`apps/judge/adapter.py`)

#### 1.1 类结构

```python
class JudgeAdapter:
    """go-judge 适配器"""
    
    def __init__(self, go_judge_url="http://gojudge:5050", timeout=30):
        """初始化适配器"""
        
    def judge(self, code, language, test_cases, time_limit, memory_limit):
        """执行完整评测流程"""
        
    def _compile_code(self, code, language, compile_cmd):
        """编译代码（两阶段：编译 + 缓存）"""
        
    def _run_code(self, run_cmd, language, input_data, 
                  time_limit, memory_limit, file_id=None, code=None):
        """运行代码"""
        
    def _delete_cached_file(self, file_id):
        """删除缓存的编译文件"""
        
    def _compare_output(self, actual, expected):
        """比较输出（规范化空白字符）"""
        
    def _get_compile_command(self, language):
        """获取编译命令"""
        
    def _get_run_command(self, language):
        """获取运行命令"""
        
    def _get_file_extension(self, language):
        """获取文件扩展名"""
```

#### 1.2 主要方法实现

##### `judge()` - 主评测方法

```python
def judge(self, code, language, test_cases, time_limit, memory_limit):
    """
    执行完整评测流程
    
    Args:
        code: 源代码字符串
        language: 编程语言 ('cpp', 'c', 'python', 'java')
        test_cases: [{'input': '...', 'output': '...'}]
        time_limit: 时间限制 (毫秒)
        memory_limit: 内存限制 (MB)
    
    Returns:
        {
            'status': 'success' | 'error',
            'result': 'AC' | 'WA' | 'TLE' | 'MLE' | 'RE' | 'CE',
            'score': 0-100,
            'time': 最大运行时间 (ms),
            'memory': 最大内存使用 (KB),
            'test_cases': [
                {
                    'id': 测试点ID,
                    'status': 'AC' | 'WA' | ...,
                    'score': 该测试点得分,
                    'time': 运行时间 (ms),
                    'memory': 内存使用 (KB),
                    'stdout': '程序输出',
                    'stderr': '错误输出'
                }
            ]
        }
    """
```

**实现逻辑**:

1. **检查是否需要编译**
   ```python
   compile_cmd = self._get_compile_command(language)
   if compile_cmd:
       # 编译代码并缓存
       file_id = self._compile_code(code, language, compile_cmd)
       if not file_id:
           return {'status': 'error', 'result': 'CE', ...}
   else:
       file_id = None
   ```

2. **遍历所有测试点**
   ```python
   for i, test_case in enumerate(test_cases):
       # 运行代码
       result = self._run_code(
           run_cmd, language, test_case['input'],
           time_limit, memory_limit, file_id, code
       )
       
       # 比较输出
       is_correct = self._compare_output(
           result['stdout'], test_case['output']
       )
       
       # 记录结果
       test_results.append({
           'id': i + 1,
           'status': 'AC' if is_correct else result['status'],
           'score': score_per_test if is_correct else 0,
           ...
       })
   ```

3. **计算总分**
   ```python
   total_score = sum(tc['score'] for tc in test_results)
   final_result = self._determine_final_result(test_results)
   
   return {
       'status': 'success',
       'result': final_result,
       'score': total_score,
       'time': max(tc['time'] for tc in test_results),
       'memory': max(tc['memory'] for tc in test_results),
       'test_cases': test_results
   }
   ```

##### `_compile_code()` - 编译代码

**关键特性**: 使用 `copyOutCached` 机制缓存编译后的二进制文件

```python
def _compile_code(self, code, language, compile_cmd):
    """
    编译代码并缓存二进制文件
    
    流程:
    1. 构建编译请求
    2. 发送 POST /run 到 go-judge
    3. 获取缓存文件的 fileId
    4. 返回 fileId 供后续运行使用
    """
    
    payload = {
        'cmd': [{
            'args': compile_cmd,  # ['/usr/bin/g++', '-std=c++17', ...]
            'env': ['PATH=/usr/bin:/bin'],
            'files': [
                {'content': ''},  # stdin
                {'name': 'stdout', 'max': 10240},
                {'name': 'stderr', 'max': 10240}
            ],
            'cpuLimit': 10000000000,  # 10秒 (纳秒)
            'memoryLimit': 536870912,  # 512MB (字节)
            'procLimit': 50,
            'copyIn': {
                f'main.{ext}': {'content': code}
            },
            'copyOut': ['stdout', 'stderr'],
            'copyOutCached': ['main']  # 缓存编译后的 main 文件
        }]
    }
    
    response = requests.post(f'{self.go_judge_url}/run', json=payload)
    results = response.json()
    result = results[0]
    
    if result['status'] != 'Accepted' or result['exitStatus'] != 0:
        # 编译失败
        return None
    
    # 获取缓存文件的 fileId
    file_id = result.get('fileIds', {}).get('main')
    return file_id
```

**注意事项**:
- 编译超时设置为 10 秒
- 内存限制为 512MB
- 使用 `copyOutCached` 缓存编译产物
- 每个编译请求都会生成一个新的 fileId

##### `_run_code()` - 运行代码

```python
def _run_code(self, run_cmd, language, input_data, 
              time_limit, memory_limit, file_id=None, code=None):
    """
    运行代码
    
    Args:
        run_cmd: 运行命令 (如 ['/w/main'])
        language: 编程语言
        input_data: 输入数据
        time_limit: 时间限制 (ms)
        memory_limit: 内存限制 (MB)
        file_id: 缓存文件的 fileId (编译型语言)
        code: 源代码 (解释型语言)
    """
    
    # 构建 copyIn
    copy_in = {}
    if file_id:
        # 使用缓存的编译文件
        copy_in['main'] = {'fileId': file_id}
    elif not self._get_compile_command(language):
        # 解释型语言，直接复制源代码
        copy_in[f'main.{self._get_file_extension(language)}'] = {
            'content': code
        }
    
    payload = {
        'cmd': [{
            'args': run_cmd,
            'env': ['PATH=/usr/bin:/bin', 'HOME=/w'],
            'files': [
                {'content': input_data},  # stdin
                {'name': 'stdout', 'max': 10485760},  # 10MB
                {'name': 'stderr', 'max': 10485760}
            ],
            'cpuLimit': time_limit * 1000000,  # ms -> ns
            'memoryLimit': memory_limit * 1048576,  # MB -> bytes
            'procLimit': 50,
            'copyIn': copy_in,
            'copyOut': ['stdout', 'stderr']
        }]
    }
    
    response = requests.post(f'{self.go_judge_url}/run', json=payload)
    results = response.json()
    result = results[0]
    
    # 解析结果
    return {
        'status': self._map_status(result['status']),
        'time': result.get('time', 0) // 1000000,  # ns -> ms
        'memory': result.get('memory', 0) // 1024,  # bytes -> KB
        'stdout': result['files'][1].get('content', ''),
        'stderr': result['files'][2].get('content', '')
    }
```

##### `_compare_output()` - 比较输出

**关键特性**: 规范化空白字符后比较

```python
def _compare_output(self, actual, expected):
    """
    比较程序输出与期望输出
    
    规则:
    1. 去除首尾空白
    2. 将所有连续空白（空格、制表符、换行符）替换为单个空格
    3. 比较规范化后的字符串
    
    示例:
    - "1  2\n3" == "1 2 3"  ✅
    - "hello   world" == "hello world"  ✅
    - "1 2 3" == "1 2 4"  ❌
    """
    import re
    
    def normalize(text):
        # 去除首尾空白
        text = text.strip()
        # 将连续空白替换为单个空格
        text = re.sub(r'\s+', ' ', text)
        return text
    
    return normalize(actual) == normalize(expected)
```

---

### 2. Celery 任务 (`apps/judge/tasks.py`)

#### 2.1 任务定义

```python
from celery import shared_task
from apps.problem.models import Submission, TestCaseResult

@shared_task(bind=True, max_retries=3)
def judge_task(self, submission_id):
    """
    异步评测任务
    
    Args:
        submission_id: 提交记录 ID
    """
    try:
        # 1. 获取提交记录
        submission = Submission.objects.get(id=submission_id)
        submission.status = 'JUDGING'
        submission.save()
        
        # 2. 读取测试用例
        test_cases = load_test_cases(submission.problem.test_cases_file)
        
        # 3. 执行评测
        from apps.judge.adapter import judge_adapter
        result = judge_adapter.judge(
            code=submission.code,
            language=submission.language,
            test_cases=test_cases,
            time_limit=submission.problem.time_limit,
            memory_limit=submission.problem.memory_limit
        )
        
        # 4. 保存评测结果
        if result['status'] == 'success':
            submission.result = result['result']
            submission.score = result['score']
            submission.execution_time = result['time']
            submission.memory_usage = result['memory']
            submission.status = 'ACCEPTED' if result['result'] == 'AC' else 'COMPLETED'
        else:
            submission.result = 'CE'
            submission.status = 'COMPLETED'
        
        submission.save()
        
        # 5. 保存每个测试点的结果
        for tc_result in result['test_cases']:
            TestCaseResult.objects.create(
                submission=submission,
                test_case_id=tc_result['id'],
                status=tc_result['status'],
                score=tc_result['score'],
                execution_time=tc_result['time'],
                memory_usage=tc_result['memory'],
                stdout=tc_result.get('stdout', ''),
                stderr=tc_result.get('stderr', '')
            )
        
    except Exception as e:
        # 重试逻辑
        raise self.retry(exc=e, countdown=60)
```

#### 2.2 任务触发

在 Submission 视图中触发异步任务：

```python
from apps.judge.tasks import judge_task

class SubmissionCreateView(APIView):
    def post(self, request):
        # 1. 创建提交记录
        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            code=data['code'],
            language=data['language'],
            status='PENDING'
        )
        
        # 2. 触发异步评测任务
        judge_task.delay(submission.id)
        
        return Response({
            'message': '提交成功，正在评测',
            'submission_id': submission.id
        })
```

---

### 3. go-judge 配置

#### 3.1 Docker 配置 (`docker-compose.yml`)

```yaml
services:
  gojudge:
    build:
      context: .
      dockerfile: deploy/Dockerfile.gojudge
    container_name: zjoj-gojudge
    restart: always
    privileged: true  # 需要特权模式创建 cgroup
    shm_size: 256m
    ports:
      - "5050:5050"
    volumes:
      - /tmp:/w  # 工作目录
    environment:
      - GO_JUDGE_HTTP_ADDR=0.0.0.0:5050
    networks:
      - zjoj-network
```

#### 3.2 自定义镜像 (`deploy/Dockerfile.gojudge`)

```dockerfile
# 多阶段构建
FROM criyle/go-judge:latest AS go-judge

# 第二阶段：基于 Debian 安装编译器
FROM debian:latest

# 更换为阿里云镜像源加速下载
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装编译器
RUN apt-get update && apt-get install -y \
    g++ gcc python3 python3-pip default-jdk \
    && rm -rf /var/lib/apt/lists/*

# 从第一阶段复制 go-judge 二进制文件
WORKDIR /opt
COPY --from=go-judge /opt/go-judge /opt/
COPY --from=go-judge /opt/mount.yaml /opt/

EXPOSE 5050/tcp 5051/tcp 5052/tcp

ENTRYPOINT ["./go-judge"]
```

**关键点**:
- 使用多阶段构建减小镜像体积
- 基于 Debian 安装编译器（g++, gcc, python3, jdk）
- 保持 root 用户运行（go-judge 需要 root 权限创建 cgroup）
- 不挂载宿主机文件系统，使用容器内的编译器

---

## 📊 评测状态说明

### 状态码映射

| go-judge 状态 | ZJOJ 状态 | 说明 |
|--------------|----------|------|
| Accepted | AC | 答案正确 |
| Wrong Answer | WA | 答案错误 |
| Time Limit Exceeded | TLE | 超时 |
| Memory Limit Exceeded | MLE | 超内存 |
| Runtime Error | RE | 运行时错误 |
| Compilation Error | CE | 编译错误 |
| Output Limit Exceeded | OLE | 输出超限 |
| System Error | SE | 系统错误 |

### 评分规则

- **AC (Accepted)**: 所有测试点通过，得满分
- **WA (Wrong Answer)**: 部分测试点通过，按比例得分
- **TLE/MLE/RE**: 未通过的测试点得 0 分
- **CE**: 编译失败，得 0 分

**示例**:
```
题目有 10 个测试点，每个 10 分
- 8 个 AC → 80 分
- 5 个 AC, 5 个 WA → 50 分
- 全部 WA → 0 分
```

---

## 🔍 调试技巧

### 1. 查看 go-judge 日志

```bash
docker logs zjoj-gojudge --tail 50
```

### 2. 手动测试 go-judge API

```bash
curl -X POST http://localhost:5050/run \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": [{
      "args": ["/bin/echo", "hello"],
      "env": ["PATH=/usr/bin:/bin"],
      "files": [
        {"content": ""},
        {"name": "stdout", "max": 1024},
        {"name": "stderr", "max": 1024}
      ],
      "cpuLimit": 1000000000,
      "memoryLimit": 268435456,
      "procLimit": 50
    }]
  }'
```

### 3. 测试编译功能

```bash
# 编译 C++ 代码
curl -X POST http://localhost:5050/run \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": [{
      "args": ["/usr/bin/g++", "-std=c++17", "-o", "/w/main", "/w/main.cpp"],
      "env": ["PATH=/usr/bin:/bin"],
      "files": [
        {"content": ""},
        {"name": "stdout", "max": 10240},
        {"name": "stderr", "max": 10240}
      ],
      "cpuLimit": 10000000000,
      "memoryLimit": 536870912,
      "procLimit": 50,
      "copyIn": {
        "main.cpp": {
          "content": "#include<iostream>\nusing namespace std;\nint main(){cout<<\"Hello\";return 0;}"
        }
      },
      "copyOut": ["stdout", "stderr"],
      "copyOutCached": ["main"]
    }]
  }'
```

### 4. 查看 Celery Worker 日志

```bash
docker logs zjoj-celery --tail 100
```

---

## ⚠️ 常见问题

### Q1: 编译失败 (CE)

**可能原因**:
1. go-judge 服务未启动
2. 编译器路径错误
3. 代码语法错误

**解决方法**:
```bash
# 检查 go-judge 是否运行
docker ps | grep gojudge

# 检查编译器是否存在
docker exec zjoj-gojudge which g++

# 查看编译错误信息
docker logs zjoj-celery | grep "Compile result"
```

### Q2: 评测超时 (TLE)

**可能原因**:
1. 代码死循环
2. 时间限制设置过短
3. go-judge 响应慢

**解决方法**:
```python
# 增加时间限制
submission.problem.time_limit = 5000  # 5秒

# 检查 go-judge 性能
curl http://localhost:5050/version
```

### Q3: 内存超限 (MLE)

**可能原因**:
1. 代码内存泄漏
2. 内存限制设置过低
3. go-judge ExtraMemoryLimit 过小

**解决方法**:
```yaml
# docker-compose.yml 中增加额外内存限制
command: ["-extra-memory-limit", "128m"]
```

### Q4: 系统错误 (SE)

**可能原因**:
1. go-judge 沙箱崩溃
2. cgroup 权限不足
3. Docker 配置问题

**解决方法**:
```bash
# 重启 go-judge
docker compose restart gojudge

# 检查 cgroup 权限
docker exec zjoj-gojudge ls -la /sys/fs/cgroup/memory/gojudge/

# 确保 privileged 模式
docker inspect zjoj-gojudge | grep Privileged
```

---

## 📈 性能优化建议

### 1. 并行评测

```python
# 使用 Celery 的 group 并行处理多个测试点
from celery import group

tasks = group([
    judge_single_test.s(submission_id, i, test_case)
    for i, test_case in enumerate(test_cases)
])
results = tasks.apply_async()
```

### 2. 编译缓存

```python
# 相同代码+语言的编译结果可以缓存
import hashlib

cache_key = f"{hashlib.md5(code.encode()).hexdigest()}_{language}"
if cache_key in compilation_cache:
    file_id = compilation_cache[cache_key]
else:
    file_id = self._compile_code(code, language, compile_cmd)
    compilation_cache[cache_key] = file_id
```

### 3. 连接池

```python
# 使用 requests.Session 复用连接
session = requests.Session()
session.mount('http://', HTTPAdapter(pool_connections=10, pool_maxsize=20))

response = session.post(f'{self.go_judge_url}/run', json=payload)
```

---

## 🔗 相关文档

- [go-judge 官方文档](GOJUDGE_DOCUMENTATION.md)
- [API 参考](04-API_REFERENCE.md)
- [数据库设计](07-DATABASE.md)

---

**最后更新**: 2026-04-27
