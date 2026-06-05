# MnMCP v2.1 - 基于真实API的实现方案

**基于抓包分析的真实迷你世界API**

---

## 🔍 发现的关键API

### 1. 认证服务器
```
certification.mini1.cn:19921
```

**登出API** (可推断登录API):
```
GET /auth/loginout?di=&ct=0&bt=1&pi=...&si=...&uin=...&appid=...&ts=...&auth=...
```

**参数**:
- `uin`: 用户ID (如 2056574316)
- `appid`: 应用ID (如 2fb0c1128f814017954f)
- `ts`: 时间戳
- `auth`: 认证签名
- `si`: 会话ID
- `pi`: 设备指纹

### 2. 房间服务器
```
openroom.mini1.cn:8080
```

**服务器配置API**:
```
GET /server/room?cmd=server_config&uin=...&auth=...
```

### 3. 聊天推送服务器
```
chatpush.mini1.cn:19601
chatpush.mini1.cn:19701
```

**分配聊天服务器**:
```
GET /minilb/alloc
```

**网关连接**:
```
GET /minigate/gate?uid=...&token=...&time=...&auth=...&cltversion=79105&apiid=110&reconnect=0
```

**JWT Token 示例**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aW4iOiIyMDU2NTc0MzE2IiwidGltZSI6MTc3MjI0Njg5MSwiZmxhZyI6MSwiZXhwIjoxNzc0ODM4ODkxLCJpc3MiOiJpbXNlcnZlciJ9.a0BOJQaCzju-D6y8RiA5CDp5jzJaR9FtZj7mhlgy3AA
```

解码后:
```json
{
  "uin": "2056574316",
  "time": 1772246891,
  "flag": 1,
  "exp": 1774838891,
  "iss": "imserver"
}
```

---

## 💡 实现策略

由于迷你世界的API需要：
1. 真实的用户账号认证
2. 复杂的签名算法 (auth参数)
3. 设备指纹 (pi参数)
4. 会话管理

**我们采用更实际的方案**:

### 方案: Minecraft 作为房主，迷你世界作为客户端

```
┌─────────────────────────────────────────────────────────┐
│                  简化的联机方案                          │
└─────────────────────────────────────────────────────────┘

[Minecraft 服务器]
    │
    ├─ 监听: 25565 (Java Edition)
    │
    └─ 玩家: Minecraft 客户端直接连接

[MnMCP 桥接器]
    │
    ├─ 作为 Minecraft 客户端连接到 MC 服务器
    │   └─ 使用 Geyser/Floodgate 支持基岩版协议
    │
    ├─ 同时作为迷你世界服务端
    │   └─ 监听 19132 (模拟迷你世界房间)
    │
    └─ 数据转发
        ├─ MNW 玩家 → 转换 → MC 服务器
        └─ MC 服务器 → 转换 → MNW 玩家

[迷你世界玩家]
    │
    └─ 手动输入地址连接: <你的IP>:19132
        (不通过官方房间列表)
```

---

## 🔧 实际实现

### 1. 使用 Geyser 作为基础

Geyser 已经实现了 Minecraft Java ↔ Bedrock 的转换，我们可以：

1. **Minecraft Java 服务器** + **Geyser 插件**
   - Geyser 监听 19132 (Bedrock 端口)
   - 自动转换 Bedrock 协议到 Java 协议

2. **MnMCP 协议适配器**
   - 将迷你世界协议转换为 Bedrock 协议
   - 连接到 Geyser 的 19132 端口

```
[迷你世界客户端]
    │ 迷你世界协议
    ▼
[MnMCP 适配器] (端口 19133)
    │ 转换为 Bedrock 协议
    ▼
[Geyser] (端口 19132)
    │ 转换为 Java 协议
    ▼
[Minecraft Java 服务器] (端口 25565)
```

### 2. 简化的连接方式

**迷你世界玩家连接步骤**:

1. 打开迷你世界
2. 点击"联机"
3. 选择"加入房间"
4. **输入地址**: `<服务器IP>:19133`
   - 局域网: `192.168.x.x:19133`
   - 公网: 需要端口转发或内网穿透

**不需要**:
- ❌ 官方房间注册
- ❌ 迷你世界账号登录
- ❌ 复杂的API调用

---

## 📝 实现代码

### MnMCP 协议适配器

```python
"""
MnMCP 协议适配器
将迷你世界协议转换为 Minecraft Bedrock 协议
"""

import asyncio
import struct
from typing import Optional

