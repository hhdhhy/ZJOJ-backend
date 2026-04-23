"""
本地 Embedding 服务
使用 sentence-transformers 将文本转换为向量
"""
import os
from sentence_transformers import SentenceTransformer
from django.conf import settings


class EmbeddingService:
    """本地 Embedding 服务"""
    
    def __init__(self, model_name=None, cache_dir=None):
        """
        初始化 Embedding 服务
        
        Args:
            model_name: 模型名称（默认使用 paraphrase-multilingual-MiniLM-L12-v2）
            cache_dir: 模型缓存目录
        """
        # 设置模型缓存目录
        if cache_dir is None:
            cache_dir = getattr(settings, 'EMBEDDING_CACHE_DIR', '/tmp/ai_models')
        
        # 确保目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 设置环境变量，使用国内镜像
        os.environ['HF_HOME'] = cache_dir
        os.environ['TRANSFORMERS_CACHE'] = cache_dir
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
        
        # 默认使用多语言轻量级模型（支持中文）
        if model_name is None:
            # 使用已下载的模型路径
            model_name = '/tmp/ai_models/models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2/snapshots'
            # 查找最新的 snapshot 目录
            import glob
            snapshots = glob.glob(f'{model_name}/*')
            if snapshots:
                model_name = snapshots[0]  # 使用第一个（最新的）snapshot
            else:
                # 如果没有找到 snapshot，回退到模型名称
                model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
        
        self.model_name = model_name
        self.cache_dir = cache_dir
        
        # 加载模型（首次运行会自动从镜像下载）
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded successfully, dimension: {self.dimension}")
    
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
        return [self.encode(text) for text in texts]
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        return self.dimension
