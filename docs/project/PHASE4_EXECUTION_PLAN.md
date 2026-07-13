# Phase 4: Minecraft Protocol Client 开发计划

**日期**: 2026-06-05  
**阶段**: Phase 4/8  
**目标**: 实现纯 Python 的 Minecraft 协议客户端

---

## 1. 需求分析

### 1.1 MN2MC 现有实现

**技术栈**: JavaScript Bridge + Node.js minecraft-protocol
```python
# MN2MC 使用 JavaScript bridge
mcprotocol = require("minecraft-protocol")
client = mcprotocol.createClient(options)
```

**问题**:
- ❌ 依赖 Node.js 环境
- ❌ 性能开销（跨语言调用）
- ❌ 部署复杂
- ❌ 类型不安全

### 1.2 MnMCP 3 目标

**技术栈**: 纯 Python 实现
```python
# MnMCP 3 纯 Python
from mcp_mc.client import MCPMinecraftClient
client = MCPMinecraftClient(server, username)
await client.connect()
```

**优势**:
- ✅ 纯 Python，部署简单
- ✅ 高性能（无跨语言开销）
- ✅ 100% 类型注解
- ✅ 模块化架构

---

## 2. 技术选型

### 2.1 可选方案

| 方案 | 库 | 优点 | 缺点 | 选择 |
|------|-----|------|------|------|
| A | mcproto | Python原生 | 不完整 | 备选 |
| B | py-minecraft-protocol | Python原生 | 更新慢 | 备选 |
| C | quarry | Python原生 | 仅协议 | 备选 |
| D | 自研协议栈 | 完全可控 | 工作量大 | ✅ 主选 |
| E | 魔改 Java bridge | 继承MN2MC | 仍有JS依赖 | ❌ 放弃 |

### 2.2 决策: 自研 + 移植

**策略**: 自研 + 参考开源实现
1. 使用 `quarry` 库作为参考
2. 移植 MN2MC 的协议逆向成果
3. 自建完整的 MC 1.19.2 协议栈

---

## 3. 实现计划

### 3.1 模块划分

```
mcp_mc/                      # MC客户端模块
├── __init__.py
├── client.py                # 主客户端 (200行)
├── protocol/                # 协议实现
│   ├── __init__.py
│   ├── connection.py        # 连接管理 (150行)
│   ├── packets.py           # 包定义 (300行)
│   ├── types.py             # 数据类型 (200行)
│   └── handshake.py         # 握手流程 (100行)
├── player/                  # 玩家数据
│   ├── __init__.py
│   ├── state.py             # 玩家状态 (150行)
│   └── inventory.py         # 背包系统 (200行)
├── world/                   # 世界数据
│   ├── __init__.py
│   ├── chunk.py             # 区块解析 (200行)
│   └── block.py             # 方块处理 (100行)
├── events/                  # 事件系统
│   ├── __init__.py
│   ├── base.py              # 事件基类 (50行)
│   ├── login.py             # 登录事件 (100行)
│   ├── game.py              # 游戏事件 (150行)
│   └── chat.py              # 聊天事件 (50行)
└── utils/
    ├── __init__.py
    ├── nbt.py               # NBT解析 (150行)
    └── uuid.py              # UUID处理 (50行)
```

### 3.2 核心功能清单

| 功能 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| **连接管理** | P0 | 4h | TCP连接，状态机 |
| **握手协议** | P0 | 4h | Handshake，Login |
| **加密** | P0 | 4h | AES-CFB8 + RSA |
| **压缩** | P0 | 2h | Zlib压缩 |
| **玩家状态** | P0 | 4h | 位置，朝向，属性 |
| **聊天** | P1 | 4h | 发送/接收消息 |
| **背包** | P1 | 6h | 物品槽位，交互 |
| **区块** | P1 | 8h | 区块加载，解析 |
| **方块** | P1 | 6h | 放置，破坏 |
| **实体** | P2 | 8h | 生物，玩家 |
| **容器** | P2 | 4h | 箱子，熔炉 |
| **高级功能** | P3 | - | 红石，命令 |

---

## 4. 数据结构

### 4.1 玩家状态

```python
@dataclass
class MCPlayerState:
    """Minecraft 玩家状态"""
    entity_id: int = 0
    uuid: UUID = field(default_factory=UUID)
    username: str = ""
    
    # 位置 (双精度浮点)
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    # 朝向
    yaw: float = 0.0      # 水平 (-180 ~ 180)
    pitch: float = 0.0    # 垂直 (-90 ~ 90)
    
    # 状态
    on_ground: bool = True
    is_sneaking: bool = False
    is_sprinting: bool = False
    
    # 游戏模式
    gamemode: Gamemode = Gamemode.SURVIVAL
    
    # 生命值
    health: float = 20.0
    food: int = 20
    saturation: float = 5.0
```

### 4.2 物品堆

```python
@dataclass
class MCItemStack:
    """Minecraft 物品堆"""
    item_id: int = 0
    count: int = 0
    nbt: Optional[dict] = None
    
    # 槽位
    slot: int = -1
```

### 4.3 背包

```python
@dataclass
class MCInventory:
    """Minecraft 背包"""
    # 物品栏 (36槽: 0-35)
    items: List[MCItemStack] = field(default_factory=list)
    
    # 装备栏 (4槽: 头盔,胸甲,护腿,靴子)
    armor: List[MCItemStack] = field(default_factory=list)
    
    # 副手
    offhand: Optional[MCItemStack] = None
    
    # 手持槽位
    hotbar_slot: int = 0
```

---

## 5. 协议实现

### 5.1 握手流程

