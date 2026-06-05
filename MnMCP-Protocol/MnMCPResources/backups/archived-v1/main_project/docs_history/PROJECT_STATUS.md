# MnMCP 项目状态

**最后更新**: 2026-03-03  
**当前版本**: v0.3.1_26w10a_Phase 7  
**状态**: Phase 7 进行中 - 联机模块重写 + 游戏数据集成 + 2.0网络架构设计

---

## 2.0 网络架构 (VPN虚拟网段 + WinTun)

### 架构概述
MnMCP 2.0 采用 **VPN虚拟网段 + WinTun驱动** 作为核心网络方案：
- **透明拦截**: 无需修改客户端配置
- **内核级性能**: 低延迟流量捕获
- **全流量捕获**: 所有网络包（包括UDP）
- **三种场景**: 完整支持场景A/B/C

### 技术债务清单

#### 高优先级（阻塞2.0发布）
- [ ] WinTun驱动自动安装
- [ ] 路由表自动配置
- [ ] 场景A包复制实现
- [ ] 场景B虚拟房间注入

#### 中优先级
- [ ] Linux TUN支持
- [ ] 性能优化
- [ ] 错误恢复机制

### 相关文档
- [2.0网络架构文档](docs/Network_2.0_Architecture.md)
- [WinTun设置指南](docs/WINTUN_SETUP.md)
- [开发日志-2026-03-03](docs/Phase7_DevLog_20260303.md)

---

## 版本说明

版本号 `v0.3.1_26w10a_Phase 7` 含义:
- `v0.3.1`: 主版本号，联机模块重写 + 完整游戏数据集成
- `26w10a`: 2026年第10周，快照a
- `Phase 7`: 当前开发阶段

---

## 项目概述

MnMCP (Minecraft & MiniWorld Cross-Platform Proxy) 是一个实现 Minecraft 和迷你世界跨平台联机的代理服务器。

### 核心功能
- ✅ 双向协议翻译 (MNW ↔ MC)
- ✅ 方块ID映射 (2969条完整双向映射，含替代规则)
- ✅ 实体/生物ID映射 (1348条，含野人↔僵尸/骷髅硬编码)
- ✅ 物品ID映射 (1460条，含替代规则)
- ✅ 生物群系映射 (90条)
- ✅ AES加密支持 (CBC/GCM)
- ✅ 异步代理服务器 (TCP + UDP双通道)
- ✅ 配置管理 (支持自定义中继服务器地址)
- ✅ 性能监控
- ✅ 错误处理
- ✅ 项目完整性检查
- 🆕 VPN虚拟网段网络包捕获 (框架完成)
- 🆕 中继服务器 Streamer版本 (TCP+UDP双通道)
- 🆕 客户端 Personal版本 (场景A/B/C框架)
- 🆕 三种联机场景支持 (A/B/C)
- 🆕 自定义中继服务器地址

---

## 开发阶段

### ✅ Phase 1: 基础实现 (v0.2.2)
- 生产级AES加密
- 方块ID映射基础
- 协议验证工具
- 密码哈希实现

### ✅ Phase 2: 协议实现 (v0.3.0)
- ACE绕过工具
- Frida Hook脚本
- 协议翻译核心
- 连接管理器

### ✅ Phase 3: 连接测试 (v0.4.0)
- Minecraft协议基础
- 代理服务器v2
- 配置系统
- 启动脚本

### ✅ Phase 4: 项目整理 (v0.4.0)
- 文件手动整理
- 测试重写 (真实测试)
- 文档整理
- 项目结构优化

### ✅ Phase 5: 稳定版本 (v0.5.0)
- 性能监控模块
- 错误处理模块
- 项目完整性检查
- 问题修复

### ✅ Phase 6: 文档与部署 (v0.2.5)
- 文档完善与更新
- 部署验证
- 发布准备

### 🚧 Phase 7: 联机模块重写 (v0.3.1) — 当前阶段

**已完成:**
- ✅ 从备份恢复13个丢失的核心模块源码
- ✅ 修复 local_proxy.py 语法错误
- ✅ 解压 csvdef.zip 全部186个CSV游戏数据定义
- ✅ 构建方块双向映射表 v3 (2969条: 2240已匹配 + 668 MNW独有→MC石头 + 61 MC独有→MNW长草)
- ✅ 构建实体/生物双向映射表 v1 (1348条: 14匹配 + 1275 MNW独有→MC村民 + 59 MC独有→MNW卡卡)
- ✅ 构建物品双向映射表 v1 (1460条: MNW独有→MC木剑, MC独有→MNW地形编辑器)
- ✅ 构建生物群系映射表 v1 (90条)
- ✅ 新增 entity_mapper.py 和 item_mapper.py 模块
- ✅ RelayServer 添加 UDP 协议支持 (MNWUDPProtocol)
- ✅ ProtocolBridge 添加高层翻译接口 (translate_mnw_to_mc / translate_mc_to_mnw)
- ✅ 更新 block_mapper.py 优先加载 v3 完整映射
- ✅ 代码审查与关键问题修复 (logger.py, protocol_translator.py, tests/__init__.py)
- ✅ 2.0网络架构文档 (VPN虚拟网段 + WinTun)
- ✅ 技术债务清单整理
- ✅ 贡献指南文档 (CONTRIBUTING.md)
- ✅ README.md 格式保护注释

