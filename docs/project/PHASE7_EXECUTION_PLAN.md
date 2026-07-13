# Phase 7: 集成测试 开发计划

**日期**: 2026-06-05  
**阶段**: Phase 7/8  
**目标**: 完整测试 MC-MNW 桥接流程

---

## 1. 测试目标

### 1.1 总体目标

验证 MnMCP 3 桥接系统的**功能正确性**、**稳定性**和**性能**。

```
┌─────────────────────────────────────────────────────────────┐
│                    Phase 7 测试范围                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   单元测试   │  │   集成测试   │  │   系统测试   │    │
│  │  ─────────  │  │  ─────────  │  │  ─────────  │    │
│  │ • 模块独立   │  │ • 模块协同   │  │ • 完整流程   │    │
│  │ • 函数正确   │  │ • 数据流转   │  │ • 端到端     │    │
│  │ • 边界条件   │  │ • 接口兼容   │  │ • 压力测试   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   功能测试   │  │   性能测试   │  │   稳定性测试 │    │
│  │  ─────────  │  │  ─────────  │  │  ─────────  │    │
│  │ • 正向流程   │  │ • 延迟测量   │  │ • 长时间     │    │
│  │ • 异常处理   │  │ • 吞吐测量   │  │ • 内存泄漏   │    │
│  │ • 边界情况   │  │ • 资源占用   │  │ • 连接恢复   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 具体目标

| 测试类型 | 目标 | 验收标准 |
|----------|------|----------|
| 单元测试 | 模块独立正确 | 覆盖率>80% |
| 集成测试 | 模块协同工作 | 数据流正确 |
| 系统测试 | 完整桥接流程 | 端到端通过 |
| 性能测试 | 延迟<50ms | 达标 |
| 稳定性测试 | 运行1小时无错 | 通过 |

---

## 2. 测试架构

### 2.1 测试目录结构

```
tests/
├── __init__.py
├── conftest.py              # pytest 配置
├── fixtures/                # 测试数据
│   ├── __init__.py
│   ├── blocks.py           # 方块测试数据
│   ├── packets.py          # 数据包测试数据
│   └── servers.py          # 服务器模拟
├── unit/                    # 单元测试
│   ├── __init__.py
│   ├── test_mapping.py     # 方块映射测试
│   ├── test_crypto.py      # 加密测试
│   ├── test_protocol.py    # 协议测试
│   ├── test_mc_client.py   # MC客户端测试
│   ├── test_mini_client.py # MNW客户端测试
│   └── test_bridge.py      # 桥接核心测试
├── integration/             # 集成测试
│   ├── __init__.py
│   ├── test_mc_flow.py     # MC流程测试
│   ├── test_mnw_flow.py    # MNW流程测试
│   └── test_bridge.py      # 桥接测试
├── system/                  # 系统测试
│   ├── __init__.py
│   ├── test_full_bridge.py # 完整桥接测试
│   └── test_performance.py # 性能测试
└── manual/                  # 手动测试
    ├── __init__.py
    ├── test_checklist.md   # 手动测试清单
    └── test_report.md      # 测试报告
```

### 2.2 测试工具

| 工具 | 用途 | 版本 |
|------|------|------|
| pytest | 测试框架 | >=7.0 |
| pytest-asyncio | 异步测试 | >=0.21 |
| pytest-cov | 覆盖率 | >=4.0 |
| pytest-benchmark | 性能测试 | >=4.0 |
| mock | 模拟 | >=4.0 |
| hypothesis | 模糊测试 | >=6.0 |

---

## 3. 单元测试计划

### 3.1 方块映射测试 (test_mapping.py)

```python
class TestBlockMapping:
    """方块映射单元测试"""
    
    def test_mc_to_mnw_basic(self):
        """测试基础 MC->MNW 映射"""
        mapper = BlockMapperIntegrated()
        assert mapper.mc_to_mnw(1) == 104  # stone
    
    def test_mnw_to_mc_basic(self):
        """测试基础 MNW->MC 映射"""
        mapper = BlockMapperIntegrated()
        assert mapper.mnw_to_mc(104) == 1  # stone
    
    def test_invalid_block(self):
        """测试无效方块"""
        mapper = BlockMapperIntegrated()
        assert mapper.mc_to_mnw(999999) is None
    
    def test_get_stats(self):
        """测试统计信息"""
        mapper = BlockMapperIntegrated()
        stats = mapper.get_stats()
        assert stats['total_mappings'] > 0
