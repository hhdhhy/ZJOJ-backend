# -*- coding: utf-8 -*-
"""
批量添加错误解决方案到知识库
包含算法特定的错误分析和通用错误类型指南
"""
import os
import sys
import django
import uuid

# 设置 Django 环境
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
django.setup()

from apps.ai_assistant.models import KnowledgeBase
from apps.ai_assistant.rag_engine import RAGEngine

# 定义要添加的错误解决方案文档
solutions = [
    {
        'title': '动态规划 WA 常见原因',
        'doc_type': 'error_solution',
        'error_type': 'WA',
        'content': '''# 动态规划 WA (Wrong Answer) 常见原因

## 1. 状态定义错误

### 问题描述
dp[i] 或 dp[i][j] 的含义不清晰，导致状态转移方程错误。

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
# 正确示例
dp = [1] * n  # 每个元素至少长度为1
for i in range(n):
    for j in range(i):
        if nums[j] < nums[i]:
            dp[i] = max(dp[i], dp[j] + 1)
```

## 2. 边界条件处理不当

### 常见问题
- **初始值设置错误**：dp[0] 应该是什么值？
- **边界情况遗漏**：空数组、单个元素等特殊情况
- **数组越界**：访问 dp[-1] 或 dp[n]

### 示例：背包问题
```python
# 错误：没有正确处理容量为0的情况
dp = [0] * (capacity + 1)
for item in items:
    for j in range(capacity, item.weight - 1, -1):
        dp[j] = max(dp[j], dp[j - item.weight] + item.value)

# 正确：确保边界条件正确
dp = [0] * (capacity + 1)
for item in items:
    for j in range(capacity, item.weight - 1, -1):
        if j >= item.weight:  # 确保不会越界
            dp[j] = max(dp[j], dp[j - item.weight] + item.value)
```

## 3. 状态转移方程错误

### 常见错误类型
1. **方向错误**：应该从前往后还是从后往前更新？
2. **依赖关系错误**：当前状态依赖哪些前驱状态？
3. **重复计算**：是否重复计算了某些状态？

### 示例：0/1背包 vs 完全背包
```python
# 0/1背包：从后往前遍历（每个物品只能选一次）
for item in items:
    for j in range(capacity, item.weight - 1, -1):
        dp[j] = max(dp[j], dp[j - item.weight] + item.value)

# 完全背包：从前往后遍历（每个物品可以选多次）
for item in items:
    for j in range(item.weight, capacity + 1):
        dp[j] = max(dp[j], dp[j - item.weight] + item.value)
```

## 4. 数据类型溢出

### 问题
当结果很大时，int 可能溢出。

### 解决
```python
# Python 不需要担心，但 C++ 需要注意
# C++ 中使用 long long
long long dp[1005];
```

## 5. 调试技巧

### 方法1：小数据测试
用最小的测试数据手动模拟 DP 过程，验证每一步是否正确。

### 方法2：打印 DP 表
```python
# 打印整个 DP 表，检查是否有异常值
for row in dp:
    print(row)
```

### 方法3：对拍
写一个暴力解法，与小数据的结果对比。

## 6. 常见陷阱

1. **忘记初始化**：dp 数组的初始值很重要
2. **循环顺序错误**：外层循环和内层循环的顺序可能影响结果
3. **状态维度不够**：有些问题需要二维甚至三维 DP
4. **最优子结构不成立**：确认问题是否真的适合用 DP

## 总结

动态规划 WA 的主要原因：
- ✅ 仔细定义状态含义
- ✅ 正确处理边界条件
- ✅ 验证状态转移方程
- ✅ 注意循环方向和顺序
- ✅ 用小数据测试验证
''',
        'source': 'ZJOJ 知识库',
        'is_active': True
    },
    
    {
        'title': '图论 TLE 优化技巧',
        'doc_type': 'error_solution',
        'error_type': 'TLE',
        'content': '''# 图论 TLE (Time Limit Exceeded) 优化技巧

## 1. 选择合适的算法

### 最短路径算法选择
| 算法 | 时间复杂度 | 适用场景 |
|------|-----------|---------|
| BFS | O(V+E) | 无权图最短路 |
| Dijkstra | O((V+E)logV) | 非负权图 |
| SPFA | O(kE) | 可能有负权，但不稳定 |
| Floyd | O(V³) | 多源最短路，小图 |

### 常见错误
```python
# 错误：在稀疏图上使用 Floyd
# V=10000 时，V³ = 10^12，必然 TLE

# 正确：使用 Dijkstra
import heapq
def dijkstra(graph, start, n):
    dist = [float('inf')] * n
    dist[start] = 0
    pq = [(0, start)]
    
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    
    return dist
```

## 2. 使用堆优化 Dijkstra

### 朴素 Dijkstra - O(V²)
```python
# TLE 风险高
def dijkstra_naive(graph, start, n):
    dist = [float('inf')] * n
    visited = [False] * n
    dist[start] = 0
    
    for _ in range(n):
        # 找最小距离的未访问节点 - O(V)
        u = -1
        min_dist = float('inf')
        for i in range(n):
            if not visited[i] and dist[i] < min_dist:
                min_dist = dist[i]
                u = i
        
        if u == -1:
            break
        
        visited[u] = True
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    
    return dist
```

### 堆优化 Dijkstra - O((V+E)logV)
```python
# 推荐使用
import heapq

def dijkstra_heap(graph, start, n):
    dist = [float('inf')] * n
    dist[start] = 0
    pq = [(0, start)]
    
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    
    return dist
```

## 3. 避免重复建图

### 错误做法
```python
# 每次查询都重新建图 - TLE
for query in queries:
    graph = build_graph(edges)  # O(E)
    result = dijkstra(graph, query.start, n)
```

### 正确做法
```python
# 只建一次图
graph = build_graph(edges)
for query in queries:
    result = dijkstra(graph, query.start, n)
```

## 4. 使用邻接表而非邻接矩阵

### 邻接矩阵 - O(V²) 空间
```python
# 适合稠密图
graph = [[float('inf')] * n for _ in range(n)]
```

### 邻接表 - O(V+E) 空间
```python
# 适合稀疏图，推荐
graph = [[] for _ in range(n)]
for u, v, w in edges:
    graph[u].append((v, w))
```

## 5. 剪枝优化

### 提前终止
```python
def dijkstra_with_pruning(graph, start, end, n):
    dist = [float('inf')] * n
    dist[start] = 0
    pq = [(0, start)]
    
    while pq:
        d, u = heapq.heappop(pq)
        
        # 已经到达终点，提前退出
        if u == end:
            return d
        
        if d > dist[u]:
            continue
        
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    
    return dist[end]
```

## 6. 并查集优化

### 用于连通性判断
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # 路径压缩
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True
```

## 7. 常见 TLE 原因总结

1. ❌ 算法选择不当（如用 Floyd 处理大图）
2. ❌ 没有使用堆优化
3. ❌ 重复建图或重复计算
4. ❌ 使用邻接矩阵处理稀疏图
5. ❌ 没有剪枝优化
6. ❌ 递归深度过大导致栈溢出

## 8. 性能对比

| 优化前 | 优化后 | 提升倍数 |
|--------|--------|---------|
| O(V²) | O((V+E)logV) | 10-100x |
| 邻接矩阵 | 邻接表 | 2-10x |
| 无剪枝 | 有剪枝 | 1.5-5x |

## 调试建议

1. **估算复杂度**：V=10⁵, E=10⁵ 时，O(V²) 必 TLE
2. **使用计时器**：本地测试运行时间
3. **渐进优化**：先保证正确，再优化性能
''',
        'source': 'ZJOJ 知识库',
        'is_active': True
    },
    
    {
        'title': '字符串 RE 常见问题',
        'doc_type': 'error_solution',
        'error_type': 'RE',
        'content': '''# 字符串 RE (Runtime Error) 常见问题

## 1. 数组/字符串越界

### 最常见的原因
```python
# 错误示例 1：索引越界
s = "hello"
print(s[5])  # IndexError: string index out of range

# 错误示例 2：负数索引
s = "hello"
n = -10
print(s[n])  # 可能得到意外结果或错误

# 正确做法
s = "hello"
if 0 <= i < len(s):
    print(s[i])
```

## 2. 空字符串处理

### 常见错误
```python
# 错误：没有检查空字符串
s = input()
first_char = s[0]  # 如果 s 为空，IndexError

# 正确：先检查
s = input()
if s:  # 或者 len(s) > 0
    first_char = s[0]
else:
    # 处理空字符串的情况
    pass
```

## 3. 递归深度超限

### 问题
Python 默认递归深度限制为 1000。

```python
# 错误：深度递归导致 RecursionError
def process_string(s, idx):
    if idx >= len(s):
        return
    # 处理 s[idx]
    process_string(s, idx + 1)  # 如果 s 很长，会栈溢出

# 解决方法 1：增加递归限制
import sys
sys.setrecursionlimit(10000)

# 解决方法 2：改为迭代
def process_string_iterative(s):
    for char in s:
        # 处理 char
        pass
```

## 4. 内存不足

### 大字符串操作
```python
# 错误：创建过多临时字符串
result = ""
for i in range(100000):
    result += str(i)  # 每次都创建新字符串，O(n²)

# 正确：使用列表拼接
result_list = []
for i in range(100000):
    result_list.append(str(i))
result = "".join(result_list)  # O(n)
```

## 5. 编码问题

### Unicode 错误
```python
# 错误：处理特殊字符
s = "你好世界"
# 在某些环境下可能出现编码错误

# 正确：明确指定编码
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

## 6. 正则表达式灾难性回溯

### 问题
某些正则表达式会导致指数级回溯。

```python
import re

# 危险：可能导致 ReDOS (正则表达式拒绝服务)
pattern = r"(a+)+b"
text = "a" * 10000  # 这会非常慢甚至卡死

# 安全：使用更精确的模式
pattern = r"a+b"
```

## 7. 字符串分割错误

### 常见错误
```python
# 错误：split 后索引越界
s = "hello"
parts = s.split(",")
first = parts[0]  # OK
second = parts[1]  # IndexError: list index out of range

# 正确：检查长度
parts = s.split(",")
if len(parts) > 1:
    second = parts[1]
else:
    second = ""  # 默认值
```

## 8. 文件读取问题

###  EOF 处理
```python
# 错误：没有处理 EOF
while True:
    line = input()  # EOFError
    process(line)

# 正确：捕获异常
import sys
for line in sys.stdin:
    process(line.strip())
```

## 9. 调试技巧

### 方法1：边界测试
```python
# 测试各种边界情况
test_cases = [
    "",           # 空字符串
    "a",          # 单字符
    "a" * 100000, # 超长字符串
    "你好",       # Unicode
    "a b c",      # 含空格
]

for test in test_cases:
    try:
        result = your_function(test)
        print(f"OK: {test[:20]}...")
    except Exception as e:
        print(f"ERROR: {e}")
```

### 方法2：打印关键信息
```python
def debug_string_operation(s):
    print(f"Length: {len(s)}")
    print(f"Type: {type(s)}")
    print(f"First 100 chars: {s[:100]}")
    # ... 你的逻辑
```

## 10. 常见 RE 错误代码

| 错误类型 | 原因 | 解决方法 |
|---------|------|---------|
| IndexError | 索引越界 | 检查边界 |
| RecursionError | 递归太深 | 改迭代或增加限制 |
| MemoryError | 内存不足 | 优化算法 |
| UnicodeError | 编码问题 | 统一使用 UTF-8 |
| EOFError | 输入结束 | 捕获异常 |

## 总结

字符串 RE 的主要预防措施：
- ✅ 始终检查边界条件
- ✅ 处理空字符串和特殊情况
- ✅ 避免过深的递归
- ✅ 使用高效字符串操作
- ✅ 充分测试边界情况
''',
        'source': 'ZJOJ 知识库',
        'is_active': True
    },
    
    {
        'title': 'WA 常见原因及调试方法',
        'doc_type': 'error_solution',
        'error_type': 'WA',
        'content': '''# WA (Wrong Answer) 常见原因及调试方法

## 什么是 WA？

WA 表示你的程序输出了结果，但与标准答案不一致。这是最常见的错误类型之一。

## 1. 边界条件错误

### 最常见的原因（占 WA 的 40%+）

```python
# 错误示例 1：忘记处理 n=0 或 n=1
def factorial(n):
    result = 1
    for i in range(1, n):  # 错误：应该是 range(1, n+1)
        result *= i
    return result

# 错误示例 2：数组边界
arr = [1, 2, 3, 4, 5]
# 访问 arr[5] 或 arr[-6] 都会出错
```

### 检查清单
- [ ] n=0, n=1 的情况是否正确？
- [ ] 空输入是否处理？
- [ ] 最大值、最小值是否考虑？
- [ ] 数组索引是否越界？

## 2. 数据类型和精度问题

### 整数溢出
```python
# Python 不用担心，但 C++/Java 需要注意
# C++ 示例
int a = 1000000000;
int b = 1000000000;
int c = a * b;  // 溢出！应该用 long long
```

### 浮点数精度
```python
# 错误：直接比较浮点数
if a / b == 0.3:  # 可能因为精度问题失败
    ...

# 正确：使用误差范围
if abs(a / b - 0.3) < 1e-9:
    ...
```

## 3. 格式错误

### 输出格式不匹配
```python
# 题目要求：每行输出一个结果
# 错误：所有结果在同一行
print(result1, result2, result3)

# 正确：每行一个
print(result1)
print(result2)
print(result3)
```

### 空格和换行
```python
# 错误：多余的空格
print(f"{a} {b} ")  # 末尾多了空格

# 正确
print(f"{a} {b}")
```

## 4. 逻辑错误

### 条件判断错误
```python
# 错误：逻辑运算符优先级
if a > 0 and b > 0 or c > 0:  # 可能是 (a>0 and b>0) or c>0
    ...

# 正确：加括号明确意图
if (a > 0 and b > 0) or c > 0:
    ...
```

### 循环错误
```python
# 错误：off-by-one
for i in range(n):  # 0 到 n-1
    ...

# 如果需要 1 到 n
for i in range(1, n + 1):
    ...
```

## 5. 特殊情况未处理

```python
# 除法问题
def divide(a, b):
    return a / b  # 如果 b=0 会出错

# 正确
def divide(a, b):
    if b == 0:
        return "undefined"  # 或其他处理方式
    return a / b
```

## 6. 调试方法

### 方法1：对小数据手工验证
```python
# 用最小的测试数据，手工计算期望输出
# 然后对比程序输出

# 示例：求和
# 输入：[1, 2, 3]
# 期望输出：6
# 实际输出：? 
```

### 方法2：打印中间结果
```python
def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    
    # 打印输入
    print(f"DEBUG: n={n}, arr={arr}", file=sys.stderr)
    
    result = compute(arr)
    
    # 打印中间结果
    print(f"DEBUG: result={result}", file=sys.stderr)
    
    print(result)
```

### 方法3：对拍（强烈推荐）
```python
# 写一个暴力解法（保证正确但慢）
def brute_force(arr):
    # 简单直接的实现
    pass

# 写一个优化解法
def optimized_solution(arr):
    # 高效但可能出错的实现
    pass

# 随机测试
import random
for _ in range(1000):
    test_data = generate_random_test()
    expected = brute_force(test_data)
    actual = optimized_solution(test_data)
    if expected != actual:
        print(f"WA! Input: {test_data}")
        print(f"Expected: {expected}")
        print(f"Actual: {actual}")
        break
```

### 方法4：使用在线评测的反馈
- 查看哪些测试点通过，哪些失败
- 分析失败的测试点特征（大数据？边界数据？）

## 7. 常见陷阱

### 陷阱1：变量未初始化
```python
# 错误
sum = 0
for i in range(n):
    sum += arr[i]
# 如果忘记 sum = 0，结果会错误
```

### 陷阱2：修改了不该修改的数据
```python
# 错误：排序改变了原数组
arr.sort()
# 如果后面还需要原数组的顺序，就错了

# 正确：复制一份
sorted_arr = sorted(arr)
```

### 陷阱3：全局变量污染
```python
# 多组测试数据时，忘记重置全局变量
total = 0

for _ in range(t):
    # 应该在每组数据开始时重置 total = 0
    ...
```

## 8. WA 调试流程

```mermaid
graph TD
    A[收到 WA] --> B[检查样例是否通过]
    B -->|否| C[修复样例错误]
    B -->|是| D[检查边界条件]
    D --> E[小数据手工验证]
    E --> F[打印中间结果]
    F --> G[对拍测试]
    G --> H[找到错误]
    H --> I[修复并提交]
```

## 9. 预防 WA 的最佳实践

1. **仔细阅读题目**：理解所有要求和约束
2. **考虑边界情况**：n=0, n=1, 最大值，最小值
3. **小数据测试**：先用样例和小型数据验证
4. **代码审查**：检查常见的逻辑错误
5. **对拍验证**：与暴力解法对比
6. **逐步提交**：先提交简单版本，再优化

## 总结

WA 是最常见的错误，主要原因：
- 40% 边界条件错误
- 25% 逻辑错误
- 15% 格式错误
- 10% 精度问题
- 10% 其他

**记住**：耐心调试，系统性地排查问题！
''',
        'source': 'ZJOJ 知识库',
        'is_active': True
    },
    
    {
        'title': 'TLE 时间复杂度优化',
        'doc_type': 'error_solution',
        'error_type': 'TLE',
        'content': '''# TLE (Time Limit Exceeded) 时间复杂度优化

## 什么是 TLE？

TLE 表示你的程序运行时间超过了题目限制。通常是因为算法效率太低。

## 1. 理解时间复杂度

### 常见复杂度等级
| 复杂度 | 名称 | n=10⁵ 时的操作次数 | 是否可行 |
|--------|------|-------------------|---------|
| O(1) | 常数 | 1 | ✅ |
| O(log n) | 对数 | ~17 | ✅ |
| O(n) | 线性 | 10⁵ | ✅ |
| O(n log n) | 线性对数 | ~1.7×10⁶ | ✅ |
| O(n²) | 平方 | 10¹⁰ | ❌ TLE |
| O(n³) | 立方 | 10¹⁵ | ❌ TLE |
| O(2ⁿ) | 指数 | 巨大 | ❌ TLE |

### 一般规则
- **1秒** ≈ **10⁸** 次操作
- n ≤ 1000：O(n²) 可行
- n ≤ 10⁵：O(n log n) 可行
- n ≤ 10⁶：O(n) 可行

## 2. 常见优化策略

### 策略1：选择更优算法

```python
# 错误：冒泡排序 O(n²)
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

# 正确：快速排序 O(n log n)
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

# 或使用内置排序
arr.sort()  # Timsort, O(n log n)
```

### 策略2：减少重复计算

```python
# 错误：重复计算
for i in range(n):
    for j in range(n):
        result = expensive_computation(i) + expensive_computation(j)

# 正确：缓存结果
cache = {}
def cached_computation(x):
    if x not in cache:
        cache[x] = expensive_computation(x)
    return cache[x]

for i in range(n):
    for j in range(n):
        result = cached_computation(i) + cached_computation(j)
```

### 策略3：使用前缀和

```python
# 问题：多次查询区间和
# 错误：每次查询 O(n)
def range_sum(arr, l, r):
    return sum(arr[l:r+1])  # O(n)

# 如果有 q 次查询，总复杂度 O(q*n)，可能 TLE

# 正确：前缀和 O(1) 查询
prefix = [0] * (n + 1)
for i in range(n):
    prefix[i + 1] = prefix[i] + arr[i]

def range_sum_fast(l, r):
    return prefix[r + 1] - prefix[l]  # O(1)
```

### 策略4：二分查找优化

```python
# 错误：线性查找 O(n)
def find_target(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1

# 正确：二分查找 O(log n) - 需要数组有序
import bisect
def find_target_fast(arr, target):
    idx = bisect.bisect_left(arr, target)
    if idx < len(arr) and arr[idx] == target:
        return idx
    return -1
```

### 策略5：双指针技巧

```python
# 问题：在有序数组中找两个数之和等于 target

# 错误：暴力枚举 O(n²)
def two_sum_brute(arr, target):
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] + arr[j] == target:
                return (i, j)
    return None

# 正确：双指针 O(n)
def two_sum_two_pointers(arr, target):
    left, right = 0, len(arr) - 1
    while left < right:
        s = arr[left] + arr[right]
        if s == target:
            return (left, right)
        elif s < target:
            left += 1
        else:
            right -= 1
    return None
```

## 3. 数据结构优化

### 使用哈希表
```python
# 错误：列表查找 O(n)
if x in my_list:  # O(n)
    ...

# 正确：集合查找 O(1)
my_set = set(my_list)
if x in my_set:  # O(1)
    ...
```

### 使用堆
```python
# 问题：维护前 K 大的元素

# 错误：每次排序 O(n log n)
top_k = sorted(arr, reverse=True)[:k]

# 正确：使用堆 O(n log k)
import heapq
top_k = heapq.nlargest(k, arr)
```

## 4. I/O 优化

### Python I/O 优化
```python
import sys
input = sys.stdin.readline  # 更快的输入

# 批量输出
output = []
for i in range(n):
    output.append(str(result[i]))
print("\\n".join(output))  # 比多次 print 快
```

## 5. 常见 TLE 模式

### 模式1：嵌套循环
```python
# 警惕双重循环
for i in range(n):      # O(n)
    for j in range(n):  # O(n)
        # 总共 O(n²)
```

**优化思路**：
- 能否用哈希表减少一层循环？
- 能否排序后用双指针？
- 能否用前缀和/差分？

### 模式2：重复搜索
```python
# 每次都要从头搜索
for query in queries:
    result = linear_search(data, query)  # O(n) each

# 优化：预处理
data_dict = {item: idx for idx, item in enumerate(data)}
for query in queries:
    result = data_dict.get(query, -1)  # O(1) each
```

## 6. 调试 TLE

### 方法1：本地计时
```python
import time

start = time.time()
# 你的代码
end = time.time()
print(f"Time: {end - start:.3f}s", file=sys.stderr)
```

### 方法2：逐步优化
1. 先保证正确性
2. 分析瓶颈在哪里
3. 针对性优化
4. 再次测试

### 方法3：复杂度分析
```python
# 在代码中标注复杂度
def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    
    # O(n) 读取输入
    # O(n log n) 排序
    arr.sort()
    
    # O(n) 处理
    result = process(arr)
    
    # 总复杂度：O(n log n)
    # n=10^5 时，约 1.7*10^6 次操作，应该在 1 秒内
```

## 7. 优化检查清单

- [ ] 算法复杂度是否可接受？
- [ ] 是否有重复计算可以缓存？
- [ ] 能否用更高效的数据结构？
- [ ] I/O 是否优化？
- [ ] 是否有不必要的操作？
- [ ] 能否用数学公式简化计算？

## 8. 实战示例

### 问题：两数之和
```python
# 题目：给定数组和目标值，找出两个数之和等于目标值

# 解法1：暴力 O(n²) - TLE
def two_sum_v1(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]

# 解法2：哈希表 O(n) - AC
def two_sum_v2(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
```

## 总结

TLE 优化的核心思想：
1. **降低复杂度**：O(n²) → O(n log n) → O(n)
2. **减少常数**：优化实现细节
3. **预处理**：用空间换时间
4. **选择合适的数据结构**

**记住**：先分析复杂度，再针对性优化！
''',
        'source': 'ZJOJ 知识库',
        'is_active': True
    }
]

