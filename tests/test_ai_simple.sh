#!/bin/bash
# 简单测试 AI 助手

API="http://101.35.233.33:8000/api"

echo "登录获取 token..."
TOKEN=$(curl -s -X POST "$API/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_student","password":"student123"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "Token: ${TOKEN:0:40}..."
echo ""

echo "测试 AI 问答（不使用 RAG）..."
curl -s -X POST "$API/ai/chat/" \
  -H "Authorization: jwt $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是动态规划？","use_rag":false}' | \
  python3 -m json.tool

echo ""
echo "测试完成！"
