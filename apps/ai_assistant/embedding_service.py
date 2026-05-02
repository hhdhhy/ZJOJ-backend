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
        # 设置模型缓存目录（使用项目内的 ai_data 目录）
        if cache_dir is None:
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            cache_dir = os.path.join(base_dir, 'ai_data', 'embedding_models')
        
        # 确保目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 设置环境变量，使用 ModelScope 镜像（国内加速）
        os.environ['HF_HOME'] = cache_dir
        os.environ['TRANSFORMERS_CACHE'] = cache_dir
        os.environ['HUGGINGFACE_HUB_CACHE'] = cache_dir
        # 优先使用 ModelScope，如果失败再回退到 hf-mirror
        os.environ['HF_ENDPOINT'] = os.environ.get('HF_ENDPOINT', 'https://hf-mirror.com')
        
        # 默认使用中文优化的轻量级模型
        if model_name is None:
            model_name = 'shibing624/text2vec-base-chinese'
        
        self.model_name = model_name
        self.cache_dir = cache_dir
        
        # 加载模型（优先使用本地已下载的模型）
        print(f"Loading embedding model: {model_name}")
        print(f"Cache directory: {cache_dir}")
        
        # 检查本地是否已有已下载的模型缓存
        local_model_path = os.path.join(cache_dir, 'shibing624', 'text2vec-base-chinese')
        if os.path.exists(local_model_path):
            print(f"✅ Found local model at: {local_model_path}")
            try:
                self.model = SentenceTransformer(local_model_path)
                self.dimension = self.model.get_sentence_embedding_dimension()
                print(f"✅ Model loaded from local cache, dimension: {self.dimension}")
                return
            except Exception as e:
                print(f"⚠️ Failed to load from local cache: {e}, will try downloading...")

        # 国内环境优先尝试 ModelScope
        print("Trying ModelScope...")
        try:
            from modelscope import snapshot_download
            model_path = snapshot_download(
                'shibing624/text2vec-base-chinese',
                cache_dir=cache_dir
            )
            self.model = SentenceTransformer(model_path)
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"✅ Model loaded from ModelScope, dimension: {self.dimension}")
        except Exception as e:
            print(f"⚠️ Failed to load from ModelScope: {e}")
            print("Trying HuggingFace mirror...")
            try:
                self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
                self.dimension = self.model.get_sentence_embedding_dimension()
                print(f"✅ Model loaded from HuggingFace, dimension: {self.dimension}")
            except Exception as e2:
                print(f"❌ Failed to load model from all sources: {e2}")
                raise
    
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
