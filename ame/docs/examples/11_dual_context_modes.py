"""
示例 11: 双模式上下文管理

演示 SESSION 和 DOCUMENT 两种上下文管理模式的使用场景。

场景1 - SESSION 模式（会话型）:
- 用户多轮对话
- 保留完整历史
- 对话结束时导出到图谱数据库

场景2 - DOCUMENT 模式（文档型）:
- 处理长文本（PDF、TXT等）
- 自动静默压缩
- 保留关键信息用于导出
"""

import asyncio
import os
from ame.foundation.llm import OpenAICaller, ContextMode


async def demo_session_mode():
    """演示会话模式（SESSION）"""
    print("\n" + "=" * 60)
    print("会话模式（SESSION）演示")
    print("=" * 60)
    
    llm = OpenAICaller(
        api_key=os.getenv("OPENAI_API_KEY", "sk-..."),
        model="gpt-3.5-turbo",
        max_context_tokens=2000  # 设置较小的限制用于演示
    )
    
    # 创建会话模式的对话
    conversation = llm.create_conversation(
        system_prompt="你是一个友好的AI助手，专注于帮助用户解决问题。",
        mode=ContextMode.SESSION
    )
    
    print(f"\n✅ 创建会话 (模式: {conversation.mode.value})")
    print(f"📊 最大上下文: {llm.max_context_tokens} tokens")
    
    # 模拟多轮对话
    questions = [
        "你好，我想学习 Python",
        "从哪里开始比较好？",
        "有什么好的书籍推荐吗？",
        "我应该先学什么？",
        "谢谢你的建议！"
    ]
    
    print("\n" + "-" * 60)
    print("开始多轮对话:")
    print("-" * 60)
    
    for i, question in enumerate(questions, 1):
        print(f"\n[轮次 {i}]")
        print(f"👤 用户: {question}")
        
        # 标记重要消息（可选）
        is_important = "推荐" in question or "开始" in question
        
        response = await llm.chat_with_history(
            conversation=conversation,
            user_message=question,
            temperature=0.7
        )
        
        # 如果是重要问题，标记回复为重要
        if is_important:
            # 获取最后一条消息并标记为重要
            if conversation.messages:
                conversation.messages[-1].metadata["important"] = True
                print("⭐ 已标记为重要消息")
        
        print(f"🤖 AI: {response.content[:150]}...")
        
        # 显示统计信息
        stats = conversation.get_compression_stats()
        print(f"📊 当前消息数: {stats['active_messages']} (归档: {stats['archived_messages']})")
    
    # 对话结束，导出到图谱
    print("\n" + "-" * 60)
    print("对话结束，准备导出到图谱数据库...")
    print("-" * 60)
    
    # 方法1：导出关键信息（根据 mode 自动选择策略）
    important_data = conversation.export_important()
    
    print(f"\n📊 导出关键信息（SESSION 模式）:")
    print(f"  - 模式: {important_data['mode']}")
    print(f"  - 总对话数: {important_data['total_conversations']}")
    print(f"  - 重要消息数: {important_data['important_count']}")
    print(f"  - 导出内容: {len(important_data['export_content'])} 条")
    
    print(f"\n📋 导出的关键消息:")
    for i, msg in enumerate(important_data['export_content'][:3], 1):
        important_tag = " ⭐" if msg.get('important') else ""
        print(f"  {i}. [{msg['role']}] {msg['content'][:50]}...{important_tag}")
    
    # 方法2：清空并导出（对话结杞时使用）
    # graph_data = conversation.clear_and_export()
    
    return important_data


