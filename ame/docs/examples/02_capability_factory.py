"""
示例 2: 能力工厂详解

演示 CapabilityFactory 的各种功能和使用模式。
"""

import asyncio
import os
from typing import List, Dict, Any

from ame.foundation.llm import OpenAICaller
from ame.foundation.embedding import OpenAIEmbedding
from ame.foundation.storage import VectorStore, GraphStore, DocumentStore
from ame.capabilities import CapabilityFactory


async def demo_retrieval_capabilities(factory: CapabilityFactory):
    """演示检索能力"""
    print("\n" + "=" * 60)
    print("检索能力演示")
    print("=" * 60)
    
    # 1. 基础检索
    print("\n[1] 创建基础检索器 (仅向量检索)...")
    basic_retriever = factory.create_retriever(
        pipeline_mode="basic",
        cache_key="basic_retriever"
    )
    print("✅ 基础检索器创建成功")
    
    # 2. 高级检索
    print("\n[2] 创建高级检索器 (向量 + 图谱 + 重排序)...")
    advanced_retriever = factory.create_retriever(
        pipeline_mode="advanced",
        cache_key="advanced_retriever"
    )
    print("✅ 高级检索器创建成功")
    
    # 3. 语义检索
    print("\n[3] 创建语义检索器 (意图自适应 + 多样性)...")
    semantic_retriever = factory.create_retriever(
        pipeline_mode="semantic",
        cache_key="semantic_retriever"
    )
    print("✅ 语义检索器创建成功")
    
    # 4. 缓存机制验证
    print("\n[4] 验证缓存机制...")
    retriever_copy = factory.create_retriever(
        pipeline_mode="basic",
        cache_key="basic_retriever"  # 相同的 cache_key
    )
    
    if retriever_copy is basic_retriever:
        print("✅ 缓存生效！两个检索器是同一个实例")
    else:
        print("❌ 缓存未生效")


async def demo_analysis_capabilities(factory: CapabilityFactory):
    """演示分析能力"""
    print("\n" + "=" * 60)
    print("分析能力演示")
    print("=" * 60)
    
    # 1. 数据分析器（不带检索）
    print("\n[1] 创建数据分析器（纯分析）...")
    analyzer_simple = factory.create_data_analyzer(
        with_retriever=False,
        cache_key="simple_analyzer"
    )
    print("✅ 简单分析器创建成功")
    
    # 2. 数据分析器（带检索增强）
    print("\n[2] 创建数据分析器（检索增强）...")
    analyzer_enhanced = factory.create_data_analyzer(
        with_retriever=True,
        cache_key="enhanced_analyzer"
    )
    print("✅ 增强分析器创建成功")
    
    # 3. 洞察生成器
    print("\n[3] 创建洞察生成器...")
    insight_generator = factory.create_insight_generator(
        cache_key="insight_generator"
    )
    print("✅ 洞察生成器创建成功")
    
    # 示例：使用分析器
    print("\n[4] 使用洞察生成器...")
    sample_data = [
        {"date": "2024-01-01", "event": "完成项目A", "mood": "开心"},
        {"date": "2024-01-02", "event": "会议讨论", "mood": "平静"},
        {"date": "2024-01-03", "event": "加班", "mood": "疲惫"}
    ]
    
    insights = await insight_generator.extract_insights(
        data=sample_data,
        context="用户工作记录"
    )
    
    print(f"📊 提取的洞察:")
    for i, insight in enumerate(insights, 1):
        print(f"  {i}. {insight}")


async def demo_generation_capabilities(factory: CapabilityFactory):
    """演示生成能力"""
    print("\n" + "=" * 60)
    print("生成能力演示")
    print("=" * 60)
    
    # 1. RAG 生成器
    print("\n[1] 创建 RAG 生成器...")
    rag_generator = factory.create_rag_generator(
        cache_key="rag_generator"
    )
    print("✅ RAG 生成器创建成功")
    
    # 2. 风格生成器（不带检索）
    print("\n[2] 创建风格生成器（纯生成）...")
    style_generator_simple = factory.create_style_generator(
        with_retriever=False,
        cache_key="simple_style"
    )
    print("✅ 简单风格生成器创建成功")
    
    # 3. 风格生成器（带检索）
    print("\n[3] 创建风格生成器（检索增强）...")
    style_generator_enhanced = factory.create_style_generator(
        with_retriever=True,
        cache_key="enhanced_style"
    )
    print("✅ 增强风格生成器创建成功")
    
    # 示例：使用风格生成器
    print("\n[4] 使用风格生成器...")
    styled_text = await style_generator_enhanced.generate(
        content="今天完成了三个任务，感觉很充实",
        style="温暖鼓励",
        context={"user_id": "demo_user"}
    )
    
    print(f"📝 原文: 今天完成了三个任务，感觉很充实")
    print(f"🎨 风格化输出: {styled_text}")