def add_solutions():
    """添加错误解决方案到知识库"""
    engine = RAGEngine()
    added_count = 0
    skipped_count = 0
    
    print("=" * 60)
    print("开始添加错误解决方案到知识库")
    print("=" * 60)
    
    for solution in solutions:
        try:
            # 检查是否已存在
            existing = KnowledgeBase.objects.filter(
                title=solution['title'],
                doc_type=solution['doc_type'],
                error_type=solution['error_type']
            ).first()
            
            if existing:
                print(f"⚠️  跳过已存在的文档: {solution['title']}")
                skipped_count += 1
                continue
            
            # 生成唯一的 vector_id
            solution['vector_id'] = str(uuid.uuid4())
            
            # 创建文档
            doc = KnowledgeBase.objects.create(**solution)
            print(f"✅ 已创建文档: {doc.title}")
            
            # 同步到向量数据库
            try:
                engine.vector_store.add_document(
                    doc_id=doc.vector_id,
                    text=doc.content,
                    metadata={
                        'title': doc.title,
                        'type': doc.doc_type,
                        'doc_id': doc.id,
                        'error_type': doc.error_type or '',
                        'source': doc.source or '',
                    }
                )
                print(f"   📚 已同步到向量数据库")
                added_count += 1
            except Exception as e:
                print(f"   ⚠️  向量数据库同步失败: {e}")
                added_count += 1
                
        except Exception as e:
            print(f"❌ 添加失败 {solution['title']}: {e}")
    
    print("\n" + "=" * 60)
    print(f"添加完成！")
    print(f"  ✅ 新增: {added_count} 个文档")
    print(f"  ⚠️  跳过: {skipped_count} 个文档")
    print(f"  📊 总计: {len(solutions)} 个文档")
    print("=" * 60)

if __name__ == '__main__':
    add_solutions()
