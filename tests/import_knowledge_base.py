#!/usr/bin/env python3
"""
批量导入知识库文档脚本
用于初始化 AI 助手的知识库
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
django.setup()

from apps.ai_assistant.models import KnowledgeBase
from apps.problem.models import Tag


def create_sample_knowledge_base():
    """创建示例知识库文档"""
    
    # 示例文档数据
    documents = [
        {
            'title': '动态规划基础',
            'content': '''动态规划（Dynamic Programming，简称DP）是一种用于解决具有最优子结构和重叠子问题性质的优化算法。

核心思想：
1. 最优子结构：问题的最优解包含其子问题的最优解
2. 重叠子问题：在递归求解过程中，相同的子问题会被多次重复计算

解题步骤：
1. 定义状态：明确 dp[i] 或 dp[i][j] 表示什么含义
2. 状态转移方程：找出当前状态与之前状态的关系
3. 初始化边界：确定最小子问题的解
4. 确定遍历顺序：通常从小到大（自底向上）或通过记忆化递归（自顶向下）

经典例子：斐波那契数列
- 暴力递归：O(2^n)
- 动态规划：O(n)

```python
def fib_dp(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[0], dp[1] = 0, 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```''',
            'doc_type': 'algorithm',
            'tags': ['动态规划', 'DP', '算法基础'],
        },
        {
            'title': '二分查找算法',
            'content': '''二分查找（Binary Search）是一种在有序数组中查找特定元素的高效算法。

时间复杂度：O(log n)

基本思想：
1. 确定查找范围的左右边界
2. 计算中间位置
3. 比较中间元素与目标值
4. 根据比较结果缩小查找范围

标准模板：
```python
def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

注意事项：
- 数组必须是有序的
- 注意边界条件的处理
- 防止整数溢出：使用 left + (right - left) // 2''',
            'doc_type': 'algorithm',
            'tags': ['二分查找', '搜索', '算法基础'],
        },
        {
            'title': 'WA（答案错误）常见原因',
            'content': '''WA（Wrong Answer）是判题系统中最常见的错误类型之一。

常见原因：
1. 边界条件处理不当
   - 数组越界
   - 特殊情况未考虑（如空输入、单个元素）
   
2. 数据类型溢出
   - 使用 int 而非 long long
   - 中间结果溢出
   
3. 精度问题
   - 浮点数比较未使用误差范围
   - 除法运算顺序错误
   
4. 逻辑错误
   - 状态转移方程错误
   - 贪心策略不正确
   
5. 输出格式错误
   - 多余的空格或换行
   - 大小写错误

调试建议：
- 使用小样本手动验证
- 打印中间变量检查逻辑
- 对比标准答案找差异
- 检查边界情况和特殊输入''',
            'doc_type': 'error_solution',
            'error_type': 'WA',
            'tags': ['调试', '常见错误'],
        },
        {
            'title': 'TLE（超时）优化技巧',
            'content': '''TLE（Time Limit Exceeded）表示程序运行时间超过限制。

常见原因：
1. 算法复杂度过高
   - 使用了 O(n²) 而非 O(n log n)
   - 未使用剪枝优化
   
2. 不必要的重复计算
   - 未使用记忆化
   - 循环中有冗余操作
   
3. I/O 效率低
   - 频繁使用 cin/cout 而未关闭同步
   - 未使用缓冲输入输出

优化技巧：
1. 选择更优的算法
   - 用空间换时间
   - 使用更高效的数据结构
   
2. 代码层面优化
   - 减少常数因子
   - 避免不必要的函数调用
   
3. I/O 优化
```cpp
// C++ 加速
ios::sync_with_stdio(false);
cin.tie(nullptr);
```

4. 剪枝优化
   - 提前终止不可能的分支
   - 使用启发式搜索''',
            'doc_type': 'error_solution',
            'error_type': 'TLE',
            'tags': ['性能优化', '超时'],
        },
        {
            'title': '快速排序模板',
            'content': '''快速排序是一种高效的排序算法，平均时间复杂度 O(n log n)。

C++ 实现：
```cpp
void quick_sort(vector<int>& nums, int left, int right) {
    if (left >= right) return;
    
    int pivot = nums[left + (right - left) / 2];
    int i = left, j = right;
    
    while (i <= j) {
        while (nums[i] < pivot) i++;
        while (nums[j] > pivot) j--;
        if (i <= j) {
            swap(nums[i], nums[j]);
            i++;
            j--;
        }
    }
    
    quick_sort(nums, left, j);
    quick_sort(nums, i, right);
}
```

Python 实现：
```python
def quick_sort(nums):
    if len(nums) <= 1:
        return nums
    pivot = nums[len(nums) // 2]
    left = [x for x in nums if x < pivot]
    middle = [x for x in nums if x == pivot]
    right = [x for x in nums if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
```

注意事项：
- 最坏情况 O(n²)，可通过随机化pivot避免
- 不稳定排序
- 原地排序版本空间复杂度 O(log n)''',
            'doc_type': 'template',
            'tags': ['排序', '代码模板', '快速排序'],
        },
    ]
    
    print(f"开始导入 {len(documents)} 个知识库文档...")
    print("=" * 60)
    
    created_count = 0
    skipped_count = 0
    
    for doc_data in documents:
        title = doc_data['title']
        
        # 检查是否已存在
        if KnowledgeBase.objects.filter(title=title).exists():
            print(f"⊘ 跳过（已存在）: {title}")
            skipped_count += 1
            continue
        
        # 提取标签
        tag_names = doc_data.pop('tags', [])
        
        # 创建文档
        try:
            import uuid
            doc_data['vector_id'] = f'kb_{uuid.uuid4().hex[:16]}'
            
            doc = KnowledgeBase.objects.create(**doc_data)
            
            # 添加标签
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                doc.tags.add(tag)
            
            print(f"✓ 创建成功: {title}")
            created_count += 1
        except Exception as e:
            print(f"✗ 创建失败: {title} - {str(e)}")
    
    print("=" * 60)
    print(f"导入完成！")
    print(f"  新建: {created_count} 个")
    print(f"  跳过: {skipped_count} 个")
    print(f"  总计: {KnowledgeBase.objects.count()} 个文档")


if __name__ == '__main__':
    create_sample_knowledge_base()
