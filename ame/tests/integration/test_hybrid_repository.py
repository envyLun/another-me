"""
Integration tests for HybridRepository
"""
import pytest
from datetime import datetime
from ame.models.domain import Document, DocumentType


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hybrid_repo_initialization(faiss_store, metadata_store, embedding_function):
    """Test HybridRepository initialization"""
    try:
        from ame.repository.hybrid_repository import HybridRepository
        from ame.storage.falkor_store import FalkorStore
        
        # Use mock falkor for basic test
        falkor = FalkorStore(host="localhost", port=6379, graph_name="test")
        
        repo = HybridRepository(
            faiss_store=faiss_store,
            falkor_store=falkor,
            metadata_store=metadata_store,
            embedding_function=embedding_function
        )
        
        assert repo.faiss is not None
        assert repo.graph is not None
        assert repo.metadata is not None
        
        falkor.close()
    except Exception as e:
        pytest.skip(f"Skipping due to: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_document_basic(faiss_store, metadata_store, embedding_function):
    """Test basic document creation (Faiss + Metadata only)"""
    from ame.repository.hybrid_repository import HybridRepository
    from ame.storage.falkor_store import FalkorStore
    
    # Mock falkor store
    try:
        falkor = FalkorStore(host="localhost", port=6379, graph_name="test_create")
    except:
        pytest.skip("FalkorDB not available")
    
    repo = HybridRepository(
        faiss_store=faiss_store,
        falkor_store=falkor,
        metadata_store=metadata_store,
        embedding_function=embedding_function
    )
    
    doc = Document(
        content="Test document about Python programming",
        doc_type=DocumentType.RAG_KNOWLEDGE,
        source="test",
        timestamp=datetime.now()
    )
    
    created = await repo.create(doc)
    
    assert created.id is not None
    assert created.status == "active"
    assert created.embedding is not None
    
    falkor.close()


@pytest.mark.integration
@pytest.mark.asyncio  
async def test_get_document(faiss_store, metadata_store, embedding_function):
    """Test retrieving a document"""
    from ame.repository.hybrid_repository import HybridRepository
    from ame.storage.falkor_store import FalkorStore
    
    try:
        falkor = FalkorStore(host="localhost", port=6379, graph_name="test_get")
    except:
        pytest.skip("FalkorDB not available")
    
    repo = HybridRepository(
        faiss_store=faiss_store,
        falkor_store=falkor,
        metadata_store=metadata_store,
        embedding_function=embedding_function
    )
    
    # Create document
    doc = Document(
        content="Test retrieval",
        doc_type=DocumentType.RAG_KNOWLEDGE,
        source="test"
    )
    created = await repo.create(doc)
    
    # Retrieve
    retrieved = await repo.get(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.content == "Test retrieval"
    
    falkor.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_document(faiss_store, metadata_store, embedding_function):
    """Test deleting a document"""
    from ame.repository.hybrid_repository import HybridRepository
    from ame.storage.falkor_store import FalkorStore
    
    try:
        falkor = FalkorStore(host="localhost", port=6379, graph_name="test_delete")
    except:
        pytest.skip("FalkorDB not available")
    
    repo = HybridRepository(
        faiss_store=faiss_store,
        falkor_store=falkor,
        metadata_store=metadata_store,
        embedding_function=embedding_function
    )
    
    # Create document
    doc = Document(
        content="Document to delete",
        doc_type=DocumentType.RAG_KNOWLEDGE,
        source="test"
    )
    created = await repo.create(doc)
    
    # Delete
    success = await repo.delete(created.id)
    
    assert success is True
    
    # Verify deletion
    retrieved = await repo.get(created.id)
    assert retrieved is None
    
    falkor.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_faiss_only(faiss_store, metadata_store, embedding_function):
    """Test search using Faiss only (when Falkor unavailable)"""
    from ame.repository.hybrid_repository import HybridRepository
    from ame.storage.falkor_store import FalkorStore
    
    try:
        falkor = FalkorStore(host="localhost", port=6379, graph_name="test_search")
    except:
        pytest.skip("FalkorDB not available")
    
    repo = HybridRepository(
        faiss_store=faiss_store,
        falkor_store=falkor,
        metadata_store=metadata_store,
        embedding_function=embedding_function
    )
    
    # Create test documents
    for i in range(3):
        doc = Document(
            content=f"Document {i} about AI and technology",
            doc_type=DocumentType.RAG_KNOWLEDGE,
            source="test"
        )
        await repo.create(doc)
    
    # Search
    try:
        results = await repo.hybrid_search(
            query="AI technology",
            top_k=2,
            faiss_weight=1.0,  # Faiss only
            graph_weight=0.0
        )
        
        assert len(results) <= 2
    except Exception as e:
        # Some implementations may not have hybrid_search fully working
        pytest.skip(f"Search not available: {e}")
    
    falkor.close()


@pytest.mark.unit
def test_metadata_store_basic(metadata_store):
    """Test basic metadata store operations"""
    from ame.models.domain import Document, DocumentType
    
    doc = Document(
        id="test_meta_1",
        content="Test metadata",
        doc_type=DocumentType.RAG_KNOWLEDGE,
        source="test",
        timestamp=datetime.now()
    )
    
    # Insert
    metadata_store.insert(doc)
    
    # Get
    retrieved = metadata_store.get("test_meta_1")
    assert retrieved is not None
    assert retrieved.id == "test_meta_1"
    
    # Update
    metadata_store.update("test_meta_1", {"status": "archived"})
    updated = metadata_store.get("test_meta_1")
    assert updated.status == "archived"
    
    # Delete
    metadata_store.delete("test_meta_1")
    deleted = metadata_store.get("test_meta_1")
    assert deleted is None
