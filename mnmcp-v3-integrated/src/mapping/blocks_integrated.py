#!/usr/bin/env python3
"""
MnMCP v3 Integrated - 方块映射系统
整合 MN2MC 的真实映射 + MnMCP 3 的高质量架构

特点:
1. 使用 MN2MC 的真实迷你世界方块ID
2. MnMCP 3 的高质量代码结构
3. 双向映射支持
4. 中文名称支持
5. 属性映射支持
"""

import json
import logging
from typing import Dict, Tuple, Optional, Set, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import IntEnum

logger = logging.getLogger(__name__)


class BlockCategory(IntEnum):
    """方块分类"""
    NATURAL = 0      # 自然方块
    BUILDING = 1     # 建筑方块
    DECORATION = 2   # 装饰方块
    REDSTONE = 3     # 红石方块
    TRANSPORT = 4    # 运输方块
    PLANT = 5        # 植物
    ORE = 6          # 矿石
    FLUID = 7        # 流体
    SPECIAL = 8      # 特殊方块


@dataclass
class BlockProperties:
    """方块属性"""
    hardness: float = 0.0
    blast_resistance: float = 0.0
    transparent: bool = False
    luminous: int = 0  # 光照等级
    gravity: bool = False
    flammable: bool = False


@dataclass
class BlockMapping:
    """
    方块映射数据 - 高质量版本
    
    整合:
    - MN2MC 的真实迷你世界ID
    - MnMCP 3 的架构质量
    - 完整的中文名称
    - 方块属性
    """
    # Minecraft
    mc_id: int
    mc_name: str
    mc_registry: str
    
    # MiniWorld
    mnw_id: int
    mnw_name: str
    
    # 元数据
    category: BlockCategory = BlockCategory.NATURAL
    properties: BlockProperties = field(default_factory=BlockProperties)
    verified: bool = True
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'mc_id': self.mc_id,
            'mc_name': self.mc_name,
            'mc_registry': self.mc_registry,
            'mnw_id': self.mnw_id,
            'mnw_name': self.mnw_name,
            'category': self.category.name,
            'properties': asdict(self.properties),
            'verified': self.verified
        }


# MN2MC 的真实方块映射数据
# 来源: MN2MC blocks.py (基于迷你世界官方ID)
MC_TO_MNW_MAPPING = {
    0: (0, "空气", "air"),
    1: (104, "岩石", "stone"),
    2: (104, "岩石", "granite"),
    3: (505, "碎石块", "polished_granite"),
    4: (104, "岩石", "diorite"),
    5: (505, "碎石块", "polished_diorite"),
    6: (104, "岩石", "andesite"),
    7: (505, "碎石块", "polished_andesite"),
    8: (100, "长草土块", "grass_block"),
    9: (101, "土块", "dirt"),
    10: (101, "土块", "coarse_dirt"),
    11: (233, "红土", "podzol"),
    12: (502, "裂纹石砖", "cobblestone"),
    13: (206, "木板", "oak_planks"),
    14: (206, "木板", "spruce_planks"),
    15: (207, "秋叶橙木板", "birch_planks"),
    16: (209, "海棠红木板", "jungle_planks"),
    17: (210, "落日橙木板", "acacia_planks"),
    18: (562, "胭脂红木板", "cherry_planks"),
    19: (211, "深栗红木板", "dark_oak_planks"),
    22: (206, "木板", "mangrove_planks"),
    23: (251, "竹子", "bamboo_planks"),
    34: (1, "地心基石", "bedrock"),
    35: (3, "静态水", "water"),
    36: (5, "静态岩浆", "lava"),
    37: (106, "黄沙", "sand"),
    39: (128, "红沙", "red_sand"),
    40: (107, "碎石堆", "gravel"),
    42: (408, "钨金块", "gold_ore"),
    43: (408, "钨金块", "deepslate_gold_ore"),
    44: (456, "黄铜块", "iron_ore"),
    45: (456, "黄铜块", "deepslate_iron_ore"),
    46: (402, "凝能矿", "coal_ore"),
    47: (402, "凝能矿", "deepslate_coal_ore"),
    48: (132, "硫黄晶砂", "nether_gold_ore"),
    49: (200, "樱桃木", "oak_log"),
    50: (201, "落叶松木", "spruce_log"),
    51: (202, "白杨木", "birch_log"),
    52: (203, "红杉木", "jungle_log"),
    53: (205, "核桃木", "acacia_log"),
    54: (254, "桃花木", "cherry_log"),
    55: (205, "核桃木", "dark_oak_log"),
    57: (386, "香蕉树干", "mangrove_log"),
    60: (563, "竹板", "bamboo_block"),
    61: (201, "落叶松木", "stripped_spruce_log"),
    62: (202, "白杨木", "stripped_birch_log"),
    63: (203, "红杉木", "stripped_jungle_log"),
    64: (205, "核桃木", "stripped_acacia_log"),
    65: (254, "桃花木", "stripped_cherry_log"),
    66: (205, "核桃木", "stripped_dark_oak_log"),
    68: (200, "樱桃木", "stripped_oak_log"),
    69: (386, "香蕉树干", "stripped_mangrove_log"),
    71: (200, "樱桃木", "oak_wood"),
    72: (201, "落叶松木", "spruce_wood"),
    73: (202, "白杨木", "birch_wood"),
    74: (203, "红杉木", "jungle_wood"),
}


