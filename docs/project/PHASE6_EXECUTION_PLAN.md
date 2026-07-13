# Phase 6: 桥接核心 开发计划

**日期**: 2026-06-05  
**阶段**: Phase 6/8  
**目标**: 实现 MC <-> MNW 双向桥接

---

## 1. 需求分析

### 1.1 核心目标

实现 **Minecraft 客户端** 和 **MiniWorld 客户端** 之间的双向数据转发和状态同步。

```
┌─────────────────────────────────────────────────────────────┐
│                    MnMCP 3 桥接架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐        ┌─────────────────┐            │
│  │  MCPMinecraft   │◄──────►│   MCPMiniWorld  │            │
│  │    Client       │        │     Client      │            │
│  │  (TCP/MC协议)   │        │  (UDP/RakNet)   │            │
│  └────────┬────────┘        └────────┬────────┘            │
│           │                          │                      │
│           │    ┌──────────────┐      │                      │
│           └───►│ MCPBridge    │◄─────┘                      │
│                │   Core       │                               │
│                │ ─────────── │                               │
│                │ • 包转发     │                               │
│                │ • 状态同步   │                               │
│                │ • 聊天桥接  │                               │
│                │ • 位置同步   │                               │
│                │ • 方块映射   │                               │
│                └──────────────┘                               │
│                                                             │
│  功能: MC玩家连接到桥接器，桥接器连接到MNW，实现"透明"游戏   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 关键功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| **数据包转发** | MC包 ↔ MNW包 | P0 |
| **玩家同步** | 位置/朝向同步 | P0 |
| **聊天桥接** | 跨游戏聊天 | P0 |
| **方块映射** | MC方块ID ↔ MNW方块ID | P0 |
| **状态同步** | 生命值/背包等 | P1 |
| **实体同步** | 生物/玩家显示 | P1 |

---

## 2. 架构设计

### 2.1 模块划分

```
mcp_core/                    # 桥接核心模块
├── __init__.py
├── bridge.py                # 主桥接器 (400行)
├── packet_router.py         # 包路由 (200行)
├── sync/
│   ├── __init__.py
│   ├── position.py          # 位置同步 (150行)
│   ├── chat.py              # 聊天同步 (100行)
│   └── state.py             # 状态同步 (150行)
├── transform/
│   ├── __init__.py
│   ├── block_mapper.py      # 方块映射 (100行)
│   ├── item_mapper.py       # 物品映射 (100行)
│   └── packet_mapper.py     # 包转换 (200行)
└── utils/
    ├── __init__.py
    └── logger.py            # 桥接日志 (50行)
```

### 2.2 核心类

```python
class MCPBridge:
    """主桥接器"""
    mc_client: MCPMinecraftClient
    mnw_client: MCPMiniClient
    router: PacketRouter
    sync_manager: SyncManager
    
    async def start() -> None: ...
    async def stop() -> None: ...
    async def forward_mc_to_mnw(packet) -> None: ...
    async def forward_mnw_to_mc(packet) -> None: ...

class PacketRouter:
    """包路由器"""
    routes: Dict[int, Callable]
    
    def register(msg_code: int, handler: Callable) -> None: ...
    async def route(packet: MCPacket, direction: Direction) -> None: ...

class SyncManager:
    """同步管理器"""
    position_sync: PositionSync
    chat_sync: ChatSync
    state_sync: StateSync
```

---

## 3. 实现计划

### 3.1 第一阶段: 基础桥接 (4h)

- [ ] 6.1.1 创建 `MCPBridge` 类
- [ ] 6.1.2 集成 MC 和 MNW 客户端
- [ ] 6.1.3 实现包捕获/转发框架
- [ ] 6.1.4 实现启动/停止流程

### 3.2 第二阶段: 包路由 (4h)

- [ ] 6.2.1 创建 `PacketRouter`
- [ ] 6.2.2 实现消息码路由表
- [ ] 6.2.3 注册关键包处理器
- [ ] 6.2.4 实现双向转发

### 3.3 第三阶段: 位置同步 (4h)

- [ ] 6.3.1 实现 MC 位置接收
- [ ] 6.3.2 转换坐标系
- [ ] 6.3.3 发送 MNW 移动请求
- [ ] 6.3.4 实现位置平滑插值

### 3.4 第四阶段: 聊天/方块 (4h)

- [ ] 6.4.1 实现聊天转发
- [ ] 6.4.2 实现方块放置转发
- [ ] 6.4.3 实现方块破坏转发
- [ ] 6.4.4 测试完整流程

**总计**: 16小时

---

## 4. 关键技术

### 4.1 包转发流程

```python
# MC -> MNW 转发
@mc_client.on('packet')
async def on_mc_packet(packet):
    # 1. 解析 MC 包
    mc_data = parse_mc_packet(packet)
    
    # 2. 转换数据
    mnw_data = transform_mc_to_mnw(mc_data)
    
    # 3. 构建 MNW 包
    mnw_packet = build_mnw_packet(mnw_data)
    
    # 4. 发送
    await mnw_client.send_packet(mnw_packet)

# MNW -> MC 转发
@mnw_client.on('packet')
async def on_mnw_packet(packet):
    # 1. 解析 MNW 包
    mnw_data = parse_mnw_packet(packet)
    
    # 2. 转换数据
    mc_data = transform_mnw_to_mc(mnw_data)
    
    # 3. 构建 MC 包
    mc_packet = build_mc_packet(mc_data)
    
    # 4. 发送
    await mc_client.send_packet(mc_packet)
