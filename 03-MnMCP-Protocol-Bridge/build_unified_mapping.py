#!/usr/bin/env python3
"""
MnMCP 跨平台映射表生成器
基于迷你世界csvdef解析数据 + Minecraft Wiki数据
生成方块、物品、实体的双向映射

规则：
- MNW有MC没有的方块 → MC用stone外观，名称同步
- MC有MNW没有的方块 → MNW用长草方块外观，名称同步
- MNW有MC没有的物品 → MC用wooden_sword外观，名称同步
- MC有MNW没有的物品 → MNW用地形编辑器外观，名称同步
- 箭/矛轨迹等计算偏差 → 以迷你世界计算方式为准

版本: v0.3.1 Phase 7
"""

import json
from pathlib import Path

DATA_DIR = Path(r"D:\Coding\MnMCP\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\data")

# ═══════════════════════════════════════════════════════════
# 方块映射 (MNW Key → MC registry name)
# 基于功能/外观相似性手工对照
# ═══════════════════════════════════════════════════════════

BLOCK_MAP = {
    # --- 基础方块 ---
    'Air': 'minecraft:air',
    'UltraStone': 'minecraft:bedrock',
    'StaticWater': 'minecraft:water',
    'Water': 'minecraft:water',
    'StaticLava': 'minecraft:lava',
    'Lava': 'minecraft:lava',
    'Stone': 'minecraft:stone',
    'Dirt': 'minecraft:dirt',
    'Grass': 'minecraft:grass_block',
    'Sand': 'minecraft:sand',
    'Gravel': 'minecraft:gravel',
    'Clay': 'minecraft:clay',
    'Sandstone': 'minecraft:sandstone',
    'RedSandstone': 'minecraft:red_sandstone',
    'RedSand': 'minecraft:red_sand',
    'SoulSand': 'minecraft:soul_sand',
    'Obsidian': 'minecraft:obsidian',
    'Bedrock': 'minecraft:bedrock',
    'Netherrack': 'minecraft:netherrack',
    'EndStone': 'minecraft:end_stone',
    'Basalt': 'minecraft:basalt',
    'Blackstone': 'minecraft:blackstone',
    'Deepslate': 'minecraft:deepslate',
    'Tuff': 'minecraft:tuff',
    'Calcite': 'minecraft:calcite',
    'Dripstone': 'minecraft:dripstone_block',
    'MossBlock': 'minecraft:moss_block',
    'MudBlock': 'minecraft:mud',
    'PackedMud': 'minecraft:packed_mud',
    'MudBricks': 'minecraft:mud_bricks',
    'SculkBlock': 'minecraft:sculk',
    
    # --- 矿石 ---
    'CoalOre': 'minecraft:coal_ore',
    'IronOre': 'minecraft:iron_ore',
    'GoldOre': 'minecraft:gold_ore',
    'DiamondOre': 'minecraft:diamond_ore',
    'EmeraldOre': 'minecraft:emerald_ore',
    'LapisOre': 'minecraft:lapis_ore',
    'RedstoneOre': 'minecraft:redstone_ore',
    'CopperOre': 'minecraft:copper_ore',
    'NetherGoldOre': 'minecraft:nether_gold_ore',
    'NetherQuartzOre': 'minecraft:nether_quartz_ore',
    'AncientDebris': 'minecraft:ancient_debris',
    'DeepslateCoalOre': 'minecraft:deepslate_coal_ore',
    'DeepslateIronOre': 'minecraft:deepslate_iron_ore',
    'DeepslateGoldOre': 'minecraft:deepslate_gold_ore',
    'DeepslateDiamondOre': 'minecraft:deepslate_diamond_ore',
    'DeepslateEmeraldOre': 'minecraft:deepslate_emerald_ore',
    'DeepslateLapisOre': 'minecraft:deepslate_lapis_ore',
    'DeepslateRedstoneOre': 'minecraft:deepslate_redstone_ore',
    'DeepslateCopperOre': 'minecraft:deepslate_copper_ore',
    # MNW独有矿石
    'BluecrystalOre': '__mnw_only__',  # 蓝晶矿 → MC用stone外观
    'StarOre': '__mnw_only__',          # 星星矿
    'ElectricStoneOre': '__mnw_only__', # 电石矿
    
    # --- 矿物块 ---
    'CoalBlock': 'minecraft:coal_block',
    'IronBlock': 'minecraft:iron_block',
    'GoldBlock': 'minecraft:gold_block',
    'DiamondBlock': 'minecraft:diamond_block',
    'EmeraldBlock': 'minecraft:emerald_block',
    'LapisBlock': 'minecraft:lapis_block',
    'RedstoneBlock': 'minecraft:redstone_block',
    'CopperBlock': 'minecraft:copper_block',
    'NetheriteBlock': 'minecraft:netherite_block',
    'QuartzBlock': 'minecraft:quartz_block',
    'AmethystBlock': 'minecraft:amethyst_block',
    
    # --- 木材 ---
    'OakLog': 'minecraft:oak_log',
    'BirchLog': 'minecraft:birch_log',
    'SpruceLog': 'minecraft:spruce_log',
    'JungleLog': 'minecraft:jungle_log',
    'AcaciaLog': 'minecraft:acacia_log',
    'DarkOakLog': 'minecraft:dark_oak_log',
    'MangroveLog': 'minecraft:mangrove_log',
    'CherryLog': 'minecraft:cherry_log',
    'CrimsonStem': 'minecraft:crimson_stem',
    'WarpedStem': 'minecraft:warped_stem',
    'OakPlanks': 'minecraft:oak_planks',
    'BirchPlanks': 'minecraft:birch_planks',
    'SprucePlanks': 'minecraft:spruce_planks',
    'JunglePlanks': 'minecraft:jungle_planks',
    'AcaciaPlanks': 'minecraft:acacia_planks',
    'DarkOakPlanks': 'minecraft:dark_oak_planks',
    'MangrovePlanks': 'minecraft:mangrove_planks',
    'CherryPlanks': 'minecraft:cherry_planks',
    'CrimsonPlanks': 'minecraft:crimson_planks',
    'WarpedPlanks': 'minecraft:warped_planks',
    'BambooBlock': 'minecraft:bamboo_block',
    'BambooPlanks': 'minecraft:bamboo_planks',
    # MNW独有木材
    'FruitTreeLog': '__mnw_only__',     # 果木
    'PeachLog': '__mnw_only__',         # 桃木
    'CoconutLog': '__mnw_only__',       # 椰木
    
    # --- 树叶 ---
    'OakLeaves': 'minecraft:oak_leaves',
    'BirchLeaves': 'minecraft:birch_leaves',
    'SpruceLeaves': 'minecraft:spruce_leaves',
    'JungleLeaves': 'minecraft:jungle_leaves',
    'AcaciaLeaves': 'minecraft:acacia_leaves',
    'DarkOakLeaves': 'minecraft:dark_oak_leaves',
    'MangroveLeaves': 'minecraft:mangrove_leaves',
    'CherryLeaves': 'minecraft:cherry_leaves',
    'AzaleaLeaves': 'minecraft:azalea_leaves',
    
    # --- 建筑方块 ---
    'StoneBrick': 'minecraft:stone_bricks',
    'MossyStoneBrick': 'minecraft:mossy_stone_bricks',
    'CrackedStoneBrick': 'minecraft:cracked_stone_bricks',
    'ChiseledStoneBrick': 'minecraft:chiseled_stone_bricks',
    'Bricks': 'minecraft:bricks',
    'NetherBrick': 'minecraft:nether_bricks',
    'RedNetherBrick': 'minecraft:red_nether_bricks',
    'EndStoneBrick': 'minecraft:end_stone_bricks',
    'DeepslateBrick': 'minecraft:deepslate_bricks',
    'DeepslateTile': 'minecraft:deepslate_tiles',
    'PolishedBlackstone': 'minecraft:polished_blackstone',
    'PolishedBlackstoneBrick': 'minecraft:polished_blackstone_bricks',
    'PolishedDeepslate': 'minecraft:polished_deepslate',
    'CobbledDeepslate': 'minecraft:cobbled_deepslate',
    'Cobblestone': 'minecraft:cobblestone',
    'MossyCobblestone': 'minecraft:mossy_cobblestone',
    'Prismarine': 'minecraft:prismarine',
    'PrismarineBrick': 'minecraft:prismarine_bricks',
    'DarkPrismarine': 'minecraft:dark_prismarine',
    'SeaLantern': 'minecraft:sea_lantern',
    'Purpur': 'minecraft:purpur_block',
    
    # --- 玻璃 ---
    'Glass': 'minecraft:glass',
    'GlassPane': 'minecraft:glass_pane',
    'WhiteStainedGlass': 'minecraft:white_stained_glass',
    'OrangeStainedGlass': 'minecraft:orange_stained_glass',
    'MagentaStainedGlass': 'minecraft:magenta_stained_glass',
    'LightBlueStainedGlass': 'minecraft:light_blue_stained_glass',
    'YellowStainedGlass': 'minecraft:yellow_stained_glass',
    'LimeStainedGlass': 'minecraft:lime_stained_glass',
    'PinkStainedGlass': 'minecraft:pink_stained_glass',
    'GrayStainedGlass': 'minecraft:gray_stained_glass',
    'LightGrayStainedGlass': 'minecraft:light_gray_stained_glass',
    'CyanStainedGlass': 'minecraft:cyan_stained_glass',
    'PurpleStainedGlass': 'minecraft:purple_stained_glass',
    'BlueStainedGlass': 'minecraft:blue_stained_glass',
    'BrownStainedGlass': 'minecraft:brown_stained_glass',
    'GreenStainedGlass': 'minecraft:green_stained_glass',
    'RedStainedGlass': 'minecraft:red_stained_glass',
    'BlackStainedGlass': 'minecraft:black_stained_glass',
    'TintedGlass': 'minecraft:tinted_glass',
    
    # --- 羊毛/地毯 ---
    'WhiteWool': 'minecraft:white_wool',
    'OrangeWool': 'minecraft:orange_wool',
    'MagentaWool': 'minecraft:magenta_wool',
    'LightBlueWool': 'minecraft:light_blue_wool',
    'YellowWool': 'minecraft:yellow_wool',
    'LimeWool': 'minecraft:lime_wool',
    'PinkWool': 'minecraft:pink_wool',
    'GrayWool': 'minecraft:gray_wool',
    'LightGrayWool': 'minecraft:light_gray_wool',
    'CyanWool': 'minecraft:cyan_wool',
    'PurpleWool': 'minecraft:purple_wool',
    'BlueWool': 'minecraft:blue_wool',
    'BrownWool': 'minecraft:brown_wool',
    'GreenWool': 'minecraft:green_wool',
    'RedWool': 'minecraft:red_wool',
    'BlackWool': 'minecraft:black_wool',
    
    # --- 功能方块 ---
    'CraftingTable': 'minecraft:crafting_table',
    'Furnace': 'minecraft:furnace',
    'BlastFurnace': 'minecraft:blast_furnace',
    'Smoker': 'minecraft:smoker',
    'Anvil': 'minecraft:anvil',
    'EnchantingTable': 'minecraft:enchanting_table',
    'BrewingStand': 'minecraft:brewing_stand',
    'Chest': 'minecraft:chest',
    'EnderChest': 'minecraft:ender_chest',
    'Barrel': 'minecraft:barrel',
    'Bed': 'minecraft:red_bed',
    'Torch': 'minecraft:torch',
    'SoulTorch': 'minecraft:soul_torch',
    'Lantern': 'minecraft:lantern',
    'SoulLantern': 'minecraft:soul_lantern',
    'Campfire': 'minecraft:campfire',
    'SoulCampfire': 'minecraft:soul_campfire',
    'TNT': 'minecraft:tnt',
    'Ladder': 'minecraft:ladder',
    'Bookshelf': 'minecraft:bookshelf',
    'Jukebox': 'minecraft:jukebox',
    'NoteBlock': 'minecraft:note_block',
    'Beacon': 'minecraft:beacon',
    'Hopper': 'minecraft:hopper',
    'Dispenser': 'minecraft:dispenser',
    'Dropper': 'minecraft:dropper',
    'Observer': 'minecraft:observer',
    'Piston': 'minecraft:piston',
    'StickyPiston': 'minecraft:sticky_piston',
    'Lever': 'minecraft:lever',
    'StoneButton': 'minecraft:stone_button',
    'OakButton': 'minecraft:oak_button',
    'StonePressurePlate': 'minecraft:stone_pressure_plate',
    'OakPressurePlate': 'minecraft:oak_pressure_plate',
    'RedstoneTorch': 'minecraft:redstone_torch',
    'RedstoneLamp': 'minecraft:redstone_lamp',
    'Repeater': 'minecraft:repeater',
    'Comparator': 'minecraft:comparator',
    'DaylightDetector': 'minecraft:daylight_detector',
    'Glowstone': 'minecraft:glowstone',
    'Shroomlight': 'minecraft:shroomlight',
    'RespawnAnchor': 'minecraft:respawn_anchor',
    'Lodestone': 'minecraft:lodestone',
    'Target': 'minecraft:target',
    
    # --- 植物 ---
    'TallGrass': 'minecraft:short_grass',
    'Fern': 'minecraft:fern',
    'LargeFern': 'minecraft:large_fern',
    'DeadBush': 'minecraft:dead_bush',
    'Dandelion': 'minecraft:dandelion',
    'Poppy': 'minecraft:poppy',
    'BlueOrchid': 'minecraft:blue_orchid',
    'Allium': 'minecraft:allium',
    'AzureBluet': 'minecraft:azure_bluet',
    'RedTulip': 'minecraft:red_tulip',
    'OrangeTulip': 'minecraft:orange_tulip',
    'WhiteTulip': 'minecraft:white_tulip',
    'PinkTulip': 'minecraft:pink_tulip',
    'OxeyeDaisy': 'minecraft:oxeye_daisy',
    'Cornflower': 'minecraft:cornflower',
    'LilyOfTheValley': 'minecraft:lily_of_the_valley',
    'Sunflower': 'minecraft:sunflower',
    'Lilac': 'minecraft:lilac',
    'RoseBush': 'minecraft:rose_bush',
    'Peony': 'minecraft:peony',
    'LilyPad': 'minecraft:lily_pad',
    'Vine': 'minecraft:vine',
    'SugarCane': 'minecraft:sugar_cane',
    'Cactus': 'minecraft:cactus',
    'Bamboo': 'minecraft:bamboo',
    'Kelp': 'minecraft:kelp',
    'SeaGrass': 'minecraft:seagrass',
    'GlowBerries': 'minecraft:cave_vines',
    'SweetBerryBush': 'minecraft:sweet_berry_bush',
    'Wheat': 'minecraft:wheat',
    'Carrot': 'minecraft:carrots',
    'Potato': 'minecraft:potatoes',
    'Beetroot': 'minecraft:beetroots',
    'Melon': 'minecraft:melon',
    'Pumpkin': 'minecraft:pumpkin',
    'CarvedPumpkin': 'minecraft:carved_pumpkin',
    'JackOLantern': 'minecraft:jack_o_lantern',
    'BrownMushroom': 'minecraft:brown_mushroom',
    'RedMushroom': 'minecraft:red_mushroom',
    'CrimsonFungus': 'minecraft:crimson_fungus',
    'WarpedFungus': 'minecraft:warped_fungus',
    'NetherWartBlock': 'minecraft:nether_wart_block',
    'WarpedWartBlock': 'minecraft:warped_wart_block',
    'WeepingVines': 'minecraft:weeping_vines',
    'TwistingVines': 'minecraft:twisting_vines',
    'CrimsonRoots': 'minecraft:crimson_roots',
    'WarpedRoots': 'minecraft:warped_roots',
    'NetherSprouts': 'minecraft:nether_sprouts',
    'MossCarpet': 'minecraft:moss_carpet',
    'Azalea': 'minecraft:azalea',
    'FloweringAzalea': 'minecraft:flowering_azalea',
    'DripleafBig': 'minecraft:big_dripleaf',
    'DripleafSmall': 'minecraft:small_dripleaf',
    'SporeBlossom': 'minecraft:spore_blossom',
    
    # --- 冰雪 ---
    'Ice': 'minecraft:ice',
    'PackedIce': 'minecraft:packed_ice',
    'BlueIce': 'minecraft:blue_ice',
    'Snow': 'minecraft:snow',
    'SnowBlock': 'minecraft:snow_block',
    'PowderSnow': 'minecraft:powder_snow',
    
    # --- 陶瓦/混凝土 ---
    'Terracotta': 'minecraft:terracotta',
    'WhiteTerracotta': 'minecraft:white_terracotta',
    'OrangeTerracotta': 'minecraft:orange_terracotta',
    'MagentaTerracotta': 'minecraft:magenta_terracotta',
    'LightBlueTerracotta': 'minecraft:light_blue_terracotta',
    'YellowTerracotta': 'minecraft:yellow_terracotta',
    'LimeTerracotta': 'minecraft:lime_terracotta',
    'PinkTerracotta': 'minecraft:pink_terracotta',
    'GrayTerracotta': 'minecraft:gray_terracotta',
    'LightGrayTerracotta': 'minecraft:light_gray_terracotta',
    'CyanTerracotta': 'minecraft:cyan_terracotta',
    'PurpleTerracotta': 'minecraft:purple_terracotta',
    'BlueTerracotta': 'minecraft:blue_terracotta',
    'BrownTerracotta': 'minecraft:brown_terracotta',
    'GreenTerracotta': 'minecraft:green_terracotta',
    'RedTerracotta': 'minecraft:red_terracotta',
    'BlackTerracotta': 'minecraft:black_terracotta',
    'WhiteConcrete': 'minecraft:white_concrete',
    'OrangeConcrete': 'minecraft:orange_concrete',
    'MagentaConcrete': 'minecraft:magenta_concrete',
    'LightBlueConcrete': 'minecraft:light_blue_concrete',
    'YellowConcrete': 'minecraft:yellow_concrete',
    'LimeConcrete': 'minecraft:lime_concrete',
    'PinkConcrete': 'minecraft:pink_concrete',
    'GrayConcrete': 'minecraft:gray_concrete',
    'LightGrayConcrete': 'minecraft:light_gray_concrete',
    'CyanConcrete': 'minecraft:cyan_concrete',
    'PurpleConcrete': 'minecraft:purple_concrete',
    'BlueConcrete': 'minecraft:blue_concrete',
    'BrownConcrete': 'minecraft:brown_concrete',
    'GreenConcrete': 'minecraft:green_concrete',
    'RedConcrete': 'minecraft:red_concrete',
    'BlackConcrete': 'minecraft:black_concrete',
}

