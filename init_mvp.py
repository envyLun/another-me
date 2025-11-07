#!/usr/bin/env python3
"""
Another Me MVP 初始化脚本
一键初始化所有存储组件并验证功能
"""
import asyncio
import sys
from pathlib import Path

# 添加 ame 到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ame.storage.faiss_store import FaissStore
from ame.storage.metadata_store import MetadataStore
from ame.storage.falkor_store import MockFalkorStore
from ame.repository.hybrid_repository import HybridRepository
from ame.models.domain import Document, DocumentType
from datetime import datetime


async def init_mvp():
    """初始化 MVP 环境"""
    print("=" * 60)
    print("🚀 Another Me MVP 初始化")
    print("=" * 60)
    print()
    
    # 1. 创建数据目录
    print("📁 创建数据目录...")
    data_dir = project_root / "data"
    (data_dir / "faiss").mkdir(parents=True, exist_ok=True)
    (data_dir / "metadata").mkdir(parents=True, exist_ok=True)
    print("   ✅ 数据目录: ./data/")
    print()
    
    # 2. 初始化存储组件
    print("💾 初始化存储组件...")
    faiss_path = data_dir / "faiss" / "mvp.index"
    metadata_path = data_dir / "metadata" / "mvp.db"
    
    faiss = FaissStore(index_path=str(faiss_path), dimension=1536)
    print(f"   ✅ Faiss 向量存储: {faiss_path}")
    
    metadata = MetadataStore(db_path=str(metadata_path))
    print(f"   ✅ SQLite 元数据库: {metadata_path}")
    
    graph = MockFalkorStore()
    print("   ✅ Falkor 图谱存储: Mock 实现")
    print()
    
    # 3. 创建混合仓库
    print("🔗 创建混合仓库...")
    repo = HybridRepository(faiss, graph, metadata)
    print("   ✅ HybridRepository 初始化完成")
    print()
    
    # 4. 创建测试文档
    print("📝 创建测试文档...")
    test_docs = [
        {
            "content": "Another Me 是一个 AI 数字分身系统，通过用户的聊天记录、日记和个人知识训练出一个'像你'的 AI",
            "entities": ["Another Me", "AI 数字分身", "聊天记录", "日记"]
        },
        {
            "content": "系统采用双存储架构：Faiss 向量数据库用于快速检索，Falkor 图谱数据库用于关系分析",
            "entities": ["双存储架构", "Faiss", "向量数据库", "Falkor", "图谱数据库"]
        },
        {
            "content": "数据分层策略：热数据（0-7天）、温数据（7-30天）、冷数据（30天+）",
            "entities": ["数据分层", "热数据", "温数据", "冷数据"]
        }
    ]
    
    doc_ids = []
    for i, test_data in enumerate(test_docs):
        doc = Document(
            content=test_data["content"],
            doc_type=DocumentType.RAG_KNOWLEDGE,
            source="mvp_init",
            timestamp=datetime.now(),
            embedding=[0.1 + i * 0.01] * 1536,  # 模拟不同的 embedding
            entities=test_data["entities"]
        )
        
        result = await repo.create(doc)
        doc_ids.append(result.id)
        print(f"   ✅ 文档 {i+1}: {result.id[:8]}... (实体: {len(result.entities)}个)")
    
    print()
    
    # 5. 测试混合检索
    print("🔍 测试混合检索...")
    search_results = await repo.hybrid_search(
        query="AI 数字分身系统",
        query_embedding=[0.11] * 1536,
        top_k=5
    )
    
    print(f"   查询: 'AI 数字分身系统'")
    print(f"   ✅ 找到 {len(search_results)} 个结果:")
    for idx, result in enumerate(search_results[:3], 1):
        print(f"      {idx}. [分数: {result.score:.3f}] {result.content[:50]}...")
    print()
    
    # 6. 显示统计信息
    print("📊 存储统计信息...")
    stats = repo.get_stats()
    print(f"   • Faiss 向量数: {stats['faiss']['total_vectors']}")
    print(f"   • 活跃文档数: {stats['faiss']['active_docs']}")
    print(f"   • 总文档数: {stats['metadata']['total']}")
    print(f"   • 热数据: {stats['metadata']['hot']} | 温数据: {stats['metadata']['warm']} | 冷数据: {stats['metadata']['cold']}")
    print()
    
    # 7. 保存索引
    print("💾 保存 Faiss 索引...")
    faiss.save()
    print(f"   ✅ 索引已保存: {faiss_path}")
    print()
    
    print("=" * 60)
    print("🎉 MVP 初始化完成！")
    print("=" * 60)
    print()
    print("📋 下一步操作:")
    print("   1. 运行测试: python test_mvp.py")
    print("   2. 查看文档: cat ame/README.md")
    print("   3. 集成到 Backend:")
    print("      - 在 backend/app/main.py 中导入 ame 模块")
    print("      - 使用 HybridRepository 替代旧的 vector_store")
    print()
    print("💡 提示:")
    print("   - 数据已持久化到 ./data/ 目录")
    print("   - 可以多次运行此脚本重新初始化")
    print("   - MVP 使用 Mock 图谱存储，生产环境建议使用 Neo4j")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(init_mvp())
    except KeyboardInterrupt:
        print("\n\n⚠️  初始化已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
