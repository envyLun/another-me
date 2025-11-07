#!/usr/bin/env python3
"""
Migration script: ChromaDB to Faiss
Migrates vector data from ChromaDB to Faiss format

Usage:
    python scripts/migrate_vector_store.py --source ./data/old_vector_store --target ./data/faiss
"""
import asyncio
import argparse
from pathlib import Path
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_from_chroma_to_faiss(source_path: str, target_path: str):
    """
    Migrate data from ChromaDB to Faiss
    
    Args:
        source_path: Path to ChromaDB directory
        target_path: Path to save Faiss index
    """
    try:
        import chromadb
        from ame.storage.faiss_store import FaissStore
        
        logger.info(f"Loading ChromaDB from {source_path}")
        chroma_client = chromadb.PersistentClient(path=source_path)
        collection = chroma_client.get_collection("default")
        
        # Get all documents
        results = collection.get(include=["embeddings", "metadatas", "documents"])
        total_docs = len(results["ids"])
        
        logger.info(f"Found {total_docs} documents to migrate")
        
        # Initialize Faiss store
        dimension = len(results["embeddings"][0]) if results["embeddings"] else 1536
        faiss_store = FaissStore(
            dimension=dimension,
            index_path=Path(target_path) / "faiss.index"
        )
        
        # Migrate in batches
        batch_size = 100
        for i in tqdm(range(0, total_docs, batch_size), desc="Migrating"):
            batch_end = min(i + batch_size, total_docs)
            
            embeddings = results["embeddings"][i:batch_end]
            doc_ids = results["ids"][i:batch_end]
            
            await faiss_store.add_batch(embeddings, doc_ids)
        
        # Save index
        faiss_store.save()
        logger.info(f"✅ Successfully migrated {total_docs} documents to {target_path}")
        
        # Print statistics
        stats = faiss_store.get_stats()
        logger.info(f"Faiss Index Stats: {stats}")
        
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Install with: pip install chromadb")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


async def verify_migration(faiss_path: str):
    """
    Verify migrated Faiss index
    
    Args:
        faiss_path: Path to Faiss index
    """
    from ame.storage.faiss_store import FaissStore
    import numpy as np
    
    logger.info(f"Verifying Faiss index at {faiss_path}")
    
    store = FaissStore(dimension=1536, index_path=Path(faiss_path) / "faiss.index")
    store.load()
    
    stats = store.get_stats()
    logger.info(f"Index stats: {stats}")
    
    # Test search
    if stats["total_vectors"] > 0:
        query = np.random.rand(1536).tolist()
        results = await store.search(query, top_k=5)
        logger.info(f"Sample search returned {len(results)} results")
    
    logger.info("✅ Verification complete")


def main():
    parser = argparse.ArgumentParser(description="Migrate vector store from ChromaDB to Faiss")
    parser.add_argument("--source", required=True, help="Source ChromaDB directory")
    parser.add_argument("--target", required=True, help="Target Faiss directory")
    parser.add_argument("--verify", action="store_true", help="Verify after migration")
    
    args = parser.parse_args()
    
    # Run migration
    asyncio.run(migrate_from_chroma_to_faiss(args.source, args.target))
    
    # Verify if requested
    if args.verify:
        asyncio.run(verify_migration(args.target))


if __name__ == "__main__":
    main()