# ═══════════════════════════════════════════════════════════
# 实体映射 (MNW Key → MC entity ID)
# ═══════════════════════════════════════════════════════════

ENTITY_MAP = {
    # --- 被动生物 ---
    'Chicken': 'minecraft:chicken',
    'Cow': 'minecraft:cow',
    'Pig': 'minecraft:pig',
    'Sheep': 'minecraft:sheep',
    'Horse': 'minecraft:horse',
    'Donkey': 'minecraft:donkey',
    'Mule': 'minecraft:mule',
    'Rabbit': 'minecraft:rabbit',
    'Wolf': 'minecraft:wolf',
    'Cat': 'minecraft:cat',
    'Ocelot': 'minecraft:ocelot',
    'Parrot': 'minecraft:parrot',
    'Fox': 'minecraft:fox',
    'Bee': 'minecraft:bee',
    'Turtle': 'minecraft:turtle',
    'Dolphin': 'minecraft:dolphin',
    'Squid': 'minecraft:squid',
    'GlowSquid': 'minecraft:glow_squid',
    'Cod': 'minecraft:cod',
    'Salmon': 'minecraft:salmon',
    'TropicalFish': 'minecraft:tropical_fish',
    'Pufferfish': 'minecraft:pufferfish',
    'Axolotl': 'minecraft:axolotl',
    'Goat': 'minecraft:goat',
    'Frog': 'minecraft:frog',
    'Tadpole': 'minecraft:tadpole',
    'Allay': 'minecraft:allay',
    'Camel': 'minecraft:camel',
    'Sniffer': 'minecraft:sniffer',
    'Bat': 'minecraft:bat',
    'IronGolem': 'minecraft:iron_golem',
    'SnowGolem': 'minecraft:snow_golem',
    'Villager': 'minecraft:villager',
    'WanderingTrader': 'minecraft:wandering_trader',
    'Llama': 'minecraft:llama',
    'TraderLlama': 'minecraft:trader_llama',
    'Panda': 'minecraft:panda',
    'Strider': 'minecraft:strider',
    'Hoglin': 'minecraft:hoglin',
    'Piglin': 'minecraft:piglin',
    'PiglinBrute': 'minecraft:piglin_brute',
    
    # --- 敌对生物 ---
    'Zombie': 'minecraft:zombie',
    'Skeleton': 'minecraft:skeleton',
    'Creeper': 'minecraft:creeper',
    'Spider': 'minecraft:spider',
    'CaveSpider': 'minecraft:cave_spider',
    'Enderman': 'minecraft:enderman',
    'Slime': 'minecraft:slime',
    'MagmaCube': 'minecraft:magma_cube',
    'Ghast': 'minecraft:ghast',
    'Blaze': 'minecraft:blaze',
    'WitherSkeleton': 'minecraft:wither_skeleton',
    'Witch': 'minecraft:witch',
    'Guardian': 'minecraft:guardian',
    'ElderGuardian': 'minecraft:elder_guardian',
    'Phantom': 'minecraft:phantom',
    'Drowned': 'minecraft:drowned',
    'Husk': 'minecraft:husk',
    'Stray': 'minecraft:stray',
    'Pillager': 'minecraft:pillager',
    'Vindicator': 'minecraft:vindicator',
    'Evoker': 'minecraft:evoker',
    'Ravager': 'minecraft:ravager',
    'Vex': 'minecraft:vex',
    'Shulker': 'minecraft:shulker',
    'Silverfish': 'minecraft:silverfish',
    'Endermite': 'minecraft:endermite',
    'ZombifiedPiglin': 'minecraft:zombified_piglin',
    'Warden': 'minecraft:warden',
    'Breeze': 'minecraft:breeze',
    
    # --- Boss ---
    'EnderDragon': 'minecraft:ender_dragon',
    'Wither': 'minecraft:wither',
    
    # --- MNW独有 ---
    'Travelingmerchant': 'minecraft:wandering_trader',
    'Desertmerchant': 'minecraft:wandering_trader',
    'IceFieldMerchant': 'minecraft:wandering_trader',
    'WildMan': '__mnw_only__',          # 野人
    'WildManChief': '__mnw_only__',     # 野人首领
    'WildManWarrior': '__mnw_only__',   # 野人战士
    'WildManArcher': '__mnw_only__',    # 野人弓箭手
    'WildManWitch': '__mnw_only__',     # 野人巫师
    'BlackDragon': 'minecraft:ender_dragon',  # 黑龙≈末影龙
    'Ostrich': '__mnw_only__',          # 鸵鸟
    'Penguin': '__mnw_only__',          # 企鹅
    'Crocodile': '__mnw_only__',        # 鳄鱼
    'Peacock': '__mnw_only__',          # 孔雀
    'Chameleon': '__mnw_only__',        # 变色龙
    'Firefly': '__mnw_only__',          # 萤火虫
    'Scorpion': '__mnw_only__',         # 蝎子
    'Piranha': '__mnw_only__',          # 食人鱼
}

