# MnMCP 3 开发路线图

**版本**: 2026-05-23-14  
**状态**: 准备开始开发  
**基于**: v5.0 Hybrid Architecture + 协议真相

---

## 🎯 核心目标

实现**混合架构桥接器**:
1. **认证模式**: 通过迷你世界官方服务器登录，获取有效会话
2. **桥接模式**: 拦截UDP流量，将迷你世界协议翻译为Minecraft协议
3. **无缝切换**: 用户在聊天栏输入命令切换模式

---

## 📊 当前状态评估

### 已有资源 (✅)

| 资源 | 状态 | 说明 |
|------|------|------|
| SO逆向分析报告 | ✅ | 69,672文件已扫描，密钥结构清晰 |
| APK反编译源码 | ✅ | 国服+外服，协议实现可参考 |
| 抓包数据 | ✅ | Proxifier日志，Wireshark捕获 |
| 加密实现 | ✅ | XXTEA, AES-128-GCM, ECDH+HKDF |
| 映射数据 | ✅ | 2,909方块, 1,289实体, 1,416物品 |
| MN2MC基础 | ✅ | 项目结构完整，需重构 |

### 技术债务 (需立即处理)

| 问题 | 优先级 | 工作量 |
|------|--------|--------|
| 硬编码密钥 | P0 | 2h |
| 错误处理缺失 | P0 | 4h |
| 全局变量重构 | P1 | 6h |
| 类型注解补全 | P1 | 4h |

---

## 🗓️ 开发阶段 (时间线版本管理)

### Phase 1: 基础重构 (Day 1-2)

**目标**: 清理技术债务，建立开发基础

#### Day 1 (2026-05-24)
- [x] 08:00-10:00 移除硬编码密钥 (TD-001)
- [x] 10:00-12:00 创建config.template.yaml
- [ ] 13:00-15:00 添加基础错误处理 (TD-003)
- [ ] 15:00-17:00 测试MN2MC启动

#### Day 2 (2026-05-24)
- [ ] 08:00-12:00 重构全局变量为类 (TD-004)
- [ ] 13:00-17:00 补充类型注解 (TD-005)

**产出**:
- `config.template.yaml` 安全配置模板
- `mn2mc/core/` 重构后的核心模块
- 类型安全代码 (mypy通过)

---

### Phase 2: UDP协议栈 (Day 3-5)

**目标**: 实现迷你世界UDP协议处理

#### Day 3 (2026-05-25)
- [ ] 实现RakNet基础协议
  - [ ] 协议头解析 (24 bytes)
  - [ ] 包序列号管理
  - [ ] ACK/NAK机制

#### Day 4 (2026-05-26)
- [ ] 实现加密层
  - [ ] ECDH密钥交换
  - [ ] HKDF密钥派生
  - [ ] AES-128-GCM加解密

#### Day 5 (2026-05-27)
- [ ] 房间发现协议
  - [ ] UDP广播监听
  - [ ] 房间列表解析
  - [ ] 伪造房间注入

**产出**:
- `mn2mc/network/raknet.py` RakNet实现
- `mn2mc/crypto/session.py` 会话管理
- `mn2mc/room/discovery.py` 房间发现

---

### Phase 3: 混合代理 (Day 6-8)

**目标**: 实现智能代理，支持模式切换

#### Day 6 (2026-05-28)
- [ ] 代理核心架构
  - [ ] SmartProxy类设计
  - [ ] 模式状态机
  - [ ] 流量分类器

#### Day 7 (2026-05-29)
- [ ] 认证劫持
  - [ ] 拦截登录响应
  - [ ] 提取session token
  - [ ] 保存玩家数据

#### Day 8 (2026-05-30)
- [ ] 模式切换
  - [ ] 聊天命令解析
  - [ ] `/mnmcp minecraft` 命令
  - [ ] `/mnmcp real` 命令

