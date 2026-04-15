"""
本地 Embedding 服务
使用 sentence-transformers 将文本转换为向量
"""
from sentence_transformers import SentenceTransformer
import os
from django.conf import settings


class EmbeddingService:
    """本地 Embedding 服务"""
    
    def __init__(self, model_name=None, cache_dir=None):
        """
        初始化 Embedding 服务
        
        Args:
            model_name: 模型名称（默认使用 ModelScope 下载的模型）
            cache_dir: 模型缓存目录（默认存到 E 盘）
        """
        # 设置模型缓存目录到非 C 盘
        if cache_dir is None:
            cache_dir = getattr(settings, 'EMBEDDING_CACHE_DIR', 'E:/ai_models/cache')
        
        # 确保目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 设置环境变量，让 huggingface 缓存到指定目录
        os.environ['HF_HOME'] = cache_dir
        os.environ['TRANSFORMERS_CACHE'] = cache_dir
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'  # 使用国内镜像
        
        # 默认使用 ModelScope 下载的模型
        if model_name is None:
            model_name = f'{cache_dir}/damo/nlp_corom_sentence-embedding_chinese-base'
        
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def encode(self, text: str) -> list:
        """
        将单个文本转换为向量
        
        Args:
            text: 输入文本
        
        Returns:
            向量列表
        """
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    def encode_batch(self, texts: list) -> list:
        """
        批量转换文本为向量
        
        Args:
            texts: 文本列表
        
        Returns:
            向量列表的列表
        """
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        return self.dimension
