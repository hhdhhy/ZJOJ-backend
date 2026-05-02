#!/bin/bash
# 测试错误解决方案接口

# 获取 token
TOKEN=$(curl -s -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test_ai","password":"test123456"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "Token: ${TOKEN:0:50}..."
echo ""

# 测试不同的提交记录
for id in 38 39 40 41 42; do
  echo "=== 测试提交记录 $id ==="
  RESPONSE=$(curl -s -X GET "http://localhost:8000/api/ai/error-solution/$id/" \
    -H "Authorization: jwt $TOKEN")
  
  echo "$RESPONSE" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f\"状态: 200, 解决方案数: {d.get('count', 0)}, 剩余配额: {d.get('remaining_quota', 'N/A')}\")
except:
    print('解析失败')
    print(sys.stdin.read()[:200])
" 2>&1
  echo ""
done
