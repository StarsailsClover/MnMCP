#!/usr/bin/env python3
"""
从MN2MC和blockdef.csv提取完整方块映射

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import sys
import csv
from pathlib import Path

MN2MC_BLOCKS_PATH = Path(r"C:\Users\Sails\Downloads\Official-MN2MC\MN2MC-main\mn2mc\mapping\blocks.py")
BLOCKDEF_CSV_PATH = Path(r"C:\Users\Sails\Documents\Workspace\NormalWorkspace\Coding\MnMCP\09-MnMCP-DevResources\MnMCPResources\csvdef\utf8\blockdef.csv")
OUTPUT_PATH = Path(r"C:\Users\Sails\Documents\Workspace\NormalWorkspace\Coding\MnMCP\src\mcp_mapping\blocks_full.py")


def load_mn2mc_mapping():
    """加载MN2MC的方块映射"""
    with open(MN2MC_BLOCKS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    mapping = {}
    in_mapping = False
    for line in content.split('\n'):
        if 'mc_to_mini_mapping = {' in line:
            in_mapping = True
            continue
        if in_mapping:
            if line.strip() == '}' or line.strip().startswith('old_mc_to_mini_mapping'):
                break
            if ':' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    try:
                        mc_id = int(parts[0].strip())
                        mnw_id_part = parts[1].strip()
                        mnw_id = int(mnw_id_part.split('#')[0].strip().rstrip(','))
                        mapping[mc_id] = mnw_id
                    except (ValueError, IndexError):
                        continue
    return mapping


def load_blockdef_names():
    """加载blockdef.csv中的方块名称"""
    names = {}
    with open(BLOCKDEF_CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        headers = next(reader)
        for row in reader:
            if len(row) >= 2:
                try:
                    block_id = int(row[0])
                    block_name = row[1]
                    names[block_id] = block_name
                except ValueError:
                    continue
    return names


def load_mc_block_names():
    """加载Minecraft方块名称"""
    mc_names = {}
    csv_path = Path(r"C:\Users\Sails\Documents\Workspace\NormalWorkspace\Coding\MnMCP\09-MnMCP-DevResources\MnMCPResources\csvdef\utf8\mc_block.csv")
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) >= 2:
                    try:
                        mc_id = int(row[0])
                        mc_name = row[1]
                        mc_names[mc_id] = mc_name
                    except ValueError:
                        continue
    return mc_names


def generate_output(mapping, mnw_names, mc_names):
    """生成输出文件内容"""
    lines = []
    lines.append('#!/usr/bin/env python3')
    lines.append('"""')
    lines.append('MnMCP v3 Integrated - 完整方块映射')
    lines.append(f'自动生成于 MN2MC blocks.py')
    lines.append(f'共 {len(mapping)} 个映射')
    lines.append('')
    lines.append('特点:')
    lines.append('1. 使用 MN2MC 的真实迷你世界方块ID')
    lines.append('2. 完整中文名称支持')
    lines.append('3. MnMCP 3 的高质量架构')
    lines.append('4. 双向映射支持')
    lines.append('"""')
    lines.append('')
    lines.append('from typing import Dict, Tuple, Optional, List')
    lines.append('from dataclasses import dataclass')
    lines.append('')
    lines.append('')
    lines.append('@dataclass')
    lines.append('class MCPBlockMapping:')
    lines.append('    mc_id: int')
    lines.append('    mc_name: str')
    lines.append('    mnw_id: int')
    lines.append('    mnw_name: str')
    lines.append('')
    lines.append('')
    lines.append('# MC ID → (MNW ID, MC Name, MNW Name)')
    lines.append('MC_TO_MNW_FULL_MAPPING: Dict[int, Tuple[int, str, str]] = {')
    
    for mc_id in sorted(mapping.keys()):
        mnw_id = mapping[mc_id]
        mc_name = mc_names.get(mc_id, 'unknown')
        mnw_name = mnw_names.get(mnw_id, '未知')
        lines.append(f"    {mc_id}: ({mnw_id}, '{mc_name}', '{mnw_name}'),")
    
    lines.append('}')
    lines.append('')
    lines.append('')
    lines.append('# MNW ID → (MC ID, MC Name, MNW Name)')
    lines.append('MNW_TO_MC_FULL_MAPPING: Dict[int, Tuple[int, str, str]] = {')
    
    mnw_to_mc = {}
    for mc_id, mnw_id in mapping.items():
        if mnw_id not in mnw_to_mc:
            mnw_to_mc[mnw_id] = mc_id
    
    for mnw_id in sorted(mnw_to_mc.keys()):
        mc_id = mnw_to_mc[mnw_id]
        mc_name = mc_names.get(mc_id, 'unknown')
        mnw_name = mnw_names.get(mnw_id, '未知')
        lines.append(f"    {mnw_id}: ({mc_id}, '{mc_name}', '{mnw_name}'),")
    
    lines.append('}')
    lines.append('')
    lines.append('')
    lines.append('# MNW ID → [MC IDs] (一对多映射)')
    lines.append('MNW_TO_MC_MULTI_MAPPING: Dict[int, List[int]] = {')
    
    mnw_to_mc_multi = {}
    for mc_id, mnw_id in mapping.items():
        if mnw_id not in mnw_to_mc_multi:
            mnw_to_mc_multi[mnw_id] = []
        mnw_to_mc_multi[mnw_id].append(mc_id)
    
    for mnw_id in sorted(mnw_to_mc_multi.keys()):
        mc_ids = mnw_to_mc_multi[mnw_id]
        lines.append(f"    {mnw_id}: {mc_ids},")
    
    lines.append('}')
    lines.append('')
    lines.append('')
    lines.append('# MC名称 → MC ID')
    lines.append('MC_NAME_TO_ID: Dict[str, int] = {')
    
    for mc_id, name in sorted(mc_names.items()):
        lines.append(f"    '{name}': {mc_id},")
    
    lines.append('}')
    lines.append('')
    lines.append('')
    lines.append('# MNW名称 → MNW ID')
    lines.append('MNW_NAME_TO_ID: Dict[str, int] = {')
    
    for mnw_id, name in sorted(mnw_names.items()):
        lines.append(f"    '{name}': {mnw_id},")
    
    lines.append('}')
    lines.append('')
    lines.append('')
    lines.append('def mc_to_mnw(mc_id: int) -> Optional[Tuple[int, str, str]]:')
    lines.append('    """')
    lines.append('    MC方块ID → MNW方块信息')
    lines.append('')
    lines.append('    Args:')
    lines.append('        mc_id: Minecraft方块ID')
    lines.append('')
    lines.append('    Returns:')
    lines.append('        (mnw_id, mc_name, mnw_name) 或 None')
    lines.append('    """')
    lines.append('    return MC_TO_MNW_FULL_MAPPING.get(mc_id)')
    lines.append('')
    lines.append('')
    lines.append('def mnw_to_mc(mnw_id: int) -> Optional[Tuple[int, str, str]]:')
    lines.append('    """')
    lines.append('    MNW方块ID → MC方块信息')
    lines.append('')
    lines.append('    Args:')
    lines.append('        mnw_id: MiniWorld方块ID')
    lines.append('')
    lines.append('    Returns:')
    lines.append('        (mc_id, mc_name, mnw_name) 或 None')
    lines.append('    """')
    lines.append('    return MNW_TO_MC_FULL_MAPPING.get(mnw_id)')
    lines.append('')
    lines.append('')
    lines.append('def mnw_to_mc_multi(mnw_id: int) -> Optional[List[int]]:')
    lines.append('    """')
    lines.append('    MNW方块ID → 所有对应的MC方块ID列表')
    lines.append('')
    lines.append('    Args:')
    lines.append('        mnw_id: MiniWorld方块ID')
    lines.append('')
    lines.append('    Returns:')
    lines.append('        MC方块ID列表 或 None')
    lines.append('    """')
    lines.append('    return MNW_TO_MC_MULTI_MAPPING.get(mnw_id)')
    lines.append('')
    lines.append('')
    lines.append('def mc_name_to_id(name: str) -> Optional[int]:')
    lines.append('    """')
    lines.append('    MC方块名称 → MC方块ID')
    lines.append('')
    lines.append('    Args:')
    lines.append('        name: Minecraft方块名称')
    lines.append('')
    lines.append('    Returns:')
    lines.append('        MC方块ID 或 None')
    lines.append('    """')
    lines.append('    return MC_NAME_TO_ID.get(name.lower())')
    lines.append('')
    lines.append('')
    lines.append('def mnw_name_to_id(name: str) -> Optional[int]:')
    lines.append('    """')
    lines.append('    MNW方块名称 → MNW方块ID')
    lines.append('')
    lines.append('    Args:')
    lines.append('        name: MiniWorld方块名称')
    lines.append('')
    lines.append('    Returns:')
    lines.append('        MNW方块ID 或 None')
    lines.append('    """')
    lines.append('    return MNW_NAME_TO_ID.get(name)')
    lines.append('')
    lines.append('')
    lines.append('def mc_name_to_mnw(name: str) -> Optional[Tuple[int, str, str]]:')
    lines.append('    """')
    lines.append('    MC方块名称 → MNW方块信息')
    lines.append('')
    lines.append('    Args:')
    lines.append('        name: Minecraft方块名称')
    lines.append('')
    lines.append('    Returns:')
    lines.append('        (mnw_id, mc_name, mnw_name) 或 None')
    lines.append('    """')
    lines.append('    mc_id = mc_name_to_id(name)')
    lines.append('    if mc_id is not None:')
    lines.append('        return mc_to_mnw(mc_id)')
    lines.append('    return None')
    lines.append('')
    lines.append('')
    lines.append('def mnw_name_to_mc(name: str) -> Optional[Tuple[int, str, str]]:')
    lines.append('    """')
    lines.append('    MNW方块名称 → MC方块信息')
    lines.append('')
    lines.append('    Args:')
    lines.append('        name: MiniWorld方块名称')
    lines.append('')
    lines.append('    Returns:')
    lines.append('        (mc_id, mc_name, mnw_name) 或 None')
    lines.append('    """')
    lines.append('    mnw_id = mnw_name_to_id(name)')
    lines.append('    if mnw_id is not None:')
    lines.append('        return mnw_to_mc(mnw_id)')
    lines.append('    return None')
    lines.append('')
    lines.append('')
    lines.append('def get_mc_block_name(mc_id: int) -> str:')
    lines.append('    """')
    lines.append('    获取MC方块名称')
    lines.append('')
    lines.append('    Args:')
    lines.append('        mc_id: MC方块ID')
    lines.append('')
    lines.append('    Returns:')
    lines.append('        方块名称')
    lines.append('    """')
    lines.append('    mapping = mc_to_mnw(mc_id)')
    lines.append('    if mapping:')
    lines.append('        return mapping[1]')
    lines.append('    return f"unknown_{mc_id}"')
    lines.append('')
    lines.append('')
    lines.append('def get_mnw_block_name(mnw_id: int) -> str:')
    lines.append('    """')
    lines.append('    获取MNW方块名称')
    lines.append('')
    lines.append('    Args:')
    lines.append('        mnw_id: MNW方块ID')
    lines.append('')
    lines.append('    Returns:')
    lines.append('        方块名称')
    lines.append('    """')
    lines.append('    mapping = mnw_to_mc(mnw_id)')
    lines.append('    if mapping:')
    lines.append('        return mapping[2]')
    lines.append('    return f"未知_{mnw_id}"')
    lines.append('')
    lines.append('')
    lines.append('def convert_mc_block(mc_id: int) -> int:')
    lines.append('    """')
    lines.append('    转换MC方块ID为MNW方块ID')
    lines.append('')
    lines.append('    Args:')
    lines.append('        mc_id: MC方块ID')
    lines.append('')
    lines.append('    Returns:')
    lines.append('        MNW方块ID，如果没有映射则返回0')
    lines.append('    """')
    lines.append('    mapping = mc_to_mnw(mc_id)')
    lines.append('    if mapping:')
    lines.append('        return mapping[0]')
    lines.append('    return 0')
    lines.append('')
    lines.append('')
    lines.append('def convert_mnw_block(mnw_id: int) -> int:')
    lines.append('    """')
    lines.append('    转换MNW方块ID为MC方块ID')
    lines.append('')
    lines.append('    Args:')
    lines.append('        mnw_id: MNW方块ID')
    lines.append('')
    lines.append('    Returns:')
    lines.append('        MC方块ID，如果没有映射则返回0')
    lines.append('    """')
    lines.append('    mapping = mnw_to_mc(mnw_id)')
    lines.append('    if mapping:')
    lines.append('        return mapping[0]')
    lines.append('    return 0')
    lines.append('')
    lines.append('')
    lines.append('if __name__ == "__main__":')
    lines.append('    print(f"总映射数: {len(MC_TO_MNW_FULL_MAPPING)}")')
    lines.append('    print(f"MNW唯一方块数: {len(MNW_TO_MC_FULL_MAPPING)}")')
    lines.append('    print(f"MNW一对多映射数: {len(MNW_TO_MC_MULTI_MAPPING)}")')
    lines.append('    print(f"MC名称数: {len(MC_NAME_TO_ID)}")')
    lines.append('    print(f"MNW名称数: {len(MNW_NAME_TO_ID)}")')
    
    return '\n'.join(lines)


def main():
    print("加载MN2MC映射...")
    mn2mc_mapping = load_mn2mc_mapping()
    print(f"  MN2MC映射数: {len(mn2mc_mapping)}")
    
    print("加载blockdef名称...")
    mnw_names = load_blockdef_names()
    print(f"  MNW名称数: {len(mnw_names)}")
    
    print("加载MC方块名称...")
    mc_names = load_mc_block_names()
    print(f"  MC名称数: {len(mc_names)}")
    
    print("生成输出文件...")
    output_content = generate_output(mn2mc_mapping, mnw_names, mc_names)
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"  输出文件: {OUTPUT_PATH}")
    print(f"  总映射数: {len(mn2mc_mapping)}")
    print("✓ 方块映射更新完成")


if __name__ == "__main__":
    main()