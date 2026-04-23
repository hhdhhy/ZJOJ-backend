#!/bin/bash
# 完整功能测试脚本 - 教练/学生权限体系 + AI应用

API_BASE="http://101.35.233.33:8000/api"

echo "========================================="
echo "ZJOJ 完整功能测试"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试结果统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
test_api() {
    local test_name="$1"
    local method="$2"
    local url="$3"
    local headers="$4"
    local data="$5"
    local expected_code="$6"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${YELLOW}测试 $TOTAL_TESTS: $test_name${NC}"
    
    # 构建curl命令
    curl_cmd="curl -s -X $method \"$url\""
    
    if [ -n "$headers" ]; then
        while IFS='|' read -r header; do
            if [ -n "$header" ]; then
                curl_cmd="$curl_cmd -H \"$header\""
            fi
        done <<< "$headers"
    fi
    
    if [ -n "$data" ]; then
        curl_cmd="$curl_cmd -d '$data'"
    fi
    
    # 执行请求
    response=$(eval $curl_cmd)
    
    # 检查响应码
    if [ -n "$expected_code" ]; then
        actual_code=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 0))" 2>/dev/null || echo "0")
        
        if [ "$actual_code" = "$expected_code" ]; then
            echo -e "${GREEN}✅ 通过 (code: $actual_code)${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}❌ 失败 (期望: $expected_code, 实际: $actual_code)${NC}"
            echo "响应: $response" | head -c 200
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        echo -e "${GREEN}✅ 已执行${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    fi
    
    echo ""
    sleep 1
}

echo "========================================="
echo "第一部分：用户注册与登录"
echo "========================================="
echo ""

# 1. 注册学生账号
test_api "注册学生账号" \
    "POST" \
    "$API_BASE/register/" \
    "Content-Type: application/json" \
    '{
        "username": "test_student",
        "email": "student@test.com",
        "telephone": "13900001001",
        "realname": "测试学生",
        "password": "student123",
        "password_confirm": "student123",
        "role": 1
    }' \
    "201"

# 2. 注册教练账号
test_api "注册教练账号" \
    "POST" \
    "$API_BASE/register/" \
    "Content-Type: application/json" \
    '{
        "username": "test_coach",
        "email": "coach@test.com",
        "telephone": "13900002001",
        "realname": "测试教练",
        "password": "coach123",
        "password_confirm": "coach123",
        "role": 2
    }' \
    "201"

# 3. 学生登录
echo -e "${YELLOW}获取学生Token...${NC}"
STUDENT_LOGIN=$(curl -s -X POST "$API_BASE/login/" \
    -H "Content-Type: application/json" \
    -d '{"username": "test_student", "password": "student123"}')
STUDENT_TOKEN=$(echo "$STUDENT_LOGIN" | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)
if [ -n "$STUDENT_TOKEN" ]; then
    echo -e "${GREEN}✅ 学生登录成功${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ 学生登录失败${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

# 4. 教练登录
echo -e "${YELLOW}获取教练Token...${NC}"
COACH_LOGIN=$(curl -s -X POST "$API_BASE/login/" \
    -H "Content-Type: application/json" \
    -d '{"username": "test_coach", "password": "coach123"}')
COACH_TOKEN=$(echo "$COACH_LOGIN" | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)
if [ -n "$COACH_TOKEN" ]; then
    echo -e "${GREEN}✅ 教练登录成功${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ 教练登录失败${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

echo "========================================="
echo "第二部分：个人信息管理"
echo "========================================="
echo ""

# 5. 查看学生信息
test_api "学生查看个人信息" \
    "GET" \
    "$API_BASE/user/profile/" \
    "Authorization: Bearer $STUDENT_TOKEN" \
    "" \
    "200"

# 6. 更新学生信息
test_api "学生更新个人信息" \
    "PUT" \
    "$API_BASE/user/profile/" \
    "Authorization: Bearer $STUDENT_TOKEN|Content-Type: application/json" \
    '{
        "bio": "热爱编程的学生",
        "avatar": "https://example.com/avatar.jpg"
    }' \
    "200"

