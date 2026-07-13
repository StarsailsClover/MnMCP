# Phase 5: MiniWorld 客户端 开发计划

**日期**: 2026-06-05  
**阶段**: Phase 5/8  
**目标**: 实现 MiniWorld 协议客户端

---

## 1. 需求分析

### 1.1 MN2MC 现有实现

**技术栈**: Python + aiorak (RakNet)
```python
# MN2MC 使用 aiorak 进行 RakNet 通信
import aiorak
conn = aiorak.Connection()
await conn.connect(ip, port)
```

**核心功能**:
- ✅ RakNet 连接管理
- ✅ MiniWorld 认证 (HTTP)
- ✅ 房间进入流程
- ✅ ProtoBuf 编解码
- ✅ 玩家控制 (移动/交互)
- ✅ 数据包转发

### 1.2 MnMCP 3 目标

**移植策略**:
1. 保留 aiorak 连接层
2. 重构协议层 (MN2MC 的 msgcode_registry)
3. 整合 MnMCP v3 的架构
4. 统一事件系统

---

## 2. 实现计划

### 2.1 模块划分

```
mcp_mini/                    # MiniWorld 客户端模块
├── __init__.py
├── client.py                # 主客户端 (300行)
├── connection.py            # RakNet 连接 (200行)
├── auth.py                  # 认证模块 (150行)
├── room.py                  # 房间管理 (150行)
├── player.py                # 玩家控制 (200行)
├── protocol/
│   ├── __init__.py
│   ├── packets.py           # 数据包定义 (200行)
│   ├── msgcode.py           # 消息码 (300行)
│   └── codec.py             # 编解码器 (150行)
├── events/
│   ├── __init__.py
│   ├── login.py             # 登录事件 (100行)
│   ├── world.py             # 世界事件 (150行)
│   └── player.py            # 玩家事件 (100行)
└── utils/
    ├── __init__.py
    ├── vector.py            # 向量 (50行)
    └── uuid.py              # UUID (50行)
```

### 2.2 功能清单

| 功能 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| **RakNet 连接** | P0 | 2h | aiorak 封装 |
| **消息码系统** | P0 | 2h | 82个消息码 |
| **认证流程** | P0 | 2h | HTTP 认证 |
| **房间进入** | P0 | 2h | 进入房间流程 |
| **玩家移动** | P1 | 2h | 位置同步 |
| **聊天** | P1 | 2h | 收发消息 |
| **方块交互** | P1 | 2h | 放置/破坏 |
| **数据包转发** | P2 | 2h | 到 MC 客户端 |

**总计**: 16小时

---

## 3. 数据结构

### 3.1 MiniWorld 玩家

```python
@dataclass
class MiniPlayer:
    """MiniWorld 玩家"""
    uin: int = 0
    name: str = ""
    room_id: str = ""
    
    # 位置
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    # 朝向
    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0
    
    # 状态
    hp: int = 100
    max_hp: int = 100
    
    # 权限
    is_host: bool = False
    is_leader: bool = False
```

### 3.2 房间信息

```python
@dataclass
class RoomInfo:
    """房间信息"""
    room_id: str = ""
    room_name: str = ""
    world_id: str = ""
    
    # 配置
    max_players: int = 10
    cur_players: int = 0
    
    # 地图
    seed: int = 0
    map_type: int = 0
    
    # 状态
    is_started: bool = False
    is_locked: bool = False
```

---

## 4. 协议实现

### 4.1 认证流程

```
Client                                    Server
  |                                         |
  |----- HTTP POST /v2/user/login --------->|
  |  {uin, passwd_md5, device_id, ...}      |
  |                                         |
  |<---- JSON Response ---------------------|
  |  {code, aid, token, ...}                |
  |                                         |
  |----- HTTP GET /v2/room/list ----------->|
  |  {aid, token}                           |
  |                                         |
  |<---- Room List ------------------------|
  |                                         |
  |----- HTTP POST /v2/room/join ---------->|
  |  {room_id}                              |
  |                                         |
  |<---- Room Server Info ------------------|
  |  {ip, port}                             |
  |                                         |
```

### 4.2 游戏流程

```
Client                                    Game Server
  |                                         |
  |----- RakNet Connect ------------------->|
  |                                         |
  |----- Msg 1001 (Enter World) ---------->|
  |  {uin, aid, token, ...}                 |
  |                                         |
  |<---- Msg 1002 (Enter World Ack) -------|
  |                                         |
  |<---- Msg 1006 (Player Enter AOI) ------|
  |                                         |
  |----- Msg 2001 (Move) ------------------>|
  |                                         |
  |<---- Msg 2004 (Player Move) -----------|
  |                                         |
  |----- Msg 9001 (Chat) ------------------>|
  |                                         |
  |<---- Msg 9002 (Chat Broadcast) --------|
  |                                         |
```

