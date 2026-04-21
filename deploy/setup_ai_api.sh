#!/bin/bash
# ZJOJ AI API Key 配置脚本
# 用法: ./setup_ai_api.sh

set -e

echo "========================================="
echo "ZJOJ AI API 配置向导"
echo "========================================="
echo ""

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo "❌ 错误: 未找到 .env 文件"
    echo "   请先运行: ./deploy/setup_env.sh"
    exit 1
fi

echo "请选择 AI 服务提供商："
echo "1. DeepSeek (推荐)"
echo "2. 智谱 AI (Zhipu)"
echo "3. 通义千问 (Qwen)"
echo "4. 跳过 AI 配置"
echo ""

read -p "请选择 [1-4]: " PROVIDER_CHOICE

case $PROVIDER_CHOICE in
    1)
        echo ""
        echo "--- DeepSeek 配置 ---"
        read -sp "请输入 DeepSeek API Key: " API_KEY
        echo ""
        
        if [ -z "$API_KEY" ]; then
            echo "❌ API Key 不能为空"
            exit 1
        fi
        
        read -p "模型名称 [deepseek-chat]: " MODEL
        MODEL=${MODEL:-deepseek-chat}
        
        read -p "API 基础URL [https://api.deepseek.com]: " BASE_URL
        BASE_URL=${BASE_URL:-https://api.deepseek.com}
        
        # 更新 .env 文件
        sed -i "s/^DEEPSEEK_API_KEY=.*/DEEPSEEK_API_KEY=$API_KEY/" .env
        sed -i "s/^DEEPSEEK_MODEL=.*/DEEPSEEK_MODEL=$MODEL/" .env
        sed -i "s|^DEEPSEEK_BASE_URL=.*|DEEPSEEK_BASE_URL=$BASE_URL|" .env
        
        echo ""
        echo "✅ DeepSeek 配置完成"
        echo "   模型: $MODEL"
        echo "   API: $BASE_URL"
        ;;
        
    2)
        echo ""
        echo "--- 智谱 AI 配置 ---"
        read -sp "请输入智谱 API Key: " API_KEY
        echo ""
        
        if [ -z "$API_KEY" ]; then
            echo "❌ API Key 不能为空"
            exit 1
        fi
        
        # 智谱使用不同的环境变量
        echo ""
        echo "⚠️  注意: 智谱 AI 需要在代码中单独配置"
        echo "   当前仅保存 API Key 到 .env 文件"
        
        # 添加到 .env
        if grep -q "^ZHIPU_API_KEY=" .env; then
            sed -i "s/^ZHIPU_API_KEY=.*/ZHIPU_API_KEY=$API_KEY/" .env
        else
            echo "" >> .env
            echo "# 智谱 AI 配置" >> .env
            echo "ZHIPU_API_KEY=$API_KEY" >> .env
        fi
        
        echo ""
        echo "✅ 智谱 API Key 已保存"
        ;;
        
    3)
        echo ""
        echo "--- 通义千问配置 ---"
        read -sp "请输入通义千问 API Key: " API_KEY
        echo ""
        
        if [ -z "$API_KEY" ]; then
            echo "❌ API Key 不能为空"
            exit 1
        fi
        
        # 通义使用不同的环境变量
        echo ""
        echo "⚠️  注意: 通义千问需要在代码中单独配置"
        echo "   当前仅保存 API Key 到 .env 文件"
        
        # 添加到 .env
        if grep -q "^DASHSCOPE_API_KEY=" .env; then
            sed -i "s/^DASHSCOPE_API_KEY=.*/DASHSCOPE_API_KEY=$API_KEY/" .env
        else
            echo "" >> .env
            echo "# 通义千问配置" >> .env
            echo "DASHSCOPE_API_KEY=$API_KEY" >> .env
        fi
        
        echo ""
        echo "✅ 通义千问 API Key 已保存"
        ;;
        
    4)
        echo ""
        echo "已跳过 AI 配置"
        echo "如需启用 AI 功能，请再次运行此脚本"
        exit 0
        ;;
        
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "重启服务以应用配置"
echo "========================================="
echo ""

read -p "是否现在重启服务？(y/N): " RESTART
if [[ $RESTART =~ ^[Yy]$ ]]; then
    echo ""
    echo "正在重启服务..."
    docker compose restart web
    
    echo ""
    echo "✅ 服务已重启"
    echo ""
    echo "查看日志: docker compose logs -f web"
else
    echo ""
    echo "稍后请手动重启服务:"
    echo "  docker compose restart web"
fi

echo ""
echo "========================================="
echo "完成！"
echo "========================================="
