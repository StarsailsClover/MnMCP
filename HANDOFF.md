# MN2MC 交接文档

> 接手日期：2026-05-23  
> 当前状态：2026-05-30  
> 客户端版本：迷你世界 1.56.0 安卓 cltversion=139101 / PC 1.56.1 cltversion=139110

---

## 一、当前里程碑

### ✅ 已打通
1. **完整 auth 链** — HTTP login → WSS s2 → openroom 创房 → 心跳维持
2. **NAT punchthrough** — C++ 双端口代理 + SLikeNet NatPunchthroughServer/Client 插件
3. **TCP 桥协议** — C++ 代理与 Python backend 之间的游戏数据+控制帧转发
4. **完整 ENTER_WORLD 握手** — `cmd 1001 → ENTER_WORLD_HC + PLAYERPERMIT_HC + CUSTOM_MSG + SS_SYNC_TASK_HC`
5. **真实地图渲染** — 用本地 `cachetrunk` 缓存文件（LZMA + ZSTD 混合压缩）转发给客户端，渲染完整地形
6. **玩家移动/飞行/心跳** — 所有移动包正常往返

### ⚠️ 待解决
- **方块交互** — 服务端发出的 `PB_BlockUpdateHC` (cmd 104) 客户端不渲染
  - 协议字段编码已逆向（见下"关键发现"）
  - hook 抓真实包确认 `Blocks[i] uint32` 位编码
  - 但实测发出去客户端无反应，**疑似缺少其他必填字段或 wire format 细节差异**
- **物品栏交互** — GridSwap / GridDiscard / BackPackEquipWeapon 尚未实现服务端响应
- **MC bridge** — Node.js `prismarine-*` 依赖问题（`minecraft-data/data/pc/common/features.json` 找不到），暂时跳过

---

## 二、架构

```
[迷你世界客户端 (Android/PC)]
        │ UDP/RakNet (16字节RakNet头 + 13字节游戏头 + protobuf payload)
        │ NAT 双端口握手:
        │   :19132 facilitator (NatPunchthroughServer)
        │   :19133 host peer (NatPunchthroughClient, GUID=host_uin)
        ▼
[mn2mc_proxy.exe] (C++, SLikeNet RakNet)
        │ TCP frame: [4B len][4B client_guid][data]
        │ 控制帧: data[0]=0x00 0x01=connect, 0x00 0x02=disconnect
        │ 游戏帧: data[0]=0x89 起的完整 RakNet 游戏 payload
        ▼
[backend.py] (Python, asyncio TCP server on :19134)
        │ 路由到 aiorak event handler 系统（FakeConnection mock）
        ▼
[mn2mc/mini/packetevents/*.py]
        │ enter_world / chat / block_punch / block_interact / ...
        │ player.send_packet() → MiniClientPacket(local_mode=True) 13B header
        ▼
[FakeConnection.send] → TCP → C++ proxy → 客户端
```

### 关键设计决策
- **C++ 代理是必要的**：Python aiorak 无法实现 RakNet NatPunchthrough；客户端必须经历完整 NAT 流程才会建立到 host 端的连接（state=6 connectionSuccess）
- **双端口模式**：单端口（facilitator 与 host 同地址）走 proxyOnly 路径会卡在 state=5（OnProxyProxySuccess 是死代码）
- **Chunks 推送时机**：必须在 `ENTER_WORLD_HC` 之后发送（客户端有 "world initialized" flag 检查，未置位时 chunk 解压被跳过）
- **真实 chunk 转发**：客户端期望的 chunk payload 解压后是 FlatBuffers 二进制（schema 未完整逆向），直接转发本地 cachetrunk 真实文件最简单

---

## 三、关键发现（逆向结果）

### 3.1 连接状态机 (UDPConnection)
来自 `liblibGameApp.so` 1.56 arm64 反编译：

| 状态 | 含义 | 转换 |
|---|---|---|
| 0 | initial | → connectToServer |
| 1 | Connected to punch | 收 0x10 后 openNatpunch → state=2 |
| 2 | NAT punching | 15s 超时 → proxyOnly fallback；收 0x43 → state=3 |
| 3 | Connected to host | 收 0x10 → **state=6 (connectionSuccess)** ✓ |
| 4 | Connected to proxy | NatpunchConnected 处理 → 发 relay 0x5C → state=5 |
| 5 | Relay waiting | **死代码**：OnProxyProxySuccess 没人调用 → 15s 超时 connectionFailed(37005) |
| 6 | Connected ✓ | 游戏开始 |

