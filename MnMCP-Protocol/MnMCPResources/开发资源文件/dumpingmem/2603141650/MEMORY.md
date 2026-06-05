# Memory

## MINIWORLD PKG Reverse Engineering (2026-03)
- PKG unpacker **v11** at `E:\TEMP_SHARE\Miniworld_pkg_unpack\pkg_unpacker.py`
  - 支持 v1 (PC端) 和 v17 (手机端)，自动识别版本
  - v17 supports --decode-textures; v1 直接原始字节提取
  - **v11新增**: 解包时自动转换二进制格式为JSON (blockmesh等)
- Python path: `C:\Program Files\Python310\python.exe`
- Full extract verified:
  - common_res.pkg (v17, 894MB): 42358 extracted, **18932 PNG**, 0 failed
  - material_res.pkg (v1, 14.7MB): **15423 extracted**, 0 failed (PC端DX11 shaders/materials)

### PKG Format — v17 (手机端)
1. **Header**: field0(4) version=17(4) index_offset(4) index_size(4); index_offset+index_size==file_size
2. **Section 1**: count(4) + N×44B `{ hash1[16] uncomp_offset[4] uncomp_size[4] hash2[16] flags[4] }`
3. **Section 3**: `count(4)` then `[name_len(4) + name(pad到4字节) + val(4)]`; val bit31=1 → Section2
4. **Decomp offset bias = 16**: block_uncomp_offsets start at 16 (PKG header size)
5. **Uncompressed blocks**: when `comp_size >= uncomp_size`, data is raw (not LZ4)

### PKG Format — v1 (PC端，material_res.pkg)
1. **Header**: 与v17完全相同
2. **Section 1**: count(4) + N×**28B** `{ hash[16] file_offset[4] file_size[4] flags[4] }` (无第二组hash)
3. **Section 3**: 紧跟Section1，`[name_len(4) + name(**无填充**) + val(4)]`；无Section2/Section4
4. **数据区**: 原始字节，无LZ4块压缩，file_offset直接是PKG文件内字节偏移
5. **文件净化**: Windows禁止字符 `<>:|?*` → 下划线（sanitize_path()）

### Texture Format (container at offset 0, payload at offset 107)
- Container header: 12 uint32 LE. h[5]=width, h[6]=height, h[7]=payload_size, h[8]=asset_type, h[9]=mips, h[11]=faces
- **type 0x41 CRN**: magic `48 78` at offset 107. CRN header (BE): width@119, height@121, levels@123, faces@124, format@125. Skip if faces!=1 or format not in (10,11,12). Use `unpack_unity_crunch` + `decode_etc2a8`
- **type 0x32**: **ASTC 6x6** (16 bytes/6x6 block). Use `decode_astc(data, w, h, 6, 6)` at offset 107
- **type 0x30, 0x3F**: 16 bytes/4x4 block. Use `decode_etc2a8` at offset 107
- **type 0x04**: RGBA32 raw at offset 107
- **type 0x05**: ARGB32 raw at offset 107 (use 'ARGB' Pillow mode)
- **type 0x03**: RGB24 raw at offset 107
- **type 0x01**: Alpha8 raw at offset 107
- **Image orientation fix**: all decoded textures require `FLIP_LEFT_RIGHT` then `rotate(180)` to be human-readable (= vertical flip). Applied in decode_texture() after frombytes.

### Decode Rate (v10, v17 纹理)
- **18,932 PNG** decoded, 0 failed; 0x32=99.8%, 0x41=99.9%, 0x30=99.7%, 0x3F=100%
- Cubemap textures (CRN faces!=1) must be skipped to avoid segfault in texture2ddecoder
- **Entropy diagnostic**: correct decodes give entropy ~4-7; bad decode ~7.7+ (noise)

### Key Libraries
- `texture2ddecoder`: `unpack_unity_crunch`, `decode_etc2a8`, `decode_etc2`, `decode_astc`
- `Pillow`: Image.frombytes for BGRA/RGBA/ARGB/RGB/L modes; transpose+rotate for orientation
- XXTEA key for Lua: `{0xF46E8EB4, 0xEE3ED14E, 0x75416160, 0xF49C720E}`