```

**测试用例**: 10+  
**预计工时**: 2h

### 3.2 加密测试 (test_crypto.py)

```python
class TestXXTEA:
    """XXTEA 加密测试"""
    
    def test_encrypt_decrypt(self):
        """测试加解密"""
        xxtea = MCPXXTEA(b"test_key_16bytes")
        plaintext = b"Hello, World!"
        ciphertext = xxtea.encrypt_zip(plaintext)
        decrypted = xxtea.decrypt_unzip(ciphertext)
        assert decrypted == plaintext
    
    def test_aes_cfb8(self):
        """测试 AES-CFB8"""
        crypto = MCProtocolCrypto()
        crypto.enable(b"key_16bytes_1234")
        plaintext = b"test"
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        assert decrypted == plaintext
```

**测试用例**: 8+  
**预计工时**: 2h

### 3.3 协议测试 (test_protocol.py)

```python
class TestProtocol:
    """协议层测试"""
    
    def test_varint_encode(self):
        """测试 VarInt 编码"""
        assert VarInt.encode(0) == b'\x00'
        assert VarInt.encode(128) == b'\x80\x01'
    
    def test_varint_decode(self):
        """测试 VarInt 解码"""
        assert VarInt.decode(b'\x00')[0] == 0
        assert VarInt.decode(b'\x80\x01')[0] == 128
    
    def test_packet_codec(self):
        """测试数据包编解码"""
        codec = MCPProtocolCodec()
        packet = codec.create_packet(9001, b"test", PacketDirection.CLIENT_TO_SERVER)
        encoded = codec.encode(packet)
        decoded = codec.decode(encoded, PacketDirection.CLIENT_TO_SERVER)
        assert decoded.msg_code == 9001
```

**测试用例**: 15+  
**预计工时**: 2h

### 3.4 MC 客户端测试 (test_mc_client.py)

```python
class TestMCClient:
    """MC 客户端测试"""
    
    @pytest.mark.asyncio
    async def test_create_client(self):
        """测试创建客户端"""
        client = MCPMinecraftClient()
        assert client is not None
    
    @pytest.mark.asyncio
    async def test_event_registration(self):
        """测试事件注册"""
        client = MCPMinecraftClient()
        
        @client.on('join')
        async def on_join():
            pass
        
        assert len(client._event_handlers['join']) == 1
```

**测试用例**: 8+  
**预计工时**: 2h

### 3.5 MNW 客户端测试 (test_mini_client.py)

```python
class TestMiniClient:
    """MNW 客户端测试"""
    
    @pytest.mark.asyncio
    async def test_create_client(self):
        """测试创建客户端"""
        config = MiniClientConfig()
        client = MCPMiniClient(config)
        assert client is not None
```

**测试用例**: 6+  
**预计工时**: 1h

### 3.6 桥接核心测试 (test_bridge.py)

```python
class TestBridge:
    """桥接核心测试"""
    
    def test_create_bridge(self):
        """测试创建桥接器"""
        config = MCPBridgeConfig()
        bridge = MCPBridge(config)
        assert bridge is not None
    
    def test_yaw_conversion(self):
        """测试 Yaw 转换"""
        bridge = MCPBridge()
        assert bridge._mc_yaw_to_mnw(0) == 180
        assert bridge._mnw_yaw_to_mc(180) == 0
