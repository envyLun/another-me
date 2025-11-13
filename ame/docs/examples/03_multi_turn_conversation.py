"""
示例 3: 多轮对话与上下文压缩

演示如何使用 ConversationHistory 进行多轮对话，
以及上下文过长时的自动压缩功能。
"""

import asyncio
import os
from ame.foundation.llm import OpenAICaller


async def demo_basic_multi_turn():
    """演示基础多轮对话"""
    print("\n" + "=" * 60)
    print("基础多轮对话演示")
    print("=" * 60)
    
    # 初始化 LLM
    llm = OpenAICaller(
        api_key=os.getenv("OPENAI_API_KEY", "sk-..."),
        model="gpt-3.5-turbo",
        max_context_tokens=1000  # 设置较小的上下文限制用于演示
    )
    
    # 创建对话历史
    conversation = llm.create_conversation(
        system_prompt="你是一个友好的 AI 助手，擅长回答编程相关问题。"
    )
    
    print(f"\n✅ 对话已创建 (最大上下文: {llm.max_context_tokens} tokens)")
    
    # 多轮对话
    questions = [
        "什么是 Python 的异步编程？",
        "能给我一个具体的例子吗？",
        "在实际项目中如何使用它？",
        "有什么常见的坑吗？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n--- 第 {i} 轮对话 ---")
        print(f"👤 用户: {question}")
        
        # 使用对话历史进行对话
        response = await llm.chat_with_history(
            conversation=conversation,
            user_message=question,
            temperature=0.7
        )
        
        print(f"🤖 AI: {response.content[:200]}...")
        print(f"📊 Token 使用: {response.usage['total_tokens']}")
        print(f"💬 历史消息数: {conversation.get_message_count()}")