## Binary Conversion Tools (2026-03-06)
工具位置: `E:\TEMP_SHARE\Miniworld_pkg_unpack\`

### 已完成
1. **parse_binary.py** - blockmesh解析器，已转换1701个文件为JSON
2. **binary_to_readable.py** - 通用二进制转可读格式（hex dump + 字符串提取）
3. **parse_formats.py** - mat/mesh格式解析器
4. **generate_summary.py** - 生成格式汇总报告

### 主要格式统计
- **blockmesh** (3402): 方块网格，平均14.55KB
- **skanim** (6074): 骨骼动画，平均0.97KB
- **emo** (4396): 表情/动作，平均9.10KB
- **mat** (4168): 材质定义，平均2.06KB
- **prefab** (2580): 预制体，平均28.79KB
- **ent** (2228): 实体定义，平均2.95KB
- **mesh** (2096): 网格模型，平均7.08KB
- **omod** (1790): 大型模型，平均166.98KB
- **lua** (9732): LuaJIT字节码（未加密）

### 格式特征
- **ENT**: magic `89 67 45 23`, 包含EntityData/EntityMotionData/ParticleEmitterData等section
- **MAT**: 材质参数列表（_EmissionTex, _MixTex, _NormalTex等）
- **MESH**: version + hash头部
- **LUA**: LuaJIT字节码 `1b 4c 4a`, 需ljd反编译

## AES加密逆向分析（2026-03-14）

### vmem 文件说明
- `E:\TEMP_SHARE\VM_passcheck\52EB1-90b07d16.vmem` (4GB)
- **重要**: 这是 **PC端 Windows x86/x64 进程**内存，不是 Android ARM64
- 包含 OpenSSL 1.0.2j (x86)，BlueStacks/MEmu 模拟器进程也在其中
- DHKeyMgr 对象在 `0xd6dc14c0`，字符串 "DHKeyMgr" 在 `0xd6dc14cc`

### libGameApp.so 关键函数（ARM64，IDA分析结果）
| 函数 | RVA | 说明 |
|------|-----|------|
| `evp_ctx_new` | 0x633439C | 初始化AES ctx对象，vtable=off_A7097D0 |
| `evp_aes_init` | 0x633526C | 设置key/iv，展开密钥 |
| `aes_decrypt_impl` | 0x5FC21FC | 解密入口，调用evp_aes_init+sub_6335B80 |
| `get_lua_const_impl` | 0x5FC0108 | `ADD X0,X0,#0x430; RET` 返回self+0x430 |
| `evp_encrypt_update` | 0x6335990 | 加密更新 |

### ARM64 AES ctx 对象内存布局（.so内）
```
obj+0x000 = vtable ptr (RVA 0xA7097D0)
obj+0x008 = initialized flag
obj+0x3CC = key_len  (uint32: 0x10/0x18/0x20)
obj+0x3D0 = iv_len   (uint32: 0x10/0x18/0x20)
obj+0x3D4 = rounds   (uint32: 0xA/0xC/0xE)
obj+0x3D8 = IV[iv_len]
obj+0x3F8 = IV copy2[iv_len]
obj+0x418 = expanded key schedule (rd_key)
obj+0x20C = 解密轮密钥表
```

### AES S-box / 查找表地址（.so RVA）
- `unk_8AC5B9C` — SubBytes S-box
- `unk_8AC6DFC` — Rcon表
- `unk_8AC6E1C/721C/761C/7A1C` — MixColumns表

