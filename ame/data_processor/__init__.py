# Data Processor Module - 兼容层
# 注意: 
#   - TextProcessor 已迁移到 foundation.utils.TextProcessor
#   - DocumentProcessor 保留在此（专门用于文档预处理：NER + Embedding）

from ame.foundation.utils import TextProcessor
from .document_processor import DocumentProcessor

# 兼容性别名
DataProcessor = TextProcessor

__all__ = [
    "DataProcessor",
    "TextProcessor",
    "DocumentProcessor",
]