**产出**:
- `mn2mc/proxy/smart_proxy.py` 智能代理
- `mn2mc/auth/interceptor.py` 认证拦截
- `mn2mc/commands/` 命令处理

---

### Phase 4: 桥接核心 (Day 9-12)

**目标**: 实现协议翻译和实体同步

#### Day 9-10 (2026-05-31 ~ 06-01)
- [ ] 玩家同步
  - [ ] 位置/旋转转换
  - [ ] 动作映射
  - [ ] 背包同步

#### Day 11-12 (2026-06-02 ~ 06-03)
- [ ] 世界同步
  - [ ] 区块转换
  - [ ] 方块放置/破坏
  - [ ] 实体生成

**产出**:
- `mn2mc/bridge/player_sync.py` 玩家同步
- `mn2mc/bridge/world_sync.py` 世界同步
- `mn2mc/bridge/entity_mapper.py` 实体映射

---

### Phase 5: 内网穿透 (Day 13-14)

**目标**: 集成frp，实现房间创建

#### Day 13 (2026-06-04)
- [ ] frp客户端集成
  - [ ] 配置文件生成
  - [ ] 进程管理
  - [ ] 状态监控

#### Day 14 (2026-06-05)
- [ ] 房间注册
  - [ ] API调用封装
  - [ ] 房间元数据构造
  - [ ] 穿透地址上报

**产出**:
- `mn2mc/tunnel/frp_client.py` FRP客户端
- `mn2mc/room/registration.py` 房间注册
- `tools/frp/` FRP二进制和配置

---

### Phase 6: 测试与优化 (Day 15-18)

**目标**: 端到端测试，性能优化

#### Day 15-16 (2026-06-06 ~ 06-07)
- [ ] 单元测试
  - [ ] crypto模块测试
  - [ ] protocol模块测试
  - [ ] bridge模块测试

#### Day 17-18 (2026-06-08 ~ 06-09)
- [ ] 性能优化
  - [ ] 异步优化
  - [ ] 内存优化
  - [ ] 延迟测试

**产出**:
- `tests/` 测试套件
- 性能基准报告
- 优化建议文档

---

## 🏗️ 模块架构

### 新目录结构

```
mn2mc/
├── __init__.py
├── version.py                    # 时间线版本
│
├── core/                         # 核心基础设施
│   ├── __init__.py
│   ├── config.py                 # 配置管理 (重构)
│   ├── exceptions.py             # 自定义异常
│   ├── logging.py                # 日志配置
│   └── types.py                  # 类型定义
│
├── crypto/                       # 加密模块
│   ├── __init__.py
│   ├── xxtea.py                  # 现有，优化
│   ├── aes_gcm.py                # AES-128-GCM
│   ├── ecdh.py                   # ECDH密钥交换
│   ├── hkdf.py                   # HKDF密钥派生
│   └── session.py                # 会话管理
│
├── network/                      # 网络层
│   ├── __init__.py
│   ├── raknet/                   # RakNet协议
│   │   ├── __init__.py
│   │   ├── packet.py             # 包结构
│   │   ├── connection.py         # 连接管理
│   │   └── server.py             # 服务端
│   ├── websocket/                # WebSocket
│   │   ├── __init__.py
│   │   └── client.py
│   └── http/                     # HTTP客户端
│       ├── __init__.py
│       └── client.py
│
├── protocol/                     # 协议解析
│   ├── __init__.py
│   ├── mini/                     # 迷你世界协议
│   │   ├── __init__.py
│   │   ├── common.py             # 公共定义
│   │   ├── login.py              # 登录协议
│   │   ├── room.py               # 房间协议
│   │   └── game.py               # 游戏协议
│   └── mc/                       # Minecraft协议
│       ├── __init__.py
│       └── (迁移现有代码)
│
├── proxy/                        # 代理层 (新增)
│   ├── __init__.py
│   ├── smart_proxy.py            # 智能代理
│   ├── interceptor.py            # 流量拦截
│   ├── classifier.py             # 流量分类
│   └── switcher.py               # 模式切换
│
├── auth/                         # 认证管理 (重构)
│   ├── __init__.py
│   ├── manager.py                # 认证管理器
│   ├── interceptor.py            # 登录拦截
│   └── session.py                # 会话存储
│
├── room/                         # 房间管理 (新增)
│   ├── __init__.py
│   ├── discovery.py              # 房间发现
│   ├── registration.py           # 房间注册
│   ├── manager.py                # 房间管理
│   └── state.py                  # 房间状态
│
├── tunnel/                       # 内网穿透 (新增)
│   ├── __init__.py
│   ├── frp_client.py             # FRP客户端
│   ├── ngrok_client.py           # Ngrok支持
│   └── manager.py                # 穿透管理
│
├── bridge/                       # 桥接核心 (重构)
│   ├── __init__.py
│   ├── base.py                   # 桥接基类
│   ├── player_sync.py            # 玩家同步
│   ├── world_sync.py             # 世界同步
│   ├── entity_mapper.py          # 实体映射
│   └── packet_translator.py      # 包翻译
│
├── mapping/                      # 数据映射 (迁移)
│   └── (保持现有)
│
├── commands/                     # 命令系统 (新增)
│   ├── __init__.py
│   ├── parser.py                 # 命令解析
│   ├── handlers.py               # 命令处理器
│   └── registry.py               # 命令注册
│
└── utils/                        # 工具函数
    └── (保持现有)
```

