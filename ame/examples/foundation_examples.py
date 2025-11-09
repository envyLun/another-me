"""
Foundation Layer 使用示例

演示如何使用 Foundation Layer 的各个模块
"""

import asyncio
from foundation.inference import (
    CascadeInferenceEngine,
    InferenceLevelBase,
    InferenceResult,
    InferenceLevel,
    create_rule_level,
    create_llm_level,
)
from foundation.llm import OpenAICaller


# ==================== 示例 1: LLM 调用器 ====================

async def example_llm_caller():
    """演示 LLM 调用器的基本使用"""
    print("=" * 50)
    print("示例 1: LLM 调用器")
    print("=" * 50)
    
    # 初始化调用器
    llm = OpenAICaller(
        api_key="your-api-key-here",  # 或从环境变量读取
        model="gpt-3.5-turbo",
        max_retries=3,
        cache_enabled=True
    )
    
    # 检查是否已配置
    if not llm.is_configured():
        print("警告: LLM 未配置，请设置 OPENAI_API_KEY 环境变量")
        return
    
    # 基本生成
    print("\n1. 基本生成:")
    try:
        response = await llm.generate(
            messages=[
                {"role": "system", "content": "你是一个有帮助的助手。"},
                {"role": "user", "content": "你好！"}
            ],
            temperature=0.7
        )
        
        print(f"回复: {response.content}")
        print(f"模型: {response.model}")
        print(f"Token 使用: {response.usage['total_tokens']}")
    except Exception as e:
        print(f"生成失败: {e}")
    
    # 使用便捷方法
    print("\n2. 使用便捷方法:")
    try:
        response = await llm.generate_with_system(
            prompt="给我讲个笑话",
            system_prompt="你是一个幽默的助手。",
            temperature=0.8
        )
        print(f"回复: {response.content}")
    except Exception as e:
        print(f"生成失败: {e}")
    
    # 流式生成
    print("\n3. 流式生成:")
    try:
        print("回复: ", end="", flush=True)
        async for chunk in llm.generate_stream(
            messages=[{"role": "user", "content": "数到10"}],
            temperature=0.3
        ):
            print(chunk, end="", flush=True)
        print()  # 换行
    except Exception as e:
        print(f"流式生成失败: {e}")
    
    # 缓存演示
    print("\n4. 缓存演示:")
    print(f"缓存大小: {llm.get_cache_size()}")
    
    # 清空缓存
    llm.clear_cache()
    print(f"清空后缓存大小: {llm.get_cache_size()}")


# ==================== 示例 2: 级联推理引擎 ====================

async def example_cascade_inference():
    """演示级联推理引擎的基本使用"""
    print("\n" + "=" * 50)
    print("示例 2: 级联推理引擎")
    print("=" * 50)
    
    # 创建 LLM 调用器
    llm = OpenAICaller()
    
    # 定义规则层级
    def rule_emotion(text, context):
        """基于规则的情绪识别"""
        positive_words = {'开心', '快乐', '高兴', '喜欢', '爱'}
        negative_words = {'难过', '伤心', '痛苦', '讨厌', '恨'}
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return InferenceResult(
                value={'type': 'positive', 'intensity': 0.8},
                confidence=0.85,
                level=InferenceLevel.RULE,
                metadata={'method': 'keyword_matching'}
            )
        elif negative_count > positive_count:
            return InferenceResult(
                value={'type': 'negative', 'intensity': 0.7},
                confidence=0.80,
                level=InferenceLevel.RULE
            )
        else:
            # 置信度不足，需要级联
            return InferenceResult(
                value={'type': 'neutral', 'intensity': 0.5},
                confidence=0.5,  # 低于阈值，会触发级联
                level=InferenceLevel.RULE
            )
    
    # 定义 LLM 层级
    def llm_prompt_builder(text, context):
        return f"""分析以下文本的情绪，返回 JSON 格式：
{{"type": "positive/negative/neutral", "intensity": 0.0-1.0}}

文本: {text}

只返回 JSON，不要其他内容。"""
    
    def llm_result_parser(response):
        import json
        try:
            data = json.loads(response)
            return InferenceResult(
                value=data,
                confidence=0.95,
                level=InferenceLevel.LLM,
                metadata={'method': 'llm_analysis'}
            )
        except:
            return InferenceResult(
                value={'type': 'neutral', 'intensity': 0.5},
                confidence=0.5,
                level=InferenceLevel.LLM
            )
    
    # 创建级联引擎
    engine = CascadeInferenceEngine(
        confidence_threshold=0.7,  # 低于此值会级联到下一层
        enable_cache=True,
        fallback_strategy="cascade"
    )
    
    # 添加推理层级
    engine.add_level(create_rule_level(rule_emotion, name="Rule Emotion"))
    
    if llm.is_configured():
        engine.add_level(
            create_llm_level(llm, llm_prompt_builder, llm_result_parser, name="LLM Emotion")
        )
    
    # 测试不同的文本
    test_texts = [
        "今天天气真好，我很开心！",
        "这件事让我很难过。",
        "今天去了超市买东西。",  # 中性文本，会触发级联
    ]
    
    for text in test_texts:
        print(f"\n文本: {text}")
        try:
            result = await engine.infer(text, context={})
            print(f"情绪类型: {result.value['type']}")
            print(f"情绪强度: {result.value['intensity']}")
            print(f"置信度: {result.confidence:.2f}")
            print(f"推理层级: {result.level.value}")
            print(f"元数据: {result.metadata}")
        except Exception as e:
            print(f"推理失败: {e}")
    
    # 统计信息
    print(f"\n引擎统计: {engine.get_statistics()}")


