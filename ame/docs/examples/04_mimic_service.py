"""
示例 4: 智能对话服务进阶

演示 MimicService 的高级功能和使用技巧。
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any

from ame.foundation.llm import OpenAICaller
from ame.foundation.embedding import OpenAIEmbedding
from ame.foundation.storage import VectorStore, GraphStore, DocumentStore
from ame.capabilities import CapabilityFactory
from ame.services.conversation import MimicService


async def demo_basic_chat(service: MimicService):
    """演示基础对话"""
    print("\n" + "=" * 60)
    print("基础对话演示")
    print("=" * 60)
    
    conversations = [
        "你好，很高兴认识你！",
        "今天天气真好，我想出去散步",
        "你能帮我推荐一本好书吗？"
    ]
    
    for msg in conversations:
        print(f"\n👤 用户: {msg}")
        
        response = await service.chat(
            user_message=msg,
            context={"user_id": "demo_user", "session_id": "session_001"}
        )
        
        print(f"🤖 AI: {response['content']}")
        print(f"📊 意图: {response.get('intent', 'unknown')}")


async def demo_streaming_chat(service: MimicService):
    """演示流式对话"""
    print("\n" + "=" * 60)
    print("流式对话演示")
    print("=" * 60)
    
    user_message = "给我讲一个关于勇气的故事"
    print(f"\n👤 用户: {user_message}")
    print("🤖 AI: ", end="", flush=True)
    
    async for chunk in service.chat_stream(
        user_message=user_message,
        context={"user_id": "demo_user"}
    ):
        print(chunk, end="", flush=True)
    
    print("\n")


async def demo_intent_routing(service: MimicService):
    """演示意图识别和智能路由"""
    print("\n" + "=" * 60)
    print("意图识别和智能路由演示")
    print("=" * 60)
    
    test_cases = [
        {
            "message": "你好",
            "expected_intent": "chat"
        },
        {
            "message": "搜索一下 Python 异步编程的资料",
            "expected_intent": "search"
        },
        {
            "message": "我昨天去了公园，心情很好",
            "expected_intent": "memory"
        },
        {
            "message": "帮我分析一下这周的数据",
            "expected_intent": "analysis"
        }
    ]
    
    for case in test_cases:
        msg = case["message"]
        expected = case["expected_intent"]
        
        print(f"\n👤 用户: {msg}")
        print(f"🎯 预期意图: {expected}")
        
        response = await service.chat(
            user_message=msg,
            context={"user_id": "demo_user"}
        )
        
        detected_intent = response.get('intent', 'unknown')
        print(f"✅ 检测到意图: {detected_intent}")
        print(f"🤖 AI: {response['content'][:100]}...")


async def demo_content_safety(service: MimicService):
    """演示内容安全过滤"""
    print("\n" + "=" * 60)
    print("内容安全过滤演示")
    print("=" * 60)
    
    test_messages = [
        "今天天气真好",
        "这是一条正常的消息",
        "包含不当内容的测试消息"
    ]
    
    for msg in test_messages:
        print(f"\n👤 测试消息: {msg}")
        
        safety = await service.check_content_safety(msg)
        
        if safety["is_safe"]:
            print("✅ 内容安全")
        else:
            print(f"⚠️ 内容不安全")
            print(f"   警告: {safety['warning']}")
            print(f"   严重程度: {safety['severity']}")
            if safety.get('matched_keywords'):
                print(f"   匹配关键词: {safety['matched_keywords']}")


async def demo_memory_management(service: MimicService):
    """演示记忆管理"""
    print("\n" + "=" * 60)
    print("记忆管理演示")
    print("=" * 60)
    
    # 不同类型的对话
    conversations = [
        {
            "message": "我今天完成了一个重要项目",
            "expected_retention": "PERMANENT"
        },
        {
            "message": "明天记得带雨伞",
            "expected_retention": "TEMPORARY"
        },
        {
            "message": "你好",
            "expected_retention": "EPHEMERAL"
        }
    ]
    
    for conv in conversations:
        msg = conv["message"]
        expected = conv["expected_retention"]
        
        print(f"\n👤 用户: {msg}")
        print(f"📋 预期记忆类型: {expected}")
        
        # 学习对话
        learning_result = await service.learn_from_conversation(
            user_message=msg,
            context={"user_id": "demo_user"}
        )
        
        print(f"✅ 实际记忆类型: {learning_result['retention_type'].value}")
        print(f"💾 是否存储: {learning_result['stored']}")
        
        if learning_result['memory_id']:
            print(f"🆔 记忆ID: {learning_result['memory_id']}")


async def demo_style_mimicry(service: MimicService):
    """演示风格模仿"""
    print("\n" + "=" * 60)
    print("风格模仿演示")
    print("=" * 60)
    
    # 先让 AI 学习一些用户的表达方式
    print("\n[步骤 1] 让 AI 学习用户的表达风格...")
    
    user_expressions = [
        "哇塞，这个太棒了！",
        "嗯嗯，我觉得可以试试",
        "emmm，让我想想",
        "超级赞！必须给个大大的赞"
    ]
    
    for expr in user_expressions:
        await service.learn_from_conversation(
            user_message=expr,
            context={"user_id": "demo_user"}
        )
        print(f"  ✅ 已学习: {expr}")
    
    # 现在让 AI 生成回复，看是否模仿了用户风格
    print("\n[步骤 2] 测试 AI 是否学会了用户的表达风格...")
    
    test_message = "你觉得这个方案怎么样？"
    print(f"\n👤 用户: {test_message}")
    
    response = await service.chat(
        user_message=test_message,
        context={
            "user_id": "demo_user",
            "enable_style_mimicry": True  # 启用风格模仿
        }
    )
    
    print(f"🤖 AI (模仿用户风格): {response['content']}")
    print("\n💡 注意 AI 是否使用了类似'哇塞'、'嗯嗯'、'emmm'等用户惯用表达")


async def demo_context_awareness(service: MimicService):
    """演示上下文感知"""
    print("\n" + "=" * 60)
    print("上下文感知演示")
    print("=" * 60)
    
    # 模拟一个完整的对话上下文
    conversation_history = []
    
    messages = [
        "我最近在学习 Python",
        "特别是异步编程这块",
        "你能给我一些建议吗？"
    ]
    
    for msg in messages:
        print(f"\n👤 用户: {msg}")
        
        # 将历史对话作为上下文传入
        response = await service.chat(
            user_message=msg,
            context={
                "user_id": "demo_user",
                "session_id": "session_context_demo",
                "conversation_history": conversation_history
            }
        )
        
        print(f"🤖 AI: {response['content']}")
        
        # 更新对话历史
        conversation_history.append({
            "role": "user",
            "content": msg,
            "timestamp": datetime.now().isoformat()
        })
        conversation_history.append({
            "role": "assistant",
            "content": response['content'],
            "timestamp": datetime.now().isoformat()
        })
    
    print("\n💡 注意 AI 如何利用之前的对话内容提供更相关的建议")


async def main():
    """主函数"""
    print("=" * 60)
    print("AME 智能对话服务进阶示例")
    print("=" * 60)
    
    # 初始化
    print("\n初始化服务...")
    
    llm = OpenAICaller(api_key=os.getenv("OPENAI_API_KEY", "sk-..."))
    embedding = OpenAIEmbedding(api_key=os.getenv("OPENAI_API_KEY", "sk-..."))
    vector_store = VectorStore(path="./data/vectors")
    graph_store = GraphStore(host="localhost", port=6379)
    document_store = DocumentStore(path="./data/documents")
    
    factory = CapabilityFactory(
        llm_caller=llm,
        embedding_function=embedding,
        vector_store=vector_store,
        graph_store=graph_store,
        document_store=document_store
    )
    
    service = MimicService(
        capability_factory=factory,
        enable_safety_filter=True,
        enable_intent_recognition=True,
        enable_memory=True
    )
    
    print("✅ MimicService 已初始化")
    
    # 运行演示
    await demo_basic_chat(service)
    await demo_streaming_chat(service)
    await demo_intent_routing(service)
    await demo_content_safety(service)
    await demo_memory_management(service)
    await demo_style_mimicry(service)
    await demo_context_awareness(service)
    
    # 总结
    print("\n" + "=" * 60)
    print("✨ 智能对话服务演示完成！")
    print("=" * 60)
    print("\n📖 关键功能:")
    print("  1. 内容安全过滤 - 检测不当内容")
    print("  2. 意图识别 - 自动判断用户意图")
    print("  3. 智能路由 - 根据意图调用不同能力")
    print("  4. 记忆管理 - 自动分类和存储对话")
    print("  5. 风格模仿 - 学习用户的表达习惯")
    print("  6. 上下文感知 - 利用历史对话提供更好的回复")


if __name__ == "__main__":
    asyncio.run(main())
