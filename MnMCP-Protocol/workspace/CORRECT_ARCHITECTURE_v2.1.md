# MnMCP v2.1 - 正确的联机架构

**问题分析**: 之前的设计错误理解了联机机制

---

## 🔍 正确理解

### 迷你世界联机机制

```
[玩家A - 房主]
    │
    ├─ 1. 在本地启动游戏服务端 (127.0.0.1:随机端口)
    │
    ├─ 2. 启动内网穿透 (frp/自研)
    │   └─ 映射: 本地端口 → 公网地址
    │
    ├─ 3. 向官方云服务器注册房间
    │   POST https://openroom.mini1.cn/create_room
    │   {
    │     "room_name": "我的房间",
    │     "public_address": "穿透后的公网地址",
    │     "max_players": 6,
    │     ...
    │   }
    │   ← 返回: { "room_id": "2067729592" }
    │
    └─ 4. 房间出现在官方房间列表

[官方云服务器]
    │
    ├─ 存储: 房间号 → 穿透地址映射
    ├─ 提供: 房间列表 API
    └─ 不转发游戏数据！

[玩家B - 加入者]
    │
    ├─ 1. 从官方云服务器获取房间列表
    │   GET https://openroom.mini1.cn/list_rooms
    │
    ├─ 2. 选择房间 (如 2067729592)
    │   获取穿透地址
    │
    └─ 3. 直接连接到玩家A的穿透地址
        TCP/UDP → 穿透地址:端口
```

### Minecraft 联机机制

```
[Minecraft 服务器]
    │
    ├─ 监听端口: 25565
    │
    └─ 局域网广播 (可选)
        UDP 广播: "我是 MC 服务器"

[Minecraft 客户端]
    │
    ├─ 方式1: 局域网扫描
    │   └─ 监听 UDP 广播
    │
    ├─ 方式2: 手动添加服务器
    │   └─ 输入 IP:端口
    │
    └─ 方式3: 服务器列表
        └─ 从配置文件读取
```

---

## ✅ 正确的解决方案

### 方案 A: 伪装成迷你世界房间 (推荐)

```
┌─────────────────────────────────────────────────────┐
│              MnMCP 桥接器 (房主模式)                 │
└─────────────────────────────────────────────────────┘

[1] 启动 Minecraft 服务器
    └─ 127.0.0.1:25565

[2] MnMCP 桥接器启动
    │
    ├─ 创建本地迷你世界服务端模拟器
    │   └─ 127.0.0.1:随机端口 (如 19132)
    │
    ├─ 启动内网穿透
    │   └─ frp/ngrok: 19132 → 公网地址
    │
    ├─ 向迷你世界官方云服务器注册房间
    │   POST https://openroom.mini1.cn/create_room
    │   └─ 获得房间号 (如 2067729592)
    │
    └─ 连接到 Minecraft 服务器
        └─ 127.0.0.1:25565

[3] 迷你世界玩家加入
    │
    ├─ 在迷你世界客户端看到房间列表
    │   └─ 房间号: 2067729592
    │       房间名: "MnMCP Bridge - Minecraft 联机"
    │
    ├─ 点击加入
    │   └─ 连接到穿透地址
    │
    ├─ MnMCP 接收连接
    │   └─ 解析迷你世界协议
    │
    └─ 转换并转发到 Minecraft
        └─ 迷你世界玩家出现在 MC 中

[4] Minecraft 玩家加入
    │
    ├─ 直接连接 MC 服务器
    │   └─ 127.0.0.1:25565
    │
    └─ MC 玩家和 MNW 玩家互相看到
```

### 方案 B: 双向桥接 (更复杂)

```
[MnMCP 桥接器 - 双模式]
    │
    ├─ 模式1: 迷你世界房主
    │   ├─ 注册到迷你世界云服务器
    │   └─ 接受迷你世界玩家
    │
    └─ 模式2: Minecraft 客户端
        ├─ 连接到 Minecraft 服务器
        └─ 代表迷你世界玩家操作
```

---

## 🔧 实现要点

### 1. 迷你世界房间注册

```python
import requests
import json

class MiniWorldRoomRegistry:
    """迷你世界房间注册器"""
    
    def __init__(self):
        self.api_base = "https://openroom.mini1.cn"
        self.room_id = None
        self.public_address = None
    
    def register_room(self, room_name: str, public_address: str, max_players: int = 6):
        """注册房间到官方云服务器"""
        
        # 1. 认证 (需要迷你世界账号)
        auth_response = requests.post(
            f"{self.api_base}/auth/login",
            json={
                "username": "your_username",
                "password": "your_password"
            }
        )
        
        if auth_response.status_code != 200:
            raise Exception("认证失败")
        
        token = auth_response.json()["token"]
        
        # 2. 创建房间
        create_response = requests.post(
            f"{self.api_base}/room/create",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "room_name": room_name,
                "public_address": public_address,
                "max_players": max_players,
                "game_mode": "survival",  # 生存模式
                "map_name": "MnMCP Bridge World",
                # 其他房间设置...
            }
        )
        
        if create_response.status_code != 200:
            raise Exception("创建房间失败")
        
        result = create_response.json()
        self.room_id = result["room_id"]
        
        print(f"✓ 房间已注册!")
        print(f"  房间号: {self.room_id}")
        print(f"  房间名: {room_name}")
        print(f"  公网地址: {public_address}")
        
        return self.room_id
    
    def update_room_status(self, player_count: int):
        """更新房间状态 (心跳)"""
        requests.post(
            f"{self.api_base}/room/{self.room_id}/heartbeat",
            json={"player_count": player_count}
        )
    
    def close_room(self):
        """关闭房间"""
        requests.post(
            f"{self.api_base}/room/{self.room_id}/close"
        )
```

