# 迷你世界地图格式分析

## 1. 本地存档目录结构

```
miniworddata{apiid}/data/w{worldid}/
  wdesc.fb            # 世界描述 (FlatBuffers)
  wdesc_bcp.fb        # 世界描述备份
  wdescbackup.fb      # 世界描述备份2
  wglobal.fb          # 世界全局数据 (FlatBuffers)
  wglobal.ex          # 世界全局扩展数据
  wterrtype.fb        # 地形类型 (4字节 uint32, 例: 01=创造平坦)
  wsize.fb            # 世界大小标记
  wmultilang.fb       # 多语言数据
  cover.data          # 封面数据
  thumb.png_          # 缩略图
  resourceList.data   # 资源列表
  m0/                 # 维度0 (主世界)
    x{X}z{Z}.r        # 区域文件 (Region, 方块数据)
    a{X}_{Z}.a         # 实体文件 (Actor)
    MechaSave/         # 机甲存档
  m1/                 # 维度1 (烈焰星/下界)
  m2/                 # 维度2 (萌眼星)
  roles/              # 角色数据
  sandbox/            # 沙盒脚本
  custommodel/        # 自定义模型
  custompic/          # 自定义图片
  customui/           # 自定义UI
  mods/               # MOD数据
  vehicle/            # 载具
  vbp/                # 蓝图
  ugc/                # UGC内容
  visualcode/         # 可视化编程
    *.db              # SQLite数据库
  buildSave/
    save_0.fb         # 建筑存档
  cityData/           # 城市数据
  string/             # 字符串资源
```

## 2. 区域文件格式 (x{X}z{Z}.r)

### 文件结构

```
[Header: 变长, protobuf varints]
  varint[0]: 未知 (例: 63)
  varint[1]: 未知 (例: 39483)
  varint[2]: 未知 (例: 8046)
  ...

[Section Table: N * 128 bytes]
  每条记录 128 字节
  记录结构:
    byte[0-1]:   section 标识/magic
    byte[2-3]:   数据标识
    byte[4-...]: 数据内容
    最后 16 字节: 看起来像偏移量/大小信息

  有效记录以 0x78 0xDA 或 0x7A 0xDA 或 0x79 0xDA 开头
  空记录全部为 0x00

[Chunk Data: 压缩的区块方块数据]
  压缩算法: 待确认 (非标准zlib, 可能是 zstd 或自定义)
```

### 观察到的模式

- 前 6 条记录有数据 (78 DA 开头)
- 第 7-16 条全零 (未使用区块)
- 第 17+ 条使用不同标记 (7A DA, 79 DA)
- 128 字节步长严格一致
- 总文件大小 ~2.6MB (满载世界)

## 3. 实体文件格式 (a{X}_{Z}.a)

- 文件大小: ~110KB (有实体的区域)
- 格式: 待分析 (可能是 FlatBuffers 或自定义二进制)

## 4. 网络传输格式 (PACKDATA, msgcode=43299/0xA923)

### 传输流程

```
客户端连接 → RakNet握手
客户端发送 PB_ROLE_CHECK_JOINFROMSRC_CH (1013)
  {Uin: 客户端UID, JoinFromSrc: "6"}
服务端发送 PACKDATA (43299) × N 个包
  每包 6132 字节 (RakNet 分片传输)
  总计 34+ 包 ≈ 204KB
客户端收完后发送 PB_ROLE_ENTER_WORLD_CH (1001)
  正常游戏循环开始
```

### PACKDATA 包格式

```
0x89 | MsgCode(2B LE = 0xA923) | Length(2B LE) | Data
```

使用标准 0x89 游戏包封装, 但 msgcode 43299 不在 ePBMsgCode 枚举中。
数据格式不是 protobuf, 是自定义二进制 (`tagPackData` 结构)。

### tagPackData 结构 (从C++反编译推断)

```
前 4 字节: 序号/标识 (通常为 0x00000000)
后续字节: 区块/世界二进制数据

相关C++类:
  tagPackData          - 数据包结构
  PB_PACKDATA          - protobuf 包装 (含 msgCode, data)
  PB_PACKDATA_CLIENT   - 客户端版本 (含 msgCode, packagedata)
  MpGameSurviveNetHandler - 生存模式网络处理
  GameNetHostMsgHandler   - 房主消息处理
  GameNetClientMsgHandler - 客户端消息处理
```

### 处理函数

| 函数 | 地址 | 大小 | 用途 |
|------|------|------|------|
| PB_PACKDATA recv | 0x300D878 | 1108 | 接收 PACKDATA |
| PB_PACKDATA main | 0x300DCCC | 3292 | 主处理器 (beginPos) |
| packdata host mode | 0x33E4720 | 1844 | 房主模式处理 |
| packdata client mode | 0x33E5528 | 1896 | 客户端模式处理 |
| packdata beginPos | 0x33E2774 | 1388 | beginPos 处理 |
| chunkSaveNew | 0x2F76F28 | 7400 | 区块序列化 |

## 5. FlatBuffers 文件 (.fb)

迷你世界使用 Google FlatBuffers 格式存储元数据。

### wdesc.fb (世界描述, 1048 bytes)

```
Magic: 80 00 00 00 (root table offset)
包含: 世界ID, 世界类型, 创建者UIN, 种子等
```

### wglobal.fb (世界全局, 8016 bytes)

```
包含: 游戏时间, 天气, 全局标志等
```

## 6. CSV 定义文件

位置: `game_script/script/csvdef/utf8/`

| 文件 | 行数 | 内容 |
|------|------|------|
| blockdef.csv | 2990 | 方块ID, 名称, 物理属性, 采集工具等 |
| biomedef.csv | - | 生物群系定义 |
| worlddef.csv | - | 世界/星球定义 (迷拉星, 烈焰星, 萌眼星) |
| homechunkdef.csv | - | 家园区块定义 |
| aidef.csv | - | AI定义 |
| buffdef.csv | - | Buff效果定义 |

### blockdef.csv 关键字段

```
ID: 方块数字ID (0=空气, 1=地心基石, ...)
Name: 方块中文名
ENName: 英文名
Key: 插件用名称
MoveCollide: 0=空气, 1=固体, 2=液体, 3=不阻挡投射物
Height: 方块高度
Texture1/Texture2: 贴图名
LightSrc: 光源强度
LightAtten: 光衰减
```

## 7. 关键发现

1. **本地房间不走 PB_SYNC_ROOM_EXTRA_HC** — 直接发 PACKDATA
2. **PACKDATA (43299) 是专用二进制通道** — 不在 ePBMsgCode 枚举中
3. **区域文件用 128 字节 section table** — 可能每个 section 对应一个 chunk column
4. **FlatBuffers 用于元数据** — wdesc.fb, wglobal.fb 等
5. **NAT 穿透由官方 punch 服务器提供** — 本地房间也经过 punch 服务器
6. **PB_ROLE_CHECK_JOINFROMSRC_CH (1013)** — 1.56.0 新增的加入来源检查包