**进行中:**
- 🚧 VPN虚拟网段 Windows WinTun 驱动集成
- 🚧 场景A/B/C 核心逻辑实现
- 🚧 迷你世界协议逆向验证

**待开发:**
- ⬜ WinTun驱动自动安装脚本
- ⬜ 路由表自动配置
- ⬜ 场景A包复制实现
- ⬜ 场景B虚拟房间注入
- ⬜ Flutter 跨平台客户端 (PC + Android)
- ⬜ Kotlin/Dart 后端服务层
- ⬜ 打包 EXE/APK
- ⬜ 算法差异处理模块 (箭/矛轨迹以MNW为准)
- ⬜ MC Bedrock RakNet 层实现

---

## 映射替代规则

| 情况 | MC端显示 | MNW端显示 |
|------|----------|-----------|
| MNW独有方块 | 石头(stone)外观，名称同步 | 正常显示 |
| MC独有方块 | 正常显示 | 长草方块外观，名称同步 |
| MNW独有物品 | 木剑外观，名称同步 | 正常显示 |
| MC独有物品 | 正常显示 | 地形编辑器外观，名称同步 |
| MNW独有生物 | 图书馆村民外观，名称同步 | 正常显示 |
| MC独有生物 | 正常显示 | 卡卡(ID=3095)外观，名称同步 |
| 野人战士(3101) | Zombie | 野人战士 |
| 野人投矛手(3105) | Skeleton | 野人投矛手 |

---

## 项目结构

```
Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/
├── src/                        # 核心源代码
│   ├── core/                   # 代理服务器核心 (13个模块已恢复)
│   │   ├── bridge_integrated.py
│   │   ├── data_flow_manager.py
│   │   ├── local_proxy.py
│   │   ├── proxy_server_v2.py
│   │   └── ...
│   ├── crypto/                 # 加密模块
│   │   ├── aes_crypto.py       # AES-128-CBC / AES-256-GCM
│   │   ├── aes_crypto_real.py  # 生产级实现
│   │   └── password_hasher.py
│   ├── protocol/               # 协议翻译
│   │   ├── block_mapper.py     # 方块映射 (v3, 2969条)
│   │   ├── entity_mapper.py    # 实体映射 (v1, 1348条) [NEW]
│   │   ├── item_mapper.py      # 物品映射 (v1, 1460条) [NEW]
│   │   ├── coordinate_converter.py
│   │   ├── packet_translator.py
│   │   ├── mc_protocol.py
│   │   └── mnw_login.py
│   ├── multiplayer/            # Phase 7 联机模块
│   │   ├── common/             # 公共组件
│   │   │   ├── config.py       # 配置管理 (支持自定义地址)
│   │   │   ├── protocol_bridge.py  # 协议桥接 (含高层翻译接口)
│   │   │   └── session.py      # 会话管理
│   │   ├── streamer/           # 服务器端
│   │   │   └── relay_server.py # 中继服务器 (TCP+UDP)
│   │   ├── personal/           # 客户端
│   │   │   ├── mnw_host_client.py  # 场景A
│   │   │   ├── mc_host_client.py   # 场景B
│   │   │   └── relay_host_client.py # 场景C
│   │   └── vpn/                # VPN网络捕获
│   │       └── network_capture.py
│   └── utils/                  # 工具模块
├── data/                       # 数据文件
│   ├── block_mapping_v3_complete.json   # 方块映射v3 [NEW]
│   ├── entity_mapping_v1_complete.json  # 实体映射v1 [NEW]
│   ├── item_mapping_v1_complete.json    # 物品映射v1 [NEW]
│   ├── biome_mapping_v1_complete.json   # 生物群系映射v1 [NEW]
│   └── ...
├── tests/                      # 测试文件
├── docs/                       # 文档
├── tools/                      # 工具脚本
│   └── build_complete_mappings.py  # 映射构建器 [NEW]
├── config.yaml                 # 配置文件
├── multiplayer_config.yaml     # 联机配置
└── start_multiplayer.py        # 联机启动器
```

---

## 数据文件统计

| 文件 | 条目数 | 说明 |
|------|--------|------|
| block_mapping_v3_complete.json | 2,969 | 方块双向映射 (含替代规则) |
| entity_mapping_v1_complete.json | 1,348 | 实体双向映射 (含替代规则) |
| item_mapping_v1_complete.json | 1,460 | 物品双向映射 (含替代规则) |
| biome_mapping_v1_complete.json | 90 | 生物群系映射 |
| mnw_gamedata_full.json | 24,507 | MNW完整游戏数据 |

---

## 联机架构

```
场景A: 迷你世界房主
  MNW客户端 → VPN捕获(包复制) → 云服(保持联机) + 中继服务器 → 协议翻译 → MC客户端

场景B: MC房主
  MC服务器 ← 中继服务器 ← 协议翻译 ← VPN拦截(注入虚拟房间) ← MNW客户端

场景C: 中继服务器房主
  中继服务器(独立世界) → MC协议端口(25565) → MC客户端
                       → MNW协议端口(19132) → VPN注入 → MNW客户端
```

---

**项目状态**: 🚧 **Phase 7 开发中 (v0.3.1_26w10a)**
