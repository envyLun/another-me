"""
示例 1: 基础使用

演示如何使用 AME 引擎的基础功能。
"""

import asyncio
import os
from typing import Dict, Any

# Foundation Layer
from ame.foundation.llm import OpenAICaller
from ame.foundation.embedding import OpenAIEmbedding
from ame.foundation.storage import VectorStore, GraphStore, DocumentStore

# Capabilities Layer
from ame.capabilities import CapabilityFactory

# Services Layer
from ame.services.conversation import MimicService


async def main():
    """基础使用示例"""
    
    print("=" * 60)
    print("AME 基础使用示例")
    print("=" * 60)
    
    # ========== 1. 初始化基础组件 ==========
    print("\n[1] 初始化基础组件...")
    
    # LLM 调用器
    llm = OpenAICaller(
        api_key=os.getenv("OPENAI_API_KEY", "sk-..."),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        max_retries=3,
        timeout=60.0
    )
    
    if not llm.is_configured():
        print("❌ LLM 未配置，请设置 OPENAI_API_KEY 环境变量")
        return
    
    print(f"✅ LLM 已配置: {llm.get_model_name()}")
    
    # Embedding 函数
    embedding = OpenAIEmbedding(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="text-embedding-ada-002"
    )
    print("✅ Embedding 已配置")
    
    # 存储组件（示例使用内存存储）
    vector_store = VectorStore(path="./data/vectors")
    graph_store = GraphStore(host="localhost", port=6379)
    document_store = DocumentStore(path="./data/documents")
    print("✅ 存储组件已初始化")
    
    # ========== 2. 创建能力工厂 ==========
    print("\n[2] 创建能力工厂...")
    
    factory = CapabilityFactory(
        llm_caller=llm,
        embedding_function=embedding,
        vector_store=vector_store,
        graph_store=graph_store,
        document_store=document_store
    )
    print("✅ 能力工厂创建成功")
    
    # ========== 3. 初始化服务 ==========
    print("\n[3] 初始化智能对话服务...")
    
    mimic_service = MimicService(
        capability_factory=factory,
        enable_safety_filter=True,
        enable_intent_recognition=True,
        enable_memory=True
    )
    print("✅ MimicService 初始化成功")
    
    # ========== 4. 基础对话 ==========
    print("\n[4] 开始对话...")
    print("-" * 60)
    
    # 示例对话 1: 简单问候
    user_message_1 = "你好，今天天气真好！"
    print(f"\n👤 用户: {user_message_1}")
    
    response_1 = await mimic_service.chat(
        user_message=user_message_1,
        context={"user_id": "demo_user"}
    )
    
    print(f"🤖 AI: {response_1['content']}")
    print(f"📊 意图: {response_1.get('intent', 'unknown')}")
    print(f"💾 已保存记忆: {response_1.get('memory_saved', False)}")
    
    # 示例对话 2: 知识问答
    user_message_2 = "Python 的 asyncio 是什么？"
    print(f"\n👤 用户: {user_message_2}")
    
    response_2 = await mimic_service.chat(
        user_message=user_message_2,
        context={"user_id": "demo_user"}
    )
    
    print(f"🤖 AI: {response_2['content']}")
    
    # ========== 5. 流式对话 ==========
    print("\n[5] 流式对话示例...")
    print("-" * 60)
    
    user_message_3 = "给我讲一个关于 AI 的小故事"
    print(f"\n👤 用户: {user_message_3}")
    print("🤖 AI: ", end="", flush=True)
    
    async for chunk in mimic_service.chat_stream(
        user_message=user_message_3,
        context={"user_id": "demo_user"}
    ):
        print(chunk, end="", flush=True)
    
    print("\n")
    
    # ========== 6. 内容安全检测 ==========
    print("\n[6] 内容安全检测示例...")
    print("-" * 60)
    
    unsafe_message = "这是一条包含不当内容的消息"
    print(f"\n👤 用户: {unsafe_message}")
    
    safety_check = await mimic_service.check_content_safety(unsafe_message)
    
    if not safety_check["is_safe"]:
        print(f"⚠️ 安全警告: {safety_check['warning']}")
        print(f"📊 严重程度: {safety_check['severity']}")
    else:
        print("✅ 内容安全")
    
    # ========== 7. 总结 ==========
    print("\n" + "=" * 60)
    print("✨ 基础使用示例完成！")
    print("=" * 60)
    print("\n📖 更多示例:")
    print("  - 02_capability_factory.py  能力工厂详解")
    print("  - 03_retrieval_system.py    检索系统使用")
    print("  - 04_mimic_service.py       智能对话进阶")
    print("  - 05_knowledge_qa.py        知识问答系统")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