echo "========================================="
echo "第三部分：班级管理"
echo "========================================="
echo ""

# 7. 教练创建班级
echo -e "${YELLOW}教练创建班级...${NC}"
CLASS_RESPONSE=$(curl -s -X POST "$API_BASE/classes/" \
    -H "Authorization: Bearer $COACH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "测试班级",
        "description": "用于测试的班级"
    }')
CLASS_ID=$(echo "$CLASS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
if [ -n "$CLASS_ID" ]; then
    echo -e "${GREEN}✅ 班级创建成功 (ID: $CLASS_ID)${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ 班级创建失败${NC}"
    echo "响应: $CLASS_RESPONSE"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

# 8. 查看班级列表（教练）
test_api "教练查看班级列表" \
    "GET" \
    "$API_BASE/classes/" \
    "Authorization: Bearer $COACH_TOKEN" \
    "" \
    "200"

# 9. 添加学生到班级
test_api "教练添加学生到班级" \
    "POST" \
    "$API_BASE/classes/$CLASS_ID/members/" \
    "Authorization: Bearer $COACH_TOKEN|Content-Type: application/json" \
    '{"username": "test_student"}' \
    "200"

# 10. 查看班级详情
test_api "查看班级详情" \
    "GET" \
    "$API_BASE/classes/$CLASS_ID/" \
    "Authorization: Bearer $COACH_TOKEN" \
    "" \
    "200"

# 11. 学生查看自己的班级
test_api "学生查看自己的班级" \
    "GET" \
    "$API_BASE/classes/" \
    "Authorization: Bearer $STUDENT_TOKEN" \
    "" \
    "200"

echo "========================================="
echo "第四部分：AI智能问答"
echo "========================================="
echo ""

# 12. AI智能问答
test_api "AI智能问答" \
    "POST" \
    "$API_BASE/ai/chat/" \
    "Authorization: Bearer $STUDENT_TOKEN|Content-Type: application/json" \
    '{
        "question": "什么是二分查找？",
        "use_rag": false
    }' \
    "200"

# 13. 查看对话历史
test_api "查看对话历史" \
    "GET" \
    "$API_BASE/ai/history/?limit=5" \
    "Authorization: Bearer $STUDENT_TOKEN" \
    "" \
    "200"

# 14. 查看使用情况
test_api "查看AI使用情况" \
    "GET" \
    "$API_BASE/ai/usage/" \
    "Authorization: Bearer $STUDENT_TOKEN" \
    "" \
    "200"

echo "========================================="
echo "第五部分：学情分析"
echo "========================================="
echo ""

# 15. 学生查看学情报告
test_api "学生查看学情报告" \
    "GET" \
    "$API_BASE/ai/report/student/?days=7" \
    "Authorization: Bearer $STUDENT_TOKEN" \
    "" \
    "200"

# 16. 教练查看班级学情报告
test_api "教练查看班级学情报告" \
    "GET" \
    "$API_BASE/ai/report/class/$CLASS_ID/?days=7" \
    "Authorization: Bearer $COACH_TOKEN" \
    "" \
    "200"

echo "========================================="
echo "第六部分：权限隔离测试"
echo "========================================="
echo ""

# 17. 学生尝试创建班级（应该失败）
test_api "学生尝试创建班级（应拒绝）" \
    "POST" \
    "$API_BASE/classes/" \
    "Authorization: Bearer $STUDENT_TOKEN|Content-Type: application/json" \
    '{"name": "非法班级"}' \
    "403"

# 18. 学生尝试查看其他班级（如果存在）
# 这里假设学生只能看到自己加入的班级

echo "========================================="
echo "测试总结"
echo "========================================="
echo ""
echo -e "总测试数: ${YELLOW}$TOTAL_TESTS${NC}"
echo -e "通过: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败: ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
else
    echo -e "${RED}⚠️  有 $FAILED_TESTS 个测试失败，请检查${NC}"
fi

echo ""
echo "========================================="
echo "测试账号信息"
echo "========================================="
echo "学生账号: test_student / student123"
echo "教练账号: test_coach / coach123"
echo "班级ID: $CLASS_ID"
echo ""
