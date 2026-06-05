# Victoria v3.0-20260605 Phase7 RC Release Notes

**版本**: Victoria v3.0-20260605 Phase7 RC  
**日期**: 2026-06-05  
**类型**: Release Candidate (RC)  
**状态**: Pre-Release

---

## 版本命名规范

```
Victoria v3.0-20260605 Phase7 RC
```

---

## 功能清单

### Phase 1-3: 基础层
- 方块映射系统 (844个映射)
- XXTEA 加密/解密
- AES-CFB8 加密 (MC)
- JWT 认证
- 统一配置系统

### Phase 4-5: 客户端层
- Minecraft 客户端 (TCP/MC协议)
- MiniWorld 客户端 (UDP/RakNet)
- 纯 Python 实现
- 100% 类型注解
- 统一事件系统

### Phase 6: 桥接核心
- MCPBridge 核心
- 双向数据转发
- 20Hz 位置同步
- 坐标转换 (Yaw映射)

### Phase 7: 测试层
- 测试基础设施
- 单元测试 (33+ 用例)
- pytest 配置

---

## 代码统计

```
核心代码:     ~4,000 行
测试代码:       ~400 行
文档:         ~2,500 行
───────────────────────
总计:         ~7,400 行

模块数:       10+ 核心模块
测试用例:     33+ 单元测试
```

---

## 快速开始

```python
from mcp_core import MCPBridge, MCPBridgeConfig

config = MCPBridgeConfig(
    mc_host="localhost",
    mc_port=25565,
    mc_username="BridgePlayer",
    mnw_uin=123456,
    mnw_passwd="password"
)

bridge = MCPBridge(config)
await bridge.start()
```

---

**Victoria v3.0-20260605 Phase7 RC**
