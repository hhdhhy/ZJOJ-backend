#!/bin/bash
# 简化版功能测试脚本

API="http://101.35.233.33:8000/api"

echo "=========================================="
echo "ZJOJ 功能测试"
echo "=========================================="
echo ""

# 1. 学生登录
echo "1. 学生登录..."
STUDENT_TOKEN=$(curl -s -X POST "$API/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_student","password":"student123"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
  
if [ -n "$STUDENT_TOKEN" ]; then
    echo "✅ 学生登录成功"
    echo "Token: ${STUDENT_TOKEN:0:40}..."
else
    echo "❌ 学生登录失败"
    exit 1
fi
echo ""

# 2. 教练登录
echo "2. 教练登录..."
COACH_TOKEN=$(curl -s -X POST "$API/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_coach","password":"coach123"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
  
if [ -n "$COACH_TOKEN" ]; then
    echo "✅ 教练登录成功"
    echo "Token: ${COACH_TOKEN:0:40}..."
else
    echo "❌ 教练登录失败"
    exit 1
fi
echo ""

# 3. 查看学生信息
echo "3. 查看学生信息..."
curl -s -X GET "$API/user/profile/" \
  -H "Authorization: jwt $STUDENT_TOKEN" | \
  python3 -m json.tool | head -20
echo ""

# 4. 创建班级
echo "4. 教练创建班级..."
CLASS_RESPONSE=$(curl -s -X POST "$API/classes/" \
  -H "Authorization: jwt $COACH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"AI测试班","description":"测试AI功能"}')
  
echo "$CLASS_RESPONSE" | python3 -m json.tool
CLASS_ID=$(echo "$CLASS_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
echo "班级ID: $CLASS_ID"
echo ""

# 5. 添加学生到班级
echo "5. 添加学生到班级..."
curl -s -X POST "$API/classes/$CLASS_ID/members/" \
  -H "Authorization: jwt $COACH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_student"}' | \
  python3 -m json.tool
echo ""

# 6. AI智能问答
echo "6. 测试AI智能问答..."
curl -s -X POST "$API/ai/chat/" \
  -H "Authorization: jwt $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是动态规划？","use_rag":false}' | \
  python3 -m json.tool | head -30
echo ""

# 7. 学生学情报告
echo "7. 学生学情报告..."
curl -s -X GET "$API/ai/report/student/?days=7" \
  -H "Authorization: jwt $STUDENT_TOKEN" | \
  python3 -m json.tool | head -40
echo ""

# 8. 班级学情报告
echo "8. 班级学情报告..."
curl -s -X GET "$API/ai/report/class/$CLASS_ID/?days=7" \
  -H "Authorization: jwt $COACH_TOKEN" | \
  python3 -m json.tool | head -40
echo ""

echo "=========================================="
echo "测试完成！"
echo "=========================================="
