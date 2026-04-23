#!/bin/bash
# 教练/学生权限体系测试脚本

API_BASE="http://101.35.233.33:8000/api"

echo "========================================="
echo "教练/学生权限体系测试"
echo "========================================="
echo ""

# 1. 注册学生账号
echo "1. 注册学生账号..."
STUDENT_RESPONSE=$(curl -s -X POST "$API_BASE/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student01",
    "email": "student01@test.com",
    "telephone": "13800001001",
    "realname": "张三",
    "password": "student123",
    "password_confirm": "student123",
    "role": 1,
    "school": "测试学校",
    "grade": "高一(1)班"
  }')
echo "$STUDENT_RESPONSE" | python3 -m json.tool
echo ""

# 2. 注册教练账号
echo "2. 注册教练账号..."
COACH_RESPONSE=$(curl -s -X POST "$API_BASE/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "coach01",
    "email": "coach01@test.com",
    "telephone": "13800002001",
    "realname": "李老师",
    "password": "coach123",
    "password_confirm": "coach123",
    "role": 2,
    "school": "测试学校"
  }')
echo "$COACH_RESPONSE" | python3 -m json.tool
echo ""

# 3. 学生登录
echo "3. 学生登录..."
STUDENT_LOGIN=$(curl -s -X POST "$API_BASE/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "student01", "password": "student123"}')
STUDENT_TOKEN=$(echo "$STUDENT_LOGIN" | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
echo "学生 Token: ${STUDENT_TOKEN:0:20}..."
echo ""

# 4. 教练登录
echo "4. 教练登录..."
COACH_LOGIN=$(curl -s -X POST "$API_BASE/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "coach01", "password": "coach123"}')
COACH_TOKEN=$(echo "$COACH_LOGIN" | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
echo "教练 Token: ${COACH_TOKEN:0:20}..."
echo ""

# 5. 查看学生信息
echo "5. 查看学生信息..."
curl -s -X GET "$API_BASE/user/profile/" \
  -H "Authorization: Bearer $STUDENT_TOKEN" | python3 -m json.tool
echo ""

# 6. 更新学生信息
echo "6. 更新学生信息..."
curl -s -X PUT "$API_BASE/user/profile/" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "热爱编程的学生",
    "avatar": "https://example.com/avatar.jpg"
  }' | python3 -m json.tool
echo ""

# 7. 教练创建班级
echo "7. 教练创建班级..."
CLASS_RESPONSE=$(curl -s -X POST "$API_BASE/classes/" \
  -H "Authorization: Bearer $COACH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "高一竞赛班",
    "school": "测试学校",
    "description": "信息学竞赛培训班"
  }')
echo "$CLASS_RESPONSE" | python3 -m json.tool
CLASS_ID=$(echo "$CLASS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['id'])")
echo ""

# 8. 查看班级列表
echo "8. 查看班级列表（教练视角）..."
curl -s -X GET "$API_BASE/classes/" \
  -H "Authorization: Bearer $COACH_TOKEN" | python3 -m json.tool
echo ""

# 9. 添加学生到班级
echo "9. 添加学生到班级..."
curl -s -X POST "$API_BASE/classes/$CLASS_ID/members/" \
  -H "Authorization: Bearer $COACH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "student01"}' | python3 -m json.tool
echo ""

# 10. 查看班级详情
echo "10. 查看班级详情..."
curl -s -X GET "$API_BASE/classes/$CLASS_ID/" \
  -H "Authorization: Bearer $COACH_TOKEN" | python3 -m json.tool
echo ""

# 11. 学生查看自己的班级
echo "11. 学生查看自己的班级..."
curl -s -X GET "$API_BASE/classes/" \
  -H "Authorization: Bearer $STUDENT_TOKEN" | python3 -m json.tool
echo ""

echo "========================================="
echo "测试完成！"
echo "========================================="
echo ""
echo "测试账号："
echo "  学生: student01 / student123"
echo "  教练: coach01 / coach123"