### PC端 vmem DHKeyMgr 分析结果
- DHKeyMgr 对象 @ `0xd6dc14c0`（Windows堆）
- vtable = `0x78415b71`（指向高熵数据 H=5.77，疑似DH密钥材料）
- 成员 `+0x68/+0x74` → `0x1e798ff0`（H=4.84，含 `40000000` 后跟高熵数据）
- 成员 `+0x00` → `0x78415b71`（64字节高熵，可能是DH公钥/共享密钥）
- PC端用 OpenSSL 1.0.2j x86，AES_KEY结构：rd_key[60](240B) + rounds(4B)
- 高熵AES_KEY候选：`0x60e64`(H=6.38), `0x1cffa8`(H=5.30)
  - `0x60e64` key: `3d2d09646d440b6603f9f1a8e27be915`
  - `0x1cffa8` key: `00b20d7ec3580f5f980584689c16c1f1`

### DHKeyMgr Lua方法表（vmem @ 0xd6dc1800）
| 方法名 | vtable | 数据指针 | 说明 |
|--------|--------|----------|------|
| GenerateClientDHKey | 0x78415b72 | 0x3c6bdd1c | — |
| GetClientPublicKey  | 0x78415b73 | 0x4b897cd6 | 全零，未初始化 |
| SetServerPublicKey  | 0x78415b74 | 0x9c25dc   | — |
| GetServerPublicKey  | 0x78415b75 | 0x38a84df0 | 含指针模式 |
| **GetDHKey**        | 0x78415b76 | **0xf1b649c9** | **H=5.74，最可信** |
| GetLoginModuleName  | 0x78415b77 | 0xa332d97f | — |
| GetLoginDhp         | 0x78415b78 | 0x6a0ebc88 | — |
| GetLoginDhg         | 0x78415b79 | 0xa04d7e0b | — |

### 候选 AES/DH 密钥（从vmem提取，待验证）
**���优先候选 — GetDHKey返回值 @ 0xf1b649c9 (H=5.74):**
```
07fc7ee6c8cf9d71742660ae8ba4d3a0fb67124f783598a34ab3546831de60d2
cc3f5d7bd456d6b64b08f02ea9b3d2cb38bd1c469d1cfb1c794b5b9089da6de3
```
- direct AES-128 ([:16]): `07fc7ee6c8cf9d71742660ae8ba4d3a0`
- direct AES-256 ([:32]): `07fc7ee6c8cf9d71742660ae8ba4d3a0fb67124f783598a34ab3546831de60d2`
- SHA256(64B)[:16]: `b2c579e0da2bac21ee906637dcc3d66c`
- SHA256(64B): `b2c579e0da2bac21ee906637dcc3d66c821e18986dd583a717084429df8e4b15`
- MD5(64B): `8ba0f842d4ad37aa2f88e2bad969e08d`

**其他候选 AES_KEY rd_key[0]:**
- 0x60e64 (H=6.38): `3d2d09646d440b6603f9f1a8e27be915`
- 0x1cffa8 (H=5.30): `00b20d7ec3580f5f980584689c16c1f1`
- 0x78415b71 (H=5.77): `699434e62653b5e8e50c334b09afb28a`

### PC端解密逻辑
- OpenSSL 1.0.2j x86，`AES_KEY` = `rd_key[60](240B) + rounds(4B)`
- AES-128: rounds=10，原始key = rd_key[0:16]
- UDP包格式: `[0x0239][长度2B][未知4B][加密数据]`，加密模式待确认(CBC/GCM)
- DHKeyMgr Lua对象 @ `0xd6dc14c0`，GetDHKey字符串 @ `0xd6dc191c`
- pcap文件: `E:/TEMP_SHARE/mini.pcapng`, `E:/TEMP_SHARE/Miniworld_pkg_unpack/miniworld_capture.pcap`

### 搜索脚本
- `E:\TEMP_SHARE\Miniworld_pkg_unpack\memory_dump\fast_find_aes2.py` — mmap快速搜索
- `E:\TEMP_SHARE\Miniworld_pkg_unpack\memory_dump\filter_aes_hits.py` — 过滤误报

### get_lua_const_impl 分析
```asm
ADD X0, X0, #0x430   ; 00 C4 10 91
RET                   ; C0 03 5F D6
```
返回 `self+0x430`，即对象内 ConstAtLua 表指针偏移。