**关键偏移**（liblibGameApp 1.56 arm64）：
```
0x76AC7D0  packet 分发器 (switch on data[0])
0x76ACC40  NatpunchConnected (state 1/3/4 分支)
0x76ACF60  0x43 NAT_PUNCH_SUCCEEDED handler
0x76AC5F4  connectToPunch (proxyOnly 决策)
0x66C8CF8  version_check ("need 14", 检查 *(a1+636))
0x67FF124  chunk blob decompress 入口
0x67FF400  post-decompress chunk parser (FlatBuffers)
```

### 3.2 Chunk 压缩格式
`PB_ChunkBlob.UnzipLen` 是 packed 32-bit：
- 高 4 位：压缩算法 (0=zlib, 1=LZ4, 2=LZMA, 3=ZSTD)
- 低 28 位：真实解压后大小

`BlobDetail` 是压缩字节流：
- LZMA: 5 字节 properties + LZMA1 raw stream
- ZSTD: 标准 ZSTD frame (magic 28 B5 2F FD)
- 解压后是 **FlatBuffers** 二进制（root_offset@0, vtable@8 with 18 entries），schema 未完整逆向

本地 chunk 缓存路径：`C:\Users\PC\AppData\Roaming\miniworddata110\data\cachetrunk\<bucket>\w<OWID>_<MapID>_<cx>_<cz>_<md5>`

### 3.3 PB_BlockUpdateHC wire 格式（cmd 104）
完整字段表（vtable @ 0xA1698B8，parser @ 0x89E75C0，serializer @ 0x89E8014）：

| field | name | wire type | proto type | struct offset | tag |
|---|---|---|---|---|---|
| 1 | ChunkX | varint | sint32 zigzag | +24 | 8 |
| 2 | ChunkZ | varint | sint32 zigzag | +28 | 16 |
| 3 | MapID | varint | int32 | +56 | 24 |
| 4 | Blocks[] | varint | uint32 repeated | +32(ptr)/+40(cnt) | 32 (or 34 packed) |
| 5 | ContainerBuf | length-delim | bytes | +48 | 42 |
| 6 | BlocksEx[] | varint | uint32 repeated | +64(ptr)/+72(cnt) | 48 (or 50 packed) |
| 7 | ContainerBufUnzipLen | varint | uint32 | +60 | 56 |
| 8 | BlockStateIndex[] | varint | uint32 repeated | +80(ptr)/+88(cnt) | 64 (or 66 packed) |

**Blocks[i] uint32 位拆分**（Dobby hook 抓真实包确认）：
```
Blocks[i] uint32 = (block_pack << 16) | pos16
  pos16      = (z << 12) | (y << 4) | x        // x,z: 4 bits (0-15 chunk-local), y: 8 bits (0-255)
  block_pack = (state << 12) | (block_id & 0xFFF)
BlocksEx[i]         = block_id >> 12  (block_id 高位，id>=4096 时用)
BlockStateIndex[i]  = 复杂 state 索引，普通方块 0
```

验证样本（hook 抓 host 玩家拆 id=614 方块）：
- `0x02660479` → x=9 y=71 z=0,   block_id=0x266=614
- `0x0266e479` → x=9 y=71 z=14
- `0x0266f479` → x=9 y=71 z=15
- `0x0266f379` → x=9 y=55 z=15

### 3.4 PB_Pos vs PB_Vector3
**重要陷阱**：
- `PB_Pos` 有 4 个字段：`X, Y, Z, Map` (sint32, sint32, sint32, uint32)
- `PB_Vector3` 只有 3 个字段：`X, Y, Z` (sint32×3, **无 Map**)
- `PB_BlockPunchCH.blockpos` / `PB_BlockInteractCH.blockpos` 都是 `PB_Vector3`，访问 `.Map` 会 `AttributeError`

### 3.5 NAT 协议细节
NatPunchthroughServer 插件返回的 RakPeer 绑定地址默认是 `0.0.0.0` → 客户端识别成 `127.0.0.1` → punch 到 loopback 失败。**必须把 RakPeer 绑定到具体 LAN IP**：
```cpp
SLNet::SocketDescriptor sd(port, lan_ip.c_str());  // 不是 nullptr！
```

Host peer 必须 attach `NatPunchthroughClient` 插件并 `Connect()` 到 facilitator 注册自己，client 才能 punch 到它：
```cpp
m_hostPeer->AttachPlugin(new NatPunchthroughClient());
m_hostPeer->Connect("127.0.0.1", 19132, ...);
```

### 3.6 房间创建参数关键点
- `connect_mode = "1"` (1=NAT punch, 2=P2P 直连但服务器拒绝, 0=拒绝)
- `auth_key = "f5711eb1640712de051e5aedc35329c3"` (openroom API 签名，**不是** sub_6473EB4 里的 900a3cc9...)
- `WORLD_OWID = 72954558563850` 必须统一所有：room_extra.MapID, WorldDesc.WorldId, RoleData.OWID, ChunkSaveDB.OWID
- LAN 模式下 `room_run_stat = "1"` 必填