async def demo_document_mode():
    """演示文档模式（DOCUMENT）"""
    print("\n" + "=" * 60)
    print("文档模式（DOCUMENT）演示")
    print("=" * 60)
    
    llm = OpenAICaller(
        api_key=os.getenv("OPENAI_API_KEY", "sk-..."),
        model="gpt-3.5-turbo",
        max_context_tokens=1500  # 较小的限制，便于触发压缩
    )
    
    # 创建文档模式的对话
    doc_conversation = llm.create_conversation(
        system_prompt="请分析以下文档内容，提取关键信息。",
        mode=ContextMode.DOCUMENT
    )
    
    print(f"\n✅ 创建文档处理会话 (模式: {doc_conversation.mode.value})")
    print(f"📊 最大上下文: {llm.max_context_tokens} tokens")
    print(f"💡 文档模式会自动静默压缩长文本")
    
    # 模拟处理长文档
    print("\n" + "-" * 60)
    print("开始处理长文档:")
    print("-" * 60)
    
    # 模拟分段上传大文档
    document_chunks = [
        """
        第一部分：Python 简介
        Python是一种高级编程语言，由Guido van Rossum于1989年创建。
        它具有简洁的语法、强大的功能和丰富的库支持。
        Python广泛应用于Web开发、数据分析、人工智能等领域。
        """,
        """
        第二部分：Python 特性
        1. 易学易用：语法简洁明了，适合初学者
        2. 跨平台：支持Windows、Linux、macOS等多个操作系统
        3. 丰富的库：拥有大量第三方库和框架
        4. 动态类型：无需声明变量类型
        5. 面向对象：支持面向对象编程范式
        """,
        """
        第三部分：Python 应用领域
        - Web开发：Django、Flask等框架
        - 数据科学：NumPy、Pandas、Matplotlib
        - 人工智能：TensorFlow、PyTorch、scikit-learn
        - 自动化运维：Ansible、SaltStack
        - 爬虫开发：Scrapy、BeautifulSoup
        """,
        """
        第四部分：学习路径
        1. 基础语法：变量、数据类型、控制流
        2. 函数与模块：函数定义、模块导入
        3. 面向对象：类、继承、多态
        4. 标准库：文件操作、网络编程
        5. 高级特性：装饰器、生成器、异步编程
        """,
        """
        第五部分：最佳实践
        1. 遵循PEP 8代码规范
        2. 编写单元测试
        3. 使用虚拟环境管理依赖
        4. 添加文档字符串
        5. 进行代码审查
        """
    ]
    
    analysis_prompts = [
        "请总结第一部分的核心内容",
        "第二部分提到了哪些重要特性？",
        "Python主要应用在哪些领域？",
        "学习Python应该遵循什么路径？",
        "有什么最佳实践建议？"
    ]
    
    for i, (chunk, prompt) in enumerate(zip(document_chunks, analysis_prompts), 1):
        print(f"\n[文档分段 {i}]")
        
        # 添加文档内容
        doc_conversation.add_message(
            role="user",
            content=f"文档内容：{chunk}\n\n{prompt}",
            important=(i == 1 or i == 3)  # 标记第1和第3段为重要
        )
        
        # 获取分析结果
        response = await llm.chat_with_history(
            conversation=doc_conversation,
            user_message="",  # 已经在上面添加了
            temperature=0.3
        )
        
        print(f"📄 处理文档分段 {i}...")
        print(f"🤖 分析结果: {response.content[:100]}...")
        
        # 显示压缩统计
        stats = doc_conversation.get_compression_stats()
        print(f"📊 统计: 活跃 {stats['active_messages']}, 归档 {stats['archived_messages']}")
        
        if stats['total_compressions'] > 0:
            print(f"🔄 已触发 {stats['total_compressions']} 次自动压缩（静默）")
    
    # 文档处理完成，导出关键信息
    print("\n" + "-" * 60)
    print("文档处理完成，导出关键信息...")
    print("-" * 60)
    
    # 方法1：导出关键信息（根据 mode 自动选择策略）
    important_data = doc_conversation.export_important()
    
    print(f"\n📊 导出关键信息（DOCUMENT 模式）:")
    print(f"  - 模式: {important_data['mode']}")
    print(f"  - 总消息数: {important_data['total_messages']}")
    print(f"  - LLM 分析次数: {important_data['analysis_count']}")
    
    print(f"\n🤖 LLM 分析结果:")
    for i, analysis in enumerate(important_data['export_content']['llm_analysis'][:3], 1):
        print(f"  {i}. {analysis['content'][:60]}...")
    
    print(f"\n📄 重要输入片段:")
    for i, inp in enumerate(important_data['export_content']['important_inputs'][:2], 1):
        print(f"  {i}. {inp['content'][:60]}...")
    
    # 方法2：导出所有信息（包括归档）
    # all_data = doc_conversation.export_all()
    
    return important_data


