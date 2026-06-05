#!/usr/bin/env python3
"""
提取 MN2MC 的完整方块映射
生成高质量的整合版映射文件
"""

import re
from pathlib import Path
from typing import Dict, Tuple

def extract_mn2mc_mappings():
    """从 MN2MC blocks.py 提取映射"""
    
    # 读取源文件
    source_path = Path(r"C:\Users\Sails\Downloads\Official-MN2MC\MN2MC-main\mn2mc\mapping\blocks.py")
    
    if not source_path.exists():
        print(f"错误: 找不到源文件 {source_path}")
        return
    
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 mc_to_mini_mapping 字典
    # 查找 mc_to_mini_mapping = { ... } 部分
    pattern = r'mc_to_mini_mapping\s*=\s*\{(.*?)\n\}'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("错误: 找不到 mc_to_mini_mapping 字典")
        return
    
    dict_content = match.group(1)
    
    # 提取每个条目
    # 格式: id: id, # name - chinese_name
    entry_pattern = r'(\d+):\s*(\d+),\s*#\s*([^\-]+)\s*-\s*(.+)'
    entries = re.findall(entry_pattern, dict_content)
    
    print(f"提取了 {len(entries)} 个映射条目")
    
    # 生成输出文件
    output = '''#!/usr/bin/env python3
"""
MnMCP v3 Integrated - 完整方块映射
自动生成于 MN2MC blocks.py
共 {count} 个映射

特点:
1. 使用 MN2MC 的真实迷你世界方块ID
2. 完整中文名称支持
3. MnMCP 3 的高质量架构
"""

from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class MCPBlockMapping:
    """方块映射数据"""
    mc_id: int
    mc_name: str
    mnw_id: int
    mnw_name: str


# MC ID → (MNW ID, MC Name, MNW Name)
MC_TO_MNW_FULL_MAPPING: Dict[int, Tuple[int, str, str]] = {{
'''
    
    # 添加映射条目
    for i, (mc_id, mnw_id, mc_name, mnw_name) in enumerate(entries):
        mc_name = mc_name.strip()
        mnw_name = mnw_name.strip()
        output += f"    {mc_id}: ({mnw_id}, '{mc_name}', '{mnw_name}'),  # {mc_name} → {mnw_name}\n"
    
    output += '''}}


class MCPBlockMapper:
    """高质量方块映射器"""
    
    def __init__(self):
        self._mc_to_mnw: Dict[int, int] = {{}}
        self._mnw_to_mc: Dict[int, int] = {{}}
        self._mappings: Dict[int, MCPBlockMapping] = {{}}
        
        self._load_mappings()
    
    def _load_mappings(self):
        """加载映射"""
        for mc_id, (mnw_id, mc_name, mnw_name) in MC_TO_MNW_FULL_MAPPING.items():
            self._mc_to_mnw[mc_id] = mnw_id
            self._mnw_to_mc[mnw_id] = mc_id
            self._mappings[mc_id] = MCPBlockMapping(
                mc_id=mc_id,
                mc_name=mc_name,
                mnw_id=mnw_id,
                mnw_name=mnw_name
            )
    
    def map_mc_to_mnw(self, mc_id: int) -> int:
        """MC ID → MNW ID"""
        return self._mc_to_mnw.get(mc_id, 104)  # 默认岩石
    
    def map_mnw_to_mc(self, mnw_id: int) -> int:
        """MNW ID → MC ID"""
        return self._mnw_to_mc.get(mnw_id, 1)  # 默认石头
    
    def get_mapping(self, mc_id: int) -> Optional[MCPBlockMapping]:
        """获取完整映射信息"""
        return self._mappings.get(mc_id)
    
    def get_stats(self) -> dict:
        """获取统计"""
        return {{
            'total_mappings': len(self._mappings),
            'mc_to_mnw': len(self._mc_to_mnw),
            'mnw_to_mc': len(self._mnw_to_mc)
        }}


# 全局实例
_block_mapper: Optional[MCPBlockMapper] = None

def get_block_mapper() -> MCPBlockMapper:
    """获取全局实例"""
    global _block_mapper
    if _block_mapper is None:
        _block_mapper = MCPBlockMapper()
    return _block_mapper


if __name__ == "__main__":
    mapper = MCPBlockMapper()
    stats = mapper.get_stats()
    print(f"方块映射加载完成:")
    print(f"  总映射数: {stats['total_mappings']}")
    print(f"  MC→MNW: {stats['mc_to_mnw']}")
    print(f"  MNW→MC: {stats['mnw_to_mc']}")
    
    # 测试几个
    test_ids = [1, 8, 49, 100]
    print("\\n映射测试:")
    for mc_id in test_ids:
        mapping = mapper.get_mapping(mc_id)
        if mapping:
            print(f"  MC {mc_id} ({mapping.mc_name}) → MNW {mapping.mnw_id} ({mapping.mnw_name})")
'''
    
    # 替换计数 (需要在输出字符串中保留 {count} 占位符)
    output = output.replace('{count}', str(len(entries)))
    
    # 写入文件
    output_path = Path(__file__).parent / "src" / "mcp_mapping" / "blocks_full.py"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"✓ 已生成: {output_path}")
    print(f"✓ 包含 {len(entries)} 个方块映射")


if __name__ == "__main__":
    extract_mn2mc_mappings()