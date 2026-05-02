#!/usr/bin/env python3
"""在服务器上直接添加错误解决方案文档"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
sys.path.insert(0, '/home/zjoj')
django.setup()

from apps.ai_assistant.models import KnowledgeBase
from apps.ai_assistant.rag_engine import RAGEngine
import uuid

print("=" * 60)
print("开始添加错误解决方案文档")
print("=" * 60)

engine = RAGEngine()

# 文档1: 动态规划 WA
try:
    doc1 = KnowledgeBase.objects.create(
        title='动态规划 WA 常见原因',
        doc_type='error_solution',
        error_type='WA',
        content="""# 动态规划 WA (Wrong Answer) 常见原因

## 1. 状态定义错误
dp[i] 的含义不清晰，导致状态转移方程错误。

### 典型错误
```python
# 错误示例：求最长上升子序列
dp = [0] * n
for i in range(n):
    for j in range(i):
        if nums[j] < nums[i]:
            dp[i] = max(dp[i], dp[j] + 1)  # 忘记初始化 dp[i] = 1
```

### 正确做法
```python
dp = [1] * n  # 每个元素至少长度为1
for i in range(n):
    for j in range(i):
        if nums[j] < nums[i]:
            dp[i] = max(dp[i], dp[j] + 1)
```

## 2. 边界条件处理不当
- 初始值设置错误：dp[0] 应该是什么值？
- 边界情况遗漏：空数组、单个元素等特殊情况
- 数组越界：访问 dp[-1] 或 dp[n]

## 3. 状态转移方程错误
- 方向错误：应该从前往后还是从后往前更新？
- 依赖关系错误：当前状态依赖哪些前驱状态？
- 重复计算：是否重复计算了某些状态？

## 4. 调试技巧
1. **小数据测试**：用最小的测试数据手动模拟 DP 过程
2. **打印 DP 表**：检查是否有异常值
3. **对拍**：写一个暴力解法对比结果

## 常见陷阱
- 忘记初始化 dp 数组
- 循环顺序错误（外层和内层循环）
- 状态维度不够（有些问题需要二维甚至三维 DP）
""",
        source='ZJOJ 知识库',
        is_active=True,
        vector_id=str(uuid.uuid4())
    )
    print(f"✅ 已创建: {doc1.title}")
    
    # 同步到向量数据库
    engine.vector_store.add_document(
        doc_id=doc1.vector_id,
        text=doc1.content,
        metadata={
            'title': doc1.title,
            'type': doc1.doc_type,
            'doc_id': doc1.id,
            'error_type': doc1.error_type,
        }
    )
    print(f"   📚 已同步到向量数据库")
except Exception as e:
    print(f"❌ 创建失败: {e}")

print("\n完成！")