---

## 四、文件清单

### 核心运行时
```
backend.py             # Python TCP backend (主入口, 启动 auth+房间+listener)
config.yaml            # 配置 (账号、xxtea_key、lan_ip 等)
mn2mc/mini/
  auth.py              # HTTP 登录
  wsconn.py            # WSS 网关 s2 token 获取
  room.py              # openroom API (create/update/close room)
  packet.py            # MiniClientPacket / MiniServerPacket encode/decode
  player.py            # MiniPlayer + FakeConnection
  msgcode_registry.py  # cmd_id ↔ proto class 映射 (667 个 codes)
  packetevents/        # event handler (按 cmd 分文件)
    enter_world.py     # cmd 1001 → ENTER_WORLD_HC + chunks 推送
    block_punch.py     # cmd 5090 → PB_BlockUpdateHC (设 air) [未生效]
    block_interact.py  # cmd 3002 → PB_BlockUpdateHC (设玩家手中方块) [未生效]
    select_shortcut.py # cmd 5098 → 更新 player.selected_block_id
    sync_move.py       # cmd 4047 → 移动同步 (MC bridge, 当前 stub)
    chat.py heartbeat.py move_item.py grid_swap.py ...
  proto/               # protobuf descriptors (从 .proto 重新编译)
raknet_proxy/
  src/
    main.cpp           # 入口 + CLI parse + 业务回调
    proxy.cpp/h        # 双端口 RakNet proxy + NatPunchthrough plugins
    backend_bridge.cpp/h  # TCP bridge to Python backend
  build/Release/mn2mc_proxy.exe
```

### 调试工具
```
inspect_chunk.py       # 单独解压验证 cachetrunk 文件 (LZMA + FlatBuffers 头分析)
test_crypto.py         # XXTEA 加解密验证
sniff_all.py / sniff_http.py  # 抓包 (网络分析阶段用过)
capture_and_parse.py   # protobuf 解码工具
mn2mc_test_connect.py  # 早期单机连接测试
test_raknet_server.py  # aiorak 单机测试 (单端口模式)
```

### 已废弃 / 旧版
```
main.py                # 旧入口 (用 aiorak 单端口模式, 不再用)
room_only.py           # 中间产物 (只跑 auth+房间, 已被 backend.py 替代)
mn2mc_gateway.py       # 早期网关探索代码
```

---

## 五、启动方式

```bash
# 1. Python backend (主入口)
cd E:\TEMP_SHARE\MN2MC
python backend.py
# → 登录、创房、加载 90 真实 chunks、监听 TCP :19134

# 2. C++ RakNet proxy (另一窗口)
"E:/TEMP_SHARE/MN2MC/raknet_proxy/build/Release/mn2mc_proxy.exe" \
    --mode dual \
    --port 19132 \
    --host-port 19133 \
    --guid 598340631 \
    --lan-ip 192.168.1.7 \
    --backend 127.0.0.1:19134

# 3. 客户端: 迷你世界 → 联机大厅 → 搜索房间 (按 UID 598340631)
```

C++ proxy 重新编译：
```bash
cd raknet_proxy/build && cmake --build . --config Release
```

---

## 六、待办 / 已知问题

### 优先级 P0：方块交互
- `PB_BlockUpdateHC` 发出去客户端不渲染
- 协议字段已逆向完整，wire 编码已确认
- 可能原因：
  - wire 字节级别仍有 1-bit 偏差（用 `[BUILD-BU]` log 对照 hook 抓真实包）
  - 缺少其他必填字段（如 `ContainerBufUnzipLen` 即使无 container 也要发？）
  - 客户端要求来自特定 host source uid
- **下一步**：装 Dobby v8 hook 5 (BlockUpdateHC parser @ 0x89E75C0) 抓我们发的包看客户端解析过程
  - 注意：装 hook 5 之前 NAT 失败过一次，可能 hook 时机问题，可以试试在 ENTER_WORLD_HC 之后才安装

### P1：物品栏 / 容器
- `PB_GridSwap` / `PB_GridDiscard` / `PB_BackPackEquipWeaponCH` 当前 handler 都依赖 `player.mcclient`（MC bridge）
- 需要服务端实现：维护虚拟 inventory state，响应客户端操作

### P2：MC bridge
- Node.js `prismarine-*` 依赖坏：`minecraft-data/data/pc/common/features.json` 缺失
- 当前 graceful skip，所有 MC 相关功能空跑
- 修复路径：`pip install --upgrade prismarine-*` 或手动 `npm i minecraft-data`

