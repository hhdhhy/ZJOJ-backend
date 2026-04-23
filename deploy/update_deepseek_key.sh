#!/bin/bash
cd ~/projects/ZJOJ-backend

# 更新 DeepSeek API Key
sed -i 's/^DEEPSEEK_API_KEY=.*/DEEPSEEK_API_KEY=sk-115bbd8a90bb4f11914d21a49b8b55ce/' .env

echo "DeepSeek API Key 已更新"
grep DEEPSEEK .env

# 重启服务
docker compose restart web

echo "服务已重启，AI功能现在可以使用了！"
