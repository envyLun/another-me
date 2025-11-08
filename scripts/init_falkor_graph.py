#!/usr/bin/env python3
"""
Initialize FalkorDB graph schema

Usage:
    python scripts/init_falkor_graph.py --host localhost --port 6379 --graph another_me
"""
import asyncio
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_graph_schema(host: str, port: int, graph_name: str):
    """
    Initialize FalkorDB graph schema and indexes
    
    Args:
        host: FalkorDB host
        port: FalkorDB port
        graph_name: Graph name
    """
    try:
        from ame.storage.falkor_store import FalkorStore
        
        logger.info(f"Connecting to FalkorDB at {host}:{port}")
        store = FalkorStore(host=host, port=port, graph_name=graph_name)
        
        logger.info("Creating indexes...")
        
        # Create indexes for faster queries
        indexes = [
            "CREATE INDEX FOR (d:Document) ON (d.id)",
            "CREATE INDEX FOR (d:Document) ON (d.timestamp)",
            "CREATE INDEX FOR (e:Entity) ON (e.name)",
            "CREATE INDEX FOR (e:Entity) ON (e.type)",
        ]
        
        for index_query in indexes:
            try:
                await store.execute_cypher(index_query, {})
                logger.info(f"✅ Created: {index_query}")
            except Exception as e:
                logger.warning(f"Index may already exist: {e}")
        
        logger.info("✅ Graph schema initialized successfully")
        
        # Test connection
        result = await store.execute_cypher("MATCH (n) RETURN count(n) as count", {})
        logger.info(f"Current node count: {result}")
        
        store.close()
        
    except ImportError:
        logger.error("❌ FalkorDB not installed. Install with: pip install falkordb redis")
    except Exception as e:
        logger.error(f"❌ Failed to initialize schema: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Initialize FalkorDB graph schema")
    parser.add_argument("--host", default="localhost", help="FalkorDB host")
    parser.add_argument("--port", type=int, default=6379, help="FalkorDB port")
    parser.add_argument("--graph", default="another_me", help="Graph name")
    
    args = parser.parse_args()
    
    asyncio.run(init_graph_schema(args.host, args.port, args.graph))


if __name__ == "__main__":
    main()
