# Minecraft 1.20.6 连接测试

**Date**: 2026-06-06  
**MC Version**: 1.20.6 (Protocol 766)  
**MNW Version**: 1.55.0+

---

## 测试目标

验证 MnMCP v3.1 与 Minecraft Java Edition 1.20.6 的连接兼容性。

---

## 测试环境

### Minecraft 服务端

```
版本: 1.20.6
类型: Paper/Spigot/Vanilla
地址: localhost 或远程服务器
端口: 25565
在线模式: 关闭 (offline-mode=true)
```

### MiniWorld

```
版本: 1.55.0+
房间: 创建测试房间
模式: 创造模式
```

---

## 快速测试

### 1. 验证协议版本

```bash
cd mnmcp-v3-integrated
python -c "
import sys
sys.path.insert(0, 'src')
from mcp_mc.client import MCClientConfig
config = MCClientConfig()
print(f'Protocol version: {config.protocol_version}')
assert config.protocol_version == 766, 'Expected 766 for 1.20.6'
print('OK: Protocol 766 (MC 1.20.6)')
"
```

### 2. 测试连接

```python
# test_mc1206.py
import asyncio
import sys
sys.path.insert(0, 'src')

from mcp_mc.client import MCPMinecraftClient, MCClientConfig

async def test_mc_1206():
    config = MCClientConfig(
        host="localhost",  # MC 服务器地址
        port=25565,
        username="TestPlayer",
        protocol_version=766  # 1.20.6
    )
    
    client = MCPMinecraftClient(config)
    
    @client.on('connect')
    async def on_connect():
        print("[MC 1.20.6] Connected to server")
    
    @client.on('login')
    async def on_login():
        print(f"[MC 1.20.6] Logged in as {client.player.username}")
    
    @client.on('join')
    async def on_join():
        print(f"[MC 1.20.6] Joined game!")
        print(f"  Entity ID: {client.player.entity_id}")
        print(f"  Gamemode: {client.player.gamemode}")
    
    # 连接
    print("Connecting to MC 1.20.6...")
    if await client.connect():
        print("Connected, starting login...")
        # 注意: 完整登录需要处理加密，可能需要离线模式
        
        # 等待
        await asyncio.sleep(5)
        
        # 断开
        await client.disconnect("Test complete")
    else:
        print("Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_mc_1206())
```

### 3. 运行测试

```bash
python test_mc1206.py
```

---

## 完整桥接测试

```python
# test_bridge_mc1206.py
import asyncio
import sys
sys.path.insert(0, 'src')

from mcp_core.bridge import MCPBridge, MCPBridgeConfig

async def test_bridge():
    config = MCPBridgeConfig(
        # MC 1.20.6 服务端
        mc_host="localhost",
        mc_port=25565,
        mc_username="BridgePlayer",
        
        # MiniWorld
        mnw_uin=123456,  # 你的 UIN
        mnw_passwd="your_password",  # 你的密码
        
        # 调试
        debug=True
    )
    
    bridge = MCPBridge(config)
    
    @bridge.on('bridging')
    async def on_bridging():
        print("=" * 60)
        print("BRIDGE ACTIVE - MC 1.20.6 <-> MNW")
        print("=" * 60)
        print(f"MC: {bridge.mc_client.player.username}")
        print(f"MNW: {bridge.mnw_client.player.name}")
    
    # 启动
    if await bridge.start():
        print("Bridge started. Press Ctrl+C to stop.")
        
        try:
            while bridge.is_running:
                await asyncio.sleep(1)
                stats = bridge.get_stats()
                print(f"Packets: MC->MNW={stats['packets_mc_to_mnw']}, "
                      f"MNW->MC={stats['packets_mnw_to_mc']}")
        except KeyboardInterrupt:
            print("\nStopping...")
        
        await bridge.stop()
    else:
        print("Failed to start bridge")

if __name__ == "__main__":
    asyncio.run(test_bridge())
```

---

## 预期结果

### 成功连接

```
[MC 1.20.6] Connected to server
[MC 1.20.6] Logged in as TestPlayer
[MC 1.20.6] Joined game!
  Entity ID: 123
  Gamemode: CREATIVE
```

### 桥接成功

```
============================================================
BRIDGE ACTIVE - MC 1.20.6 <-> MNW
============================================================
MC: BridgePlayer
MNW: YourName

Packets: MC->MNW=10, MNW->MC=8
```

---

## 故障排除

### 问题 1: 连接被拒绝

```
Failed to connect: [Errno 111] Connection refused
```

**解决**:
1. 确保 MC 服务器正在运行
2. 检查 `server.properties` 中的 `server-ip` 和 `server-port`
3. 关闭在线模式: `online-mode=false`

### 问题 2: 协议版本不匹配

```
Protocol version mismatch
```

**解决**:
- 确认 MC 服务器是 1.20.6
- 确认 protocol_version=766

### 问题 3: 登录失败

```
Login failed: Invalid credentials
```

**解决**:
- 使用离线模式服务器
- 或实现正版登录流程

---

## 测试清单

- [ ] MC 1.20.6 服务器运行
- [ ] 协议版本检查 (766)
- [ ] 连接测试
- [ ] 登录测试
- [ ] 加入游戏测试
- [ ] 位置同步测试
- [ ] 聊天桥接测试
- [ ] 断开连接测试

---

**Ready for MC 1.20.6 testing!**
