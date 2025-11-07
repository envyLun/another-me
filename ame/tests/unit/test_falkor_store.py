"""
Integration tests for FalkorStore

Note: Requires FalkorDB running on localhost:6379
Run with: docker run -p 6379:6379 falkordb/falkordb
"""
import pytest
from datetime import datetime


@pytest.mark.integration
@pytest.mark.requires_falkor
@pytest.mark.asyncio
async def test_falkor_initialization():
    """Test FalkorStore initialization"""
    try:
        from ame.storage.falkor_store import FalkorStore
        store = FalkorStore(
            host="localhost",
            port=6379,
            graph_name="test_init"
        )
        assert store.client is not None
        assert store.graph is not None
        store.close()
    except ImportError:
        pytest.skip("FalkorDB not installed")


@pytest.mark.integration
@pytest.mark.requires_falkor
@pytest.mark.asyncio
async def test_create_document_node(falkor_store):
    """Test creating a document node"""
    node_id = await falkor_store.create_node("Document", {
        "id": "doc_1",
        "content": "Test content",
        "timestamp": datetime.now().isoformat()
    })
    
    assert node_id is not None
    assert node_id == "doc_1"


@pytest.mark.integration
@pytest.mark.requires_falkor
@pytest.mark.asyncio
async def test_create_entity_node(falkor_store):
    """Test creating an entity node"""
    entity_id = await falkor_store.get_or_create_entity("Python", "Technology")
    
    assert entity_id is not None
    
    # Creating again should return same ID
    entity_id_2 = await falkor_store.get_or_create_entity("Python", "Technology")
    assert entity_id == entity_id_2


@pytest.mark.integration
@pytest.mark.requires_falkor
@pytest.mark.asyncio
async def test_create_relation(falkor_store):
    """Test creating a relationship between nodes"""
    # Create document node
    doc_id = await falkor_store.create_node("Document", {
        "id": "doc_1",
        "content": "Python is great"
    })
    
    # Create entity node
    entity_id = await falkor_store.get_or_create_entity("Python")
    
    # Create relationship
    success = await falkor_store.create_relation(doc_id, entity_id, "MENTIONS")
    
    assert success is True


@pytest.mark.integration
@pytest.mark.requires_falkor
@pytest.mark.asyncio
async def test_search_by_entities(falkor_store):
    """Test searching documents by entities"""
    # Create test data
    doc_id_1 = await falkor_store.create_node("Document", {
        "id": "doc_1",
        "content": "AI and machine learning",
        "timestamp": datetime.now().isoformat()
    })
    
    doc_id_2 = await falkor_store.create_node("Document", {
        "id": "doc_2",
        "content": "Deep learning with AI",
        "timestamp": datetime.now().isoformat()
    })
    
    # Create entities
    ai_entity = await falkor_store.get_or_create_entity("AI")
    ml_entity = await falkor_store.get_or_create_entity("machine learning")
    
    # Create relationships
    await falkor_store.create_relation(doc_id_1, ai_entity, "MENTIONS")
    await falkor_store.create_relation(doc_id_1, ml_entity, "MENTIONS")
    await falkor_store.create_relation(doc_id_2, ai_entity, "MENTIONS")
    
    # Search by entity
    results = await falkor_store.search_by_entities("", ["AI"], top_k=10)
    
    assert len(results) >= 1
    assert any(r["doc_id"] in ["doc_1", "doc_2"] for r in results)
    assert all(r["source"] == "graph" for r in results)


@pytest.mark.integration
@pytest.mark.requires_falkor
@pytest.mark.asyncio
async def test_find_related_docs(falkor_store):
    """Test finding related documents through multi-hop queries"""
    # Create document chain: doc1 -> entity1 <- doc2 -> entity2 <- doc3
    doc1 = await falkor_store.create_node("Document", {"id": "doc_1"})
    doc2 = await falkor_store.create_node("Document", {"id": "doc_2"})
    doc3 = await falkor_store.create_node("Document", {"id": "doc_3"})
    
    entity1 = await falkor_store.get_or_create_entity("Python")
    entity2 = await falkor_store.get_or_create_entity("AI")
    
    await falkor_store.create_relation(doc1, entity1, "MENTIONS")
    await falkor_store.create_relation(doc2, entity1, "MENTIONS")
    await falkor_store.create_relation(doc2, entity2, "MENTIONS")
    await falkor_store.create_relation(doc3, entity2, "MENTIONS")
    
    # Find docs related to doc_1 within 2 hops
    related = await falkor_store.find_related_docs("doc_1", max_hops=2, limit=10)
    
    assert isinstance(related, list)
    # Should find doc_2 (1 hop) and possibly doc_3 (2 hops)
    assert len(related) >= 1


