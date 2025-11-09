"""
Capabilities Layer 使用示例

展示如何使用 Memory、Retrieval 和 Intent 模块
"""
import asyncio
from ame.foundation import (
    OpenAIEmbedding,
    OpenAICaller,
    VectorStore,
    GraphStore,
    MetadataStore,
)
from ame.foundation.nlp.ner import HybridNER
from ame.capabilities import (
    MemoryManager,
    HybridRetriever,
    IntentRecognizer,
)


async def memory_example():
    """Memory 模块示例"""
    print("\n=== Memory 模块示例 ===")
    
    # 初始化组件
    embedding = OpenAIEmbedding(api_key="your-api-key")
    vector_store = VectorStore(dimension=1536)
    metadata_store = MetadataStore()
    
    # 创建记忆管理器
    memory_mgr = MemoryManager(
        embedding=embedding,
        vector_store=vector_store,
        metadata_store=metadata_store,
        decay_factor=0.99
    )
    
    # 存储记忆
    memory_id = await memory_mgr.store(
        content="今天完成了项目的核心功能开发，感觉很有成就感",
        importance=0.8,
        emotion="happy",
        category="work",
        tags=["项目", "开发"]
    )
    print(f"存储记忆: {memory_id}")
    
    # 检索记忆
    results = await memory_mgr.retrieve(
        query="项目进展如何",
        top_k=5,
        time_decay=True,
        importance_threshold=0.5
    )
    
    for memory in results:
        print(f"- {memory.content} (重要性: {memory.importance}, 情绪: {memory.emotion})")


async def retrieval_example():
    """Retrieval 模块示例"""
    print("\n=== Retrieval 模块示例 ===")
    
    # 初始化组件
    embedding = OpenAIEmbedding(api_key="your-api-key")
    vector_store = VectorStore(dimension=1536)
    graph_store = GraphStore()
    metadata_store = MetadataStore()
    llm = OpenAICaller(api_key="your-api-key")
    ner = HybridNER(llm_caller=llm)
    
    # 创建混合检索器
    retriever = HybridRetriever(
        embedding=embedding,
        vector_store=vector_store,
        graph_store=graph_store,
        metadata_store=metadata_store,
        ner=ner,
        vector_weight=0.6,
        graph_weight=0.4
    )
    
    # 混合检索
    from ame.capabilities.retrieval import RetrievalStrategy
    results = await retriever.retrieve(
        query="如何提高工作效率",
        top_k=10,
        strategy=RetrievalStrategy.HYBRID,
        rerank=True
    )
    
    for result in results:
        print(f"- [{result.source}] {result.content[:50]}... (分数: {result.score:.3f})")


async def intent_example():
    """Intent 模块示例"""
    print("\n=== Intent 模块示例 ===")
    
    # 初始化组件
    llm = OpenAICaller(api_key="your-api-key")
    ner = HybridNER(llm_caller=llm)
    
    # 创建意图识别器
    intent_recognizer = IntentRecognizer(
        llm_caller=llm,
        ner=ner,
        use_cascade=True,
        confidence_threshold=0.7
    )
    
    # 测试不同的用户输入
    test_inputs = [
        "帮我找一下上周关于项目的讨论记录",
        "记住我明天要开会",
        "最近心情怎么样",
        "分析一下我的工作效率",
    ]
    
    for text in test_inputs:
        result = await intent_recognizer.recognize(text)
        print(f"\n输入: {text}")
        print(f"意图: {result.intent.value} (置信度: {result.confidence:.2f})")
        print(f"实体: {result.entities}")
        print(f"槽位: {result.slots}")


async def full_workflow_example():
    """完整工作流示例"""
    print("\n=== 完整工作流示例 ===")
    
    # 初始化所有组件
    api_key = "your-api-key"
    
    embedding = OpenAIEmbedding(api_key=api_key)
    llm = OpenAICaller(api_key=api_key)
    ner = HybridNER(llm_caller=llm)
    
    vector_store = VectorStore(dimension=1536)
    graph_store = GraphStore()
    metadata_store = MetadataStore()
    
    # 创建能力模块
    memory_mgr = MemoryManager(
        embedding=embedding,
        vector_store=vector_store,
        metadata_store=metadata_store
    )
    
    retriever = HybridRetriever(
        embedding=embedding,
        vector_store=vector_store,
        graph_store=graph_store,
        metadata_store=metadata_store,
        ner=ner
    )
    
    intent_recognizer = IntentRecognizer(
        llm_caller=llm,
        ner=ner,
        use_cascade=True
    )
    
    # 模拟用户交互
    user_input = "帮我找一下上周关于机器学习的笔记"
    
    # 1. 识别意图
    intent_result = await intent_recognizer.recognize(user_input)
    print(f"识别意图: {intent_result.intent.value}")
    
    # 2. 根据意图执行操作
    from ame.capabilities.intent import UserIntent
    
    if intent_result.intent == UserIntent.SEARCH:
        # 执行检索
        results = await retriever.retrieve(
            query=user_input,
            top_k=5,
            rerank=True
        )
        print(f"\n找到 {len(results)} 条结果:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.content[:100]}...")
    
    elif intent_result.intent == UserIntent.MEMORIZE:
        # 存储记忆
        content = intent_result.slots.get("content", user_input)
        memory_id = await memory_mgr.store(
            content=content,
            importance=0.7,
            category="note"
        )
        print(f"已保存记忆: {memory_id}")
    
    elif intent_result.intent == UserIntent.RECALL:
        # 检索记忆
        time_range = intent_result.slots.get("time_range")
        memories = await memory_mgr.retrieve(
            query=user_input,
            top_k=10,
            time_decay=True
        )
        print(f"找到 {len(memories)} 条记忆")


async def main():
    """主函数"""
    print("=" * 60)
    print("Capabilities Layer 使用示例")
    print("=" * 60)
    
    # 运行各个示例
    # 注意：需要配置有效的 API Key 才能运行
    
    # await memory_example()
    # await retrieval_example()
    # await intent_example()
    # await full_workflow_example()
    
    print("\n注意：请配置有效的 OpenAI API Key 后运行示例")
    print("修改代码中的 'your-api-key' 为实际的 API Key")


if __name__ == "__main__":
    asyncio.run(main())
