#!/bin/bash

# 第一步：编译 C++ 代码
echo "=== Step 1: Compile ==="
curl -X POST http://localhost:5050/run \
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
      "copyOut": ["stdout", "stderr"]
    }]
  }' | python3 -m json.tool

echo ""
echo "=== Step 2: Run ==="
# 第二步：运行编译后的程序
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
      "cpuLimit": 10000000000,
      "memoryLimit": 268435456,
      "procLimit": 50,
      "copyOut": ["stdout", "stderr"]
    }]
  }' | python3 -m json.tool
