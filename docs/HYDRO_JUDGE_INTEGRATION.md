# HydroJudge 集成指南

## 📋 概述

已成功集成 HydroJudge 评测系统到 ZJOJ 平台。

## ✅ 已完成的工作

### 1. 数据库模型

创建了以下模型（`apps/problem/models.py`）：

- **Submission** - 代码提交记录
  - 存储用户提交的代码
  - 记录评测状态和结果
  - 支持多种编程语言（C/C++/Java/Python）

- **TestCaseResult** - 测试点结果
  - 存储每个测试点的详细评测结果
  - 包括运行时间、内存使用、得分等

### 2. HydroJudge 客户端

创建了 `apps/judge/hydro_client.py`：

```python
from apps.judge.hydro_client import HydroJudgeClient

client = HydroJudgeClient()
result = client.judge(submission)
```

**功能**：
- 与 HydroJudge 沙箱服务通信
- 准备评测数据（题目配置、测试用例、用户代码）
- 解析评测结果
- 错误处理和超时控制

### 3. 评测任务处理器

创建了 `apps/judge/task_processor.py`：

```python
from apps.judge.task_processor import JudgeTaskProcessor

processor = JudgeTaskProcessor()
success = processor.process(submission_id)
```

**功能**：
- 异步处理评测任务
- 更新数据库中的评测结果
- 保存每个测试点的详细信息
- 错误处理和日志记录

### 4. API 序列化器

在 `apps/problem/serializers.py` 中添加了：

- **SubmitCodeSerializer** - 提交代码验证
- **SubmissionListSerializer** - 提交列表展示
- **SubmissionDetailSerializer** - 提交详情（含测试点结果）
- **TestCaseResultSerializer** - 测试点结果展示

## 🔧 配置说明

### 1. 注册 judge 应用

在 `ZJOJ/settings.py` 中添加：

```python
INSTALLED_APPS = [
    # ... 其他应用
    'apps.judge',
]
```

### 2. 配置 HydroJudge 服务地址

在 `ZJOJ/settings.py` 中添加：

```python
# HydroJudge 配置
HYDRO_JUDGE_URL = 'http://localhost:5050'  # HydroJudge 服务地址
HYDRO_JUDGE_TIMEOUT = 30  # 超时时间（秒）
```

### 3. 启动 HydroJudge 服务

需要单独启动 HydroJudge 沙箱服务：

```bash
# 克隆 HydroJudge
git clone https://github.com/hydro-dev/HydroJudge.git
cd HydroJudge

# 安装依赖
npm install

# 启动服务
npm start
```

## 📝 使用示例

### 提交代码

```python
# views.py 中添加提交接口
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.problem.serializers import SubmitCodeSerializer
from apps.judge.task_processor import JudgeTaskProcessor

class SubmitCodeView(APIView):
    """提交代码接口"""
    
    def post(self, request):
        serializer = SubmitCodeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # 创建提交记录
            submission = serializer.save()
            
            # 异步执行评测（建议使用 Celery）
            processor = JudgeTaskProcessor()
            # 同步评测（生产环境应改为异步）
            processor.process(submission.id)
            
            return Response({
                'message': '提交成功',
                'submission_id': submission.id
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
```

### 查询提交结果

```python
from apps.problem.models import Submission
from apps.problem.serializers import SubmissionDetailSerializer

class SubmissionDetailView(APIView):
    """提交详情接口"""
    
    def get(self, request, submission_id):
        try:
            submission = Submission.objects.get(id=submission_id)
            serializer = SubmissionDetailSerializer(submission)
            return Response(serializer.data)
        except Submission.DoesNotExist:
            return Response({
                'error': '提交记录不存在'
            }, status=status.HTTP_404_NOT_FOUND)
```

## 🚀 下一步工作

### 1. 添加 API 路由

在 `apps/problem/urls.py` 中添加：

```python
from apps.problem.views import SubmitCodeView, SubmissionListView, SubmissionDetailView

urlpatterns = [
    # ... 现有路由
    
    # 提交相关
    path('submissions/', SubmissionListView.as_view(), name='submission-list'),
    path('submissions/submit/', SubmitCodeView.as_view(), name='submit-code'),
    path('submissions/<int:submission_id>/', SubmissionDetailView.as_view(), name='submission-detail'),
]
```

### 2. 实现异步评测

使用 Celery 实现异步评测：

```python
# tasks.py
from celery import shared_task
from apps.judge.task_processor import JudgeTaskProcessor

@shared_task
def judge_submission(submission_id):
    processor = JudgeTaskProcessor()
    return processor.process(submission_id)

# views.py 中调用
judge_submission.delay(submission.id)
```

### 3. 添加实时推送

使用 WebSocket 推送评测结果：

```python
# 当评测完成时
channels.layers.get_channel_layer().group_send(
    f'user_{user_id}',
    {
        'type': 'judgement_complete',
        'submission_id': submission.id,
        'result': submission.result,
        'score': submission.score
    }
)
```

## 📊 评测流程

```
用户提交代码
    ↓
创建 Submission 记录（状态：等待评测）
    ↓
调用 JudgeTaskProcessor
    ↓
更新状态为"评测中"
    ↓
HydroJudgeClient 准备评测数据
    ↓
发送请求到 HydroJudge 沙箱
    ↓
沙箱编译并运行代码
    ↓
逐组测试点对比输出
    ↓
返回评测结果
    ↓
保存结果到数据库
    ↓
更新 Submission 状态为"已完成"
```

## ⚠️ 注意事项

1. **测试用例存储**：需要在 `media/problems/{problem_id}/tests/` 目录下存放 `.in` 和 `.out` 文件

2. **安全性**：
   - HydroJudge 沙箱提供隔离环境
   - 限制时间和内存使用
   - 防止恶意代码

3. **性能优化**：
   - 使用异步任务队列（Celery）
   - 缓存热门题目的测试数据
   - 批量评测优化

4. **错误处理**：
   - 网络超时
   - 沙箱服务不可用
   - 编译错误
   - 运行时错误

## 🎯 支持的评测结果

- **AC** (Accepted) - 答案正确
- **WA** (Wrong Answer) - 答案错误
- **TLE** (Time Limit Exceeded) - 超时
- **MLE** (Memory Limit Exceeded) - 超内存
- **RE** (Runtime Error) - 运行时错误
- **CE** (Compilation Error) - 编译错误
- **SE** (System Error) - 系统错误

## 📖 相关文档

- [HydroJudge GitHub](https://github.com/hydro-dev/HydroJudge)
- [PROBLEM_MODULE.md](./PROBLEM_MODULE.md) - 题目模块详细文档
