#!/usr/bin/env python3
"""
添加错误解决方案到知识库
"""
import os
import sys
import django
import uuid

# 设置 Django 环境
sys.path.insert(0, '/home/zjoj')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings_production')
django.setup()

from apps.ai_assistant.models import KnowledgeBase
from apps.ai_assistant.rag_engine import get_rag_engine

# 定义错误解决方案文档
solutions = [
    {
        'title': 'RE 运行时错误解决方案',
        'doc_type': 'error_solution',
        'error_type': 'RE',
        'content': '''# RE (Runtime Error) 运行时错误

## 常见原因

1. **数组越界**
   - 访问了数组或字符串的不存在的位置
   - 检查数组大小和循环边界
   
2. **空指针/除零错误**
   - 使用了未初始化的指针
   - 除数为 0
   
3. **栈溢出**
   - 递归深度过大
   - 局部数组过大
   
4. **内存访问违规**
   - 使用了已释放的内存
   - 野指针

## 解决方法

### Python
```python
# 错误示例
arr = [1, 2, 3]
print(arr[5])  # IndexError

# 正确做法
if index < len(arr):
    print(arr[index])
```

### C++
```cpp
// 错误示例
int arr[10];
cout << arr[10];  // 越界

// 正确做法
if (index >= 0 && index < 10) {
    cout << arr[index];
}
```

## 调试技巧

1. 使用 IDE 的调试器查看崩溃位置
2. 添加边界检查
3. 使用 valgrind (C/C++) 检测内存错误
4. 检查递归终止条件
''',
        'source': 'ZJOJ 知识库',
        'is_active': True
    },
    {
        'title': 'MLE 内存超限解决方案',
        'doc_type': 'error_solution',
        'error_type': 'MLE',
        'content': '''# MLE (Memory Limit Exceeded) 内存超限

## 常见原因

1. **数组开得太大**
   - 超过了题目内存限制
   - 使用了不必要的大数组
   
2. **未释放内存**
   - C/C++ 中 malloc/new 后未 free/delete
   - 递归调用未释放栈空间
   
3. **数据结构选择不当**
   - 使用了内存占用大的数据结构
   - 重复存储相同数据

## 解决方法

### 优化数组大小
```cpp
// 错误：数组太大
int dp[1000000][1000000];  // 约 4TB！

// 正确：使用滚动数组
int dp[2][1000000];  // 约 8MB
```

### Python 优化
```python
# 使用生成器而不是列表
def generate_numbers(n):
    for i in range(n):
        yield i  # 节省内存

# 而不是
numbers = [i for i in range(n)]  # 占用大量内存
```

## 调试技巧

1. 查看题目内存限制
2. 使用 memory_profiler (Python) 分析内存使用
3. 优化数据结构和算法
4. 及时释放不需要的内存
''',
        'source': 'ZJOJ 知识库',
        'is_active': True
    },
    {
        'title': 'CE 编译错误解决方案',
        'doc_type': 'error_solution',
        'error_type': 'CE',
        'content': '''# CE (Compilation Error) 编译错误

## 常见原因

1. **语法错误**
   - 缺少分号、括号
   - 拼写错误
   
2. **类型错误**
   - 类型不匹配
   - 使用了未声明的变量
   
3. **头文件缺失**
   - 使用了库函数但未包含头文件
   - C++ 中未使用 std:: 前缀

## 解决方法

### C++ 常见错误
```cpp
// 错误：缺少头文件
#include <iostream>
// #include <vector>  // 缺少！

int main() {
    vector<int> v;  // 编译错误
    return 0;
}

// 正确：
#include <iostream>
#include <vector>
using namespace std;

int main() {
    vector<int> v;
    return 0;
}
```

### Python 常见错误
```python
# 错误：缩进错误
def foo():
print("hello")  # IndentationError

# 正确：
def foo():
    print("hello")
```

## 调试技巧

1. 仔细阅读编译器错误信息
2. 从第一个错误开始修复
3. 使用 IDE 的代码检查功能
4. 检查头文件和命名空间
''',
        'source': 'ZJOJ 知识库',
        'is_active': True
    },
    {
        'title': 'PE 格式错误解决方案',
        'doc_type': 'error_solution',
        'error_type': 'PE',
        'content': '''# PE (Presentation Error) 格式错误

## 常见原因

1. **多余的空格**
   - 行尾有多余空格
   - 输出格式不符合要求
   
2. **换行符问题**
   - 缺少或多出换行
   - Windows/Linux 换行符不同
   
3. **输出格式不匹配**
   - 空格数量不对
   - 大小写不匹配

## 解决方法

### Python
```python
# 错误：行尾有多余空格
print(f"{a} {b} ")  # 多了一个空格

# 正确：
print(f"{a} {b}")

# 或者使用 join
print(' '.join(map(str, [a, b])))
```

### C++
```cpp
// 错误：行尾有空格
for (int i = 0; i < n; i++) {
    cout << arr[i] << " ";  // 最后一个元素后有多余空格
}
cout << endl;

// 正确：
for (int i = 0; i < n; i++) {
    if (i > 0) cout << " ";
    cout << arr[i];
}
cout << endl;
```

## 调试技巧

1. 逐字符对比样例输出
2. 使用 diff 工具比较输出
3. 注意行尾空格和换行
4. 检查题目输出格式要求
''',
        'source': 'ZJOJ 知识库',
        'is_active': True
    }
]

print("=" * 60)
print("开始添加错误解决方案到知识库")
print("=" * 60)

engine = get_rag_engine()
added_count = 0

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
            added_count += 1  # 仍然计入成功创建
            
    except Exception as e:
        print(f"❌ 添加失败 {solution['title']}: {e}")

print()
print("=" * 60)
print(f"完成！成功添加 {added_count} 个错误解决方案")
print("=" * 60)
