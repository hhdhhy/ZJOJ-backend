#!/usr/bin/env python3
"""在服务器上添加所有5个错误解决方案文档"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
sys.path.insert(0, '/home/zjoj')
django.setup()

from apps.ai_assistant.models import KnowledgeBase
from apps.ai_assistant.rag_engine import RAGEngine
import uuid

print("=" * 60)
print("批量添加5个错误解决方案文档")
print("=" * 60)

engine = RAGEngine()
added = 0

# 文档列表
docs_data = [
    {
        'title': '图论 TLE 优化技巧',
        'doc_type': 'error_solution',
        'error_type': 'TLE',
        'content': """# 图论 TLE (Time Limit Exceeded) 优化技巧

## 1. 选择合适的算法

### 最短路径算法选择
| 算法 | 时间复杂度 | 适用场景 |
|------|-----------|---------|
| BFS | O(V+E) | 无权图最短路 |
| Dijkstra | O((V+E)logV) | 非负权图 |
| SPFA | O(kE) | 可能有负权，但不稳定 |
| Floyd | O(V³) | 多源最短路，小图 |

## 2. 使用堆优化 Dijkstra

### 朴素 Dijkstra - O(V²) - 可能TLE
```python
def dijkstra_naive(graph, start, n):
    dist = [float('inf')] * n
    visited = [False] * n
    dist[start] = 0
    
    for _ in range(n):
        u = -1
        min_dist = float('inf')
        for i in range(n):
            if not visited[i] and dist[i] < min_dist:
                min_dist = dist[i]
                u = i
        if u == -1: break
        visited[u] = True
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist
```

### 堆优化 Dijkstra - O((V+E)logV) - 推荐
```python
import heapq
def dijkstra_heap(graph, start, n):
    dist = [float('inf')] * n
    dist[start] = 0
    pq = [(0, start)]
    
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    return dist
```

## 3. 常见 TLE 原因
1. ❌ 算法选择不当（如用 Floyd 处理大图）
2. ❌ 没有使用堆优化
3. ❌ 重复建图或重复计算
4. ❌ 使用邻接矩阵处理稀疏图
5. ❌ 没有剪枝优化

## 4. 性能对比
| 优化前 | 优化后 | 提升倍数 |
|--------|--------|---------|
| O(V²) | O((V+E)logV) | 10-100x |
| 邻接矩阵 | 邻接表 | 2-10x |
""",
        'source': 'ZJOJ 知识库'
    },
    {
        'title': '字符串 RE 常见问题',
        'doc_type': 'error_solution',
        'error_type': 'RE',
        'content': """# 字符串 RE (Runtime Error) 常见问题

## 1. 数组/字符串越界（最常见）
```python
# 错误示例
s = "hello"
print(s[5])  # IndexError: string index out of range

# 正确做法
if 0 <= i < len(s):
    print(s[i])
```

## 2. 空字符串处理
```python
# 错误：没有检查空字符串
s = input()
first_char = s[0]  # 如果 s 为空，IndexError

# 正确：先检查
if s:  # 或者 len(s) > 0
    first_char = s[0]
```

## 3. 递归深度超限
Python 默认递归深度限制为 1000。

```python
# 解决方法1：增加递归限制
import sys
sys.setrecursionlimit(10000)

# 解决方法2：改为迭代（推荐）
def process_iterative(s):
    for char in s:
        pass  # 处理字符
```

## 4. 内存不足
```python
# 错误：创建过多临时字符串 O(n²)
result = ""
for i in range(100000):
    result += str(i)

# 正确：使用列表拼接 O(n)
result_list = []
for i in range(100000):
    result_list.append(str(i))
result = "".join(result_list)
```

## 5. 常见 RE 错误代码
| 错误类型 | 原因 | 解决方法 |
|---------|------|---------|
| IndexError | 索引越界 | 检查边界 |
| RecursionError | 递归太深 | 改迭代或增加限制 |
| MemoryError | 内存不足 | 优化算法 |
""",
        'source': 'ZJOJ 知识库'
    },
    {
        'title': 'WA 常见原因及调试方法',
        'doc_type': 'error_solution',
        'error_type': 'WA',
        'content': """# WA (Wrong Answer) 常见原因及调试方法

## 1. 边界条件错误（占 WA 的 40%+）

### 检查清单
- [ ] n=0, n=1 的情况是否正确？
- [ ] 空输入是否处理？
- [ ] 最大值、最小值是否考虑？
- [ ] 数组索引是否越界？

```python
# 错误示例
def factorial(n):
    result = 1
    for i in range(1, n):  # 错误：应该是 range(1, n+1)
        result *= i
    return result
```

## 2. 数据类型和精度问题

### 浮点数精度
```python
# 错误：直接比较浮点数
if a / b == 0.3:  # 可能因为精度问题失败

# 正确：使用误差范围
if abs(a / b - 0.3) < 1e-9:
```

