# MnMCP Phase 4 执行计划 - 协议转换核心

**版本**: 2026-05-30-25  
**阶段**: Phase 4 - Protocol Bridge Core  
**前置**: Phase 1-3, 6 完成 ✅

---

## 🎯 Phase 4 目标

实现迷你世界与Minecraft之间的**实时协议转换**：

1. **玩家数据同步** - 位置、动作、状态
2. **区块数据转换** - 方块映射、地形同步
3. **游戏操作桥接** - 放置/破坏方块、交互
4. **聊天消息桥接** - 双向通信

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    MnMCP Protocol Bridge                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐      ┌─────────────────┐          │
│  │  MiniWorld      │      │  Minecraft      │          │
│  │  Client         │      │  Client         │          │
│  │  (Port 19132)   │      │  (Port 19133)   │          │
│  └────────┬────────┘      └────────┬────────┘          │
│           │                        │                    │
│           ▼                        ▼                    │
│  ┌─────────────────┐      ┌─────────────────┐          │
│  │  MiniWorld      │      │  Minecraft      │          │
│  │  Protocol       │      │  Protocol       │          │
│  │  Decoder        │      │  Encoder      │          │
│  └────────┬────────┘      └────────┬────────┘          │
│           │                        │                    │
│           └──────────┬─────────────┘                    │
│                      │                                  │
│                      ▼                                  │
│           ┌─────────────────┐                           │
│           │  Protocol Bridge │                           │
│           │  (核心转换层)    │                           │
│           │  - 数据包转换    │                           │
│           │  - 坐标映射      │                           │
│           │  - 方块映射      │                           │
│           │  - 实体同步      │                           │
│           └────────┬────────┘                           │
│                    │                                    │
│                    ▼                                    │
│           ┌─────────────────┐                           │
│           │  World Service   │                           │
│           │  (后端服务)      │                           │
│           │  (Port 19134)   │                           │
│           └─────────────────┘                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 开发任务

### 任务4.1: 协议桥接核心

**文件**: `mnmcp/bridge/protocol_bridge.py`

```python
class ProtocolBridge:
    """
    核心协议桥接器
    
    功能:
    - 接收迷你世界数据包
    - 转换为Minecraft格式
    - 双向同步
    """
    
    def __init__(self):
        self.mini_handler = MiniWorldProtocolHandler()
        self.mc_handler = MinecraftProtocolHandler()
        self.block_mapper = BlockMapper()
        self.entity_mapper = EntityMapper()
    
    async def convert_packet(self, mini_packet: bytes) -> bytes:
        """迷你世界 → Minecraft"""
        # 解析迷你世界包
        parsed = self.mini_handler.parse(mini_packet)
        
        # 转换数据
        converted = self._convert_data(parsed)
        
        # 编码为MC格式
        return self.mc_handler.encode(converted)
    
    def _convert_data(self, data: dict) -> dict:
        """数据格式转换"""
        # 坐标转换
        # 方块ID映射
        # 实体类型映射
        pass
```

### 任务4.2: 玩家同步

**文件**: `mnmcp/bridge/player_sync.py`

```python
class PlayerSync:
    """玩家数据同步"""
    
    async def sync_position(self, mini_player, mc_player):
        """同步玩家位置"""
        # 迷你世界坐标 → Minecraft坐标
        # 发送位置更新包
        pass
    
    async def sync_action(self, mini_action, mc_player):
        """同步玩家动作"""
        # 动作转换
        # 动画同步
        pass
```

### 任务4.3: 区块转换

**文件**: `mnmcp/bridge/chunk_converter.py`

```python
class ChunkConverter:
    """区块数据转换"""
    
    def convert_chunk(self, mini_chunk: bytes, x: int, z: int) -> bytes:
        """转换单个区块"""
        # 解析迷你世界区块格式
        # 映射方块ID
        # 编码为Minecraft Anvil格式
        pass
```

### 任务4.4: 方块操作桥接

**文件**: `mnmcp/bridge/block_bridge.py`

```python
class BlockBridge:
    """方块操作桥接"""
    
    async def on_block_break(self, position, player):
        """处理方块破坏"""
        # 在两个世界同步破坏
        pass
    
    async def on_block_place(self, position, block_id, player):
        """处理方块放置"""
        # 映射方块ID
        # 在两个世界同步放置
        pass
```

### 任务4.5: 聊天桥接

**文件**: `mnmcp/bridge/chat_bridge.py`

```python
class ChatBridge:
    """聊天消息桥接"""
    
    async def relay_message(self, source: str, message: str, sender: str):
        """转发聊天消息"""
        # 迷你世界 → Minecraft
        # Minecraft → 迷你世界
        # 格式化消息
        pass
```

---

## 🔄 数据流

### 玩家移动同步

```
迷你世界客户端
    ↓
发送位置更新包 (RakNet)
    ↓
RakNetServer 接收
    ↓
ProtocolBridge 转换
    - 坐标转换 (X, Y, Z)
    - 旋转角度转换
    ↓
MinecraftServer 发送
    ↓
Minecraft客户端 接收位置更新
```

### 方块操作同步

```
Minecraft客户端
    ↓
发送方块放置 (TCP)
    ↓
MinecraftServer 接收
    ↓
BlockBridge 处理
    - 方块ID映射 (MC → MiniWorld)
    ↓
RakNetServer 转发
    ↓
迷你世界客户端 接收方块更新
```

---

## 📊 映射数据使用

### 方块映射

```python
# mnmcp/mapping/blocks.py
BLOCK_MAPPING = {
    # 迷你世界ID → Minecraft ID
    100: "minecraft:grass_block",  # 草地
    101: "minecraft:dirt",         # 泥土
    102: "minecraft:stone",        # 石头
    # ... 2,909个方块
}

# 反向映射
REVERSE_BLOCK_MAPPING = {v: k for k, v in BLOCK_MAPPING.items()}
```

### 实体映射

```python
# mnmcp/mapping/mobs.py
MOB_MAPPING = {
    # 迷你世界实体ID → Minecraft实体ID
    1000: "minecraft:zombie",
    1001: "minecraft:skeleton",
    # ... 1,289个实体
}
```

---

## 📝 实施步骤

### Day 1 (今天)

1. **创建桥接核心**
   ```bash
   mkdir mnmcp/bridge
   touch mnmcp/bridge/__init__.py
   touch mnmcp/bridge/protocol_bridge.py
   touch mnmcp/bridge/player_sync.py
   touch mnmcp/bridge/chunk_converter.py
   touch mnmcp/bridge/block_bridge.py
   touch mnmcp/bridge/chat_bridge.py
   ```

2. **实现基础转换**
   - 协议桥接器框架
   - 数据包解析/编码
   - 坐标转换

### Day 2 (明天)

3. **玩家同步**
   - 位置同步
   - 动作同步
   - 状态同步

4. **区块转换**
   - 区块解析
   - 方块映射
   - Anvil格式编码

### Day 3 (后天)

5. **方块操作**
   - 放置/破坏处理
   - 方块ID映射
   - 同步确认

6. **聊天桥接**
   - 消息转发
   - 格式化
   - 玩家名映射

---

## ✅ 完成标准

- [ ] ProtocolBridge 核心实现
- [ ] 玩家位置实时同步 (<100ms延迟)
- [ ] 方块操作双向同步
- [ ] 聊天消息桥接
- [ ] 区块数据转换
- [ ] 实体同步
- [ ] 集成测试

---

## 🎯 下一步

**立即开始**: 创建桥接模块并编写 ProtocolBridge 核心类
