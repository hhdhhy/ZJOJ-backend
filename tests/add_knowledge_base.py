"""
添加知识库测试数据
"""
import os
import sys
import django

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
django.setup()

from apps.ai_assistant.models import KnowledgeBase

# 准备测试文档
documents = [
    {
        "title": "二分查找算法",
        "content": """二分查找（Binary Search）是一种在有序数组中查找特定元素的搜索算法。

算法原理：
1. 从数组的中间元素开始搜索
2. 如果中间元素等于目标值，返回索引
3. 如果目标值小于中间元素，在左半部分继续搜索
4. 如果目标值大于中间元素，在右半部分继续搜索
5. 重复上述步骤直到找到目标值或搜索范围为空

时间复杂度：O(log n)
空间复杂度：O(1)

Python实现：
```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # 未找到
```

应用场景：
- 在有序数组中快速查找元素
- 查找第一个/最后一个出现的位置
- 查找峰值元素
- 解决单调性问题""",
        "doc_type": "algorithm",
        "tags": ["搜索", "二分", "基础算法"]
    },
    {
        "title": "快速排序算法",
        "content": """快速排序（Quick Sort）是一种高效的排序算法，采用分治法策略。

算法原理：
1. 选择一个基准元素（pivot）
2. 将数组分为两部分：小于基准和大于基准的元素
3. 递归地对两部分进行排序

时间复杂度：
- 平均情况：O(n log n)
- 最坏情况：O(n²)（已排序数组且选择首/尾为基准）
- 最好情况：O(n log n)

空间复杂度：O(log n)（递归栈）

Python实现：
```python
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)
```

优化技巧：
- 随机选择基准元素
- 三数取中法选择基准
- 小数组使用插入排序
- 尾递归优化""",
        "doc_type": "algorithm",
        "tags": ["排序", "分治", "基础算法"]
    },
    {
        "title": "动态规划基础",
        "content": """动态规划（Dynamic Programming, DP）是一种通过将复杂问题分解为子问题来求解的方法。

核心思想：
1. 最优子结构：问题的最优解包含子问题的最优解
2. 重叠子问题：子问题会被重复计算
3. 状态转移方程：描述状态之间的关系

解题步骤：
1. 定义状态：dp[i]表示什么含义
2. 确定初始条件：边界情况
3. 找出状态转移方程
4. 确定计算顺序

经典问题：
- 斐波那契数列：dp[i] = dp[i-1] + dp[i-2]
- 背包问题：dp[i][j] = max(dp[i-1][j], dp[i-1][j-w[i]] + v[i])
- 最长公共子序列（LCS）
- 编辑距离

示例 - 爬楼梯：
```python
def climb_stairs(n):
    if n <= 2:
        return n
    
    dp = [0] * (n + 1)
    dp[1], dp[2] = 1, 2
    
    for i in range(3, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]
```

时间复杂度：O(n)
空间复杂度：可优化至O(1)""",
        "doc_type": "algorithm",
        "tags": ["动态规划", "DP", "进阶算法"]
    },
    {
        "title": "图的遍历 - BFS和DFS",
        "content": """图的遍历是图算法的基础，主要有两种方式：广度优先搜索（BFS）和深度优先搜索（DFS）。

## 广度优先搜索（BFS）

特点：
- 使用队列实现
- 逐层访问节点
- 适合求最短路径

Python实现：
```python
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        node = queue.popleft()
        print(node)
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

时间复杂度：O(V + E)，V为顶点数，E为边数

## 深度优先搜索（DFS）

特点：
- 使用递归或栈实现
- 深入探索每个分支
- 适合检测环、拓扑排序

Python实现（递归）：
```python
def dfs(graph, node, visited=None):
    if visited is None:
        visited = set()
    
    visited.add(node)
    print(node)
    
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
```

应用场景：
- BFS：最短路径、社交网络好友推荐
- DFS：迷宫求解、拓扑排序、连通分量检测""",
        "doc_type": "concept",
        "tags": ["图论", "BFS", "DFS", "遍历"]
    },
    {
        "title": "哈希表原理与应用",
        "content": """哈希表（Hash Table）是一种基于键值对的数据结构，提供高效的查找、插入和删除操作。

工作原理：
1. 通过哈希函数将键转换为数组索引
2. 在该索引位置存储值
3. 处理冲突（链地址法或开放寻址法）

时间复杂度：
- 平均情况：O(1)
- 最坏情况：O(n)（所有键都冲突）

Python中的字典就是哈希表的实现：
```python
# 创建哈希表
hash_map = {}

# 插入
hash_map['key'] = 'value'

# 查找
if 'key' in hash_map:
    value = hash_map['key']

# 删除
del hash_map['key']
```

常见应用：
1. 两数之和：用哈希表存储已遍历的元素
2. 计数：统计元素出现次数
3. 去重：利用集合的唯一性
4. 缓存：LRU缓存实现

示例 - 两数之和：
```python
def two_sum(nums, target):
    hash_map = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        
        if complement in hash_map:
            return [hash_map[complement], i]
        
        hash_map[num] = i
    
    return []
```

设计要点：
- 选择合适的哈希函数
- 合理设置初始容量
- 负载因子控制在0.75左右
- 及时扩容""",
        "doc_type": "concept",
        "tags": ["哈希表", "字典", "数据结构"]
    }
]

# 添加到数据库
print("开始添加知识库文档...")
for doc_data in documents:
    tags = doc_data.pop('tags', [])  # 移除tags字段（暂不设置）
    
    # 生成唯一的vector_id
    import uuid
    doc_data['vector_id'] = f'kb_{uuid.uuid4().hex[:12]}'
    
    doc = KnowledgeBase.objects.create(**doc_data)
    print(f"✅ 添加: {doc.title}")

print(f"\n总共添加了 {len(documents)} 个文档到知识库")
print("现在可以进行RAG测试了！")
