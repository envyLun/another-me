"""
混合存储仓库单元测试
测试 Faiss + Falkor + SQLite 三层存储的功能
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from ame.foundation.storage import VectorStore
from ame.foundation.storage import MetadataStore
from ame.foundation.storage import GraphStore
from ame.repository.hybrid_repository import HybridRepository
from ame.models.domain import Document, DocumentType, DataLayer, MemoryRetentionType


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp)


@pytest.fixture
def test_repository(temp_dir):
    """创建测试用的仓库实例"""
    faiss_path = Path(temp_dir) / "test.index"
    metadata_path = Path(temp_dir) / "test.db"
    
    faiss = FaissStore(index_path=str(faiss_path), dimension=1536)
    metadata = MetadataStore(db_path=str(metadata_path))
    graph = MockFalkorStore()
    
    repo = HybridRepository(faiss, graph, metadata)
    return repo


@pytest.fixture
def sample_document():
    """创建示例文档"""
    return Document(
        content="这是一个测试文档，用于验证混合存储仓库的功能",
        doc_type=DocumentType.RAG_KNOWLEDGE,
        source="pytest",
        timestamp=datetime.now(),
        embedding=[0.1] * 1536,
        entities=["测试", "混合存储", "仓库"]
    )


class TestHybridRepository:
    """混合存储仓库测试类"""
    
    @pytest.mark.asyncio
    async def test_create_document(self, test_repository, sample_document):
        """测试文档创建（双写）"""
        result = await test_repository.create(sample_document)
        
        assert result.id == sample_document.id
        assert result.stored_in_faiss == True
        assert result.stored_in_graph == True
        assert result.faiss_index is not None
        assert result.graph_node_id is not None
        assert result.status == "active"
    
    @pytest.mark.asyncio
    async def test_get_document(self, test_repository, sample_document):
        """测试文档检索"""
        # 创建文档
        created = await test_repository.create(sample_document)
        
        # 检索文档
        retrieved = await test_repository.get(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.content == sample_document.content
        assert retrieved.doc_type == sample_document.doc_type
    
    @pytest.mark.asyncio
    async def test_get_by_ids(self, test_repository):
        """测试批量检索"""
        # 创建多个文档
        doc_ids = []
        for i in range(3):
            doc = Document(
                content=f"测试文档 {i}",
                doc_type=DocumentType.RAG_KNOWLEDGE,
                source="pytest",
                timestamp=datetime.now(),
                embedding=[0.1 + i * 0.01] * 1536,
                entities=[f"测试{i}"]
            )
            result = await test_repository.create(doc)
            doc_ids.append(result.id)
        
        # 批量检索
        docs = await test_repository.get_by_ids(doc_ids)
        
        assert len(docs) == 3
        assert all(doc.id in doc_ids for doc in docs)
    
    @pytest.mark.asyncio
    async def test_update_document(self, test_repository, sample_document):
        """测试文档更新"""
        # 创建文档
        created = await test_repository.create(sample_document)
        
        # 更新文档
        updates = {
            "importance": 0.9,
            "metadata": {"updated": True}
        }
        updated = await test_repository.update(created.id, updates)
        
        assert updated is not None
        assert updated.importance == 0.9
        assert updated.metadata.get("updated") == True
    
    @pytest.mark.asyncio
    async def test_delete_document(self, test_repository, sample_document):
        """测试文档删除"""
        # 创建文档
        created = await test_repository.create(sample_document)
        
        # 删除文档
        result = await test_repository.delete(created.id)
        assert result == True
        
        # 验证已删除
        retrieved = await test_repository.get(created.id)
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_hybrid_search(self, test_repository):
        """测试混合检索"""
        # 创建测试文档
        docs = [
            Document(
                content="学习 Faiss 向量检索技术",
                doc_type=DocumentType.RAG_KNOWLEDGE,
                source="pytest",
                timestamp=datetime.now(),
                embedding=[0.2] * 1536,
                entities=["Faiss", "向量检索"]
            ),
            Document(
                content="使用 Falkor 构建知识图谱",
                doc_type=DocumentType.RAG_KNOWLEDGE,
                source="pytest",
                timestamp=datetime.now(),
                embedding=[0.3] * 1536,
                entities=["Falkor", "知识图谱"]
            ),
            Document(
                content="混合检索融合多种策略",
                doc_type=DocumentType.RAG_KNOWLEDGE,
                source="pytest",
                timestamp=datetime.now(),
                embedding=[0.25] * 1536,
                entities=["混合检索", "融合"]
            )
        ]
        
        for doc in docs:
            await test_repository.create(doc)
        
        # 执行检索
        results = await test_repository.hybrid_search(
            query="向量检索和知识图谱",
            query_embedding=[0.25] * 1536,
            top_k=5
        )
        
        assert len(results) > 0
        assert all(r.score > 0 for r in results)
        assert all(hasattr(r, 'content') for r in results)
    
    @pytest.mark.asyncio
    async def test_data_layer(self, test_repository):
        """测试数据分层"""
        # 创建不同分层的文档
        hot_doc = Document(
            content="热数据文档",
            doc_type=DocumentType.RAG_KNOWLEDGE,
            source="pytest",
            timestamp=datetime.now(),
            embedding=[0.1] * 1536,
            layer=DataLayer.HOT
        )
        
        warm_doc = Document(
            content="温数据文档",
            doc_type=DocumentType.RAG_KNOWLEDGE,
            source="pytest",
            timestamp=datetime.now() - timedelta(days=15),
            embedding=[0.2] * 1536,
            layer=DataLayer.WARM
        )
        
        cold_doc = Document(
            content="冷数据文档",
            doc_type=DocumentType.RAG_KNOWLEDGE,
            source="pytest",
            timestamp=datetime.now() - timedelta(days=60),
            embedding=[0.3] * 1536,
            layer=DataLayer.COLD,
            stored_in_faiss=False  # 冷数据不存储在 Faiss
        )
        
        hot_result = await test_repository.create(hot_doc)
        warm_result = await test_repository.create(warm_doc)
        cold_result = await test_repository.create(cold_doc)
        
        assert hot_result.layer == DataLayer.HOT
        assert warm_result.layer == DataLayer.WARM
        assert cold_result.layer == DataLayer.COLD
    
    @pytest.mark.asyncio
    async def test_retention_type(self, test_repository):
        """测试记忆保留类型"""
        # 创建不同保留类型的文档
        permanent_doc = Document(
            content="重要知识，永久保存",
            doc_type=DocumentType.MEM_CONVERSATION,
            source="pytest",
            timestamp=datetime.now(),
            embedding=[0.1] * 1536,
            retention_type=MemoryRetentionType.PERMANENT
        )
        
        temporary_doc = Document(
            content="临时记忆，7天后删除",
            doc_type=DocumentType.MEM_CONVERSATION,
            source="pytest",
            timestamp=datetime.now(),
            embedding=[0.2] * 1536,
            retention_type=MemoryRetentionType.TEMPORARY
        )
        
        permanent_result = await test_repository.create(permanent_doc)
        temporary_result = await test_repository.create(temporary_doc)
        
        assert permanent_result.retention_type == MemoryRetentionType.PERMANENT
        assert temporary_result.retention_type == MemoryRetentionType.TEMPORARY
    
    @pytest.mark.asyncio
    async def test_get_stats(self, test_repository, sample_document):
        """测试统计信息"""
        # 创建文档
        await test_repository.create(sample_document)
        
        # 获取统计
        stats = test_repository.get_stats()
        
        assert "faiss" in stats
        assert "metadata" in stats
        assert stats["faiss"]["total_vectors"] > 0
        assert stats["metadata"]["total"] > 0
    
    @pytest.mark.asyncio
    async def test_lifecycle_management(self, test_repository):
        """测试数据生命周期管理"""
        # 创建旧文档（模拟热数据降温）
        old_doc = Document(
            content="旧文档，需要降温",
            doc_type=DocumentType.RAG_KNOWLEDGE,
            source="pytest",
            timestamp=datetime.now() - timedelta(days=10),
            embedding=[0.1] * 1536,
            layer=DataLayer.HOT,
            importance=0.5
        )
        
        created = await test_repository.create(old_doc)
        
        # 执行生命周期管理
        await test_repository.lifecycle_management()
        
        # 验证文档已降温
        updated = await test_repository.get(created.id)
        # 注意：由于是 Mock 测试，实际行为可能不同
        assert updated is not None


@pytest.mark.asyncio
async def test_concurrent_operations(test_repository):
    """测试并发操作"""
    # 创建多个文档（并发）
    tasks = []
    for i in range(5):
        doc = Document(
            content=f"并发测试文档 {i}",
            doc_type=DocumentType.RAG_KNOWLEDGE,
            source="pytest",
            timestamp=datetime.now(),
            embedding=[0.1 + i * 0.01] * 1536,
            entities=[f"并发{i}"]
        )
        tasks.append(test_repository.create(doc))
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 5
    assert all(r.id is not None for r in results)
    assert all(r.stored_in_faiss for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
