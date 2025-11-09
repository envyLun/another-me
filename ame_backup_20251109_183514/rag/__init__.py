"""
RAG (Retrieval-Augmented Generation) 模块 (兼容层)

该模块为了向后兼容，导出 capabilities.generation 的类。
新代码请直接使用: from ame.capabilities.generation import RAGGenerator
"""

from .knowledge_base import KnowledgeBase

__all__ = [
    'KnowledgeBase',
]
