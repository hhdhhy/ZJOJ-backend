"""
本地 Embedding 服务
使用 sentence-transformers 将文本转换为向量
"""
import os
import hashlib
import numpy as np
from django.conf import settings


class EmbeddingService:
    """本地 Embedding 服务（简化版，使用哈希生成向量）"""
    
    def __init__(self, dimension=384):
        """
        初始化 Embedding 服务
        
        Args:
            dimension: 向量维度（默认384）
        """
        self.dimension = dimension
    
    def encode(self, text: str) -> list:
        """
        将单个文本转换为向量（使用哈希方法）
        
        Args:
            text: 输入文本
        
        Returns:
            向量列表
        """
        # 使用 SHA256 哈希生成固定长度的向量
        hash_bytes = hashlib.sha256(text.encode('utf-8')).digest()
        
        # 扩展到指定维度
        vector = np.zeros(self.dimension)
        for i in range(min(len(hash_bytes), self.dimension)):
            vector[i] = hash_bytes[i % len(hash_bytes)] / 255.0
        
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector.tolist()
    
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
