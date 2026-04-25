#!/bin/bash
# 测试聊天记录详情接口

API="http://101.35.233.33:8000/api"

echo "=========================================="
echo "测试聊天记录详情接口"
echo "=========================================="
echo ""

# 登录获取 token
echo "1. 登录获取 token..."
TOKEN=$(curl -s -X POST "$API/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_student","password":"student123"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "✅ Token: ${TOKEN:0:40}..."
echo ""

# 获取聊天记录列表，找到第一个 ID
echo "2. 获取聊天记录列表..."
FIRST_ID=$(curl -s -X GET "$API/ai/history/?limit=1" \
  -H "Authorization: jwt $TOKEN" | \
  python3 -c "import sys,json; data=json.load(sys.stdin); print(data['results'][0]['id'] if data['results'] else 'None')")

echo "第一条记录 ID: $FIRST_ID"
echo ""

if [ "$FIRST_ID" != "None" ]; then
  # 测试获取单条记录详情
  echo "3. 获取聊天记录详情 (ID=$FIRST_ID)..."
  curl -s -X GET "$API/ai/history/$FIRST_ID/" \
    -H "Authorization: jwt $TOKEN" | \
    python3 -m json.tool
  
  echo ""
  echo "✅ 测试成功！"
else
  echo "⚠️ 没有聊天记录，无法测试详情接口"
fi

echo ""
echo "=========================================="
