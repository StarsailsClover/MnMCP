#!/usr/bin/env python3
"""测试方块映射"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_mapping.blocks_full import MCPBlockMapper

mapper = MCPBlockMapper()
stats = mapper.get_stats()

print("=" * 60)
print(" MnMCP v3 Integrated - 方块映射测试 ".center(60))
print("=" * 60)
print(f"\n✓ 方块映射加载成功!")
print(f"  总映射数: {stats['total_mappings']}")
print(f"  MC→MNW: {stats['mc_to_mnw']}")
print(f"  MNW→MC: {stats['mnw_to_mc']}")

# 测试映射
print("\n映射测试:")
test_ids = [1, 8, 49, 100]
for mc_id in test_ids:
    m = mapper.get_mapping(mc_id)
    if m:
        print(f"  MC {mc_id:3d} ({m.mc_name:20s}) → MNW {m.mnw_id:3d} ({m.mnw_name})")

# 反向映射测试
print("\n反向映射测试:")
mnw_ids = [104, 100, 200]
for mnw_id in mnw_ids:
    mc_id = mapper.map_mnw_to_mc(mnw_id)
    m = mapper.get_mapping(mc_id)
    if m:
        print(f"  MNW {mnw_id:3d} ({m.mnw_name:10s}) → MC {mc_id:3d} ({m.mc_name})")

print("\n" + "=" * 60)