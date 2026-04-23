#!/bin/bash
cd ~/projects/ZJOJ-backend

echo "=== 测试1: 注册学生 ==="
curl -s -X POST http://101.35.233.33:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test_student","email":"student@test.com","telephone":"13900001001","realname":"测试学生","password":"student123","password_confirm":"student123","role":1}'

echo ""
echo "=== 测试2: 注册教练 ==="
curl -s -X POST http://101.35.233.33:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test_coach","email":"coach@test.com","telephone":"13900002001","realname":"测试教练","password":"coach123","password_confirm":"coach123","role":2}'

echo ""
echo "=== 测试3: 学生登录 ==="
STUDENT_TOKEN=$(curl -s -X POST http://101.35.233.33:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test_student","password":"student123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
echo "Student Token: ${STUDENT_TOKEN:0:30}..."

echo ""
echo "=== 测试4: 教练登录 ==="
COACH_TOKEN=$(curl -s -X POST http://101.35.233.33:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test_coach","password":"coach123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
echo "Coach Token: ${COACH_TOKEN:0:30}..."

echo ""
echo "=== 测试5: 学生查看个人信息 ==="
curl -s -X GET http://101.35.233.33:8000/api/user/profile/ \
  -H "Authorization: Bearer $STUDENT_TOKEN"

echo ""
echo "=== 测试6: 教练创建班级 ==="
CLASS_RESPONSE=$(curl -s -X POST http://101.35.233.33:8000/api/classes/ \
  -H "Authorization: Bearer $COACH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试班级","description":"用于测试"}')
echo "$CLASS_RESPONSE"
CLASS_ID=$(echo "$CLASS_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])")
echo "Class ID: $CLASS_ID"

echo ""
echo "=== 测试7: 添加学生到班级 ==="
curl -s -X POST http://101.35.233.33:8000/api/classes/$CLASS_ID/members/ \
  -H "Authorization: Bearer $COACH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_student"}'

echo ""
echo "=== 测试8: AI智能问答 ==="
curl -s -X POST http://101.35.233.33:8000/api/ai/chat/ \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是二分查找？","use_rag":false}'

echo ""
echo "=== 测试9: 学生学情报告 ==="
curl -s -X GET http://101.35.233.33:8000/api/ai/report/student/?days=7 \
  -H "Authorization: Bearer $STUDENT_TOKEN"

echo ""
echo "=== 测试10: 班级学情报告 ==="
curl -s -X GET http://101.35.233.33:8000/api/ai/report/class/$CLASS_ID/?days=7 \
  -H "Authorization: Bearer $COACH_TOKEN"

echo ""
echo "=== 所有测试完成 ==="
