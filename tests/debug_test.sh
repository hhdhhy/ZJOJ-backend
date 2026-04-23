#!/bin/bash
cd ~/projects/ZJOJ-backend

echo "=== 获取教练Token ==="
COACH_TOKEN=$(curl -s -X POST http://101.35.233.33:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test_coach","password":"coach123"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "Token: ${COACH_TOKEN:0:40}..."
echo ""

echo "=== 测试创建班级 ==="
curl -v -X POST http://101.35.233.33:8000/api/classes/ \
  -H "Authorization: jwt $COACH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试班","description":"测试"}' 2>&1

echo ""
echo "=== 测试AI问答 ==="
STUDENT_TOKEN=$(curl -s -X POST http://101.35.233.33:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test_student","password":"student123"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -v -X POST http://101.35.233.33:8000/api/ai/chat/ \
  -H "Authorization: jwt $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"你好","use_rag":false}' 2>&1
