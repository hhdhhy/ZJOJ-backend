#!/bin/bash
# 测试 go-judge 编译功能

echo "=== 测试1: 编译 C++ 代码 ==="
curl -X POST http://localhost:5050/run \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": [{
      "args": ["/usr/bin/g++", "-std=c++17", "-O2", "-o", "/w/main", "/w/main.cpp"],
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
  }' | python3 -m json.tool

echo ""
echo "=== 测试2: 运行编译后的程序 ==="
# 假设 file_id 是 TEST_FILE_ID（需要替换为实际的 ID）
curl -X POST http://localhost:5050/run \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": [{
      "args": ["/w/main"],
      "env": ["PATH=/usr/bin:/bin"],
      "files": [
        {"content": "1 2"},
        {"name": "stdout", "max": 10240},
        {"name": "stderr", "max": 10240}
      ],
      "cpuLimit": 1000000000,
      "memoryLimit": 268435456,
      "procLimit": 50,
      "copyIn": {
        "main": {
          "fileId": "TEST_FILE_ID"
        }
      },
      "copyOut": ["stdout", "stderr"]
    }]
  }' | python3 -m json.tool