# ═══════════════════════════════════════════════════════════
# 物理/机制差异映射
# ═══════════════════════════════════════════════════════════

MECHANICS_DIFF = {
    'projectile_trajectory': {
        'description': '投射物轨迹计算',
        'priority': 'mnw',  # 以迷你世界为准
        'details': {
            'arrow': {
                'mnw': '重力加速度约9.0, 初速度约1.5, 空气阻力0.01',
                'mc': '重力加速度0.05/tick, 初速度3.0, 阻力0.01/tick',
                'note': '以MNW计算方式为准，MC端需要转换',
            },
            'spear': {
                'mnw': '标枪/矛有独立轨迹，重力更大，射程更短',
                'mc': 'MC用三叉戟(trident)对应，轨迹不同',
                'note': '以MNW计算方式为准',
            },
            'throwable': {
                'mnw': '投掷物（雪球等）弧线更平',
                'mc': 'MC投掷物弧线更陡',
                'note': '以MNW计算方式为准',
            },
        },
    },
    'damage_calculation': {
        'description': '伤害计算',
        'priority': 'convert',
        'details': {
            'mnw_formula': 'damage = base_attack * (1 - armor_reduction)',
            'mc_formula': 'damage = base_attack * (1 - min(20, max(armor/5, armor - damage/(2+toughness/4))) / 25)',
            'note': '需要双向转换，保持伤害比例一致',
        },
    },
    'health_system': {
        'description': '生命值系统',
        'priority': 'convert',
        'details': {
            'mnw': '玩家默认20HP，显示为数字',
            'mc': '玩家默认20HP(10颗心)，显示为心形图标',
            'note': '数值相同，仅显示方式不同',
        },
    },
    'hunger_system': {
        'description': '饥饿系统',
        'priority': 'convert',
        'details': {
            'mnw': '饥饿值100，消耗速率不同',
            'mc': '饥饿值20(10个鸡腿)，有饱和度',
            'note': 'MNW饥饿值/5=MC饥饿值',
        },
    },
    'fall_damage': {
        'description': '摔落伤害',
        'priority': 'mnw',
        'details': {
            'mnw': '超过3格开始受伤，每格1HP',
            'mc': '超过3格开始受伤，每格1HP',
            'note': '基本一致，无需转换',
        },
    },
    'day_night_cycle': {
        'description': '昼夜循环',
        'priority': 'convert',
        'details': {
            'mnw': '一天约20分钟',
            'mc': '一天20分钟(24000 ticks)',
            'note': '基本一致',
        },
    },
}