async def demo_graph_export_format():
    """演示导出格式"""
    print("\n" + "=" * 60)
    print("📊 导出格式演示")
    print("=" * 60)
    
    print("\n✨ SESSION 模式导出格式（用户对话）:")
    print("""
    {
        "mode": "session",
        "total_conversations": 20,           // 总对话数
        "important_count": 5,                // 重要消息数
        "export_content": [
            {
                "role": "user",
                "content": "记住：我的生日是1990-01-01",
                "timestamp": "2024-01-01T10:00:00",
                "important": true              // 标记为重要
            },
            {
                "role": "assistant",
                "content": "好的，我已经记住了您的生日...",
                "timestamp": "2024-01-01T10:00:05",
                "important": false
            },
            // ... 最近的5条对话
        ]
    }
    
    💡 说明：
    - 导出所有标记为 important=True 的消息
    - 附加最近的 5 条对话（保持上下文）
    - 自动去重
    - 适合存入图谱，建立用户画像和对话关系
    """)
    
    print("\n📄 DOCUMENT 模式导出格式（文档处理）:")
    print("""
    {
        "mode": "document",
        "total_messages": 50,                // 总消息数（含压缩的）
        "analysis_count": 10,                // LLM 分析次数
        "export_content": {
            "llm_analysis": [                 // LLM 的分析结果
                {
                    "content": "文档核心观点：本文讨论了...",
                    "timestamp": "2024-01-01T10:05:00"
                },
                {
                    "content": "关键信息：作者认为...",
                    "timestamp": "2024-01-01T10:06:00"
                }
                // ... 更多分析结果
            ],
            "important_inputs": [             // 标记为重要的原始输入
                {
                    "content": "PDF第一章节内容...（前200字符）",
                    "timestamp": "2024-01-01T10:00:00"
                }
                // ... 更多重要输入片段
            ]
        }
    }
    
    💡 说明：
    - llm_analysis: 提取所有 assistant 的回复（大模型解析结果）
    - important_inputs: 提取标记为重要的用户输入（原始文档关键部分）
    - 内容超过200字符会被截断（加...）
    - 适合存入图谱，建立文档实体和关键信息
    """)


async def demo_comparison():
    """演示两种模式的对比"""
    print("\n" + "=" * 60)
    print("两种模式对比")
    print("=" * 60)
    
    comparison_table = """
    ┌─────────────────┬───────────────────────┬───────────────────────┐
    │     特性        │   SESSION 模式        │   DOCUMENT 模式       │
    ├─────────────────┼───────────────────────┼───────────────────────┤
    │ 使用场景        │ 用户多轮对话          │ 长文本处理            │
    │ 压缩策略        │ 尽量保留完整历史      │ 自动静默压缩          │
    │ 导出时机        │ 对话结束时            │ 处理完成时            │
    │ 导出内容        │ 重要消息+最近对话     │ LLM分析结果          │
    │ 重要性标记      │ 支持                  │ 支持                  │
    │ 归档机制        │ 支持                  │ 支持                  │
    │ 日志级别        │ WARNING（压缩时）     │ INFO（静默压缩）      │
    │ 典型用途        │ 聊天、问答            │ PDF分析、文档解析     │
    │ 图谱存储        │ 对话关系、用户画像    │ 文档实体、关键信息    │
    └─────────────────┴───────────────────────┴───────────────────────┘
    """
    
    print(comparison_table)
    
    print("\n💡 使用建议:")
    print("  1. SESSION 模式（用户对话）：")
    print("     - 用于用户日常对话")
    print("     - 对话结束时调用 export_important() 或 clear_and_export()")
    print("     - 导出内容：标记为 important 的消息 + 最近5条对话")
    print("     - 可存入图谱建立用户画像、对话关系")
    print("")
    print("  2. DOCUMENT 模式（文档处理）：")
    print("     - 用于处理上传的文档（PDF、TXT等）")
    print("     - 处理完成后调用 export_important()")
    print("     - 导出内容：LLM 的分析结果（assistant 回复）")
    print("     - 可存入图谱建立文档实体、关键信息")
    print("")
    print("  3. 共同点：")
    print("     - 都会归档被压缩的消息（信息不丢失）")
    print("     - 都支持导出关键信息（export_important）")
    print("     - 都支持导出所有信息（export_all）")
    print("     - 都支持重要性标记（important=True）")


async def main():
    """主函数"""
    print("=" * 60)
    print("AME 双模式上下文管理示例")
    print("=" * 60)
    
    # 运行演示
    await demo_session_mode()
    await demo_document_mode()
    await demo_graph_export_format()
    await demo_comparison()
    
    # 总结
    print("\n" + "=" * 60)
    print("✨ 演示完成！")
    print("=" * 60)
    
    print("\n📖 核心功能:")
    print("  1. SESSION 模式 - 用户对话，导出重要信息")
    print("  2. DOCUMENT 模式 - 文档处理，导出 LLM 分析结果")
    print("  3. 重要性标记 - important=True 优先保留")
    print("  4. 归档机制 - 压缩的消息自动归档")
    print("  5. 导出能力 - export_important() / export_all() / clear_and_export()")
    print("  6. 统计信息 - get_compression_stats()")
    
    print("\n💾 导出说明:")
    print("  export_important() - 导出关键信息（根据 mode 自动选择策略）")
    print("    SESSION: 重要消息 + 最近5条对话")
    print("    DOCUMENT: LLM 分析结果 + 重要输入片段")
    print("  ")
    print("  export_all() - 导出所有消息（包括归档）")
    print("    适用于需要完整历史或数据备份")
    print("  ")
    print("  clear_and_export() - 清空并导出关键信息")
    print("    对话/文档处理结束时调用")


if __name__ == "__main__":
    asyncio.run(main())
