# MnMCP 测试指南

**Version**: Victoria v3.1-20260605 Phase8 RC

---

## 快速测试

### 1. 环境检查

```bash
# 检查 Python 版本
python --version  # 需要 3.9+

# 检查 Git
git --version
```

### 2. 安装依赖

```bash
cd mnmcp-v3-integrated

# 安装依赖
pip install pyyaml

# 可选依赖（完整功能）
pip install aiohttp cryptography
```

### 3. 运行验证脚本

```bash
python verify_mn3.py
```

**预期输出**:
```
MnMCP v3 重构版验证
...
[1/10] 测试方块映射系统
  总映射数: 56
...
[10/10] 测试桥接核心

总计: 10/10 通过 (100%)
所有测试通过！MnMCP v3 重构成功！
```

---

## 功能测试

### 测试 1: 方块映射

```python
# test_mapping.py
from src.mcp_mapping.blocks_integrated import BlockMapperIntegrated

mapper = BlockMapperIntegrated()

# MC Stone (ID: 1) -> MNW
mnw_id = mapper.mc_to_mnw(1)
print(f"MC Stone (1) -> MNW: {mnw_id}")

# 反向映射
mc_id = mapper.mnw_to_mc(mnw_id)
print(f"MNW {mnw_id} -> MC: {mc_id}")
```

### 测试 2: 协议编解码

```python
# test_protocol.py
from src.mcp_protocol.codec import MCPProtocolCodec, PacketDirection

codec = MCPProtocolCodec()

# 创建数据包
packet = codec.create_packet(
    msg_code=9001,
    data=b'{"msg":"Hello"}',
    direction=PacketDirection.CLIENT_TO_SERVER
)

# 编码
encoded = codec.encode(packet)
print(f"Encoded: {len(encoded)} bytes")

# 解码
decoded = codec.decode(encoded, PacketDirection.CLIENT_TO_SERVER)
print(f"Message: {decoded.get_message_name()}")
```

### 测试 3: 加密

```python
# test_crypto.py
from src.mcp_crypto.xxtea_mcp import MCPXXTEA

xxtea = MCPXXTEA(b"test_key_16bytes")

plaintext = b"Hello, MnMCP!"
encrypted = xxtea.encrypt_zip(plaintext)
decrypted = xxtea.decrypt_unzip(encrypted)

assert decrypted == plaintext
print("加密/解密测试通过")
```

### 测试 4: 桥接核心

```python
# test_bridge.py
import asyncio
from src.mcp_core.bridge import MCPBridge, MCPBridgeConfig

async def test_bridge():
    config = MCPBridgeConfig(
        mc_host="localhost",
        mc_port=25565,
        mc_username="TestPlayer",
        mnw_uin=123456,
        mnw_passwd="password"
    )
    
    bridge = MCPBridge(config)
    
    # 测试 Yaw 转换
    mc_yaw = 0  # 南
    mnw_yaw = bridge._mc_yaw_to_mnw(mc_yaw)
    print(f"MC Yaw {mc_yaw} -> MNW Yaw {mnw_yaw}")
    
    # 反向
    back_to_mc = bridge._mnw_yaw_to_mc(mnw_yaw)
    print(f"MNW Yaw {mnw_yaw} -> MC Yaw {back_to_mc}")
    
    assert back_to_mc == mc_yaw
    print("坐标转换测试通过")

asyncio.run(test_bridge())
```

---

## 集成测试

### 测试 5: 完整流程（需要服务器）

```python
# test_full.py
import asyncio
from src.mcp_core.bridge import MCPBridge, MCPBridgeConfig

async def main():
    config = MCPBridgeConfig(
        mc_host="localhost",      # MC 服务器地址
        mc_port=25565,             # MC 端口
        mc_username="BridgePlayer",
        mnw_uin=123456,            # 你的 MNW UIN
        mnw_passwd="your_password" # 你的 MNW 密码
    )
    
    bridge = MCPBridge(config)
    
    @bridge.on('bridging')
    async def on_bridging():
        print("桥接启动成功！")
        print(f"MC: {bridge.mc_client.player.username}")
        print(f"MNW: {bridge.mnw_client.player.name}")
    
    # 启动桥接
    if await bridge.start():
        print("桥接器运行中...")
        
        # 保持运行
        while bridge.is_running:
            await asyncio.sleep(1)
            
            # 显示统计
            stats = bridge.get_stats()
            print(f"包转发: MC->MNW={stats['packets_mc_to_mnw']}, "
                  f"MNW->MC={stats['packets_mnw_to_mc']}")
    
    # 停止
    await bridge.stop()

asyncio.run(main())
```

---

## 测试清单

### 单元测试
- [ ] 方块映射 (test_mapping.py)
- [ ] 加密模块 (test_crypto.py)
- [ ] 协议编解码 (test_protocol.py)
- [ ] MC 客户端 (test_mc_client.py)
- [ ] MNW 客户端 (test_mini_client.py)
- [ ] 桥接核心 (test_bridge.py)

### 集成测试
- [ ] 完整流程 (test_full.py)
- [ ] 位置同步
- [ ] 聊天转发

### 手动测试
- [ ] 安装依赖
- [ ] 运行验证脚本
- [ ] 检查统计信息

---

## 故障排除

### 问题 1: 模块未找到
```
ModuleNotFoundError: No module named 'yaml'
```
**解决**: `pip install pyyaml`

### 问题 2: 相对导入错误
```
ImportError: attempted relative import beyond top-level package
```
**解决**: 使用 `sys.path.insert(0, 'src')` 或从根目录运行

### 问题 3: 网络连接失败
```
Failed to connect to github.com
```
**解决**: 检查网络或稍后重试

---

## 性能测试

```python
# benchmark.py
import time
from src.mcp_protocol.codec import MCPProtocolCodec, PacketDirection

codec = MCPProtocolCodec()

# 测试 1000 次编解码
start = time.time()
for i in range(1000):
    packet = codec.create_packet(9001, b"test", PacketDirection.CLIENT_TO_SERVER)
    encoded = codec.encode(packet)
    decoded = codec.decode(encoded, PacketDirection.CLIENT_TO_SERVER)
end = time.time()

print(f"1000 次编解码: {end - start:.3f} 秒")
print(f"每次平均: {(end - start) / 1000 * 1000:.3f} ms")
```

---

**准备就绪，开始测试！**
