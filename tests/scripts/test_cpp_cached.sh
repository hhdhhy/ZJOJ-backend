#!/bin/bash

# 第一步：编译 C++ 代码并缓存
echo "=== Step 1: Compile ==="
COMPILE_RESULT=$(curl -s -X POST http://localhost:5050/run \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": [{
      "args": ["/usr/bin/g++", "-std=c++17", "-O2", "/w/main.cpp", "-o", "/w/main"],
      "env": ["PATH=/usr/bin:/bin"],
      "files": [
        {"content": ""},
        {"name": "stdout", "max": 10240},
        {"name": "stderr", "max": 10240}
      ],
      "cpuLimit": 10000000000,
      "memoryLimit": 536870912,
      "procLimit": 50,
      "copyIn": {
        "main.cpp": {
          "content": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}"
        }
      },
      "copyOut": ["stdout", "stderr"],
      "copyOutCached": ["main"]
    }]
  }')

echo "$COMPILE_RESULT" | python3 -m json.tool

# 提取 fileId
FILE_ID=$(echo "$COMPILE_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['fileIds']['main'])")
echo ""
echo "File ID: $FILE_ID"

echo ""
echo "=== Step 2: Run with cached file ==="
# 第二步：使用缓存的文件运行
curl -X POST http://localhost:5050/run \
  -H "Content-Type: application/json" \
  -d "{
    \"cmd\": [{
      \"args\": [\"/w/main\"],
      \"env\": [\"PATH=/usr/bin:/bin\"],
      \"files\": [
        {\"content\": \"1 2\"},
        {\"name\": \"stdout\", \"max\": 10240},
        {\"name\": \"stderr\", \"max\": 10240}
      ],
      \"cpuLimit\": 10000000000,
      \"memoryLimit\": 268435456,
      \"procLimit\": 50,
      \"copyIn\": {
        \"main\": {
          \"fileId\": \"$FILE_ID\"
        }
      },
      \"copyOut\": [\"stdout\", \"stderr\"]
    }]
  }" | python3 -m json.tool

echo ""
echo "=== Step 3: Delete cached file ==="
# 第三步：删除缓存文件
curl -X DELETE "http://localhost:5050/file/$FILE_ID"
