# AI 助手系统详细实现文档

## 📋 概述

本文档详细描述 ZJOJ AI 助手的完整实现，包括 RAG 架构、向量检索、文本嵌入、DeepSeek API 集成等核心技术。

---

## 🏗️ 系统架构

### RAG 架构图

```
用户提问
    ↓
┌─────────────────────────┐
│   Query Preprocessing   │
│   - 问题解析             │
│   - 关键词提取           │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   Vector Embedding      │
│   (text2vec-base-chinese)│
│   - 将问题转换为向量     │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   ChromaDB Retrieval    │
│   - 相似度搜索           │
│   - 返回 Top-K 相关文档  │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   Prompt Construction   │
│   - 组合上下文 + 问题    │
│   - 构建提示词模板       │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   DeepSeek API          │
│   - 调用大语言模型       │
│   - 生成回答             │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   Response Postprocess  │
│   - 格式化输出           │
│   - 添加引用来源         │
└───────────┬─────────────┘
            ↓
        返回给用户
```

### 组件交互图

```
┌──────────────────────────────────────────┐
│         Django Web Server                │
│                                          │
│  ┌──────────────┐    ┌────────────────┐ │
│  │ AI Chat View │───▶│ RAG Service    │ │
│  └──────────────┘    └───────┬────────┘ │
└──────────────────────────────┼──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Embedding Model    │
                    │  (text2vec)         │
                    │                     │
                    │  - 加载本地模型      │
                    │  - 生成向量嵌入      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   ChromaDB          │
                    │   (Vector DB)       │
                    │                     │
                    │  - 存储文档向量      │
                    │  - 相似度检索        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   DeepSeek API      │
                    │   (Cloud LLM)       │
                    │                     │
                    │  - 接收提示词        │
                    │  - 生成回答          │
                    └─────────────────────┘
```

---

## 🔧 核心组件详解

### 1. RAG Service (`apps/ai_assistant/rag_service.py`)

#### 1.1 类结构

```python
class RAGService:
    """RAG (Retrieval-Augmented Generation) 服务"""
    
    def __init__(self):
        """初始化 RAG 服务"""
        self.embedding_model = EmbeddingModel()
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection("zjoj_docs")
        self.deepseek_api_key = settings.DEEPSEEK_API_KEY
        
    def add_document(self, doc_id, content, metadata=None):
        """添加文档到知识库"""
        
    def query(self, question, top_k=5):
        """查询并生成回答"""
        
    def _retrieve(self, query_vector, top_k=5):
        """从 ChromaDB 检索相关文档"""
        
    def _construct_prompt(self, question, contexts):
        """构建提示词"""
        
    def _generate_response(self, prompt):
        """调用 DeepSeek API 生成回答"""
```

#### 1.2 主要方法实现

##### `query()` - 主查询方法

```python
def query(self, question, top_k=5):
    """
    处理用户查询
    
    Args:
        question: 用户问题
        top_k: 返回最相关的 K 个文档
    
    Returns:
        {
            'answer': 'AI 生成的回答',
            'contexts': [
                {
                    'content': '相关文档内容',
                    'metadata': {...},
                    'score': 相似度分数
                }
            ],
            'sources': ['来源1', '来源2']
        }
    """
    
    # 1. 将问题转换为向量
    query_vector = self.embedding_model.encode(question)
    
    # 2. 检索相关文档
    contexts = self._retrieve(query_vector, top_k)
    
    # 3. 构建提示词
    prompt = self._construct_prompt(question, contexts)
    
    # 4. 调用 DeepSeek API
    answer = self._generate_response(prompt)
    
    # 5. 提取来源
    sources = [ctx['metadata'].get('source', 'Unknown') for ctx in contexts]
    
    return {
        'answer': answer,
        'contexts': contexts,
        'sources': list(set(sources))
    }
```

##### `_retrieve()` - 向量检索

```python
def _retrieve(self, query_vector, top_k=5):
    """
    从 ChromaDB 检索最相关的文档
    
    Args:
        query_vector: 查询向量 (768维)
        top_k: 返回前 K 个结果
    
    Returns:
        [
            {
                'content': '文档内容',
                'metadata': {'source': '...', 'title': '...'},
                'score': 0.85  # 相似度分数
            }
        ]
    """
    
    results = self.collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=['documents', 'metadatas', 'distances']
    )
    
    contexts = []
    for i, doc in enumerate(results['documents'][0]):
        contexts.append({
            'content': doc,
            'metadata': results['metadatas'][0][i],
            'score': 1 - results['distances'][0][i]  # 距离转相似度
        })
    
    return contexts
```

