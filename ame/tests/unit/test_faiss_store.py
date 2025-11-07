"""
Unit tests for FaissStore
"""
import pytest
import numpy as np
from ame.storage.faiss_store import FaissStore


@pytest.mark.unit
@pytest.mark.asyncio
async def test_faiss_store_initialization(tmp_data_dir):
    """Test FaissStore initialization"""
    store = FaissStore(dimension=128, index_path=tmp_data_dir / "test.index")
    
    assert store.dimension == 128
    assert store.index is not None
    assert store.index.ntotal == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_single_vector(faiss_store):
    """Test adding a single vector"""
    embedding = np.random.rand(128).tolist()
    doc_id = "doc_1"
    
    faiss_id = await faiss_store.add(embedding, doc_id)
    
    assert isinstance(faiss_id, int)
    assert faiss_id >= 0
    assert doc_id in faiss_store.reverse_id_map
    assert faiss_store.index.ntotal == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_batch_vectors(faiss_store, sample_embeddings, sample_doc_ids):
    """Test batch adding vectors"""
    embeddings = sample_embeddings[:5]
    doc_ids = sample_doc_ids[:5]
    
    faiss_ids = await faiss_store.add_batch(embeddings, doc_ids)
    
    assert len(faiss_ids) == 5
    assert faiss_store.index.ntotal == 5
    
    # Check all IDs are mapped
    for doc_id in doc_ids:
        assert doc_id in faiss_store.reverse_id_map


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_vectors(faiss_store):
    """Test vector similarity search"""
    # Add some vectors
    embeddings = [np.random.rand(128).tolist() for _ in range(10)]
    doc_ids = [f"doc_{i}" for i in range(10)]
    
    await faiss_store.add_batch(embeddings, doc_ids)
    
    # Search using the first embedding
    query_embedding = embeddings[0]
    results = await faiss_store.search(query_embedding, top_k=3)
    
    assert len(results) <= 3
    assert results[0]["doc_id"] == "doc_0"  # Should match itself
    assert results[0]["score"] > 0.99  # High similarity
    assert results[0]["source"] == "faiss"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_empty_index(faiss_store):
    """Test searching in empty index"""
    query_embedding = np.random.rand(128).tolist()
    results = await faiss_store.search(query_embedding, top_k=5)
    
    assert results == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remove_vector(faiss_store):
    """Test removing a vector"""
    embedding = np.random.rand(128).tolist()
    doc_id = "doc_to_remove"
    
    await faiss_store.add(embedding, doc_id)
    assert doc_id in faiss_store.reverse_id_map
    
    success = await faiss_store.remove(doc_id)
    
    assert success is True
    assert doc_id not in faiss_store.reverse_id_map


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remove_batch(faiss_store, sample_embeddings, sample_doc_ids):
    """Test batch removal"""
    await faiss_store.add_batch(sample_embeddings[:5], sample_doc_ids[:5])
    
    doc_ids_to_remove = sample_doc_ids[:3]
    count = await faiss_store.remove_batch(doc_ids_to_remove)
    
    assert count == 3
    for doc_id in doc_ids_to_remove:
        assert doc_id not in faiss_store.reverse_id_map


@pytest.mark.unit
@pytest.mark.asyncio
async def test_persistence(tmp_data_dir):
    """Test saving and loading index"""
    index_path = tmp_data_dir / "persist_test.index"
    
    # Create and populate store
    store1 = FaissStore(dimension=128, index_path=index_path)
    embedding = np.random.rand(128).tolist()
    await store1.add(embedding, "doc_1")
    store1.save()
    
    # Load in new instance
    store2 = FaissStore(dimension=128, index_path=index_path)
    store2.load()
    
    assert store2.index.ntotal == 1
    assert "doc_1" in store2.reverse_id_map
    
    # Search should work
    results = await store2.search(embedding, top_k=1)
    assert len(results) == 1
    assert results[0]["doc_id"] == "doc_1"


@pytest.mark.unit
def test_get_stats(faiss_store):
    """Test getting index statistics"""
    stats = faiss_store.get_stats()
    
    assert "total_vectors" in stats
    assert "dimension" in stats
    assert "is_trained" in stats
    assert "active_docs" in stats
    assert "deleted_docs" in stats
    
    assert stats["dimension"] == 128
    assert stats["total_vectors"] == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rebuild_index(faiss_store):
    """Test rebuilding index after deletions"""
    # Add vectors
    embeddings = [np.random.rand(128).tolist() for _ in range(5)]
    doc_ids = [f"doc_{i}" for i in range(5)]
    await faiss_store.add_batch(embeddings, doc_ids)
    
    # Remove some
    await faiss_store.remove_batch(["doc_1", "doc_3"])
    
    # Rebuild with remaining
    remaining_embeddings = [embeddings[i] for i in [0, 2, 4]]
    remaining_ids = ["doc_0", "doc_2", "doc_4"]
    faiss_store.rebuild_index(remaining_embeddings, remaining_ids)
    
    stats = faiss_store.get_stats()
    assert stats["total_vectors"] == 3
    assert stats["active_docs"] == 3
    assert stats["deleted_docs"] == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_error_handling_dimension_mismatch(faiss_store):
    """Test error handling for dimension mismatch"""
    wrong_embedding = np.random.rand(256).tolist()  # Wrong dimension
    
    with pytest.raises(Exception):
        await faiss_store.add(wrong_embedding, "doc_1")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_batch_add_length_mismatch(faiss_store):
    """Test error when embeddings and IDs length don't match"""
    embeddings = [np.random.rand(128).tolist() for _ in range(5)]
    doc_ids = ["doc_1", "doc_2"]  # Only 2 IDs
    
    with pytest.raises(ValueError):
        await faiss_store.add_batch(embeddings, doc_ids)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_search_performance(faiss_store, benchmark):
    """Benchmark search performance"""
    # Add 1000 vectors
    embeddings = [np.random.rand(128).tolist() for _ in range(1000)]
    doc_ids = [f"doc_{i}" for i in range(1000)]
    await faiss_store.add_batch(embeddings, doc_ids)
    
    query = np.random.rand(128).tolist()
    
    import time
    start = time.time()
    results = await faiss_store.search(query, top_k=10)
    latency = (time.time() - start) * 1000
    
    assert latency < 100  # Should be < 100ms
    assert len(results) == 10