```

**测试用例**: 6+  
**预计工时**: 1h

**单元测试总计**: 53+ 用例, 10h

---

## 4. 集成测试计划

### 4.1 MC 流程测试 (test_mc_flow.py)

| 测试项 | 场景 | 预期结果 |
|--------|------|----------|
| test_connect | 连接本地服务器 | 连接成功 |
| test_login | 登录流程 | 登录成功 |
| test_position_sync | 位置同步 | 位置更新 |
| test_chat | 聊天发送 | 消息发送 |

**测试用例**: 4+  
**预计工时**: 2h

### 4.2 MNW 流程测试 (test_mnw_flow.py)

| 测试项 | 场景 | 预期结果 |
|--------|------|----------|
| test_login | HTTP 认证 | 获取 token |
| test_room_list | 房间列表 | 返回房间 |
| test_join_room | 加入房间 | 进入世界 |
| test_move | 移动请求 | 位置更新 |

**测试用例**: 4+  
**预计工时**: 2h

### 4.3 桥接测试 (test_bridge.py)

| 测试项 | 场景 | 预期结果 |
|--------|------|----------|
| test_start_bridge | 启动桥接 | 两个客户端连接 |
| test_position_bridge | 位置桥接 | MC移动->MNW更新 |
| test_chat_bridge | 聊天桥接 | 消息转发 |
| test_stop_bridge | 停止桥接 | 优雅断开 |

**测试用例**: 4+  
**预计工时**: 2h

**集成测试总计**: 12+ 用例, 6h

---

## 5. 系统测试计划

### 5.1 完整桥接测试 (test_full_bridge.py)

```python
@pytest.mark.system
def test_full_bridge_flow():
    """
    完整桥接流程测试
    
    1. 启动桥接器
    2. MC 客户端连接本地服务器
    3. MNW 客户端连接房间
    4. 移动 MC 玩家
    5. 验证 MNW 玩家位置更新
    6. 发送 MC 聊天
    7. 验证 MNW 收到聊天
    8. 停止桥接器
    """
    pass
```

**测试用例**: 2+  
**预计工时**: 2h

### 5.2 性能测试 (test_performance.py)

| 测试项 | 指标 | 目标 |
|--------|------|------|
| test_latency | 包转发延迟 | <50ms |
| test_throughput | 包吞吐量 | >1000/s |
| test_memory | 内存占用 | <100MB |
| test_cpu | CPU 占用 | <10% |

**测试用例**: 4+  
**预计工时**: 2h

**系统测试总计**: 6+ 用例, 4h

---

## 6. 手动测试清单

### 6.1 功能测试

- [ ] 启动桥接器
- [ ] MC 客户端连接
- [ ] MNW 客户端连接
- [ ] MC 移动 -> MNW 可见
- [ ] MNW 移动 -> MC 可见
- [ ] MC 聊天 -> MNW 收到
- [ ] MNW 聊天 -> MC 收到
- [ ] MC 放置方块 -> MNW 可见
- [ ] MNW 放置方块 -> MC 可见
- [ ] 断开桥接器

### 6.2 异常测试

- [ ] MC 断开 -> 桥接器处理
- [ ] MNW 断开 -> 桥接器处理
- [ ] 网络抖动 -> 自动恢复
- [ ] 高延迟 -> 平滑同步

---

## 7. 测试执行计划

| 阶段 | 任务 | 计划 | 状态 |
|------|------|------|------|
| 7.1 | 单元测试 | 10h | ⏳ |
| 7.2 | 集成测试 | 6h | ⏳ |
| 7.3 | 系统测试 | 4h | ⏳ |
| 7.4 | 手动测试 | 4h | ⏳ |
| **总计** | | **24h** | |

**实际目标**: 8h (核心测试)

---

## 8. 验收标准

### 8.1 覆盖率目标

| 模块 | 目标 | 最低 |
|------|------|------|
| mcp_mapping | 80% | 70% |
| mcp_crypto | 90% | 80% |
| mcp_protocol | 80% | 70% |
| mcp_mc | 60% | 50% |
| mcp_mini | 60% | 50% |
| mcp_core | 70% | 60% |
| **总体** | **75%** | **65%** |

### 8.2 功能验收

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 系统测试通过
- [ ] 手动测试通过
- [ ] 性能达标

---

## 9. 风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| 缺少测试环境 | 高 | 高 | 使用 Mock |
| 时间不足 | 中 | 中 | 优先核心测试 |
| 测试不稳定 | 中 | 中 | 重试机制 |
| 覆盖率不足 | 低 | 中 | 逐步补充 |

---

## 10. 交付物

| 交付物 | 说明 | 状态 |
|--------|------|------|
| tests/ 目录 | 完整测试代码 | ⏳ |
| pytest.ini | 测试配置 | ⏳ |
| coverage_report.html | 覆盖率报告 | ⏳ |
| test_report.md | 测试报告 | ⏳ |

---

**Phase 7 开发计划完成，开始实施！**
