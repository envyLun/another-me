"""
文档检索服务 - 委托给 RetrievalPipeline

重构后版本:
- 职责: 文档检索服务,封装 Pipeline 调用
- 不包含: 存储管理、文档预处理
- 依赖: DocumentStore + RetrievalPipeline
"""

from typing import List, Dict, Optional, Any
from datetime import datetime

from ame.models.domain import Document, SearchResult
from ame.storage.document_store import DocumentStore
from ame.retrieval.pipeline import RetrievalPipeline
from ame.retrieval.base import RetrievalResult


class DocumentSearchService:
    """
    文档检索服务
    
    设计理念:
    - 委托给 RetrievalPipeline 执行检索
    - 负责结果映射和过滤
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
        
        流程:
        1. 委托给 pipeline 执行检索
        2. 获取完整文档信息
        3. 应用过滤器
        4. 构建搜索结果
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filters: 过滤条件
                - doc_type: 文档类型
                - after: 开始时间
                - before: 结束时间
                - min_score: 最小分数
        
        Returns:
            results: 搜索结果列表
        """
        # 1. 委托给 pipeline 执行检索
        retrieval_results = await self.pipeline.execute(
            query=query,
            top_k=top_k * 2,  # 检索更多用于过滤
            context=filters or {}
        )
        
        if not retrieval_results:
            return []
        
        # 2. 提取文档 ID
        doc_ids = [r.metadata.get("doc_id") for r in retrieval_results if r.metadata.get("doc_id")]
        
        # 3. 获取完整文档
        docs = await self.store.get_by_ids(doc_ids)
        doc_map = {doc.id: doc for doc in docs}
        
        # 4. 应用过滤器并构建结果
        search_results = []
        
        for r in retrieval_results:
            doc_id = r.metadata.get("doc_id")
            doc = doc_map.get(doc_id)
            
            if not doc:
                continue
            
            # 应用过滤器
            if filters and not self._match_filters(doc, r.score, filters):
                continue
            
            # 构建搜索结果
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
        """
        基于时间范围检索文档
        
        Args:
            start_date: 开始时间
            end_date: 结束时间
            doc_type: 文档类型过滤（可选）
            limit: 返回数量限制
        
        Returns:
            documents: 文档列表（按时间降序）
        """
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
        """
        检索指定日期的文档
        
        Args:
            date: 目标日期
            doc_type: 文档类型过滤（可选）
            limit: 返回数量限制
        
        Returns:
            documents: 文档列表
        """
        # 计算当日的开始和结束时间
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
        """
        查找相似文档
        
        流程:
        1. 获取源文档
        2. 使用文档内容作为查询
        3. 排除源文档本身
        
        Args:
            doc_id: 源文档 ID
            top_k: 返回结果数量
        
        Returns:
            results: 相似文档列表
        """
        # 获取源文档
        doc = await self.store.get(doc_id)
        if not doc:
            return []
        
        # 使用文档内容作为查询
        results = await self.search(
            query=doc.content,
            top_k=top_k + 1  # +1 以排除自身
        )
        
        # 排除源文档本身
        return [r for r in results if r.doc_id != doc_id][:top_k]
    
    # ========== 私有方法 ==========
    
    def _match_filters(
        self,
        doc: Document,
        score: float,
        filters: Dict[str, Any]
    ) -> bool:
        """
        检查文档是否匹配过滤条件
        
        Args:
            doc: 文档对象
            score: 检索分数
            filters: 过滤条件
        
        Returns:
            matched: 是否匹配
        """
        # 文档类型过滤
        if "doc_type" in filters:
            if doc.doc_type != filters["doc_type"]:
                return False
        
        # 时间范围过滤
        if "after" in filters and doc.timestamp:
            if doc.timestamp < filters["after"]:
                return False
        
        if "before" in filters and doc.timestamp:
            if doc.timestamp > filters["before"]:
                return False
        
        # 最小分数过滤
        if "min_score" in filters:
            if score < filters["min_score"]:
                return False
        
        # 状态过滤
        if "status" in filters:
            if doc.status != filters["status"]:
                return False
        
        return True
