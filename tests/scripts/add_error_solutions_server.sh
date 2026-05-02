#!/bin/bash
# 在服务器上执行此脚本添加错误解决方案文档

echo "=========================================="
echo "添加错误解决方案到知识库"
echo "=========================================="

cd /home/zjoj/ZJOJ

# 激活虚拟环境
source .venv/bin/activate

# 执行 Python 脚本
python tests/scripts/add_error_solutions_detailed.py

echo ""
echo "=========================================="
echo "完成！请检查输出结果"
echo "=========================================="
