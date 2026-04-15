"""
ChromaDB 向量数据库操作
"""
import chromadb
from chromadb.config import Settings
from django.conf import settings
from .embedding_service import EmbeddingService


class VectorStore:
    """ChromaDB 向量数据库"""
    
    def __init__(self, collection_name='knowledge_base'):
        """
        初始化向量数据库
        
        Args:
            collection_name: 集合名称
        """
        # 获取 ChromaDB 存储路径（E盘）
        persist_directory = getattr(settings, 'CHROMA_DB_PATH', 'E:/ai_data/chroma_db')
        
        # 创建客户端
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False  # 关闭遥测
            )
        )
        
        # 初始化 Embedding 服务
        self.embedding_service = EmbeddingService()
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={'hnsw:space': 'cosine'}  # 使用余弦相似度
        )
    
    def add_document(self, doc_id: str, text: str, metadata: dict):
        """
        添加文档到向量数据库
        
        Args:
            doc_id: 文档ID（唯一）
            text: 文档文本内容
            metadata: 元数据（如标题、类型等）
        """
        # 生成向量
        embedding = self.embedding_service.encode(text)
        
        # 添加到集合
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text]
        )
    
    def add_batch(self, doc_ids: list, texts: list, metadatas: list):
        """
        批量添加文档
        
        Args:
            doc_ids: 文档ID列表
            texts: 文本列表
            metadatas: 元数据列表
        """
        # 批量生成向量
        embeddings = self.embedding_service.encode_batch(texts)
        
        # 批量添加
        self.collection.add(
            ids=doc_ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )
    
    def search(self, query: str, top_k=5, filter_metadata=None) -> list:
        """
        检索相似文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_metadata: 过滤条件（可选）
        
        Returns:
            相似文档列表，按相似度降序排列
        """
        # 生成查询向量
        query_embedding = self.embedding_service.encode(query)
        
        # 执行搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata,
            include=['documents', 'metadatas', 'distances']
        )
        
        # 格式化结果
        documents = []
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                documents.append({
                    'id': doc_id,
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'similarity': 1 - results['distances'][0][i]  # 转换为相似度
                })
        
        return documents
    
    def delete_document(self, doc_id: str):
        """
        删除文档
        
        Args:
            doc_id: 文档ID
        """
        self.collection.delete(ids=[doc_id])
    
    def delete_by_filter(self, filter_metadata: dict):
        """
        根据过滤条件删除文档
        
        Args:
            filter_metadata: 过滤条件
        """
        self.collection.delete(where=filter_metadata)
    
    def get_document_count(self) -> int:
        """获取文档总数"""
        return self.collection.count()
    
    def get_document(self, doc_id: str) -> dict:
        """
        获取单个文档
        
        Args:
            doc_id: 文档ID
        
        Returns:
            文档信息，不存在返回 None
        """
        result = self.collection.get(ids=[doc_id])
        if result['ids']:
            return {
                'id': result['ids'][0],
                'content': result['documents'][0],
                'metadata': result['metadatas'][0]
            }
        return None
    
    def update_document(self, doc_id: str, text: str, metadata: dict):
        """
        更新文档
        
        Args:
            doc_id: 文档ID
            text: 新文本
            metadata: 新元数据
        """
        embedding = self.embedding_service.encode(text)
        self.collection.update(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text]
        )
