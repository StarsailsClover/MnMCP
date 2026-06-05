# MnMCP v3.0 - 基于 Clash Meta 的代理方案

**核心思路**: 使用 Clash Meta 作为中间人代理，拦截和修改双方的网络流量

---

## 🎯 正确理解

### Minecraft Java 局域网模式

```
[Minecraft Java 客户端]
    │
    ├─ 打开局域网游戏 (Open to LAN)
    │   └─ 在本地启动一个临时服务器
    │       监听随机端口 (如 54321)
    │
    └─ 通过 UDP 广播通知其他玩家
        UDP 224.0.2.60:4445
        消息: "[MOTD]世界名称[/MOTD][AD]54321[/AD]"
```

### 迷你世界联机模式

```
[迷你世界客户端]
    │
    ├─ 方式1: 创建房间
    │   ├─ 本地启动游戏服务端
    │   ├─ 内网穿透到公网
    │   └─ 注册到官方云服务器
    │       POST https://openroom.mini1.cn/room/create
    │       → 获得房间号
    │
    └─ 方式2: 加入房间
        ├─ 从官方云服务器获取房间列表
        │   GET https://openroom.mini1.cn/room/list
        └─ 连接到房间的穿透地址
```

---

## 💡 Clash Meta 代理方案

### 方案 A: 伪造迷你世界房间列表 (推荐)

```
┌─────────────────────────────────────────────────────────────┐
│              Clash Meta 中间人代理                           │
└─────────────────────────────────────────────────────────────┘

[迷你世界客户端]
    │
    ├─ 所有网络流量通过 Clash Meta
    │   设置系统代理: 127.0.0.1:7890
    │
    ├─ 请求房间列表
    │   GET https://openroom.mini1.cn/room/list
    │   ↓
    │   [Clash Meta 拦截]
    │   ↓
    │   返回伪造的房间列表:
    │   {
    │     "rooms": [
    │       {
    │         "room_id": "999999999",
    │         "room_name": "Minecraft 联机房间",
    │         "host": "127.0.0.1:19132",  ← 指向本地桥接器
    │         "players": "1/6",
    │         ...
    │       }
    │     ]
    │   }
    │
    └─ 点击加入房间 999999999
        连接到 127.0.0.1:19132
        ↓
        [MnMCP 桥接器]
        ↓
        转换协议并连接到 Minecraft 局域网
        ↓
        [Minecraft Java 客户端的局域网服务器]
```

### 方案 B: 伪造 Minecraft 局域网广播

```
[Minecraft Java 客户端]
    │
    ├─ 打开局域网 (端口 54321)
    │
    └─ UDP 广播: 224.0.2.60:4445

[MnMCP 桥接器]
    │
    ├─ 监听 UDP 广播
    │   发现 Minecraft 局域网: 127.0.0.1:54321
    │
    ├─ 启动迷你世界服务端模拟器
    │   监听: 127.0.0.1:19132
    │
    ├─ 注册到迷你世界云服务器 (通过 Clash Meta 伪造)
    │   或者
    │   等待迷你世界客户端手动连接
    │
    └─ 数据转发
        迷你世界 ↔ MnMCP ↔ Minecraft
```

---

## 🔧 实现方案

### 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                    完整架构图                                │
└─────────────────────────────────────────────────────────────┘

[迷你世界客户端]
    │ 设置代理: 127.0.0.1:7890
    ▼