# ═══════════════════════════════════════════════════════════
# 占位方块/物品定义
# ═══════════════════════════════════════════════════════════

FALLBACK = {
    'mnw_block_no_mc': {
        'mc_appearance': 'minecraft:stone',
        'description': 'MNW有MC没有的方块，MC端用石头外观，名称同步',
    },
    'mc_block_no_mnw': {
        'mnw_appearance': 'LongGrass',  # 长草方块
        'mnw_appearance_id': 31,
        'description': 'MC有MNW没有的方块，MNW端用长草方块外观，名称同步',
    },
    'mnw_item_no_mc': {
        'mc_appearance': 'minecraft:wooden_sword',
        'description': 'MNW有MC没有的物品，MC端用木剑外观，名称同步',
    },
    'mc_item_no_mnw': {
        'mnw_appearance': 'TerrainEditor',  # 地形编辑器
        'description': 'MC有MNW没有的物品，MNW端用地形编辑器外观，名称同步',
    },
}


def build_mapping():
    """构建完整映射并保存"""
    # 加载解析的MNW数据
    gamedata_path = DATA_DIR / 'mnw_gamedata_full.json'
    with open(gamedata_path, 'r', encoding='utf-8') as f:
        mnw_data = json.load(f)
    
    # 构建方块映射
    block_mappings = []
    mnw_blocks = {b['key']: b for b in mnw_data['blocks'] if b['key']}
    
    mapped = 0
    mnw_only = 0
    
    for key, mc_id in BLOCK_MAP.items():
        mnw_block = mnw_blocks.get(key, {})
        entry = {
            'mnw_key': key,
            'mnw_id': mnw_block.get('id', -1),
            'mnw_name_cn': mnw_block.get('name_cn', key),
            'mc_registry': mc_id,
            'mapped': mc_id != '__mnw_only__',
        }
        if mc_id == '__mnw_only__':
            entry['mc_fallback'] = FALLBACK['mnw_block_no_mc']['mc_appearance']
            mnw_only += 1
        else:
            mapped += 1
        block_mappings.append(entry)
    
    # 统计未映射的MNW方块
    mapped_keys = set(BLOCK_MAP.keys())
    unmapped_mnw = [b for b in mnw_data['blocks'] 
                    if b['key'] and b['key'] not in mapped_keys and b['name_cn']]
    
    for b in unmapped_mnw:
        block_mappings.append({
            'mnw_key': b['key'],
            'mnw_id': b['id'],
            'mnw_name_cn': b['name_cn'],
            'mc_registry': '__mnw_only__',
            'mc_fallback': FALLBACK['mnw_block_no_mc']['mc_appearance'],
            'mapped': False,
        })
    
    # 实体映射
    entity_mappings = []
    for key, mc_id in ENTITY_MAP.items():
        entity_mappings.append({
            'mnw_key': key,
            'mc_entity': mc_id,
            'mapped': mc_id != '__mnw_only__',
            'mc_fallback': 'minecraft:pig' if mc_id == '__mnw_only__' else None,
        })
    
    output = {
        'version': '3.0.0',
        'mc_version': '1.20.6',
        'mnw_version': '1.53.x',
        'generated': 'auto + manual review',
        'stats': {
            'block_mappings': len(block_mappings),
            'block_mapped': sum(1 for b in block_mappings if b['mapped']),
            'block_mnw_only': sum(1 for b in block_mappings if not b['mapped']),
            'entity_mappings': len(entity_mappings),
            'entity_mapped': sum(1 for e in entity_mappings if e['mapped']),
        },
        'fallback_rules': FALLBACK,
        'mechanics_diff': MECHANICS_DIFF,
        'block_mappings': block_mappings,
        'entity_mappings': entity_mappings,
    }
    
    out_path = DATA_DIR / 'mnw_mc_unified_mapping.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"统一映射已生成: {out_path}")
    print(f"  文件大小: {os.path.getsize(out_path)/1024:.0f} KB")
    print(f"  方块映射: {output['stats']['block_mapped']} 已映射 / {output['stats']['block_mnw_only']} MNW独有")
    print(f"  实体映射: {output['stats']['entity_mapped']} 已映射")
    
    return output


if __name__ == '__main__':
    import os
    build_mapping()