```

### 4.2 位置同步

```python
# 坐标转换
# MC: X (东+), Y (上+), Z (南+)
# MNW: X (东+), Y (上+), Z (南+)
# 坐标系相同，直接映射

# 朝向转换
# MC: Yaw (-180~180, 0=南), Pitch (-90~90)
# MNW: Yaw (0~360, 0=北), Pitch (-90~90)
# 需要转换

def mc_yaw_to_mnw(yaw: float) -> float:
    """MC Yaw -> MNW Yaw"""
    # MC: 0=南, -90=东, 180=北, 90=西
    # MNW: 0=北, 90=东, 180=南, 270=西
    mnw_yaw = (yaw + 180) % 360
    return mnw_yaw

def mnw_yaw_to_mc(yaw: float) -> float:
    """MNW Yaw -> MC Yaw"""
    mc_yaw = (yaw - 180) % 360
    if mc_yaw > 180:
        mc_yaw -= 360
    return mc_yaw
```

### 4.3 方块映射

```python
# 使用已有的 BlockMapper
from mcp_mapping.blocks_integrated import BlockMapperIntegrated

mapper = BlockMapperIntegrated()

# MC -> MNW
mc_block_id = 1  # Stone
mnw_block_id = mapper.mc_to_mnw(mc_block_id)

# MNW -> MC
mnw_block_id = 504
mc_block_id = mapper.mnw_to_mc(mnw_block_id)
```

---

## 5. 数据结构

### 5.1 桥接配置

```python
@dataclass
class BridgeConfig:
    """桥接配置"""
    # MC 服务器
    mc_host: str = "127.0.0.1"
    mc_port: int = 25565
    
    # MNW 服务器 (通过代理或直连)
    mnw_host: str = "127.0.0.1"
    mnw_port: int = 19132
    
    # 认证
    mnw_uin: int = 0
    mnw_passwd: str = ""
    
    # 同步设置
    sync_interval: float = 0.05  # 20Hz
    position_threshold: float = 0.1  # 最小移动距离
    
    # 调试
    log_packets: bool = False
    log_sync: bool = False
```

### 5.2 桥接状态

```python
@dataclass
class BridgeState:
    """桥接状态"""
    started_at: Optional[datetime] = None
    
    mc_connected: bool = False
    mc_logged_in: bool = False
    mc_in_game: bool = False
    
    mnw_connected: bool = False
    mnw_logged_in: bool = False
    mnw_in_game: bool = False
    
    packets_forwarded_mc_to_mnw: int = 0
    packets_forwarded_mnw_to_mc: int = 0
    
    last_position_sync: Optional[datetime] = None
    last_chat_sync: Optional[datetime] = None
```

---

## 6. 关键映射

### 6.1 数据包映射表

| MC 包 | MNW 包 | 转换 |
|-------|--------|------|
| Player Position (0x11) | RoleMoveCH (2001) | 位置+朝向 |
| Chat Message (0x03) | ChatContentCH (9001) | 消息内容 |
| Player Block Placement (0x2D) | PlaceBlockCH (6001) | 方块ID映射 |
| Player Digging (0x1A) | DestroyBlockCH (6003) | 位置 |
| Animation (0x2B) | InputActionCH (4001) | 动作类型 |

### 6.2 事件映射表

| MC 事件 | MNW 事件 | 处理 |
|---------|----------|------|
| on_join | on_enter_world | 初始化同步 |
| on_chat | on_chat | 转发消息 |
| on_move | on_move | 位置同步 |
| on_block_change | on_block_update | 方块同步 |

---

## 7. 验收标准

### 7.1 功能验收

| 测试项 | 标准 | 方法 |
|--------|------|------|
| 启动桥接 | MC和MNW都连接成功 | 集成测试 |
| 位置同步 | MC移动 -> MNW可见 | 手动测试 |
| 聊天桥接 | MC聊天 -> MNW可见 | 手动测试 |
| 方块放置 | MC放置 -> MNW可见 | 手动测试 |
| 断开处理 | 优雅断开 | 单元测试 |

### 7.2 性能验收

| 指标 | 目标 | 测试方法 |
|------|------|----------|
| 延迟 | < 50ms | 测量往返时间 |
| 包丢失 | < 1% | 计数对比 |
| CPU 占用 | < 10% | 系统监控 |
| 内存占用 | < 100MB | 内存监控 |

---

## 8. 风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| 协议不匹配 | 中 | 高 | 对比 MN2MC 实现 |
| 同步延迟 | 中 | 中 | 优化转发逻辑 |
| 方块映射错误 | 低 | 中 | 完善映射表 |
| 连接不稳定 | 低 | 高 | 实现重连机制 |

---

## 9. 进度跟踪

| 阶段 | 任务 | 计划 | 实际 | 状态 |
|------|------|------|------|------|
| 6.1 | 基础桥接 | 4h | - | ⏳ |
| 6.2 | 包路由 | 4h | - | ⏳ |
| 6.3 | 位置同步 | 4h | - | ⏳ |
| 6.4 | 聊天/方块 | 4h | - | ⏳ |
| **总计** | | **16h** | | |

---

**Phase 6 开发计划完成，开始实施！**
