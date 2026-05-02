#!/bin/bash
# 在服务器上直接添加错误解决方案文档（无需 Git）

echo "=========================================="
echo "在服务器上添加错误解决方案文档"
echo "=========================================="

# 进入容器
docker exec -i zjoj-web python3 << 'PYTHON_SCRIPT'
import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
sys.path.insert(0, '/home/zjoj')
django.setup()

from apps.ai_assistant.models import KnowledgeBase
from apps.ai_assistant.rag_engine import RAGEngine
import uuid

print("开始添加文档...")

# 文档1: 动态规划 WA
doc1 = KnowledgeBase.objects.create(
    title='动态规划 WA 常见原因',
    doc_type='error_solution',
    error_type='WA',
    content='''# 动态规划 WA (Wrong Answer) 常见原因

## 1. 状态定义错误
dp[i] 的含义不清晰，导致状态转移方程错误。

## 2. 边界条件处理不当
- 初始值设置错误
- 边界情况遗漏（空数组、单个元素）
- 数组越界

## 3. 状态转移方程错误
- 方向错误：应该从前往后还是从后往前更新？
- 依赖关系错误
- 重复计算

## 4. 调试技巧
1. 小数据测试：手动模拟 DP 过程
2. 打印 DP 表检查异常值
3. 对拍：与暴力解法对比

## 常见陷阱
- 忘记初始化 dp 数组
- 循环顺序错误
- 状态维度不够
''',
    source='ZJOJ 知识库',
    is_active=True,
    vector_id=str(uuid.uuid4())
)
print(f"✅ 已创建: {doc1.title}")

# 同步到向量数据库
try:
    engine = RAGEngine()
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
    print(f"   ⚠️ 向量同步失败: {e}")

print("\n完成！已添加 1 个文档")
PYTHON_SCRIPT

echo ""
echo "=========================================="
echo "提示：由于文档内容较长，建议分批添加"
echo "完整脚本请参考: tests/scripts/add_error_solutions_detailed.py"
echo "=========================================="