##### `_construct_prompt()` - 构建提示词

```python
def _construct_prompt(self, question, contexts):
    """
    构建 DeepSeek API 的提示词
    
    模板:
    ```
    你是一个编程助手，请根据以下上下文回答问题。
    
    上下文:
    1. {context1}
    2. {context2}
    ...
    
    问题: {question}
    
    回答:
    ```
    """
    
    context_text = "\n\n".join([
        f"{i+1}. {ctx['content'][:500]}"  # 限制每个上下文长度
        for i, ctx in enumerate(contexts)
    ])
    
    prompt = f"""你是一个专业的编程助手，请根据以下上下文回答问题。

上下文信息:
{context_text}

用户问题: {question}

请给出详细、准确的回答。如果上下文中没有相关信息，请说明你不知道。"""
    
    return prompt
```

##### `_generate_response()` - 调用 DeepSeek API

```python
def _generate_response(self, prompt):
    """
    调用 DeepSeek API 生成回答
    
    Args:
        prompt: 提示词
    
    Returns:
        str: AI 生成的回答
    """
    
    import requests
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.deepseek_api_key}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的编程助手"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        raise Exception(f"DeepSeek API error: {response.text}")
```

---

### 2. Embedding Model (`apps/ai_assistant/embedding_model.py`)

#### 2.1 模型加载

```python
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    """文本嵌入模型"""
    
    def __init__(self, model_name="shibing624/text2vec-base-chinese"):
        """
        加载预训练的文本嵌入模型
        
        Args:
            model_name: 模型名称 (HuggingFace)
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = 768  # 向量维度
        
    def encode(self, text):
        """
        将文本转换为向量
        
        Args:
            text: 输入文本
        
        Returns:
            list: 768维向量
        """
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def encode_batch(self, texts):
        """
        批量转换文本为向量
        
        Args:
            texts: 文本列表
        
        Returns:
            list: 向量列表
        """
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
```

#### 2.2 模型配置

**模型选择**: `shibing624/text2vec-base-chinese`

**特性**:
- 基于 BERT 架构
- 支持中文文本
- 输出 768 维向量
- 适用于语义相似度计算

**安装依赖**:
```bash
pip install sentence-transformers
pip install torch
```

**首次加载**:
```python
# 模型会自动从 HuggingFace 下载并缓存
model = EmbeddingModel()
# 缓存位置: ~/.cache/huggingface/hub/
```

---

### 3. ChromaDB 集成

#### 3.1 数据库初始化

```python
import chromadb

class ChromaDBManager:
    """ChromaDB 管理器"""
    
    def __init__(self, persist_directory="./chroma_db"):
        """
        初始化 ChromaDB
        
        Args:
            persist_directory: 数据持久化目录
        """
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="zjoj_docs",
            metadata={"description": "ZJOJ 知识库文档"}
        )
        
    def add_documents(self, documents, ids, metadatas):
        """
        批量添加文档
        
        Args:
            documents: 文档内容列表
            ids: 文档 ID 列表
            metadatas: 元数据列表
        """
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
    def search(self, query_embedding, top_k=5):
        """
        相似度搜索
        
        Args:
            query_embedding: 查询向量
            top_k: 返回前 K 个结果
        
        Returns:
            dict: 搜索结果
        """
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
```

#### 3.2 文档索引示例

```python
# 初始化
db_manager = ChromaDBManager()
embedding_model = EmbeddingModel()

# 准备文档
documents = [
    "go-judge 是一个代码评测沙箱系统...",
    "Celery 是一个分布式任务队列...",
    "Django REST Framework 用于构建 API..."
]

# 生成向量
embeddings = embedding_model.encode_batch(documents)

# 添加到 ChromaDB
db_manager.collection.add(
    documents=documents,
    ids=["doc_1", "doc_2", "doc_3"],
    metadatas=[
        {"source": "judge_system.md", "category": "评测系统"},
        {"source": "celery.md", "category": "异步任务"},
        {"source": "drf.md", "category": "API框架"}
    ]
)
```

---

## 📊 数据流详解

### 1. 文档入库流程

