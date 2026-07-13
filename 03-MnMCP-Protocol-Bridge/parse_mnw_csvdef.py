#!/usr/bin/env python3
"""
MnMCP 迷你世界CSV数据解析器 v2
从解包的csvdef中提取方块、物品、实体、维度等全量ID
"""

import csv
import json
import os
from pathlib import Path

CSV_DIR = Path(r"D:\Coding\MnMCP\MnMCPResources\csvdef\utf8")
OUT_DIR = Path(r"D:\Coding\MnMCP\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\data")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def read_csv(filepath):
    """读取CSV: 第0行=中文描述, 第1行=英文字段名, 第2行起=数据"""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    if len(lines) < 3:
        return [], []
    header = [h.strip() for h in lines[1].strip().split(',')]
    rows = []
    reader = csv.reader(lines[2:])
    for cols in reader:
        if len(cols) < len(header):
            cols += [''] * (len(header) - len(cols))
        row = {header[i]: cols[i].strip() for i in range(len(header))}
        rows.append(row)
    return header, rows


def g(row, *keys):
    """从row中取第一个存在的key的值"""
    for k in keys:
        v = row.get(k, '').strip()
        if v:
            return v
    return ''


def parse_blocks():
    print("=== blockdef.csv ===")
    _, rows = read_csv(CSV_DIR / "blockdef.csv")
    blocks = []
    for r in rows:
        bid = g(r, 'ID', 'id')
        if not bid or not bid.isdigit():
            continue
        blocks.append({
            'id': int(bid),
            'name_cn': g(r, 'Name'),
            'name_en': g(r, 'ENName'),
            'key': g(r, 'Key'),
            'hardness': g(r, 'Hardness'),
            'anti_explode': g(r, 'AntiExplode'),
            'move_collide': g(r, 'MoveCollide'),
            'gravity': g(r, 'GravityEffect'),
            'burn_speed': g(r, 'BurnSpeed'),
            'light_level': g(r, 'LightSource', 'LightStrength'),
        })
    print(f"  总数: {len(blocks)}")
    for b in blocks[:8]:
        print(f"  {b['id']:4d} | {b['key']:28s} | {b['name_cn']}")
    return blocks


def parse_items():
    print("\n=== itemdef.csv ===")
    _, rows = read_csv(CSV_DIR / "itemdef.csv")
    items = []
    for r in rows:
        iid = g(r, 'ID', 'id')
        if not iid or not iid.isdigit():
            continue
        items.append({
            'id': int(iid),
            'name_cn': g(r, 'Name'),
            'key': g(r, 'Key'),
            'item_type': g(r, 'ItemType'),
            'category1': g(r, 'Category1'),
            'category2': g(r, 'Category2'),
        })
    print(f"  总数: {len(items)}")
    for i in items[:8]:
        print(f"  {i['id']:5d} | {i['key']:28s} | {i['name_cn']}")
    return items


def parse_entities():
    print("\n=== monster.csv ===")
    _, rows = read_csv(CSV_DIR / "monster.csv")
    ents = []
    for r in rows:
        eid = g(r, 'ID', 'id')
        if not eid or not eid.isdigit():
            continue
        ents.append({
            'id': int(eid),
            'name_cn': g(r, 'Name'),
            'name_en': g(r, 'ENName'),
            'key': g(r, 'Key'),
            'type': g(r, 'Type'),
            'health': g(r, 'Life'),
            'attack': g(r, 'Attack'),
            'speed': g(r, 'Speed'),
            'armor': g(r, 'ArmorPhysics'),
        })
    print(f"  总数: {len(ents)}")
    # 跳过备用ID
    real = [e for e in ents if e['name_cn'] and '备用' not in e['name_cn']]
    for e in real[:8]:
        print(f"  {e['id']:5d} | {e['key']:25s} | {e['name_cn']:10s} | HP={e['health']}")
    return ents


def parse_biomes():
    print("\n=== biomedef.csv ===")
    _, rows = read_csv(CSV_DIR / "biomedef.csv")
    biomes = []
    for r in rows:
        bid = g(r, 'ID', 'id')
        if not bid or not bid.isdigit():
            continue
        biomes.append({
            'id': int(bid),
            'name_cn': g(r, 'Name'),
            'key': g(r, 'Key'),
        })
    print(f"  总数: {len(biomes)}")
    for b in biomes[:8]:
        print(f"  {b['id']:4d} | {b['name_cn']}")
    return biomes


def parse_tools():
    print("\n=== tooldef.csv ===")
    _, rows = read_csv(CSV_DIR / "tooldef.csv")
    tools = []
    for r in rows:
        tid = g(r, 'ID', 'id')
        if not tid or not tid.isdigit():
            continue
        tools.append({
            'id': int(tid),
            'name_cn': g(r, 'Name'),
            'key': g(r, 'Key'),
            'durability': g(r, 'Durability'),
            'attack': g(r, 'Attack'),
            'speed': g(r, 'Speed', 'MineSpeed'),
        })
    print(f"  总数: {len(tools)}")
    real = [t for t in tools if t['name_cn']]
    for t in real[:8]:
        print(f"  {t['id']:5d} | {t['key']:25s} | {t['name_cn']}")
    return tools


def parse_crafting():
    print("\n=== crafting.csv ===")
    _, rows = read_csv(CSV_DIR / "crafting.csv")
    recipes = []
    for r in rows:
        rid = g(r, 'ID', 'id')
        if not rid or not rid.isdigit():
            continue
        recipes.append({
            'id': int(rid),
            'output': g(r, 'OutputID', 'Output'),
            'output_num': g(r, 'OutputNum'),
        })
    print(f"  总数: {len(recipes)}")
    return recipes


def main():
    print("MnMCP 迷你世界数据解析器 v2")
    print("=" * 50)

    blocks = parse_blocks()
    items = parse_items()
    entities = parse_entities()
    biomes = parse_biomes()
    tools = parse_tools()
    recipes = parse_crafting()

    output = {
        'version': '2.0.0',
        'source': 'MiniWorld csvdef (decompiled)',
        'mnw_version': '1.53.x',
        'stats': {
            'blocks': len(blocks),
            'items': len(items),
            'entities': len(entities),
            'biomes': len(biomes),
            'tools': len(tools),
            'recipes': len(recipes),
        },
        'blocks': blocks,
        'items': items,
        'entities': entities,
        'biomes': biomes,
        'tools': tools,
        'recipes': recipes,
    }

    out_path = OUT_DIR / 'mnw_gamedata_full.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"保存: {out_path} ({os.path.getsize(out_path)/1024:.0f} KB)")
    for k, v in output['stats'].items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
