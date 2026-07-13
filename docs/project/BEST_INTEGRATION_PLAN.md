# MnMCP 最佳整合执行计划

**执行策略**: 基础层 → 中间层 → 上层 → 验证  
**命名规范**: 统一前缀 `mcp_` 避免冲突  
**质量标准**: 保持 MnMCP 3 的 ⭐⭐⭐⭐⭐ 质量

---

## 📋 执行顺序 (依赖优化)

### Phase 1: 数据层 (无依赖) ✅
- [x] 方块映射系统 (56/1160)

### Phase 2: 配置层 (无依赖) 🔄
- [ ] 统一配置系统
- [ ] 环境变量管理
- [ ] 多版本配置

### Phase 3: 加密层 (配置依赖) ⏳
- [ ] XXTEA (MN2MC)
- [ ] ECDH (MN2MC)
- [ ] AES-GCM (MN2MC)

### Phase 4: 认证层 (加密依赖) ⏳
- [ ] HTTP 登录 (MN2MC)
- [ ] JWT 解析 (MN2MC)
- [ ] Session 管理 (MN2MC)

### Phase 5: 网络层 (认证依赖) ⏳
- [ ] MC 客户端 (MN2MC)
- [ ] MNW 客户端 (MN2MC)
- [ ] 连接池管理

### Phase 6: 协议层 (网络依赖) ⏳
- [ ] ProtoBuf 协议 (MN2MC)
- [ ] 数据包编解码
- [ ] 事件系统

### Phase 7: 桥接层 (协议依赖) ⏳
- [ ] 双向转发
- [ ] 状态同步
- [ ] 错误恢复

### Phase 8: 验证 (全依赖) ⏳
- [ ] 单元测试
- [ ] 集成测试
- [ ] 局域网测试

---

## 🏗️ 新命名规范

### 模块命名
```
旧: mn2mc/          → 新: mcp_core/
旧: mini/           → 新: mcp_mini/
旧: mc/             → 新: mcp_mc/
旧: mapping/         → 新: mcp_mapping/
旧: crypto/         → 新: mcp_crypto/
旧: config.py       → 新: mcp_config.py
```

### 类命名
```
旧: BlockMapper     → 新: MCPBlockMapper
旧: MiniWorldLogin  → 新: MCPAuthManager
旧: MCClient        → 新: MCPMinecraftClient
旧: MiniPlayer      → 新: MCPMiniWorldClient
旧: BridgeServer    → 新: MCPBridgeServer
```

### 函数命名
```
旧: mc_to_mini()    → 新: map_mc_to_mnw()
旧: login()         → 新: authenticate()
旧: connect()       → 新: establish_connection()
```

---

## 🚀 立即开始 Phase 2-3

### 当前任务

1. **提取完整方块映射** (1160个)
2. **重构配置系统** (统一)
3. **移植加密模块** (XXTEA/ECDH/AES)

### 预期产出

- `mcp_mapping/blocks_full.py` - 完整1160个映射
- `mcp_config/unified.py` - 统一配置
- `mcp_crypto/xxtea.py` - XXTEA加密
- `mcp_crypto/ecdh.py` - ECDH密钥交换
- `mcp_crypto/aes_gcm.py` - AES加密

---

**开始执行！**