```
Client                                    Server
  |                                         |
  |----- Handshake (0x00) ---------------->|
  |  {version, addr, port, next_state=2}    |
  |                                         |
  |----- Login Start (0x00) --------------->|
  |  {username}                             |
  |                                         |
  |<---- Encryption Request (0x01) ---------|
  |  {server_id, pubkey, verify_token}      |
  |                                         |
  |----- Encryption Response (0x01) ------->|
  |  {shared_secret, verify_token}          |
  |                                         |
  |<---- Set Compression (0x03) ------------|
  |  {threshold}                            |
  |                                         |
  |<---- Login Success (0x02) --------------|
  |  {uuid, username}                       |
  |                                         |
  |<---- Join Game (0x26) -----------------|
  |  {entity_id, gamemode, dimension, ...}  |
  |                                         |
  |----- Client Settings (0x07) ----------->|
  |  {locale, view_distance, chat_flags}    |
  |                                         |
  |<---- Player Position And Look (0x38) ----|
  |  {x, y, z, yaw, pitch}                  |
  |                                         |
  |----- Teleport Confirm (0x00) ----------->|
  |                                         |
```

### 5.2 关键数据包

| 包名 | ID | 方向 | 说明 |
|------|-----|------|------|
| Handshake | 0x00 | C->S | 协议版本，目标地址 |
| Login Start | 0x00 | C->S | 用户名 |
| Encryption Request | 0x01 | S->C | 公钥，验证令牌 |
| Encryption Response | 0x01 | C->S | 共享密钥，验证令牌 |
| Login Success | 0x02 | S->C | UUID，用户名 |
| Join Game | 0x26 | S->C | 游戏初始状态 |
| Player Position And Look | 0x38 | S->C | 玩家位置和朝向 |
| Teleport Confirm | 0x00 | C->S | 确认传送 |
| Keep Alive | 0x12 | S->C / C->S | 心跳 |
| Chat Message | 0x0F | C->S | 发送消息 |
| Chat | 0x0E | S->C | 接收消息 |

---

## 6. 实现步骤

### 6.1 第一阶段: 基础连接 (4h)

- [ ] 创建 `MCProtocolConnection` 类
- [ ] 实现 TCP 连接
- [ ] 实现 VarInt 编解码
- [ ] 实现基本数据类型

### 6.2 第二阶段: 握手 (4h)

- [ ] Handshake 数据包
- [ ] Login Start
- [ ] 状态机管理

### 6.3 第三阶段: 加密 (4h)

- [ ] AES-CFB8 加密
- [ ] RSA 密钥交换
- [ ] 验证令牌处理

### 6.4 第四阶段: 游戏状态 (4h)

- [ ] Join Game 处理
- [ ] 玩家状态初始化
- [ ] 位置同步

### 6.5 第五阶段: 事件系统 (4h)

- [ ] 事件注册
- [ ] 数据包分发
- [ ] 回调处理

**第一阶段总计**: 20h

---

## 7. 与 MNW 集成

### 7.1 数据流

```
┌─────────────────────────────────────────────────────────────┐
│                    MnMCP 3 桥接架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  MiniWorld   │         │  Minecraft   │                 │
│  │   Client     │◄───────►│   Client     │                 │
│  │  (aiorak)    │         │ (mcp_mc)     │                 │
│  └──────┬───────┘         └──────┬───────┘                 │
│         │                        │                         │
│         │     ┌──────────┐       │                         │
│         └────►│  Bridge  │◄──────┘                         │
│               │  Core    │                                    │
│               └────┬─────┘                                    │
│                    │                                          │
│                    ▼                                          │
│               ┌──────────┐                                    │
│               │  Events  │                                    │
│               └──────────┘                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 关键转换

| 功能 | MNW 格式 | MC 格式 | 转换器 |
|------|----------|---------|--------|
| 位置 | Vector3f | double x3 | 直接映射 |
| 朝向 | Rotation | yaw/pitch | 单位转换 |
| 聊天 | string | JSON | 格式转换 |
| 方块 | uint32 | varint | ID映射 |
| 物品 | GridItem | ItemStack | 数据映射 |

---

## 8. 验收标准

### 8.1 功能验收

| 测试项 | 标准 | 方法 |
|--------|------|------|
| 连接到MC服务器 | 成功完成握手 | 单元测试 |
| 加密通信 | 通过在线模式认证 | 集成测试 |
| 接收数据包 | 正确处理Join Game | 单元测试 |
| 发送数据包 | Keep Alive正常 | 单元测试 |
| 位置同步 | 与服务器同步 | 集成测试 |
| 聊天 | 收发正常 | 集成测试 |

### 8.2 质量验收

- [ ] 类型注解覆盖率 100%
- [ ] 单元测试覆盖率 >80%
- [ ] 文档字符串完整
- [ ] 无 mypy 错误
- [ ] 无 pylint 警告

---

## 9. 风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| 协议复杂度高 | 高 | 高 | 分阶段实现，优先核心功能 |
| 加密实现困难 | 中 | 高 | 参考 quarry 实现 |
| 时间超期 | 中 | 中 | 先实现 MVP，后续迭代 |
| 测试不足 | 中 | 中 | 建立持续集成 |

---

## 10. 进度跟踪

| 阶段 | 任务 | 计划 | 实际 | 状态 |
|------|------|------|------|------|
| 4.1 | 基础连接 | 4h | - | ⏳ |
| 4.2 | 握手流程 | 4h | - | ⏳ |
| 4.3 | 加密实现 | 4h | - | ⏳ |
| 4.4 | 游戏状态 | 4h | - | ⏳ |
| 4.5 | 事件系统 | 4h | - | ⏳ |
| **总计** | | **20h** | | |

---

**Phase 4 开发计划完成，开始实施！**
