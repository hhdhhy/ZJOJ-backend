#!/bin/bash
# go-judge cgroup pids 限制修复脚本

echo "=== 检查并修复 go-judge cgroup pids 限制 ==="

# 1. 验证 clone3=0 参数
echo -e "\n[1] 检查 clone3 参数:"
if cat /proc/cmdline | grep -q "clone3=0"; then
    echo "✅ clone3=0 已生效"
else
    echo "❌ clone3=0 未生效，需要重启服务器"
    exit 1
fi

# 2. 停止现有 go-judge 进程
echo -e "\n[2] 停止现有 go-judge 进程..."
sudo pkill -9 executorserver 2>/dev/null
sudo supervisorctl stop go-judge 2>/dev/null
sleep 2

# 3. 启动 go-judge
echo -e "\n[3] 启动 go-judge..."
sudo systemd-run --scope -p Delegate=yes /usr/local/bin/executorserver -http-addr 0.0.0.0:5050 &
sleep 3

# 4. 查找并修改所有相关 cgroup 的 pids.max
echo -e "\n[4] 检查并修改 cgroup pids 限制..."
GOJUDGE_SCOPE=$(find /sys/fs/cgroup/system.slice -name "gojudge.scope" -type d 2>/dev/null | head -1)

if [ -n "$GOJUDGE_SCOPE" ]; then
    echo "找到 gojudge.scope: $GOJUDGE_SCOPE"
    
    # 修改父 scope 的 pids.max
    if [ -f "$GOJUDGE_SCOPE/pids.max" ]; then
        echo "设置 $GOJUDGE_SCOPE/pids.max = max"
        echo 'max' | sudo tee "$GOJUDGE_SCOPE/pids.max" > /dev/null
    fi
    
    # 修改 containers 子目录的 pids.max
    if [ -f "$GOJUDGE_SCOPE/containers/pids.max" ]; then
        echo "设置 $GOJUDGE_SCOPE/containers/pids.max = max"
        echo 'max' | sudo tee "$GOJUDGE_SCOPE/containers/pids.max" > /dev/null
    fi
    
    # 修改 api 子目录的 pids.max
    if [ -f "$GOJUDGE_SCOPE/api/pids.max" ]; then
        echo "设置 $GOJUDGE_SCOPE/api/pids.max = max"
        echo 'max' | sudo tee "$GOJUDGE_SCOPE/api/pids.max" > /dev/null
    fi
else
    echo "⚠️  未找到 gojudge.scope，go-judge 可能未启动"
fi

# 5. 测试 go-judge
echo -e "\n[5] 测试 go-judge..."
sleep 2
RESULT=$(curl -s http://localhost:5050/run -X POST \
  -H 'Content-Type: application/json' \
  -d '{"cmd":[{"args":["/bin/echo","Hello World!"]}]}' 2>/dev/null)

echo "$RESULT" | python3 -m json.tool

# 6. 检查结果
if echo "$RESULT" | grep -q '"status": "Accepted"'; then
    echo -e "\n✅ go-judge 测试成功！"
    exit 0
else
    echo -e "\n❌ go-judge 测试失败"
    echo -e "\n查看内核日志:"
    sudo dmesg | grep -i 'cgroup.*fork' | tail -3
    exit 1
fi