async def demo_memory_capabilities(factory: CapabilityFactory):
    """演示记忆能力"""
    print("\n" + "=" * 60)
    print("记忆能力演示")
    print("=" * 60)
    
    # 1. 创建记忆管理器
    print("\n[1] 创建记忆管理器...")
    memory_manager = factory.create_memory_manager(
        cache_key="memory_manager"
    )
    print("✅ 记忆管理器创建成功")
    
    # 2. 存储记忆
    print("\n[2] 存储记忆...")
    memory_id_1 = await memory_manager.store(
        content="今天学习了 Python 异步编程",
        importance=0.8,
        category="学习",
        tags=["编程", "Python", "异步"],
        metadata={"user_id": "demo_user", "date": "2024-01-01"}
    )
    print(f"✅ 记忆已保存，ID: {memory_id_1}")
    
    memory_id_2 = await memory_manager.store(
        content="完成了一个有趣的项目",
        importance=0.9,
        category="工作",
        tags=["项目", "成就"],
        metadata={"user_id": "demo_user", "date": "2024-01-02"}
    )
    print(f"✅ 记忆已保存，ID: {memory_id_2}")
    
    # 3. 检索记忆
    print("\n[3] 检索记忆...")
    memories = await memory_manager.retrieve(
        query="编程学习",
        top_k=5,
        filters={"user_id": "demo_user"}
    )
    
    print(f"📚 找到 {len(memories)} 条相关记忆:")
    for memory in memories:
        print(f"  - {memory['content']} (重要性: {memory['importance']})")


async def demo_intent_capabilities(factory: CapabilityFactory):
    """演示意图识别能力"""
    print("\n" + "=" * 60)
    print("意图识别能力演示")
    print("=" * 60)
    
    # 1. 创建意图识别器
    print("\n[1] 创建意图识别器...")
    intent_recognizer = factory.create_intent_recognizer(
        cache_key="intent_recognizer"
    )
    print("✅ 意图识别器创建成功")
    
    # 2. 识别不同意图
    test_messages = [
        "你好，今天天气怎么样？",
        "帮我搜索一下 Python 的异步编程资料",
        "我昨天去了公园，心情很好",
        "帮我分析一下这周的工作数据"
    ]
    
    print("\n[2] 识别用户意图...")
    for msg in test_messages:
        intent = await intent_recognizer.recognize(
            message=msg,
            context={"user_id": "demo_user"}
        )
        
        print(f"\n  消息: {msg}")
        print(f"  意图: {intent.intent_type}")
        print(f"  置信度: {intent.confidence:.2f}")
        if intent.entities:
            print(f"  实体: {intent.entities}")


async def demo_capability_combinations(factory: CapabilityFactory):
    """演示能力组合"""
    print("\n" + "=" * 60)
    print("能力组合演示")
    print("=" * 60)
    
    print("\n演示如何组合多个能力实现复杂功能...")
    
    # 1. 获取各种能力
    retriever = factory.create_retriever(pipeline_mode="advanced", cache_key="combo_retriever")
    analyzer = factory.create_data_analyzer(with_retriever=True, cache_key="combo_analyzer")
    generator = factory.create_style_generator(with_retriever=True, cache_key="combo_generator")
    memory = factory.create_memory_manager(cache_key="combo_memory")
    
    print("✅ 已创建：检索器、分析器、生成器、记忆管理器")
    
    # 2. 组合使用示例
    print("\n[场景] 用户询问：'帮我总结一下上周的学习情况'")
    
    # Step 1: 检索相关记忆
    print("\n  Step 1: 检索相关记忆...")
    memories = await retriever.retrieve(
        query="上周学习",
        top_k=10,
        filters={"category": "学习"}
    )
    print(f"  ✅ 找到 {len(memories)} 条相关记忆")
    
    # Step 2: 数据分析
    print("\n  Step 2: 分析学习数据...")
    analysis = await analyzer.analyze(
        data=memories,
        analysis_type="summary"
    )
    print(f"  ✅ 分析完成")
    
    # Step 3: 生成总结
    print("\n  Step 3: 生成温暖的总结...")
    summary = await generator.generate(
        content=analysis["summary"],
        style="温暖鼓励",
        context={"analysis": analysis}
    )
    print(f"\n  📝 生成的总结:")
    print(f"  {summary}")
    
    # Step 4: 保存对话记忆
    print("\n  Step 4: 保存对话记忆...")
    await memory.store(
        content=f"用户询问了学习总结，系统生成了总结",
        importance=0.7,
        category="对话",
        tags=["总结", "学习"]
    )
    print("  ✅ 对话记忆已保存")


async def main():
    """主函数"""
    print("=" * 60)
    print("AME 能力工厂详解")
    print("=" * 60)
    
    # 初始化基础组件
    print("\n初始化基础组件...")
    llm = OpenAICaller(api_key=os.getenv("OPENAI_API_KEY", "sk-..."))
    embedding = OpenAIEmbedding(api_key=os.getenv("OPENAI_API_KEY", "sk-..."))
    vector_store = VectorStore(path="./data/vectors")
    graph_store = GraphStore(host="localhost", port=6379)
    document_store = DocumentStore(path="./data/documents")
    
    # 创建工厂
    factory = CapabilityFactory(
        llm_caller=llm,
        embedding_function=embedding,
        vector_store=vector_store,
        graph_store=graph_store,
        document_store=document_store
    )
    print("✅ 能力工厂已创建")
    
    # 运行各个演示
    await demo_retrieval_capabilities(factory)
    await demo_analysis_capabilities(factory)
    await demo_generation_capabilities(factory)
    await demo_memory_capabilities(factory)
    await demo_intent_capabilities(factory)
    await demo_capability_combinations(factory)
    
    # 总结
    print("\n" + "=" * 60)
    print("✨ 能力工厂演示完成！")
    print("=" * 60)
    print("\n📖 关键要点:")
    print("  1. 使用 CapabilityFactory 统一管理所有能力")
    print("  2. 通过 cache_key 复用能力实例，提高性能")
    print("  3. 不同能力可以灵活组合，实现复杂功能")
    print("  4. Service 层应该注入 Factory，而非直接创建")


if __name__ == "__main__":
    asyncio.run(main())
