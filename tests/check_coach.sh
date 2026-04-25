#!/bin/bash
# 检查教练用户信息

API="http://101.35.233.33:8000/api"

echo "检查 test_coach 用户信息..."

TOKEN=$(curl -s -X POST "$API/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_coach","password":"coach123"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "Token: ${TOKEN:0:40}..."
echo ""

curl -s -X GET "$API/user/profile/" \
  -H "Authorization: jwt $TOKEN" | \
  python3 -m json.tool
