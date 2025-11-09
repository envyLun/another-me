"""
文档预处理器 - NER + Embedding

重构后版本:
- 职责: 文档预处理,包含 NER 实体提取和 Embedding 生成
- 不包含: 存储逻辑、检索逻辑
- 依赖: NER Service + Embedding Function
"""

import asyncio
from typing import List, Callable, Optional, Any

from ame.models.domain import Document
from ame.foundation.nlp.ner import NERBase


class DocumentProcessor:
    """
    文档预处理器（NER + Embedding）
    
    设计理念:
    - 在文档存储前进行预处理
    - 生成 embedding 向量
    - 提取实体（NER）
    - 支持批量处理
    """
    
    def __init__(
        self,
        ner_service: NERBase,
        embedding_function: Callable[[str], Any]
    ):
        """
        初始化文档处理器
        
        Args:
            ner_service: NER 实体提取服务
            embedding_function: Embedding 生成函数
                输入: 文本 (str)
                输出: 向量 (List[float]) 或 awaitable
        """
        self.ner = ner_service
        self.embedding_fn = embedding_function
    
    async def process(self, doc: Document) -> Document:
        """
        预处理单个文档
        
        流程:
        1. 生成 embedding（如果缺失）
        2. 提取实体（NER）
        3. 返回增强后的文档
        
        Args:
            doc: 原始文档对象
        
        Returns:
            doc: 增强后的文档对象
        """
        # 1. 生成 embedding
        if not doc.embedding and doc.content:
            embedding_result = self.embedding_fn(doc.content)
            
            # 处理异步和同步两种情况
            if asyncio.iscoroutine(embedding_result):
                doc.embedding = await embedding_result
            else:
                doc.embedding = embedding_result
        
        # 2. 提取实体（NER）
        if not doc.entities and doc.content:
            entities = await self.ner.extract(doc.content)
            
            # 提取实体文本
            doc.entities = [e.text for e in entities]
            
            # 保留完整实体对象（包含类型和分数）
            if not hasattr(doc, "entity_objects"):
                doc.entity_objects = entities
        
        return doc
    
    async def batch_process(
        self,
        docs: List[Document],
        max_concurrent: int = 4
    ) -> List[Document]:
        """
        批量预处理文档（并发处理）
        
        Args:
            docs: 文档列表
            max_concurrent: 最大并发数
        
        Returns:
            docs: 增强后的文档列表
        """
        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(doc):
            async with semaphore:
                return await self.process(doc)
        
        # 并发处理
        tasks = [process_with_semaphore(doc) for doc in docs]
        processed_docs = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤异常结果
        valid_docs = []
        for i, result in enumerate(processed_docs):
            if isinstance(result, Exception):
                print(f"Warning: Document {docs[i].id} processing failed: {result}")
            else:
                valid_docs.append(result)
        
        return valid_docs
    
    async def update_embedding(self, doc: Document) -> Document:
        """
        仅更新 embedding（用于内容更新后）
        
        Args:
            doc: 文档对象
        
        Returns:
            doc: 更新 embedding 后的文档
        """
        if not doc.content:
            return doc
        
        embedding_result = self.embedding_fn(doc.content)
        
        if asyncio.iscoroutine(embedding_result):
            doc.embedding = await embedding_result
        else:
            doc.embedding = embedding_result
        
        return doc
    
    async def update_entities(self, doc: Document) -> Document:
        """
        仅更新实体（用于内容更新后）
        
        Args:
            doc: 文档对象
        
        Returns:
            doc: 更新实体后的文档
        """
        if not doc.content:
            return doc
        
        entities = await self.ner.extract(doc.content)
        doc.entities = [e.text for e in entities]
        
        if not hasattr(doc, "entity_objects"):
            doc.entity_objects = entities
        
        return doc