### 2. 内网穿透集成

```python
import subprocess
import time

class FrpTunnel:
    """frp 内网穿透"""
    
    def __init__(self, local_port: int, frp_server: str = "frp.example.com"):
        self.local_port = local_port
        self.frp_server = frp_server
        self.process = None
        self.public_address = None
    
    def start(self):
        """启动 frp 客户端"""
        
        # 创建 frp 配置
        config = f"""
[common]
server_addr = {self.frp_server}
server_port = 7000

[mnmcp_bridge]
type = tcp
local_ip = 127.0.0.1
local_port = {self.local_port}
remote_port = 0  # 自动分配
"""
        
        with open("frpc.ini", "w") as f:
            f.write(config)
        
        # 启动 frpc
        self.process = subprocess.Popen(
            ["frpc", "-c", "frpc.ini"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待启动并获取公网地址
        time.sleep(2)
        
        # 从日志中解析公网地址
        # TODO: 实际实现需要解析 frpc 输出
        self.public_address = f"{self.frp_server}:12345"
        
        print(f"✓ 内网穿透已启动")
        print(f"  本地端口: {self.local_port}")
        print(f"  公网地址: {self.public_address}")
        
        return self.public_address
    
    def stop(self):
        """停止 frp"""
        if self.process:
            self.process.terminate()
            self.process.wait()
```

### 3. 完整流程

```python
async def main():
    # 1. 启动 Minecraft 连接
    mc_connector = MinecraftConnector(config)
    await mc_connector.connect()
    
    # 2. 启动本地迷你世界服务端
    mnw_server = MiniWorldRoomSimulator(config, mapping_mgr)
    await mnw_server.start()  # 监听 19132
    
    # 3. 启动内网穿透
    tunnel = FrpTunnel(local_port=19132)
    public_address = tunnel.start()
    
    # 4. 注册到迷你世界云服务器
    registry = MiniWorldRoomRegistry()
    room_id = registry.register_room(
        room_name="MnMCP Bridge - Minecraft 联机",
        public_address=public_address,
        max_players=6
    )
    
    print("=" * 60)
    print("✓ 桥接器已启动!")
    print("=" * 60)
    print(f"迷你世界玩家:")
    print(f"  1. 打开迷你世界客户端")
    print(f"  2. 在房间列表中找到房间号: {room_id}")
    print(f"  3. 点击加入")
    print()
    print(f"Minecraft 玩家:")
    print(f"  直接连接: 127.0.0.1:25565")
    print("=" * 60)
    
    # 5. 开始数据转发
    await bridge_loop()
```

---

## ⚠️ 关键问题

### 1. 迷你世界 API 未公开

**问题**: 迷你世界的房间注册 API 不是公开的

**解决方案**:
- 方案 A: 逆向分析迷你世界客户端，找到 API 端点和协议
- 方案 B: 使用抓包工具捕获真实的房间注册请求
- 方案 C: 模拟迷你世界客户端的行为

### 2. 需要迷你世界账号

**问题**: 注册房间需要登录迷你世界账号

**解决方案**:
- 用户提供自己的迷你世界账号
- 桥接器代表用户创建房间

### 3. 协议加密

**问题**: 迷你世界的通信可能是加密的

**解决方案**:
- 使用之前分析的加密密钥
- 实现完整的加密/解密流程

---

## 📋 下一步行动

### 立即需要做的

1. **抓包分析房间注册流程**
   ```bash
   # 使用 Wireshark 或 Charles
   # 捕获迷你世界创建房间时的网络请求
   ```

2. **找到房间注册 API**
   - 端点 URL
   - 请求格式
   - 认证方式
   - 响应格式

3. **实现房间注册**
   - 模拟迷你世界客户端
   - 发送正确的注册请求
   - 获取房间号

4. **集成内网穿透**
   - 使用 frp 或 ngrok
   - 获取公网地址
   - 配置端口映射

---

## 🎯 正确的测试流程

### Step 1: 准备

```bash
# 1. 启动 Minecraft 服务器
java -jar server.jar

# 2. 启动 frp 服务器 (如果自建)
frps -c frps.ini

# 3. 准备迷你世界账号
# 用户名: your_username
# 密码: your_password
```

### Step 2: 启动桥接器

```bash
python mnmcp_bridge_v2.1.py \
  --mnw-username your_username \
  --mnw-password your_password \
  --mc-server 127.0.0.1:25565 \
  --frp-server frp.example.com
```

### Step 3: 迷你世界玩家加入

1. 打开迷你世界客户端
2. 点击"联机"
3. 在房间列表中看到桥接器创建的房间
4. 点击加入

### Step 4: Minecraft 玩家加入

1. 打开 Minecraft
2. 多人游戏 → 添加服务器
3. 输入: 127.0.0.1:25565
4. 加入服务器

### Step 5: 验证联机

- 迷你世界玩家和 Minecraft 玩家互相看到
- 可以互动、聊天、建造

---

**关键**: 我们需要先逆向分析迷你世界的房间注册 API！

你能提供一个迷你世界创建房间时的抓包文件吗？或者我们可以一起分析 MnMCPResources 中的相关文件。