class MnWToBedrockAdapter:
    """迷你世界 → Bedrock 协议适配器"""
    
    def __init__(self, geyser_host: str = "127.0.0.1", geyser_port: int = 19132):
        self.geyser_host = geyser_host
        self.geyser_port = geyser_port
        self.server = None
        self.clients = {}
        
    async def start(self, listen_port: int = 19133):
        """启动适配器"""
        self.server = await asyncio.start_server(
            self.handle_mnw_client,
            '0.0.0.0',
            listen_port
        )
        
        print(f"✓ MnMCP 适配器已启动")
        print(f"  监听端口: {listen_port}")
        print(f"  Geyser 地址: {self.geyser_host}:{self.geyser_port}")
        print()
        print(f"迷你世界玩家请连接: <服务器IP>:{listen_port}")
        
        async with self.server:
            await self.server.serve_forever()
    
    async def handle_mnw_client(self, reader, writer):
        """处理迷你世界客户端连接"""
        addr = writer.get_extra_info('peername')
        print(f"[MNW] 新连接: {addr}")
        
        try:
            # 连接到 Geyser
            geyser_reader, geyser_writer = await asyncio.open_connection(
                self.geyser_host,
                self.geyser_port
            )
            
            print(f"[MNW] {addr} → Geyser 连接成功")
            
            # 双向转发
            await asyncio.gather(
                self.forward_mnw_to_bedrock(reader, geyser_writer, addr),
                self.forward_bedrock_to_mnw(geyser_reader, writer, addr)
            )
            
        except Exception as e:
            print(f"[MNW] {addr} 错误: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            print(f"[MNW] {addr} 断开连接")
    
    async def forward_mnw_to_bedrock(self, mnw_reader, bedrock_writer, addr):
        """转发: 迷你世界 → Bedrock"""
        while True:
            try:
                # 读取迷你世界数据包
                data = await mnw_reader.read(4096)
                if not data:
                    break
                
                # 转换协议
                bedrock_packet = self.convert_mnw_to_bedrock(data)
                
                if bedrock_packet:
                    bedrock_writer.write(bedrock_packet)
                    await bedrock_writer.drain()
                    
            except Exception as e:
                print(f"[MNW→BE] {addr} 错误: {e}")
                break
    
    async def forward_bedrock_to_mnw(self, bedrock_reader, mnw_writer, addr):
        """转发: Bedrock → 迷你世界"""
        while True:
            try:
                # 读取 Bedrock 数据包
                data = await bedrock_reader.read(4096)
                if not data:
                    break
                
                # 转换协议
                mnw_packet = self.convert_bedrock_to_mnw(data)
                
                if mnw_packet:
                    mnw_writer.write(mnw_packet)
                    await mnw_writer.drain()
                    
            except Exception as e:
                print(f"[BE→MNW] {addr} 错误: {e}")
                break
    
    def convert_mnw_to_bedrock(self, mnw_data: bytes) -> Optional[bytes]:
        """转换: 迷你世界协议 → Bedrock 协议"""
        # TODO: 实现协议转换
        # 1. 解析迷你世界数据包
        # 2. 映射到 Bedrock 数据包
        # 3. 应用方块/实体映射
        return mnw_data  # 临时直接转发
    
    def convert_bedrock_to_mnw(self, bedrock_data: bytes) -> Optional[bytes]:
        """转换: Bedrock 协议 → 迷你世界协议"""
        # TODO: 实现协议转换
        return bedrock_data  # 临时直接转发


async def main():
    """主函数"""
    print("=" * 60)
    print("MnMCP v2.1 - 协议适配器")
    print("=" * 60)
    print()
    
    adapter = MnWToBedrockAdapter(
        geyser_host="127.0.0.1",
        geyser_port=19132
    )
    
    await adapter.start(listen_port=19133)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🎯 测试步骤 (修正版)

### Step 1: 安装 Geyser

```bash
# 下载 Geyser-Spigot.jar
# 放到 Minecraft 服务器的 plugins 目录

# 配置 Geyser (config.yml)
bedrock:
  address: 0.0.0.0
  port: 19132

remote:
  address: 127.0.0.1
  port: 25565
```

### Step 2: 启动 Minecraft 服务器

```bash
java -jar spigot-1.20.6.jar
```

**检查**: Geyser 应该显示:
```
[Geyser] Listening on 0.0.0.0:19132
```

### Step 3: 启动 MnMCP 适配器

```bash
python mnmcp_adapter_v2.1.py
```

**检查**: 应该显示:
```
✓ MnMCP 适配器已启动
  监听端口: 19133
  Geyser 地址: 127.0.0.1:19132

迷你世界玩家请连接: <服务器IP>:19133
```

### Step 4: 迷你世界连接

1. 打开迷你世界 1.55.0
2. 点击"联机"
3. 选择"加入房间"
4. **输入地址**: `127.0.0.1:19133` (或你的局域网IP)
5. 点击"连接"

### Step 5: Minecraft 连接

1. 打开 Minecraft 1.20.6
2. 多人游戏
3. 添加服务器: `127.0.0.1:25565`
4. 加入服务器

---

## ✅ 这个方案的优势

1. **不需要官方API**
   - 不需要迷你世界账号
   - 不需要房间注册
   - 不需要复杂的签名

2. **利用现有工具**
   - Geyser 已经实现了 Java ↔ Bedrock
   - 我们只需要实现 MNW ↔ Bedrock

3. **更容易测试**
   - 可以直接输入IP连接
   - 不依赖外部服务
   - 局域网即可测试

4. **更灵活**
   - 支持自建服务器
   - 支持端口转发
   - 支持内网穿透

---

**下一步**: 实现 MnW ↔ Bedrock 的协议转换！

这个方案更实际可行，你觉得如何？
