#!/bin/bash
# 完整测试 AI 助手功能

API="http://101.35.233.33:8000/api"

echo "=========================================="
echo "AI 助手完整功能测试"
echo "=========================================="
echo ""

# 1. 登录获取 token
echo "1. 登录获取 token..."
TOKEN=$(curl -s -X POST "$API/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_student","password":"student123"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "✅ Token: ${TOKEN:0:40}..."
echo ""

# 2. 测试不使用 RAG 的问答
echo "2. 测试 AI 问答（不使用 RAG）..."
curl -s -X POST "$API/ai/chat/" \
  -H "Authorization: jwt $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是动态规划？","use_rag":false}' | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"回答长度: {len(data.get('answer', ''))} 字符\")
print(f\"Tokens 使用: {data.get('tokens_used', 0)}\")
print(f\"剩余配额: {data.get('remaining_quota', 0)}\")
print(f\"Chat ID: {data.get('chat_id', 0)}\")
"
echo ""

# 3. 测试使用 RAG 的问答（首次可能没有知识库内容）
echo "3. 测试 AI 问答（使用 RAG）..."
curl -s -X POST "$API/ai/chat/" \
  -H "Authorization: jwt $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是动态规划？","use_rag":true,"top_k":3}' | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"回答长度: {len(data.get('answer', ''))} 字符\")
print(f\"Tokens 使用: {data.get('tokens_used', 0)}\")
print(f\"剩余配额: {data.get('remaining_quota', 0)}\")
print(f\"Chat ID: {data.get('chat_id', 0)}\")
"
echo ""

# 4. 查看聊天历史
echo "4. 查看聊天历史..."
curl -s -X GET "$API/ai/history/?page=1&page_size=5" \
  -H "Authorization: jwt $TOKEN" | \
  python3 -m json.tool | head -30
echo ""

# 5. 获取特定聊天记录详情
echo "5. 获取聊天记录详情（chat_id=1）..."
curl -s -X GET "$API/ai/history/1/" \
  -H "Authorization: jwt $TOKEN" | \
  python3 -m json.tool | head -40
echo ""

# 6. 测试添加知识文档（需要先有班级）
echo "6. 测试添加知识文档..."
# 先创建一个教练账号
COACH_TOKEN=$(curl -s -X POST "$API/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_coach","password":"coach123"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin).get('token', ''))")

if [ -n "$COACH_TOKEN" ]; then
  echo "✅ 教练 Token: ${COACH_TOKEN:0:40}..."
  
  # 尝试添加知识文档
  curl -s -X POST "$API/ai/knowledge/" \
    -H "Authorization: jwt $COACH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "title":"动态规划基础教程",
      "content":"动态规划是一种算法思想，用于解决具有最优子结构和重叠子问题性质的问题。核心步骤包括：定义状态、状态转移方程、初始化、计算顺序。",
      "category":"algorithm",
      "tags":["动态规划","算法","DP"]
    }' | python3 -m json.tool
else
  echo "⚠️ 教练账号不存在，跳过知识文档测试"
fi
echo ""

# 7. 查看知识库列表
echo "7. 查看知识库列表..."
curl -s -X GET "$API/ai/knowledge/?page=1&page_size=5" \
  -H "Authorization: jwt $TOKEN" | \
  python3 -m json.tool | head -30
echo ""

echo "=========================================="
echo "测试完成！"
echo "=========================================="
