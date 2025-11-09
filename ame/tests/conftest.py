"""
Pytest configuration and shared fixtures
"""
import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
import numpy as np


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def tmp_data_dir():
    """Create temporary data directory"""
    temp_dir = tempfile.mkdtemp(prefix="ame_test_")
    data_dir = Path(temp_dir) / "test_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    yield data_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
async def metadata_store(tmp_data_dir):
    """Create metadata store for testing"""
    from ame.foundation.storage import MetadataStore
    store = MetadataStore(db_path=str(tmp_data_dir / "metadata.db"))
    yield store
    # Cleanup happens automatically with tmp_data_dir


@pytest.fixture
async def faiss_store(tmp_data_dir):
    """Create Faiss store for testing"""
    from ame.foundation.storage import VectorStore
    store = VectorStore(
        dimension=128,  # Smaller dimension for testing
        index_path=str(tmp_data_dir / "faiss.index")
    )
    yield store
    # Cleanup happens automatically with tmp_data_dir


@pytest.fixture
async def falkor_store():
    """
    Create FalkorDB store for testing
    
    Note: Requires FalkorDB running on localhost:6379
    Use docker: docker run -p 6379:6379 falkordb/falkordb
    """
    try:
        from ame.foundation.storage import GraphStore
        store = GraphStore(
            host="localhost",
            port=6379,
            graph_name="test_graph"
        )
        yield store
        # Cleanup: delete test graph
        try:
            await store.execute_cypher("MATCH (n) DETACH DELETE n", {})
        except:
            pass
        store.close()
    except ImportError:
        pytest.skip("FalkorDB not available")


def mock_embedding_fn(text: str) -> list:
    """Mock embedding function for testing"""
    # Generate deterministic embeddings based on text hash
    np.random.seed(hash(text) % (2**32))
    return np.random.rand(128).tolist()


@pytest.fixture
def embedding_function():
    """Provide mock embedding function"""
    return mock_embedding_fn


@pytest.fixture
def sample_documents():
    """Generate sample documents for testing"""
    from datetime import datetime, timedelta
    from ame.models.domain import Document, DocumentType
    
    docs = []
    for i in range(10):
        doc = Document(
            content=f"This is test document {i} about AI and technology",
            doc_type=DocumentType.RAG_KNOWLEDGE,
            source="test",
            timestamp=datetime.now() - timedelta(days=i),
            entities=["AI", "technology"] if i % 2 == 0 else ["Python", "programming"]
        )
        docs.append(doc)
    
    return docs


@pytest.fixture
def sample_conversations():
    """Generate sample conversations for testing"""
    from datetime import datetime, timedelta
    from ame.models.domain import Document, DocumentType
    
    conversations = []
    for i in range(5):
        conv = Document(
            content=f"User conversation {i} with meaningful content",
            doc_type=DocumentType.MEM_CONVERSATION,
            source="user",
            timestamp=datetime.now() - timedelta(hours=i),
            metadata={"conversation_id": f"conv_{i}"}
        )
        conversations.append(conv)
    
    return conversations


# Test data fixtures
@pytest.fixture
def sample_embeddings():
    """Generate sample embeddings"""
    return [np.random.rand(128).tolist() for _ in range(10)]


@pytest.fixture
def sample_doc_ids():
    """Generate sample document IDs"""
    return [f"doc_{i}" for i in range(10)]


# Performance testing fixtures
@pytest.fixture
def benchmark_docs(sample_documents):
    """Generate more documents for benchmark testing"""
    from datetime import datetime, timedelta
    from ame.models.domain import Document, DocumentType
    
    docs = sample_documents.copy()
    for i in range(10, 100):
        doc = Document(
            content=f"Benchmark document {i} with test content",
            doc_type=DocumentType.RAG_KNOWLEDGE,
            source="benchmark",
            timestamp=datetime.now() - timedelta(hours=i),
        )
        docs.append(doc)
    
    return docs


# Markers for test categorization
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests requiring multiple components"
    )
    config.addinivalue_line(
        "markers", "benchmark: Performance benchmark tests"
    )
    config.addinivalue_line(
        "markers", "requires_falkor: Tests requiring FalkorDB instance"
    )