## Network Protocol Analysis (2026-03-06/07)
位置: `E:\TEMP_SHARE\Miniworld_pkg_unpack\`

### 核心架构
- **TCP (8080)**: 未加密，Protobuf格式 `[长度4B][消息ID 4B][数据]`
- **UDP (8000/4023)**: **AES-GCM加密**，格式 `[0x0239][长度2B][未知4B][加密数据]`
- 加密库: libilink_network.so (7.6MB)
- 关键函数: `AesGcmEncrypt`, `AesGcmDecrypt`, `AesGcmEncryptWithCompress`

### AES-GCM加密细节 (2026-03-07)
- **算法**: AES-128/256-GCM (Galois/Counter Mode)
- **密钥管理**: 动态生成（非硬编码），使用ECDH密钥交换
- **测试结果**:
  - 从.rodata提取的50个密钥均无法正确解密
  - 测试了AES-128所有模式(ECB/CBC/CTR/CFB/OFB/GCM)均失败
  - Protobuf解析失败，说明密钥不对
- **工具**:
  - `test_aes_gcm.py` - AES-GCM测试脚本
  - `test_aes128.py` - AES-128全模式测试
  - `test_multiple_packets.py` - 多包测试
- **结论**: 必须使用动态分析获取运行时密钥

### 下一步（必须）
1. **Frida Hook** - Hook `AesGcmDecrypt` 函数捕获运行时密钥/nonce/AAD
2. **IDA Pro深度分析** - 分析libilink_network.so的ECDH密钥交换逻辑
3. **抓包分析握手** - 分析TLS/ECDH握手过程，提取密钥交换参数

## Auth签名算法（已破解，2026-03-07）

### 算法
```python
auth = md5(secret_key + timestamp).hexdigest()
```

### 密钥
```
SECRET_KEY = "01c13e71f95db3bf60483a98a23d5327"
```
来源: `pkg/game_script/script/luascript/clientex/accountmanager.lua`

### URL格式
```
https://minipal.mini1.cn/v1/getMeta?mini_id={uid}&s2t={server_ts}&auth={md5}&ts={ts}&sign_type=client&appid=0&res_id={rid}
```

### 关键函数 (libGameApp.so)
- 0x64A2CA8 - auth生成核心
- 0x2F227B4 - Lua函数调用接口(函数805返回密钥)

### 工具
- `generate_auth.py` - 签名生成器（可用）
- `AUTH_ALGORITHM_COMPLETE.md` - 完整算法文档

## 联机协议（已分析，2026-03-07）

### 协议类型
- **Protobuf** 二进制序列化
- **CH** (Client→Host) 客户端发送
- **HC** (Host→Client) 服务器推送

### 核心消息
```protobuf
// 客户端→服务器
PB_RoleEnterWorldCH          // 进入世界
PB_HeartBeatCH               // 心跳
PB_BackPackShortcutOpCH      // 背包操作
PB_EquipWeaponCH             // 装备武器

// 服务器→客户端
PB_AchievementSyncHC         // 成就同步
PB_HomelandRanchInfoHC       // 家园信息
DispatcherMessage_PB_CHAT_HC // 聊天消息
```

### 关键函数 (libGameApp.so)
- 0x2F7B8AC - sendToHost (发送消息)
- 0x31FFBC8 - OnRecvMessage (接收消息)
- 0x3732D08 - OnRecvMultiplayerMessage (多人消息)

### 数据结构 (game.common)
```protobuf
PB_Vector3                   // 3D向量
PB_RoleInfo                  // 角色信息
PB_PlayerVipInfo             // VIP信息
PB_MoveMotion                // 移动动作
```

### 分析文档
- `MULTIPLAYER_PROTOCOL_ANALYSIS.md` - 完整联机协议
- `FINAL_REPORT.md` - 总体分析报告
- 7个IDA分析脚本

# currentDate
Today's date is 2026-03-07.