---

## 📝 每日开发流程

### 晨会 (09:00)
- 回顾昨日进度
- 确认今日目标
- 识别阻塞问题

### 开发时间 (09:30-12:00, 13:00-17:00)
- 专注开发
- 每2小时提交一次
- 提交信息格式: `YYYY-MM-DD-HH: 描述`

### 日终总结 (17:30)
- 更新进度到DEVELOPMENT_PROGRESS.md
- 记录遇到的问题
- 更新技术债务

### 版本标记
- 每日结束创建tag: `git tag 2026-05-24`
- 每周结束创建里程碑tag: `git tag 2026-05-24-milestone`

---

## 🧪 测试策略

### 单元测试
```bash
pytest tests/unit/ -v --cov=mn2mc
```

### 集成测试
```bash
pytest tests/integration/ -v
```

### 端到端测试
```bash
python -m mn2mc.test.e2e
```

### 性能测试
```bash
python -m mn2mc.test.benchmark
```

---

## 📊 成功指标

| 指标 | 目标 | 当前 | 状态 |
|------|------|------|------|
| 代码测试覆盖率 | >80% | 0% | 🔴 |
| 类型检查通过率 | 100% | ~30% | 🟡 |
| P0技术债务 | 0 | 3 | 🔴 |
| UDP协议实现 | 完整 | 0% | 🔴 |
| 桥接功能 | 可用 | 0% | 🔴 |
| 文档完整度 | >90% | ~50% | 🟡 |

---

## ⚠️ 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 协议变更 | 中 | 高 | 保留协议版本兼容层 |
| 加密算法理解错误 | 中 | 高 | 多参考逆向工程报告 |
| 性能瓶颈 | 中 | 中 | 早期性能测试 |
| 依赖更新问题 | 低 | 中 | 锁定依赖版本 |

---

## ✅ 准备完成确认

启动开发前确认:

- [x] 开发路线图已制定
- [x] 技术债务已识别
- [x] 模块架构已设计
- [x] 资源文件已清点
- [x] 时间线版本机制已建立
- [ ] 配置模板已创建 (待完成)
- [ ] 开发环境已准备 (待完成)

---

**下一步**: 开始Phase 1 - 基础重构

**预计完成**: 2026-06-09 (18个工作日)  
**里程碑**: 每个Phase结束进行演示
