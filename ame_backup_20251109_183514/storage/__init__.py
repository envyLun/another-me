"""
AME Storage Module (兼容层)

该模块为了向后兼容，导出 foundation.storage 的类。
新代码请直接使用: from ame.foundation.storage import ...
"""
from ame.foundation.storage import (
    VectorStore as FaissStore,  # 兼容别名
    GraphStore as FalkorStore,   # 兼容别名
    MetadataStore,
    DocumentStore,
)

__all__ = [
    "MetadataStore",
    "FaissStore",     # 旧名称
    "FalkorStore",    # 旧名称
    "DocumentStore",
]
