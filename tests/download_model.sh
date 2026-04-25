#!/bin/bash
# 在容器内下载 embedding 模型

echo "开始下载 embedding 模型..."

docker exec zjoj-web bash -c '
export HF_ENDPOINT=https://hf-mirror.com
export HF_HOME=/tmp/ai_models
export TRANSFORMERS_CACHE=/tmp/ai_models

python3 << 'PYTHON_EOF'
import sys
import os
from sentence_transformers import SentenceTransformer

# 设置国内镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HOME'] = '/tmp/ai_models'
os.environ['TRANSFORMERS_CACHE'] = '/tmp/ai_models'

print("配置信息:")
print(f"HF_ENDPOINT: {os.environ.get('HF_ENDPOINT')}")
print(f"HF_HOME: {os.environ.get('HF_HOME')}")
print()

model_name = "paraphrase-multilingual-MiniLM-L12-v2"
cache_dir = "/tmp/ai_models"

print(f"正在下载模型: {model_name}")
print(f"缓存目录: {cache_dir}")
print()

try:
    model = SentenceTransformer(model_name, cache_folder=cache_dir)
    dimension = model.get_sentence_embedding_dimension()
    print(f"✅ 模型下载成功!")
    print(f"   模型名称: {model_name}")
    print(f"   向量维度: {dimension}")
except Exception as e:
    print(f"❌ 模型下载失败: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_EOF
'

if [ $? -eq 0 ]; then
    echo ""
    echo "模型下载完成！现在重启服务以加载模型..."
    docker restart zjoj-web
    echo "请等待 15 秒让服务启动..."
    sleep 15
    echo ""
    echo "检查服务状态..."
    docker logs zjoj-web --tail 20 | grep -E "(Model loaded|Listening|worker)"
else
    echo ""
    echo "❌ 模型下载失败，请检查网络连接"
fi