[Clash Meta] (端口 7890)
    │
    ├─ 规则1: openroom.mini1.cn/* → MnMCP API 服务器
    │   拦截房间列表请求，返回伪造数据
    │
    └─ 规则2: 其他流量 → DIRECT
    
[MnMCP API 服务器] (端口 8080)
    │
    ├─ GET /room/list
    │   → 返回包含 Minecraft 房间的列表
    │
    └─ GET /room/info?room_id=999999999
        → 返回房间详情 (指向本地桥接器)

[MnMCP 桥接器] (端口 19132)
    │
    ├─ 监听迷你世界连接
    │
    ├─ 发现 Minecraft 局域网房间
    │   监听 UDP 224.0.2.60:4445
    │
    └─ 协议转换
        迷你世界协议 ↔ Minecraft Java 协议

[Minecraft Java 客户端]
    │
    └─ 打开局域网 (端口 54321)
```

---

## 📝 实现步骤

### Step 1: Clash Meta 配置

```yaml
# clash_meta_mnmcp.yaml

port: 7890
socks-port: 7891
allow-lan: true
mode: rule
log-level: info

# DNS 配置
dns:
  enable: true
  listen: 0.0.0.0:53
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  fake-ip-filter:
    - '*.mini1.cn'  # 不要 fake-ip 迷你世界域名
  nameserver:
    - 223.5.5.5
    - 119.29.29.29

# HTTP 代理配置
proxies:
  - name: "MnMCP-API"
    type: http
    server: 127.0.0.1
    port: 8080

# 代理组
proxy-groups:
  - name: "MiniWorld"
    type: select
    proxies:
      - MnMCP-API
      - DIRECT

# 路由规则
rules:
  # 拦截迷你世界房间API
  - DOMAIN,openroom.mini1.cn,MnMCP-API
  - DOMAIN,chatpush.mini1.cn,MnMCP-API
  
  # 其他迷你世界流量直连
  - DOMAIN-SUFFIX,mini1.cn,DIRECT
  
  # 本地流量直连
  - IP-CIDR,127.0.0.0/8,DIRECT
  - IP-CIDR,192.168.0.0/16,DIRECT
  
  # 默认直连
  - MATCH,DIRECT
```

### Step 2: MnMCP API 服务器

```python
"""
MnMCP API 服务器
伪造迷你世界房间列表，指向 Minecraft 局域网
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

class MnMCPAPIHandler(BaseHTTPRequestHandler):
    """处理迷你世界API请求"""
    
    # 存储发现的 Minecraft 房间
    minecraft_rooms = []
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        if path == '/room/list' or path == '/server/room':
            # 房间列表请求
            self.send_room_list()
        
        elif path == '/room/info':
            # 房间详情请求
            room_id = query.get('room_id', [''])[0]
            self.send_room_info(room_id)
        
        else:
            # 其他请求，返回404
            self.send_error(404)
    
    def send_room_list(self):
        """发送伪造的房间列表"""
        # 构造包含 Minecraft 房间的列表
        rooms = [
            {
                "room_id": "999999999",
                "room_name": "🎮 Minecraft 联机房间",
                "room_type": "survival",
                "host_name": "MnMCP Bridge",
                "current_players": len(self.minecraft_rooms),
                "max_players": 20,
                "map_name": "Minecraft World",
                "game_mode": "生存模式",
                "is_public": True,
                "host_address": "127.0.0.1:19132",  # 指向桥接器
                "version": "1.55.0",
                "ping": 10
            }
        ]
        
        # 添加真实的迷你世界房间 (如果有)
        # rooms.extend(real_miniworld_rooms)
        
        response = {
            "code": 0,
            "message": "success",
            "data": {
                "rooms": rooms,
                "total": len(rooms)
            }
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
        print(f"[API] 返回房间列表: {len(rooms)} 个房间")
    
    def send_room_info(self, room_id):
        """发送房间详情"""
        if room_id == "999999999":
            # Minecraft 房间详情
            room_info = {
                "room_id": "999999999",
                "room_name": "🎮 Minecraft 联机房间",
                "host_address": "127.0.0.1:19132",
                "host_port": 19132,
                "game_mode": "survival",
                "difficulty": "normal",
                "max_players": 20,
                "current_players": 1,
                "version": "1.55.0"
            }
            
            response = {
                "code": 0,
                "message": "success",
                "data": room_info
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
            print(f"[API] 返回房间详情: {room_id}")
        else:
            self.send_error(404, "Room not found")
    
    def log_message(self, format, *args):
        """自定义日志"""
        print(f"[API] {self.address_string()} - {format % args}")


def start_api_server(port=8080):
    """启动 API 服务器"""
    server = HTTPServer(('127.0.0.1', port), MnMCPAPIHandler)
    print(f"✓ MnMCP API 服务器已启动: http://127.0.0.1:{port}")
    print(f"  房间列表: http://127.0.0.1:{port}/room/list")
    print()
    server.serve_forever()


if __name__ == "__main__":
    start_api_server()
```

### Step 3: Minecraft 局域网发现

```python
"""
Minecraft 局域网房间发现
监听 UDP 广播，发现 Minecraft 局域网房间
"""

import socket
import struct
import re

class MinecraftLANDiscovery:
    """Minecraft 局域网发现"""
    
    MULTICAST_GROUP = '224.0.2.60'
    MULTICAST_PORT = 4445
    
    def __init__(self):
        self.sock = None
        self.discovered_servers = {}
    
    def start(self):
        """开始监听"""
        # 创建 UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # 绑定到多播端口
        self.sock.bind(('', self.MULTICAST_PORT))
        
        # 加入多播组
        mreq = struct.pack('4sl', socket.inet_aton(self.MULTICAST_GROUP), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        print(f"✓ 开始监听 Minecraft 局域网广播")
        print(f"  多播组: {self.MULTICAST_GROUP}:{self.MULTICAST_PORT}")
        print()
        
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                self.parse_broadcast(data.decode('utf-8', errors='ignore'), addr)
            except Exception as e:
                print(f"[LAN] 错误: {e}")
    
    def parse_broadcast(self, message, addr):
        """解析广播消息"""
        # Minecraft 局域网广播格式:
        # [MOTD]世界名称[/MOTD][AD]端口[/AD]
        
        motd_match = re.search(r'\[MOTD\](.*?)\[/MOTD\]', message)
        port_match = re.search(r'\[AD\](\d+)\[/AD\]', message)
        
        if motd_match and port_match:
            world_name = motd_match.group(1)
            port = int(port_match.group(1))
            
            server_key = f"{addr[0]}:{port}"
            
            if server_key not in self.discovered_servers:
                self.discovered_servers[server_key] = {
                    'host': addr[0],
                    'port': port,
                    'world_name': world_name
                }
                
                print(f"[LAN] 发现 Minecraft 服务器:")
                print(f"  地址: {addr[0]}:{port}")
                print(f"  世界: {world_name}")
                print()


if __name__ == "__main__":
    discovery = MinecraftLANDiscovery()
    discovery.start()
```

---

## 🚀 完整使用流程

### 1. 启动 Clash Meta

```bash
clash-meta -f clash_meta_mnmcp.yaml
```

### 2. 启动 MnMCP API 服务器

```bash
python mnmcp_api_server.py
```

### 3. 启动 Minecraft 局域网发现

```bash
python minecraft_lan_discovery.py
```

### 4. 启动 MnMCP 桥接器

```bash
python mnmcp_bridge_v3.py
```

### 5. 启动 Minecraft Java 客户端

1. 打开 Minecraft 1.20.6
2. 单人游戏 → 选择世界
3. 按 ESC → 打开局域网
4. 选择游戏模式
5. 点击"创造一个局域网世界"
6. 记下端口号 (如: 54321)

### 6. 配置迷你世界代理

1. 打开迷你世界
2. 设置系统代理: 127.0.0.1:7890
   - Windows: 设置 → 网络 → 代理
   - 或使用 Proxifier 强制代理

### 7. 迷你世界加入

1. 打开迷你世界
2. 点击"联机"
3. 在房间列表中看到 "🎮 Minecraft 联机房间"
4. 点击加入

---

## 💡 优势

1. ✅ 利用 Clash Meta 的强大代理功能
2. ✅ 可以拦截和修改任何HTTP/HTTPS请求
3. ✅ 不需要修改迷你世界客户端
4. ✅ 不需要root/越狱
5. ✅ 可以伪造任何API响应

---

## ⚠️ 技术难点

1. **HTTPS 拦截**
   - 需要安装 Clash Meta 的 CA 证书
   - 迷你世界可能有证书校验

2. **API 签名**
   - 迷你世界的API可能有签名验证
   - 需要逆向分析签名算法

3. **协议转换**
   - 仍然需要实现完整的协议转换
   - 迷你世界 ↔ Minecraft Java

---

这个方案更符合你的需求吗？我们可以基于 Clash Meta 来实现！