### P3：完整 chunk 生成
- 当前只能转发本地 cachetrunk 真实文件，世界固定在 OWID=72954558563850
- 自定义地图需要逆向 chunk FlatBuffers schema (`sub_67FF400`, 8120 字节)
- 已知字段：vtable 18 个 entries，root @ offset 44, vtable @ offset 8

---

## 七、调试工具

### Dobby hook (`E:\TEMP_SHARE\dobby_hook_trace\app\src\main\cpp\native-lib.cpp`)
v8 部署的 5 个 hook：
```
0x9AED538  lws_ssl_capable_write (WSS 出站抓包)
0x8DF2E10  RakNet sendto wrapper (UDP 出站抓包 + 完整 RakNet 解析)
0x76ACC40  NatpunchConnected (强制 state 1→3 跳过 NAT，已不需要)
0x66C8CF8  version_check (auto-patch 版本号为 14)
0x89E75C0  PB_BlockUpdateHC parser (入站 cmd=104 抓包 dump 字段) ← 用于位编码逆向
```

**安装 hook 5 时观察到 NAT 失败现象**——可能 hook 时机问题，建议改成"延迟到 ENTER_WORLD 后安装"。

### IDA 脚本目录
`E:\TEMP_SHARE\ida_scripts\` 下有 40+ 个针对 1.56 SO 的反编译脚本和报告，关键的有：
- `liblibGameApp156_connection_debug_report.txt` — 连接状态机
- `liblibGameApp156_chunk_decode_focus_report.txt` — chunk 解压
- `liblibGameApp156_blockupdate_parser_report.txt` — PB_BlockUpdateHC wire 格式
- `liblibGameApp156_block_update_reverse_report.txt` — 块更新相关

### Lua 反编译
迷你世界用魔改 LuaJIT (header `1B 4C 4A 90`)，用 `E:\TEMP_SHARE\ljd-master-xiuzheng`：
```bash
python main.py --polish <lua_bytecode_file>
```
关键 Lua 文件已反编译到 `E:\TEMP_SHARE\ida_scripts\decompiled_*.txt`：
- `decompiled_block.txt` — services/block.lua (host-side Block API)
- `decompiled_ugc_block.txt` — ugc framework block
- `decompiled_chunk_lua.txt` — chunk service stub
- `decompiled_enter_world_*.txt` — 进世界协议
- `decompiled_managerbase_lua.txt` — 客户端 manager base
- `decompiled_roomservice_lua.txt` — 房间服务 (auth/room 流程参考)

---

## 八、关键的"踩坑"经验

1. **打 hook 时确认它不影响早期协议**：hook 5 (BlockUpdateHC parser) 实测干扰 NAT punch，疑似 hook 安装时机太早

2. **proto 字段类型陷阱**：
   - `PB_BlockUpdateHC` 的 `Blocks/BlocksEx/BlockStateIndex` 都是 `repeated uint32`（不是 packed default，但客户端两种 wire format 都支持）
   - `PB_Vector3` 不是 `PB_Pos`（很多 sub-message 用前者，没 `Map` 字段）

3. **OWID 必须全局统一**：room_extra.MapID / WorldDesc.WorldId / RoleData.OWID / ChunkSaveDB.OWID 任何一处不一致都可能导致客户端 reject chunks 或卡 loading

4. **chunks 推送时机**：必须 ENTER_WORLD_HC 之后发，否则客户端 `*(world_state+1) & 2` flag 未置位，整个 chunk 解压被跳过

5. **C++ 代理作为 __main__ 的导入陷阱**：`backend.py` 作为 __main__ 运行时，从 packetevents 里 `import backend` 是空模块。必须用 `sys.modules['__main__']` 访问

6. **enter_world.py 的 `ActorSyncFrequency` 字段不存在于 1.56**：旧版字段，已删除（新字段名 `MoveSyncType`）

---

## 九、记忆备份位置

详细笔记在 Claude Code 记忆系统：
```
C:\Users\PC\.claude\projects\C--Users-PC\memory\
├── MEMORY.md (索引)
├── project_miniworld_mc_bridge.md          (MN ↔ MC bridge 终极目标)
├── project_miniworld_milestone.md          (本里程碑 + BlockUpdateHC bit pack)
├── project_miniworld_connection_statemachine.md  (UDPConnection 三条路径)
├── project_miniworld_chunk_format.md       (FlatBuffers chunk 格式)
├── project_miniworld_account_uid.md        (账号 UID 协议)
├── reference_miniworld_ida_offsets.md      (IDA 偏移参考表)
└── reference_miniworld_bytecode_path.md    (LuaJIT 反编译路径)
```
