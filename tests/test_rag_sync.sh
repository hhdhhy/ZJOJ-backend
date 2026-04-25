#!/bin/bash
# 测试 RAG 检索增强生成功能

API="http://101.35.233.33:8000/api"

echo "=========================================="
echo "测试 RAG 检索增强生成"
echo "=========================================="
echo ""

# 学生登录
echo "1. 学生登录..."
STUDENT_TOKEN=$(curl -s -X POST "$API/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_student","password":"student123"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "✅ Token: ${STUDENT_TOKEN:0:40}..."
echo ""

# 测试 RAG 模式问答
echo "2. 测试 RAG 模式问答（关于动态规划）..."
RAG_RESULT=$(curl -s -X POST "$API/ai/chat/" \
  -H "Authorization: jwt $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "动态规划的核心思想是什么？",
    "use_rag": true,
    "top_k": 3
  }')

echo "$RAG_RESULT" | python3 -m json.tool
echo ""

# 提取是否有引用来源
HAS_SOURCES=$(echo "$RAG_RESULT" | python3 -c "import sys,json; data=json.load(sys.stdin); print('有' if data.get('sources') else '无')")
echo "✅ 引用来源: $HAS_SOURCES"
echo ""

# 测试不使用 RAG 的问答
echo "3. 测试简单对话模式（不使用 RAG）..."
CHAT_RESULT=$(curl -s -X POST "$API/ai/chat/" \
  -H "Authorization: jwt $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "你好，请介绍一下自己",
    "use_rag": false
  }')

echo "$CHAT_RESULT" | python3 -m json.tool
echo ""

# 测试二分查找相关问题
echo "4. 测试二分查找相关问题..."
BINARY_SEARCH_RESULT=$(curl -s -X POST "$API/ai/chat/" \
  -H "Authorization: jwt $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "二分查找的时间复杂度是多少？",
    "use_rag": true,
    "top_k": 2
  }')

echo "$BINARY_SEARCH_RESULT" | python3 -m json.tool
echo ""

# 检查引用来源数量
SOURCE_COUNT=$(echo "$BINARY_SEARCH_RESULT" | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data.get('sources', [])))")
echo "✅ 引用来源数量: $SOURCE_COUNT"
echo ""

echo "=========================================="
echo "✅ RAG 功能测试完成！"
echo "=========================================="
