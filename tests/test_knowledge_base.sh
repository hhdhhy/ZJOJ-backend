#!/bin/bash
# 测试知识库管理接口

API="http://101.35.233.33:8000/api"

echo "=========================================="
echo "测试知识库管理接口"
echo "=========================================="
echo ""

# 教练登录
echo "1. 教练登录..."
COACH_TOKEN=$(curl -s -X POST "$API/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_coach","password":"coach123"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "✅ 教练 Token: ${COACH_TOKEN:0:40}..."
echo ""

# 创建知识库文档
echo "2. 创建知识库文档..."
CREATE_RESULT=$(curl -s -X POST "$API/ai/knowledge/" \
  -H "Authorization: jwt $COACH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "动态规划基础教程",
    "content": "动态规划是一种算法思想，用于解决具有最优子结构和重叠子问题性质的问题。核心步骤包括：定义状态、状态转移方程、初始化、计算顺序。",
    "doc_type": "algorithm",
    "tag_names": ["DP", "算法", "动态规划"]
  }')

echo "$CREATE_RESULT" | python3 -m json.tool
echo ""

# 提取 ID
KB_ID=$(echo "$CREATE_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data', {}).get('id', ''))")

if [ -n "$KB_ID" ]; then
  echo "✅ 创建成功，ID: $KB_ID"
  echo ""
  
  # 获取知识库列表
  echo "3. 获取知识库列表..."
  curl -s -X GET "$API/ai/knowledge/?page=1&page_size=5" \
    -H "Authorization: jwt $COACH_TOKEN" | \
    python3 -m json.tool | head -40
  echo ""
  
  # 获取单个文档详情
  echo "4. 获取文档详情 (ID=$KB_ID)..."
  curl -s -X GET "$API/ai/knowledge/$KB_ID/" \
    -H "Authorization: jwt $COACH_TOKEN" | \
    python3 -m json.tool
  echo ""
  
  # 更新文档
  echo "5. 更新文档..."
  curl -s -X PUT "$API/ai/knowledge/$KB_ID/" \
    -H "Authorization: jwt $COACH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"title": "动态规划基础教程（已更新）"}' | \
    python3 -m json.tool
  echo ""
  
  # 学生尝试创建（应该失败）
  echo "6. 学生尝试创建文档（应该被拒绝）..."
  STUDENT_TOKEN=$(curl -s -X POST "$API/login/" \
    -H "Content-Type: application/json" \
    -d '{"username":"test_student","password":"student123"}' | \
    python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
  
  curl -s -X POST "$API/ai/knowledge/" \
    -H "Authorization: jwt $STUDENT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"title":"测试","content":"测试内容","doc_type":"algorithm"}' | \
    python3 -m json.tool
  echo ""
  
  echo "=========================================="
  echo "✅ 所有测试完成！"
  echo "=========================================="
else
  echo "❌ 创建失败"
fi
