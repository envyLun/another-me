"""
AME 引擎层
场景引擎 + 核心引擎协同架构
"""
from ame.engines.work_engine import WorkEngine
from ame.engines.life_engine import LifeEngine

__all__ = [
    "WorkEngine",
    "LifeEngine",
]
