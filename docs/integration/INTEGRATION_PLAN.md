# MnMCP 3 + MN2MC + MnMCP-MN2MC 整合重构方案

**日期**: 2026-06-04  
**目标**: 取长补短，打造最强版本  
**策略**: 整合三版本优点，统一高质量架构

---

## 📊 三版本对比分析

### MnMCP 3 (当前)

| 优势 | 劣势 |
|------|------|
| ✅ 高质量代码结构 | ❌ 25% 实现度 |
| ✅ 类型注解 90%+ | ❌ 大量 TODO |
| ✅ 文档完整 | ❌ Mock 后端 |
| ✅ 结构化日志 | ❌ 缺乏真实协议 |

### MN2MC (Official)

| 优势 | 劣势 |
|------|------|
| ✅ 60% 实现度 | ❌ 代码质量一般 |
| ✅ 真实方块映射 (迷你世界ID) | ❌ 类型注解少 |
| ✅ 完整登录认证 | ❌ 文档不足 |
| ✅ 实际网络连接 | ❌ 架构较乱 |

### MnMCP-MN2MC (改进版)

| 优势 | 劣势 |
|------|------|
| ✅ 基于 MN2MC | ❌ 版本较老 |
| ✅ 可能有改进 | ❌ 需要对比 |

---

## 🎯 整合策略

### 核心原则

1. **架构**: 使用 MnMCP 3 的高质量架构
2. **实现**: 移植 MN2MC 的真实功能
3. **质量**: 统一代码质量标准
4. **兼容**: 保持向后兼容

---

## 🔧 具体整合方案

### Phase 1: 方块映射系统 (优先级: P0)

#### 当前问题
- MnMCP 3: 201个映射，使用自研ID系统
- MN2MC: 真实迷你世界方块ID

#### 整合方案
```python
# 新架构: 三层映射
MC_ID → MNW_ID (官方) → MNW_Name

# 示例
MC stone (1) → MNW 104 (岩石) → "岩石"
MC grass_block (2) → MNW 100 (长草土块) → "长草土块"
```

**实施步骤**:
1. 提取 MN2MC 的 blocks.py 映射
2. 重构为高质量 BlockMapper 类
3. 添加双向查询
4. 添加名称查找
5. 添加属性映射

### Phase 2: 登录认证系统 (优先级: P0)

#### 当前问题
- MnMCP 3: Mock 登录
- MN2MC: 真实 JWT + XXTEA + Sign

#### 整合方案
```python
# 新架构: 完整认证流程
1. XXTEA 加密请求
2. MD5 签名
3. HTTP POST 登录
4. JWT Token 解析
5. Session 维护
```

**实施步骤**:
1. 提取 MN2MC auth.py
2. 重构为 AsyncAuthManager
3. 添加错误处理
4. 添加自动重连
5. 添加状态管理

### Phase 3: 网络客户端 (优先级: P0)

#### 当前问题
- MnMCP 3: 框架
- MN2MC: 实际 aiosock + packet 处理

#### 整合方案
```python
# 新架构: 双向客户端
class DualClient:
    - mc_client: Minecraft 连接
    - mnw_client: MiniWorld 连接
    - bridge: 协议转换
```

**实施步骤**:
1. 提取 MN2MC mc/client.py
2. 提取 MN2MC mini/player.py
3. 重构为统一接口
4. 添加事件系统
5. 添加错误恢复

### Phase 4: 数据包事件 (优先级: P1)

#### 当前问题
- MnMCP 3: 占位符
- MN2MC: 完整事件系统

#### 整合方案
```python
# MN2MC 模式: 装饰器注册
def add_event(name, handler):
    EVENTS[name] = handler

@event("login")
async def on_login(client, data):
    pass
```

**实施步骤**:
1. 提取所有 packetevents
2. 重构为类方法
3. 添加类型注解
4. 添加文档

### Phase 5: 协议层 (优先级: P1)

#### 当前问题
- MnMCP 3: 自研协议
- MN2MC: ProtoBuf + Common

#### 整合方案
```python
# 统一使用 MN2MC 的 proto 层
- common.py: 基础消息
- ch.py: 频道消息
- hc.py: 高阶消息
```

---

## 📁 新架构设计

```
mnmcp_v3_integrated/
├── src/
│   ├── __init__.py
│   ├── config.py              # MnMCP 3 高质量配置
│   ├── bridge/                # 整合版桥接
│   │   ├── __init__.py
│   │   ├── core.py           # 核心桥接逻辑
│   │   └── events.py         # 事件处理
│   ├── mc/                    # Minecraft 客户端 (来自 MN2MC)
│   │   ├── __init__.py
│   │   ├── client.py         # MCClient (重构)
│   │   ├── packet.py         # 数据包处理
│   │   └── packetevents/     # 事件处理器 (全部移植)
│   ├── mini/                  # MiniWorld 客户端 (来自 MN2MC)
│   │   ├── __init__.py
│   │   ├── auth.py           # 认证 (重构)
│   │   ├── player.py         # 玩家控制
│   │   ├── packet.py         # 数据包
│   │   ├── packetevents/     # 事件处理器
│   │   └── proto/            # ProtoBuf 定义
│   │       ├── common.py
│   │       ├── ch.py
│   │       └── hc.py
│   ├── mapping/               # 方块映射 (整合)
│   │   ├── __init__.py
│   │   ├── blocks.py         # MN2MC 映射 + 质量提升
│   │   ├── items.py          # 物品映射
│   │   ├── mobs.py           # 生物映射
│   │   └── face.py           # 朝向映射
│   ├── crypto/                # 加密 (MN2MC + 改进)
│   │   ├── __init__.py
│   │   ├── xxtea.py          # XXTEA (MN2MC)
│   │   ├── ecdh.py           # ECDH (MN2MC)
│   │   ├── aes_gcm.py        # AES (MN2MC)
│   │   └── hkdf.py           # HKDF (MN2MC)
│   └── utils/                 # 工具函数
│       ├── __init__.py
│       └── helpers.py
├── tests/                     # 测试套件
├── tools/                     # 工具
│   └── mitm.py               # 中间人代理 (MN2MC)
└── main.py                    # 入口
```

---

## ⚡ 实施计划

### Week 1: 核心移植
- [ ] 方块映射系统重构
- [ ] 登录认证移植
- [ ] 基础客户端连接

### Week 2: 协议层
- [ ] ProtoBuf 协议移植
- [ ] 数据包事件系统
- [ ] 双向转发实现

### Week 3: 测试优化
- [ ] 整合测试套件
- [ ] 性能优化
- [ ] 文档更新

---

## 📈 预期成果

### 实现度目标
| 模块 | 当前 | 目标 |
|------|------|------|
| 方块映射 | 25% | 85% |
| 登录认证 | 10% | 90% |
| 网络连接 | 20% | 80% |
| 数据包处理 | 15% | 75% |
| 整体 | 25% | 80% |

### 质量目标
- 类型注解覆盖率: 85%+
- 文档覆盖率: 80%+
- 测试覆盖率: 70%+
- 代码复杂度: 适中

---

## ✅ 验收标准

- [ ] 使用 MN2MC 的真实方块映射 (1000+)
- [ ] 完整登录认证流程
- [ ] 实际网络连接 (非 Mock)
- [ ] 双向数据包转发
- [ ] 玩家位置同步
- [ ] 方块同步
- [ ] 聊天转发
- [ ] 局域网测试通过

---

**准备开始重构？**
