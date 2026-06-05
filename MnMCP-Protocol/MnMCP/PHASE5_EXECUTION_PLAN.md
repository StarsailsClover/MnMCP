# MnMCP Phase 5 执行计划 - 内网穿透

**版本**: 2026-05-31  
**阶段**: Phase 5 - NAT Traversal & Room Registration  
**依赖**: Phase 4 完成 ✅

---

## 🎯 Phase 5 目标

实现内网穿透功能，使MiniWorld房间可被外部玩家发现和连接：

1. **FRP客户端集成** - 内网穿透隧道
2. **房间注册API** - 向中心服务器注册
3. **心跳维持** - 保持房间在线
4. **地址发现** - 玩家发现房间

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────┐
│              MnMCP NAT Traversal System                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│  │ MiniWorld   │     │  FRP Client │     │  Center   │ │
│  │ Local Server│ ←→  │  (Tunnel)   │ ←→  │  Server   │ │
│  │  :19132     │     │             │     │  (Cloud)  │ │
│  └─────────────┘     └─────────────┘     └─────┬─────┘ │
│                                                  │       │
│  ┌─────────────┐     ┌─────────────┐           │       │
│  │ Minecraft   │     │  Room       │           │       │
│  │ Client      │     │  Registry   │           │       │
│  │  :19133     │     │             │           │       │
│  └─────────────┘     └─────────────┘           │       │
│                                                  │       │
│  External Player ←──────────────────────────────┘       │
│  (Discovers via Center Server)                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 开发任务

### 任务5.1: FRP客户端集成

**文件**: `mnmcp/tunnel/frp_client.py`

```python
class FRPClient:
    """FRP (Fast Reverse Proxy) client."""
    
    async def start_tunnel(self, local_port, remote_port):
        """Create tunnel from cloud to local."""
        pass
    
    async def stop_tunnel(self):
        """Stop tunnel."""
        pass
    
    def get_tunnel_url(self):
        """Get public URL."""
        pass
```

### 任务5.2: 房间注册

**文件**: `mnmcp/room/registry.py`

```python
class RoomRegistry:
    """Register room with center server."""
    
    async def register_room(self, room_info):
        """Register new room."""
        pass
    
    async def heartbeat(self, room_id):
        """Send heartbeat to keep room alive."""
        pass
    
    async def unregister_room(self, room_id):
        """Unregister room."""
        pass
```

### 任务5.3: 房间发现

**文件**: `mnmcp/room/discovery_client.py`

```python
class RoomDiscoveryClient:
    """Client for discovering rooms."""
    
    async def list_rooms(self):
        """Get room list from center."""
        pass
    
    async def get_room_info(self, room_id):
        """Get room details."""
        pass
```

---

## 📝 实施步骤

### Day 1 (今天)

1. 创建tunnel模块
2. 实现FRP客户端框架
3. 创建room注册模块

### Day 2 (明天)

4. 实现房间注册API
5. 实现心跳机制
6. 完善Phase 3

---

## 🔧 Phase 3 完善计划

### 需要完善的组件

| 组件 | 问题 | 解决方案 |
|------|------|----------|
| AuthInterceptor | 基本框架 | 添加实际拦截逻辑 |
| SmartProxy | 模式切换 | 添加状态持久化 |
| CommandParser | 命令解析 | 添加权限控制 |
| RoomList | 伪造房间 | 添加动态房间 |

### 完善任务

1. **AuthInterceptor完善**
   - 实际WebSocket拦截
   - 会话提取逻辑
   - 登录成功回调

2. **SmartProxy完善**
   - 添加持久化
   - 错误恢复
   - 状态同步

3. **集成测试**
   - 端到端测试
   - 压力测试

---

## ✅ Phase 5 完成标准

- [ ] FRP客户端可用
- [ ] 房间注册API完成
- [ ] 心跳机制实现
- [ ] 房间发现可用
- [ ] 集成测试通过

---

**立即开始Phase 5开发！**