class BlockMapperIntegrated:
    """
    整合版方块映射器
    
    结合:
    - MN2MC 的真实迷你世界ID
    - MnMCP 3 的高质量架构
    
    功能:
    1. MC ID → MNW ID (使用真实迷你世界ID)
    2. MNW ID → MC ID
    3. 名称查找
    4. 分类查询
    5. 属性查询
    """
    
    def __init__(self):
        # 核心映射存储
        self._mc_to_mnw: Dict[int, int] = {}
        self._mnw_to_mc: Dict[int, int] = {}
        self._mappings: Dict[int, BlockMapping] = {}
        
        # 名称索引
        self._mc_name_to_id: Dict[str, int] = {}
        self._mnw_name_to_id: Dict[str, int] = {}
        
        # 分类索引
        self._category_index: Dict[BlockCategory, List[int]] = {}
        
        # 未映射统计
        self._unmapped_mc: Set[int] = set()
        self._unmapped_mnw: Set[int] = set()
        
        # 加载映射
        self._load_mappings()
        
        logger.info(f"整合版方块映射器初始化完成，已加载 {len(self._mappings)} 个映射")
    
    def _load_mappings(self):
        """加载映射数据"""
        # 加载核心映射
        for mc_id, (mnw_id, mnw_name, mc_name) in MC_TO_MNW_MAPPING.items():
            self._add_mapping(mc_id, mnw_id, mc_name, mnw_name)
        
        logger.info(f"从 MN2MC 加载了 {len(MC_TO_MNW_MAPPING)} 个核心映射")
    
    def _add_mapping(self, mc_id: int, mnw_id: int, mc_name: str, mnw_name: str):
        """添加单个映射"""
        # 核心映射
        self._mc_to_mnw[mc_id] = mnw_id
        self._mnw_to_mc[mnw_id] = mc_id
        
        # 构建完整映射对象
        mapping = BlockMapping(
            mc_id=mc_id,
            mc_name=mc_name,
            mc_registry=f"minecraft:{mc_name}",
            mnw_id=mnw_id,
            mnw_name=mnw_name,
            category=self._infer_category(mc_name),
            properties=self._infer_properties(mc_name)
        )
        self._mappings[mc_id] = mapping
        
        # 名称索引
        self._mc_name_to_id[mc_name] = mc_id
        self._mnw_name_to_id[mnw_name] = mnw_id
        
        # 分类索引
        if mapping.category not in self._category_index:
            self._category_index[mapping.category] = []
        self._category_index[mapping.category].append(mc_id)
    
    def _infer_category(self, mc_name: str) -> BlockCategory:
        """推断方块分类"""
        name_lower = mc_name.lower()
        
        if any(w in name_lower for w in ['ore', 'gold', 'iron', 'coal', 'diamond']):
            return BlockCategory.ORE
        if any(w in name_lower for w in ['planks', 'stone', 'brick']):
            return BlockCategory.BUILDING
        if any(w in name_lower for w in ['log', 'wood', 'leaves', 'sapling']):
            return BlockCategory.PLANT
        if any(w in name_lower for w in ['water', 'lava']):
            return BlockCategory.FLUID
        if any(w in name_lower for w in ['redstone', 'button', 'lever']):
            return BlockCategory.REDSTONE
        
        return BlockCategory.NATURAL
    
    def _infer_properties(self, mc_name: str) -> BlockProperties:
        """推断方块属性"""
        name_lower = mc_name.lower()
        
        # 默认值
        hardness = 1.0
        blast_resistance = 1.0
        transparent = False
        luminous = 0
        
        # 根据名称推断
        if 'ore' in name_lower:
            hardness = 3.0
            blast_resistance = 3.0
        elif 'stone' in name_lower or 'brick' in name_lower:
            hardness = 1.5
            blast_resistance = 6.0
        elif 'planks' in name_lower or 'log' in name_lower:
            hardness = 2.0
            blast_resistance = 3.0
            flammable = True
        elif 'leaves' in name_lower:
            hardness = 0.2
            blast_resistance = 0.2
            transparent = True
            flammable = True
        elif 'glass' in name_lower:
            hardness = 0.3
            blast_resistance = 0.3
            transparent = True
        elif 'water' in name_lower or 'lava' in name_lower:
            transparent = True
        
        return BlockProperties(
            hardness=hardness,
            blast_resistance=blast_resistance,
            transparent=transparent,
            luminous=luminous
        )
    
    # ============== 核心映射方法 ==============
    
    def mc_to_mnw(self, mc_id: int) -> int:
        """
        Minecraft ID → MiniWorld ID
        使用 MN2MC 的真实迷你世界ID
        """
        if mc_id in self._mc_to_mnw:
            return self._mc_to_mnw[mc_id]
        
        # 记录未映射
        if mc_id not in self._unmapped_mc:
            self._unmapped_mc.add(mc_id)
            logger.debug(f"未映射的 MC 方块 ID: {mc_id}")
        
        # 默认返回岩石 (104)
        return 104
    
    def mnw_to_mc(self, mnw_id: int) -> int:
        """MiniWorld ID → Minecraft ID"""
        if mnw_id in self._mnw_to_mc:
            return self._mnw_to_mc[mnw_id]
        
        # 记录未映射
        if mnw_id not in self._unmapped_mnw:
            self._unmapped_mnw.add(mnw_id)
            logger.debug(f"未映射的 MNW 方块 ID: {mnw_id}")
        
        # 默认返回石头 (1)
        return 1
    
    # ============== 查询方法 ==============
    
    def get_by_mc_name(self, name: str) -> Optional[BlockMapping]:
        """通过 MC 名称查找"""
        mc_id = self._mc_name_to_id.get(name)
        if mc_id:
            return self._mappings.get(mc_id)
        return None
    
    def get_by_mnw_name(self, name: str) -> Optional[BlockMapping]:
        """通过 MNW 名称查找"""
        mnw_id = self._mnw_name_to_id.get(name)
        if mnw_id:
            mc_id = self._mnw_to_mc.get(mnw_id)
            if mc_id:
                return self._mappings.get(mc_id)
        return None
    
    def get_by_category(self, category: BlockCategory) -> List[BlockMapping]:
        """通过分类查找"""
        mc_ids = self._category_index.get(category, [])
        return [self._mappings[mc_id] for mc_id in mc_ids if mc_id in self._mappings]
    
    def get_mapping(self, mc_id: int) -> Optional[BlockMapping]:
        """获取完整映射信息"""
        return self._mappings.get(mc_id)
    
    # ============== 统计方法 ==============
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total_mappings': len(self._mappings),
            'mc_to_mnw_mappings': len(self._mc_to_mnw),
            'mnw_to_mc_mappings': len(self._mnw_to_mc),
            'unmapped_mc_ids': len(self._unmapped_mc),
            'unmapped_mnw_ids': len(self._unmapped_mnw),
            'categories': {
                cat.name: len(ids)
                for cat, ids in self._category_index.items()
            }
        }
    
    def print_sample(self, count: int = 10):
        """打印样本映射"""
        print(f"\n方块映射样本 (前{count}个):")
        print("-" * 80)
        print(f"{'MC ID':<8} {'MC 名称':<25} {'→':<3} {'MNW ID':<8} {'MNW 名称':<20}")
        print("-" * 80)
        
        for i, (mc_id, mapping) in enumerate(self._mappings.items()):
            if i >= count:
                break
            print(f"{mapping.mc_id:<8} {mapping.mc_name:<25} → {mapping.mnw_id:<8} {mapping.mnw_name:<20}")
        
        print("-" * 80)