## 3. 格式错误
- 输出格式不匹配（空格、换行）
- 多余的空格或缺少换行

## 4. 逻辑错误
```python
# 错误：逻辑运算符优先级
if a > 0 and b > 0 or c > 0:  # 可能是 (a>0 and b>0) or c>0

# 正确：加括号明确意图
if (a > 0 and b > 0) or c > 0:
```

## 5. 调试方法

### 方法1：对小数据手工验证
用最小的测试数据，手工计算期望输出，然后对比程序输出。

### 方法2：打印中间结果
```python
import sys
print(f"DEBUG: n={n}, arr={arr}", file=sys.stderr)
```

### 方法3：对拍（强烈推荐）
写一个暴力解法（保证正确但慢），与优化解法对比结果。

## 6. WA 调试流程
1. 检查样例是否通过
2. 检查边界条件
3. 小数据手工验证
4. 打印中间结果
5. 对拍测试
6. 找到错误并修复
""",
        'source': 'ZJOJ 知识库'
    },
    {
        'title': 'TLE 时间复杂度优化',
        'doc_type': 'error_solution',
        'error_type': 'TLE',
        'content': """# TLE (Time Limit Exceeded) 时间复杂度优化

## 1. 理解时间复杂度

### 常见复杂度等级
| 复杂度 | n=10⁵ 时的操作次数 | 是否可行 |
|--------|-------------------|---------|
| O(1) | 1 | ✅ |
| O(log n) | ~17 | ✅ |
| O(n) | 10⁵ | ✅ |
| O(n log n) | ~1.7×10⁶ | ✅ |
| O(n²) | 10¹⁰ | ❌ TLE |
| O(n³) | 10¹⁵ | ❌ TLE |

**一般规则**：1秒 ≈ 10⁸ 次操作

## 2. 常见优化策略

### 策略1：选择更优算法
```python
# 错误：冒泡排序 O(n²)
def bubble_sort(arr):
    for i in range(n):
        for j in range(n-1-i):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

# 正确：使用内置排序 O(n log n)
arr.sort()
```

### 策略2：使用前缀和
```python
# 错误：每次查询 O(n)
def range_sum(arr, l, r):
    return sum(arr[l:r+1])

# 正确：前缀和 O(1) 查询
prefix = [0] * (n + 1)
for i in range(n):
    prefix[i+1] = prefix[i] + arr[i]

def range_sum_fast(l, r):
    return prefix[r+1] - prefix[l]
```

### 策略3：二分查找优化
```python
# 错误：线性查找 O(n)
def find_target(arr, target):
    for i, val in enumerate(arr):
        if val == target: return i

# 正确：二分查找 O(log n)
import bisect
idx = bisect.bisect_left(arr, target)
```

### 策略4：双指针技巧
```python
# 错误：暴力枚举 O(n²)
for i in range(n):
    for j in range(i+1, n):
        if arr[i] + arr[j] == target: ...

# 正确：双指针 O(n)
left, right = 0, len(arr)-1
while left < right:
    s = arr[left] + arr[right]
    if s == target: return (left, right)
    elif s < target: left += 1
    else: right -= 1
```

## 3. 数据结构优化
- 使用哈希表：O(n) → O(1) 查找
- 使用堆：维护前 K 大/小元素
- 使用前缀和/差分：区间查询优化

## 4. I/O 优化
```python
import sys
input = sys.stdin.readline  # 更快的输入

# 批量输出
output = []
for i in range(n):
    output.append(str(result[i]))
print("\\n".join(output))
```
""",
        'source': 'ZJOJ 知识库'
    }
]

# 批量添加
for i, data in enumerate(docs_data, 2):
    try:
        # 检查是否已存在
        existing = KnowledgeBase.objects.filter(
            title=data['title'],
            doc_type=data['doc_type'],
            error_type=data['error_type']
        ).first()
        
        if existing:
            print(f"⚠️  跳过已存在: {data['title']}")
            continue
        
        data['vector_id'] = str(uuid.uuid4())
        data['is_active'] = True
        
        doc = KnowledgeBase.objects.create(**data)
        print(f"✅ [{i}/5] 已创建: {doc.title}")
        
        # 同步到向量数据库
        engine.vector_store.add_document(
            doc_id=doc.vector_id,
            text=doc.content,
            metadata={
                'title': doc.title,
                'type': doc.doc_type,
                'doc_id': doc.id,
                'error_type': doc.error_type,
            }
        )
        print(f"   📚 已同步到向量数据库")
        added += 1
        
    except Exception as e:
        print(f"❌ [{i}/5] 创建失败 {data['title']}: {e}")

print("\n" + "=" * 60)
print(f"批量添加完成！")
print(f"  ✅ 新增: {added} 个文档")
print(f"  📊 总计尝试: {len(docs_data)} 个文档")
print("=" * 60)