async def demo_streaming_multi_turn():
    """演示流式多轮对话"""
    print("\n" + "=" * 60)
    print("流式多轮对话演示")
    print("=" * 60)
    
    llm = OpenAICaller(
        api_key=os.getenv("OPENAI_API_KEY", "sk-..."),
        model="gpt-3.5-turbo"
    )
    
    conversation = llm.create_conversation(
        system_prompt="你是一个讲故事高手，善于续写故事。"
    )
    
    print(f"\n✅ 对话已创建")
    
    # 流式对话
    prompts = [
        "给我讲一个关于勇气的故事的开头",
        "然后呢？继续讲",
        "最后怎么样了？"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n--- 第 {i} 轮对话 ---")
        print(f"👤 用户: {prompt}")
        print("🤖 AI: ", end="", flush=True)
        
        async for chunk in llm.chat_stream_with_history(
            conversation=conversation,
            user_message=prompt,
            temperature=0.8
        ):
            print(chunk, end="", flush=True)
        
        print("\n")


async def demo_context_compression():
    """演示上下文自动压缩"""
    print("\n" + "=" * 60)
    print("上下文自动压缩演示")
    print("=" * 60)
    
    # 设置较小的上下文限制，便于触发压缩
    llm = OpenAICaller(
        api_key=os.getenv("OPENAI_API_KEY", "sk-..."),
        model="gpt-3.5-turbo",
        max_context_tokens=500  # 故意设置得很小
    )
    
    conversation = llm.create_conversation(
        system_prompt="你是一个 AI 助手。"
    )
    
    print(f"\n✅ 对话已创建 (最大上下文: {llm.max_context_tokens} tokens)")
    print("⚠️  由于上下文限制较小，将演示自动压缩功能")
    
    # 进行多轮对话，逐渐填满上下文
    messages = [
        "请详细介绍一下 Python 的历史和发展",
        "Python 有哪些主要的应用领域？",
        "Python 的优缺点分别是什么？",
        "Python 2 和 Python 3 有什么区别？",
        "如何学习 Python？",
        "Python 的未来发展趋势是什么？"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n--- 第 {i} 轮对话 ---")
        print(f"👤 用户: {msg}")
        
        # 计算当前上下文 token 数
        current_messages = conversation.get_messages()
        total_tokens = sum(
            llm.estimate_tokens(m.get("content", "")) 
            for m in current_messages
        )
        
        print(f"📊 当前上下文 tokens: {total_tokens}/{llm.max_context_tokens}")
        
        # 发送消息
        response = await llm.chat_with_history(
            conversation=conversation,
            user_message=msg,
            temperature=0.7
        )
        
        print(f"🤖 AI: {response.content[:150]}...")
        print(f"💬 历史消息数: {conversation.get_message_count()}")
        
        # 检查是否触发了压缩
        if "compressed" in response.metadata:
            print("🔄 触发了上下文压缩！")


async def demo_manual_compression():
    """演示手动压缩功能"""
    print("\n" + "=" * 60)
    print("手动压缩演示")
    print("=" * 60)
    
    llm = OpenAICaller(
        api_key=os.getenv("OPENAI_API_KEY", "sk-..."),
        model="gpt-3.5-turbo"
    )
    
    # 创建一个较长的消息列表
    messages = [
        {"role": "system", "content": "你是一个 AI 助手。"},
        {"role": "user", "content": "第一个问题：" + "a" * 100},
        {"role": "assistant", "content": "第一个回答：" + "b" * 100},
        {"role": "user", "content": "第二个问题：" + "c" * 100},
        {"role": "assistant", "content": "第二个回答：" + "d" * 100},
        {"role": "user", "content": "第三个问题：" + "e" * 100},
        {"role": "assistant", "content": "第三个回答：" + "f" * 100},
    ]
    
    print(f"\n原始消息数: {len(messages)}")
    
    # 计算总 token 数
    total_tokens = sum(llm.estimate_tokens(msg["content"]) for msg in messages)
    print(f"原始 token 数: {total_tokens}")
    
    # 压缩到 200 tokens
    compressed = llm.compress_messages(messages, max_tokens=200)
    
    print(f"\n压缩后消息数: {len(compressed)}")
    compressed_tokens = sum(llm.estimate_tokens(msg["content"]) for msg in compressed)
    print(f"压缩后 token 数: {compressed_tokens}")
    
    print(f"\n✅ 压缩效果:")
    print(f"  - 移除消息数: {len(messages) - len(compressed)}")
    print(f"  - 节省 tokens: {total_tokens - compressed_tokens}")
    print(f"  - 压缩率: {(1 - compressed_tokens/total_tokens)*100:.1f}%")
    
    # 显示压缩后的消息
    print(f"\n📋 压缩后的消息:")
    for msg in compressed:
        role = msg["role"]
        content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
        print(f"  [{role}] {content}")


async def demo_token_estimation():
    """演示 token 估算功能"""
    print("\n" + "=" * 60)
    print("Token 估算演示")
    print("=" * 60)
    
    llm = OpenAICaller(
        api_key=os.getenv("OPENAI_API_KEY", "sk-..."),
        model="gpt-3.5-turbo"
    )
    
    test_texts = [
        "Hello, world!",
        "你好，世界！",
        "This is a longer English sentence with more words.",
        "这是一个更长的中文句子，包含更多的字符。",
        "混合 Mixed 文本 text with 中英文 English and Chinese.",
    ]
    
    print("\n📊 Token 估算结果:")
    print("-" * 60)
    
    for text in test_texts:
        tokens = llm.estimate_tokens(text)
        chars = len(text)
        ratio = chars / tokens if tokens > 0 else 0
        
        print(f"\n文本: {text}")
        print(f"  - 字符数: {chars}")
        print(f"  - 估算 tokens: {tokens}")
        print(f"  - 字符/token 比: {ratio:.2f}")


async def main():
    """主函数"""
    print("=" * 60)
    print("多轮对话与上下文压缩示例")
    print("=" * 60)
    
    # 运行各个演示
    await demo_basic_multi_turn()
    await demo_streaming_multi_turn()
    await demo_context_compression()
    await demo_manual_compression()
    await demo_token_estimation()
    
    # 总结
    print("\n" + "=" * 60)
    print("✨ 演示完成！")
    print("=" * 60)
    print("\n📖 关键功能:")
    print("  1. ConversationHistory - 多轮对话历史管理")
    print("  2. chat_with_history() - 使用历史的对话")
    print("  3. chat_stream_with_history() - 流式多轮对话")
    print("  4. 自动上下文压缩 - 超过限制时无感压缩")
    print("  5. estimate_tokens() - 精确的 token 估算")
    print("  6. compress_messages() - 手动压缩消息")
    print("\n💡 压缩策略:")
    print("  - 保留系统消息（system）")
    print("  - 保留最新的对话（从新到旧）")
    print("  - 自动移除最早的消息")
    print("  - 日志记录压缩过程")


if __name__ == "__main__":
    asyncio.run(main())
ß