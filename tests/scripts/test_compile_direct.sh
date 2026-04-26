#!/bin/bash
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
          "content": "#include<bits/stdc++.h>\nusing namespace std;\nint main() { int x; cin>>x; cout<<1; return 0; }"
        }
      },
      "copyOut": ["stdout", "stderr"],
      "copyOutCached": ["main"]
    }]
  }'