@pytest.mark.integration
@pytest.mark.requires_falkor
@pytest.mark.asyncio
async def test_entity_evolution_analysis(falkor_store):
    """Test analyzing entity evolution over time"""
    from datetime import timedelta
    
    # Create documents mentioning same entity at different times
    now = datetime.now()
    
    for i in range(3):
        doc_id = await falkor_store.create_node("Document", {
            "id": f"doc_{i}",
            "content": f"Document {i} about Python",
            "timestamp": (now - timedelta(days=i)).isoformat()
        })
        
        entity = await falkor_store.get_or_create_entity("Python")
        await falkor_store.create_relation(entity, doc_id, "MENTIONED_IN")
    
    # Analyze evolution
    timeline = await falkor_store.analyze_entity_evolution("Python")
    
    assert isinstance(timeline, list)
    # Should return chronologically ordered results


@pytest.mark.integration
@pytest.mark.requires_falkor
@pytest.mark.asyncio
async def test_delete_node(falkor_store):
    """Test deleting a node"""
    doc_id = await falkor_store.create_node("Document", {"id": "doc_to_delete"})
    
    success = await falkor_store.delete_node(doc_id)
    
    assert success is True


@pytest.mark.integration
@pytest.mark.requires_falkor
@pytest.mark.asyncio
async def test_execute_custom_cypher(falkor_store):
    """Test executing custom Cypher queries"""
    # Create test data
    await falkor_store.create_node("Document", {
        "id": "doc_1",
        "content": "Test"
    })
    
    # Execute custom query
    results = await falkor_store.execute_cypher(
        "MATCH (d:Document) RETURN d.id AS id LIMIT 5",
        {}
    )
    
    assert isinstance(results, list)


@pytest.mark.integration
@pytest.mark.requires_falkor
@pytest.mark.asyncio
async def test_multiple_entity_search(falkor_store):
    """Test searching with multiple entities"""
    # Create document with multiple entities
    doc_id = await falkor_store.create_node("Document", {
        "id": "multi_doc",
        "content": "Python and AI together",
        "timestamp": datetime.now().isoformat()
    })
    
    python_entity = await falkor_store.get_or_create_entity("Python")
    ai_entity = await falkor_store.get_or_create_entity("AI")
    
    await falkor_store.create_relation(doc_id, python_entity, "MENTIONS")
    await falkor_store.create_relation(doc_id, ai_entity, "MENTIONS")
    
    # Search with multiple entities
    results = await falkor_store.search_by_entities(
        "",
        ["Python", "AI"],
        top_k=10
    )
    
    assert len(results) >= 1
    # Document with both entities should have higher score
    top_result = results[0]
    assert top_result["doc_id"] == "multi_doc"
    assert top_result["score"] > 0


@pytest.mark.benchmark
@pytest.mark.requires_falkor
@pytest.mark.asyncio
async def test_graph_query_performance(falkor_store):
    """Benchmark graph query performance"""
    import time
    
    # Create test graph
    for i in range(50):
        doc_id = await falkor_store.create_node("Document", {
            "id": f"perf_doc_{i}",
            "timestamp": datetime.now().isoformat()
        })
        
        entity = await falkor_store.get_or_create_entity(f"Entity_{i % 10}")
        await falkor_store.create_relation(doc_id, entity, "MENTIONS")
    
    # Benchmark search
    start = time.time()
    results = await falkor_store.search_by_entities(
        "",
        ["Entity_0", "Entity_1"],
        top_k=10
    )
    latency = (time.time() - start) * 1000
    
    assert latency < 200  # Should be < 200ms
    assert len(results) > 0
