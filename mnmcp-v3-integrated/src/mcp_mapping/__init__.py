"""
MnMCP Mapping Module
方块、物品、生物映射
"""

# 先使用之前的 blocks_integrated
from .blocks_integrated import BlockMapperIntegrated, BlockMapping, BlockCategory

__all__ = ['BlockMapperIntegrated', 'BlockMapping', 'BlockCategory']