```
原始文档 (Markdown/PDF/TXT)
    ↓
┌─────────────────────┐
│  Document Parser    │
│  - 提取文本内容      │
│  - 清理格式          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Text Chunking      │
│  - 分段 (每段500字)  │
│  - 保持语义完整性    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Embedding Model    │
│  - 生成向量 (768维)  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  ChromaDB Storage   │
│  - 存储向量 + 原文   │
│  - 建立索引          │
└─────────────────────┘
```

### 2. 查询响应流程

```
用户问题
    ↓
┌─────────────────────┐
│  Query Embedding    │
│  - 生成问题向量      │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Vector Search      │
│  - ChromaDB 检索     │
│  - 返回 Top-5 文档   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Prompt Builder     │
│  - 组合上下文        │
│  - 构建提示词        │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  DeepSeek API       │
│  - 调用 LLM          │
│  - 生成回答          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Response Formatter │
│  - 格式化输出        │
│  - 添加引用          │
└──────────┬──────────┘
           ↓
      返回给用户
```

---

## 🔍 API 接口

### POST /api/ai/chat/

**请求**:
```json
{
  "question": "如何使用 go-judge 编译 C++ 代码？",
  "top_k": 5
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "answer": "使用 go-judge 编译 C++ 代码需要以下步骤:\n\n1. 准备编译命令...\n2. 设置 copyOutCached...\n\n详细示例见下文。",
    "contexts": [
      {
        "content": "go-judge 是一个代码评测沙箱系统，支持 C/C++、Python、Java 等多种语言...",
        "metadata": {
          "source": "JUDGE_SYSTEM.md",
          "category": "评测系统"
        },
        "score": 0.92
      }
    ],
    "sources": ["JUDGE_SYSTEM.md", "GOJUDGE_DOCUMENTATION.md"]
  }
}
```

---

## ⚙️ 配置说明

### 环境变量

```bash
# .env 文件
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
EMBEDDING_MODEL_NAME=shibing624/text2vec-base-chinese
CHROMA_DB_PATH=./chroma_db
AI_MAX_TOKENS=2000
AI_TEMPERATURE=0.7
```

### Django 配置

```python
# settings.py

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Embedding 模型配置
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME', 'shibing624/text2vec-base-chinese')

# ChromaDB 配置
CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', './chroma_db')

# AI 助手参数
AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', 2000))
AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', 0.7))
AI_TOP_K = int(os.getenv('AI_TOP_K', 5))
```

---

## 📈 性能优化

### 1. 向量缓存

```python
from functools import lru_cache

class EmbeddingModel:
    @lru_cache(maxsize=1000)
    def encode_cached(self, text):
        """缓存常用文本的向量"""
        return self.encode(text)
```

### 2. 批量索引

```python
# 批量添加文档时，一次性生成所有向量
documents = [...]  # 1000 个文档
embeddings = embedding_model.encode_batch(documents)  # 批量编码
chroma_db.add(documents, embeddings, ids, metadatas)
```

### 3. 异步调用

```python
@shared_task
def async_generate_answer(question, context_ids):
    """异步生成回答，避免阻塞主线程"""
    rag_service = RAGService()
    result = rag_service.query(question)
    return result
```

---

## ⚠️ 常见问题

### Q1: 模型加载失败

**错误**: `OSError: Can't load model 'shibing624/text2vec-base-chinese'`

**解决方法**:
```bash
# 检查网络连接
ping huggingface.co

# 使用镜像源
export HF_ENDPOINT=https://hf-mirror.com
pip install -U huggingface_hub

# 手动下载模型
git clone https://hf-mirror.com/shibing624/text2vec-base-chinese
```

### Q2: ChromaDB 查询慢

**原因**: 文档数量过多或未建立索引

**解决方法**:
```python
# 定期压缩数据库
chroma_client.persist()

# 使用更高效的分段策略
# 每段控制在 300-500 字
```

### Q3: DeepSeek API 调用失败

**错误**: `401 Unauthorized`

**解决方法**:
```bash
# 检查 API Key 是否正确
echo $DEEPSEEK_API_KEY

# 检查余额是否充足
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     https://api.deepseek.com/v1/user/balance
```

---

## 🔗 相关文档

- [AI 助手模块](06-MODULES/ai-assistant.md)
- [API 参考](04-API_REFERENCE.md)
- [部署指南](03-DEPLOYMENT.md)

---

**最后更新**: 2026-04-27