### 4.3 关键消息码

| 消息码 | 名称 | 方向 | 说明 |
|--------|------|------|------|
| 11 | HeartBeatCH | C->S | 心跳请求 |
| 12 | HeartBeatHC | S->C | 心跳响应 |
| 1001 | RoleEnterWorldCH | C->S | 进入世界 |
| 1002 | RoleEnterWorldHC | S->C | 进入确认 |
| 1006 | ActorEnterAOIHC | S->C | 玩家进入视野 |
| 2001 | RoleMoveCH | C->S | 移动请求 |
| 2004 | ActorMoveHC | S->C | 玩家移动 |
| 6001 | PlaceBlockCH | C->S | 放置方块 |
| 6002 | PlaceBlockHC | S->C | 方块放置 |
| 9001 | ChatContentCH | C->S | 聊天消息 |
| 9002 | ChatContentHC | S->C | 聊天广播 |

---

## 5. 实现步骤

### 5.1 第一阶段: 基础连接 (4h)

- [ ] 5.1.1 创建 `MiniConnection` 类
- [ ] 5.1.2 封装 aiorak
- [ ] 5.1.3 实现消息码注册表
- [ ] 5.1.4 实现基本收发

### 5.2 第二阶段: 认证 (4h)

- [ ] 5.2.1 实现 HTTP 认证
- [ ] 5.2.2 房间列表获取
- [ ] 5.2.3 房间进入
- [ ] 5.2.4 连接游戏服务器

### 5.3 第三阶段: 游戏逻辑 (4h)

- [ ] 5.3.1 进入世界流程
- [ ] 5.3.2 玩家状态同步
- [ ] 5.3.3 移动控制
- [ ] 5.3.4 聊天系统

### 5.4 第四阶段: 整合 (4h)

- [ ] 5.4.1 与 MC 客户端统一接口
- [ ] 5.4.2 数据包转发准备
- [ ] 5.4.3 事件系统集成
- [ ] 5.4.4 测试验证

---

## 6. 与 MC 客户端集成

### 6.1 统一接口

```python
# 抽象基类
class ProtocolClient(ABC):
    async def connect(self) -> bool: ...
    async def login(self) -> bool: ...
    async def disconnect(self) -> None: ...
    
    @abstractmethod
    async def send_position(self, x, y, z, yaw, pitch) -> bool: ...
    
    @abstractmethod
    async def send_chat(self, message: str) -> bool: ...

# MC 客户端
class MCPMinecraftClient(ProtocolClient): ...

# MNW 客户端  
class MCPMiniClient(ProtocolClient): ...
```

### 6.2 桥接准备

```python
class MCPBridge:
    def __init__(self):
        self.mc_client: MCPMinecraftClient = ...
        self.mnw_client: MCPMiniClient = ...
    
    async def forward_mnw_to_mc(self, packet):
        # MNW -> MC 转发
        ...
    
    async def forward_mc_to_mnw(self, packet):
        # MC -> MNW 转发
        ...
```

---

## 7. 验收标准

### 7.1 功能验收

| 测试项 | 标准 | 方法 |
|--------|------|------|
| 连接到MNW服务器 | 成功完成认证 | 单元测试 |
| 进入房间 | 收到Enter World Ack | 集成测试 |
| 位置同步 | 与服务器同步 | 集成测试 |
| 聊天 | 收发正常 | 集成测试 |
| 与MC接口一致 | API兼容 | 代码审查 |

### 7.2 质量验收

- [ ] 类型注解覆盖率 100%
- [ ] 单元测试覆盖率 >80%
- [ ] 文档字符串完整
- [ ] 无 mypy 错误

---

## 8. 风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| aiorak 兼容问题 | 低 | 高 | 测试不同版本 |
| 协议细节变化 | 中 | 中 | 对比 MN2MC 实现 |
| 认证流程变化 | 中 | 高 | 关注版本更新 |

---

## 9. 进度跟踪

| 阶段 | 任务 | 计划 | 实际 | 状态 |
|------|------|------|------|------|
| 5.1 | 基础连接 | 4h | - | ⏳ |
| 5.2 | 认证流程 | 4h | - | ⏳ |
| 5.3 | 游戏逻辑 | 4h | - | ⏳ |
| 5.4 | 整合 | 4h | - | ⏳ |
| **总计** | | **16h** | | |

---

**Phase 5 开发计划完成，开始实施！**
