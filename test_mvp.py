#!/usr/bin/env python3
"""
Another Me MVP 功能测试
测试所有核心模块的功能
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加 ame 到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ame.storage.faiss_store import FaissStore
from ame.storage.metadata_store import MetadataStore
from ame.storage.falkor_store import MockFalkorStore
from ame.repository.hybrid_repository import HybridRepository
from ame.models.domain import Document, DocumentType, MemoryRetentionType
from ame.mem.conversation_filter import ConversationFilter
from ame.mem.analyze_engine import AnalyzeEngine


async def test_mvp():
    """测试 MVP 所有核心功能"""
    print("=" * 60)
    print("🧪 Another Me MVP 功能测试")
    print("=" * 60)
    print()
    
    # 初始化
    print("📦 初始化测试环境...")
    data_dir = project_root / "data"
    faiss = FaissStore(index_path=str(data_dir / "faiss" / "mvp.index"))
    metadata = MetadataStore(db_path=str(data_dir / "metadata" / "mvp.db"))
    graph = MockFalkorStore()
    repo = HybridRepository(faiss, graph, metadata)
    print("   ✅ 环境初始化完成\n")
    
    test_results = []
    
    # 测试1: 文档创建
    print("🧪 测试 1: 文档创建与双写")
    try:
        doc = Document(
            content="学习 Faiss 向量检索技术，用于构建高性能的相似度搜索系统",
            doc_type=DocumentType.RAG_KNOWLEDGE,
            source="学习笔记",
            timestamp=datetime.now(),
            embedding=[0.2] * 1536,
            entities=["Faiss", "向量检索", "相似度搜索", "高性能"]
        )
        
        result = await repo.create(doc)
        
        assert result.id is not None, "文档 ID 为空"
        assert result.stored_in_faiss == True, "未存储到 Faiss"
        assert result.stored_in_graph == True, "未存储到 Falkor"
        
        print(f"   ✅ 文档创建成功: {result.id[:8]}...")
        print(f"   ✅ 双写验证: Faiss={result.stored_in_faiss}, Graph={result.stored_in_graph}")
        test_results.append(("文档创建", True))
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        test_results.append(("文档创建", False))
    print()
    
    # 测试2: 文档检索
    print("🧪 测试 2: 文档检索")
    try:
        retrieved = await repo.get(result.id)
        assert retrieved is not None, "检索失败"
        assert retrieved.content == doc.content, "内容不匹配"
        
        print(f"   ✅ 检索成功: {retrieved.id[:8]}...")
        print(f"   ✅ 内容匹配: {retrieved.content[:30]}...")
        test_results.append(("文档检索", True))
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        test_results.append(("文档检索", False))
    print()
    
    # 测试3: 混合检索
    print("🧪 测试 3: 混合检索（Faiss + Falkor）")
    try:
        search_results = await repo.hybrid_search(
            query="向量检索系统",
            query_embedding=[0.2] * 1536,
            top_k=5
        )
        
        assert len(search_results) > 0, "未找到结果"
        assert all(r.score > 0 for r in search_results), "分数异常"
        
        print(f"   ✅ 检索成功: 找到 {len(search_results)} 个结果")
        for idx, r in enumerate(search_results[:3], 1):
            print(f"      {idx}. [分数: {r.score:.3f}] {r.content[:40]}...")
        test_results.append(("混合检索", True))
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        test_results.append(("混合检索", False))
    print()
    
    # 测试4: 对话过滤器
    print("🧪 测试 4: 对话过滤器")
    try:
        filter = ConversationFilter()
        
        # 测试永久记忆
        retention1 = await filter.classify_conversation("今天学习了 Faiss，很有收获，记录一下重要知识点")
        assert retention1 == MemoryRetentionType.PERMANENT, "永久记忆分类错误"
        print(f"   ✅ 永久记忆分类正确: '{retention1.value}'")
        
        # 测试闲聊
        retention2 = await filter.classify_conversation("你好")
        assert retention2 == MemoryRetentionType.CASUAL_CHAT, "闲聊分类错误"
        print(f"   ✅ 闲聊分类正确: '{retention2.value}'")
        
        # 测试临时记忆
        retention3 = await filter.classify_conversation("明天记得去开会")
        assert retention3 == MemoryRetentionType.TEMPORARY, "临时记忆分类错误"
        print(f"   ✅ 临时记忆分类正确: '{retention3.value}'")
        
        # 测试存储判断
        should_store1 = filter.should_store(retention1)
        should_store2 = filter.should_store(retention2)
        assert should_store1 == True and should_store2 == False, "存储判断错误"
        print(f"   ✅ 存储判断正确: PERMANENT={should_store1}, CASUAL_CHAT={should_store2}")
        
        test_results.append(("对话过滤", True))
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        test_results.append(("对话过滤", False))
    print()
    
    # 测试5: 数据分析引擎
    print("🧪 测试 5: 数据分析引擎")
    try:
        analyzer = AnalyzeEngine(repo)
        
        # 创建测试数据
        for i in range(5):
            work_doc = Document(
                content=f"工作日志 Day {i+1}: 完成了重要任务 Task-{i+1}，取得了显著进展",
                doc_type=DocumentType.WORK_LOG,
                source="工作日志",
                timestamp=datetime.now() - timedelta(days=i),
                embedding=[0.3 + i * 0.01] * 1536,
                entities=[f"Task-{i+1}", "工作", "进展"],
                importance=0.8
            )
            await repo.create(work_doc)
        
        # 收集数据
        start = datetime.now() - timedelta(days=7)
        docs = await analyzer.collect_time_range("user1", start)
        assert len(docs) > 0, "未收集到数据"
        print(f"   ✅ 数据收集成功: {len(docs)} 条记录")
        
        # 提取洞察
        insights = await analyzer.extract_insights(docs, ["key_tasks", "achievements"])
        assert "key_tasks" in insights, "关键任务提取失败"
        assert "achievements" in insights, "成就提取失败"
        
        print(f"   ✅ 洞察提取成功:")
        print(f"      - 关键任务: {len(insights.get('key_tasks', []))} 个")
        print(f"      - 成就记录: {len(insights.get('achievements', []))} 个")
        
        test_results.append(("数据分析", True))
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        test_results.append(("数据分析", False))
    print()
    
    # 测试6: 统计信息
    print("🧪 测试 6: 统计信息")
    try:
        stats = repo.get_stats()
        
        assert "faiss" in stats, "Faiss 统计缺失"
        assert "metadata" in stats, "元数据统计缺失"
        
        print(f"   ✅ Faiss 统计:")
        print(f"      - 总向量数: {stats['faiss']['total_vectors']}")
        print(f"      - 活跃文档: {stats['faiss']['active_docs']}")
        print(f"   ✅ 元数据统计:")
        print(f"      - 总文档数: {stats['metadata']['total']}")
        print(f"      - 热数据: {stats['metadata']['hot']}")
        print(f"      - 温数据: {stats['metadata']['warm']}")
        print(f"      - 冷数据: {stats['metadata']['cold']}")
        
        test_results.append(("统计信息", True))
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        test_results.append(("统计信息", False))
    print()
    
    # 测试总结
    print("=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status}: {test_name}")
    
    print()
    print(f"   总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！MVP 功能正常")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(test_mvp())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