# 全局映射器实例
_block_mapper: Optional[BlockMapperIntegrated] = None


def get_block_mapper() -> BlockMapperIntegrated:
    """获取全局方块映射器实例"""
    global _block_mapper
    if _block_mapper is None:
        _block_mapper = BlockMapperIntegrated()
    return _block_mapper


if __name__ == "__main__":
    # 测试
    mapper = BlockMapperIntegrated()
    
    print("=" * 60)
    print(" MnMCP v3 Integrated - 方块映射测试 ".center(60))
    print("=" * 60)
    
    # 打印样本
    mapper.print_sample(15)
    
    # 测试映射
    print("\n映射测试:")
    test_ids = [1, 8, 49, 200]
    for mc_id in test_ids:
        mnw_id = mapper.mc_to_mnw(mc_id)
        mapping = mapper.get_mapping(mc_id)
        if mapping:
            print(f"  MC {mc_id} ({mapping.mc_name}) → MNW {mnw_id} ({mapping.mnw_name})")
        else:
            print(f"  MC {mc_id} → MNW {mnw_id}")
    
    # 统计
    print("\n统计:")
    stats = mapper.get_stats()
    print(f"  总映射数: {stats['total_mappings']}")
    print(f"  分类分布:")
    for cat, count in stats['categories'].items():
        print(f"    {cat}: {count}")
