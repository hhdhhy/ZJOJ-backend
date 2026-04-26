#!/bin/bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOiJSRDk2cWFWM3FzczZTVTY3R3JIUDNzIiwiZXhwIjoxNzc3MjM4ODY5LjgxODk1NDd9.MRSiBrI3kfbPHaR4ss3rqQP_V7m_6_HkVvvFhRcCyfo"

echo "=== 测试1: 创建知识库文档 ==="
curl -s -X POST http://localhost:8000/api/ai/knowledge/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "二分查找算法",
    "content": "二分查找是一种在有序数组中查找特定元素的搜索算法。搜索过程从数组的中间元素开始，如果中间元素正好是要查找的元素，则搜索过程结束；如果某一特定元素大于或者小于中间元素，则在数组大于或小于中间元素的那一半中查找，而且跟开始一样从中间元素开始比较。如果在某一步骤数组为空，则代表找不到。这种搜索算法每一次比较都使搜索范围缩小一半。时间复杂度为O(log n)。",
    "doc_type": "algorithm"
  }' | python3 -m json.tool

echo ""
echo "=== 测试2: 等待3秒让向量同步完成 ==="
sleep 3

echo ""
echo "=== 测试3: AI知识问答 ==="
curl -s -X POST http://localhost:8000/api/ai/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "二分查找的时间复杂度是多少？",
    "use_rag": true
  }' | python3 -m json.tool

echo ""
echo "=== 测试完成 ==="