# ==================== 示例 3: 自定义推理层级 ====================

async def example_custom_inference_level():
    """演示如何创建自定义推理层级"""
    print("\n" + "=" * 50)
    print("示例 3: 自定义推理层级")
    print("=" * 50)
    
    # 方法 1: 继承 InferenceLevelBase
    class CustomInferenceLevel(InferenceLevelBase):
        """自定义推理层级"""
        
        def __init__(self, name: str):
            self.name = name
        
        async def infer(self, input_data, context):
            # 实现自定义推理逻辑
            result = f"Processed by {self.name}: {input_data}"
            return InferenceResult(
                value=result,
                confidence=0.9,
                level=InferenceLevel.FAST_MODEL,
                metadata={'custom_level': True}
            )
        
        def get_level(self):
            return InferenceLevel.FAST_MODEL
        
        def get_name(self):
            return self.name
    
    # 创建引擎并添加自定义层级
    engine = CascadeInferenceEngine()
    engine.add_level(CustomInferenceLevel(name="My Custom Level"))
    
    # 测试
    result = await engine.infer("test input", context={})
    print(f"结果: {result.value}")
    print(f"层级: {result.level.value}")


# ==================== 示例 4: 集成推理模式 ====================

async def example_ensemble_inference():
    """演示集成推理模式"""
    print("\n" + "=" * 50)
    print("示例 4: 集成推理模式")
    print("=" * 50)
    
    def level_a(text, context):
        return InferenceResult(
            value="Result A",
            confidence=0.7,
            level=InferenceLevel.RULE
        )
    
    def level_b(text, context):
        return InferenceResult(
            value="Result B",
            confidence=0.9,  # 更高的置信度
            level=InferenceLevel.FAST_MODEL
        )
    
    # 创建集成模式引擎
    engine = CascadeInferenceEngine(
        fallback_strategy="ensemble"  # 使用集成模式
    )
    
    engine.add_level(create_rule_level(level_a, name="Level A"))
    engine.add_level(create_rule_level(level_b, name="Level B"))
    
    # 执行推理（会选择置信度最高的结果）
    result = await engine.infer("test", context={})
    print(f"最佳结果: {result.value}")
    print(f"置信度: {result.confidence}")
    print(f"来自层级: {result.level.value}")


# ==================== 主函数 ====================

async def main():
    """运行所有示例"""
    print("Foundation Layer 使用示例")
    print("=" * 50)
    
    # 示例 1: LLM 调用器
    await example_llm_caller()
    
    # 示例 2: 级联推理引擎
    await example_cascade_inference()
    
    # 示例 3: 自定义推理层级
    await example_custom_inference_level()
    
    # 示例 4: 集成推理模式
    await example_ensemble_inference()
    
    print("\n" + "=" * 50)
    print("所有示例运行完成！")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
