"""
Search Service - 文档检索服务

提供文档检索的业务级服务
基于 RetrievalPipeline 和 DocumentStore
"""

from typing import List, Dict, Optional, Any
from datetime import datetime

from ame.models.domain import Document, SearchResult
from ame.storage.document_store import DocumentStore
from ame.retrieval.pipeline import RetrievalPipeline
from ame.retrieval.base import RetrievalResult


class SearchService:
    """
    文档检索服务
    
    职责：
    - 委托检索管道执行检索
    - 结果映射和过滤
    - 提供便捷的检索接口
    """
    
    def __init__(
        self,
        document_store: DocumentStore,
        retrieval_pipeline: RetrievalPipeline
    ):
        """
        初始化检索服务
        
        Args:
            document_store: 文档存储实例
            retrieval_pipeline: 检索管道实例
        """
        self.store = document_store
        self.pipeline = retrieval_pipeline
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        执行文档检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filters: 过滤条件
        
        Returns:
            results: 搜索结果列表
        """
        # 委托给 pipeline 执行检索
        retrieval_results = await self.pipeline.execute(
            query=query,
            top_k=top_k * 2,
            context=filters or {}
        )
        
        if not retrieval_results:
            return []
        
        # 提取文档 ID
        doc_ids = [r.metadata.get("doc_id") for r in retrieval_results if r.metadata.get("doc_id")]
        
        # 获取完整文档
        docs = await self.store.get_by_ids(doc_ids)
        doc_map = {doc.id: doc for doc in docs}
        
        # 应用过滤器并构建结果
        search_results = []
        
        for r in retrieval_results:
            doc_id = r.metadata.get("doc_id")
            doc = doc_map.get(doc_id)
            
            if not doc:
                continue
            
            if filters and not self._match_filters(doc, r.score, filters):
                continue
            
            search_results.append(SearchResult(
                doc_id=doc.id,
                content=doc.content,
                score=r.score,
                source=r.source,
                metadata=doc.metadata,
                entities=doc.entities
            ))
        
        return search_results[:top_k]
    
    async def search_by_time_range(
        self,
        start_date: datetime,
        end_date: datetime,
        doc_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Document]:
        """基于时间范围检索文档"""
        return await self.store.list({
            "after": start_date,
            "before": end_date,
            "doc_type": doc_type,
            "limit": limit
        })
    
    async def search_by_date(
        self,
        date: datetime,
        doc_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Document]:
        """检索指定日期的文档"""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return await self.search_by_time_range(
            start_date=start_date,
            end_date=end_date,
            doc_type=doc_type,
            limit=limit
        )
    
    async def search_similar(
        self,
        doc_id: str,
        top_k: int = 10
    ) -> List[SearchResult]:
        """查找相似文档"""
        doc = await self.store.get(doc_id)
        if not doc:
            return []
        
        results = await self.search(
            query=doc.content,
            top_k=top_k + 1
        )
        
        return [r for r in results if r.doc_id != doc_id][:top_k]
    
    def _match_filters(
        self,
        doc: Document,
        score: float,
        filters: Dict[str, Any]
    ) -> bool:
        """检查文档是否匹配过滤条件"""
        if "doc_type" in filters and doc.doc_type != filters["doc_type"]:
            return False
        
        if "after" in filters and doc.timestamp and doc.timestamp < filters["after"]:
            return False
        
        if "before" in filters and doc.timestamp and doc.timestamp > filters["before"]:
            return False
        
        if "min_score" in filters and score < filters["min_score"]:
            return False
        
        if "status" in filters and doc.status != filters["status"]:
            return False
        
        return True
