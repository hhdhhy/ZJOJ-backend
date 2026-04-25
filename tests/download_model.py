#!/usr/bin/env python3
"""在容器内下载 embedding 模型"""
import sys
import os

# 设置国内镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HOME'] = '/tmp/ai_models'
os.environ['TRANSFORMERS_CACHE'] = '/tmp/ai_models'

print('配置信息:')
print(f"HF_ENDPOINT: {os.environ.get('HF_ENDPOINT')}")
print(f"HF_HOME: {os.environ.get('HF_HOME')}")
print()

model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
cache_dir = '/tmp/ai_models'

print(f'正在下载模型: {model_name}')
print(f'缓存目录: {cache_dir}')
print()

try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name, cache_folder=cache_dir)
    dimension = model.get_sentence_embedding_dimension()
    print(f'✅ 模型下载成功!')
    print(f'   模型名称: {model_name}')
    print(f'   向量维度: {dimension}')
except Exception as e:
    print(f'❌ 模型下载失败: {e}', file=sys.stderr)
    sys.exit(1)
