# BlockConnect-MnMCP 重构计划

**版本**: v2.0.0-restructure  
**日期**: 2026-04-24  
**状态**: 规划阶段

---

## 🎯 重构目标

### 核心目标
1. **清理敏感信息** - 移除所有硬编码密钥、服务器地址、用户凭证
2. **重构架构** - 基于新发现的"本地服务端+内网穿透"模式
3. **模块化设计** - 清晰的模块边界和依赖关系
4. **生产就绪** - 完整的错误处理、日志、测试
5. **开源友好** - 完善的文档、示例、贡献指南

### 非目标
- ❌ 不改变核心协议实现
- ❌ 不重写已验证的加密模块
- ❌ 不删除现有功能

---

## 📋 发现总结

### 关键发现

#### 1. 迷你世界联机机制
基于抓包分析和代码审查，确认迷你世界采用以下架构：

```
[玩家A - 房主]
    │
    ├─ 本地游戏服务端 (127.0.0.1:随机端口)
    │   └─ 处理游戏逻辑、世界数据
    │
    ├─ 内网穿透客户端
    │   ├─ 建立隧道: 本地端口 → 公网地址
    │   └─ 可能使用: frp / 自研穿透
    │
    └─ 注册到中心服务器
        ├─ POST https://openroom.mini1.cn/create_room
        ├─ 提交: 房间信息 + 穿透地址
        └─ 获取: 房间号

[中心服务器] (mini1.cn)
    │
    ├─ 房间注册表
    │   └─ 存储: {房间号 → 穿透地址}
    │
    └─ 房间列表服务
        └─ 返回: 可加入的房间列表

[玩家B - 加入者]
    │
    ├─ 请求房间列表
    │   └─ GET https://openroom.mini1.cn/list_rooms
    │
    ├─ 选择房间
    │   └─ 获取房间的穿透地址
    │
    └─ 直接连接到玩家A
        └─ TCP 连接: 穿透地址:端口
```

**证据**:
- 抓包中发现大量 127.0.0.1 连接
- 服务器只返回房间元数据，不转发游戏数据
- 玩家间直连，无需经过中心服务器

#### 2. 资源文件清单

已发现的关键资源：

**SO 库文件** (共约 200+ 个):
- `liblibGameApp.so` - 游戏核心
- `libilink_network.so` - 网络通信
- `libEncryptor.so` - 加密模块
- `libInnoSecure.so` - 安全防护
- `libqmcheat.so` - 反作弊
- 等等...

**JAR 文件**:
- `Geyser-Spigot.jar` - Minecraft 基岩版桥接
- `floodgate-spigot.jar` - 无验证登录
- JADX 反编译工具 (多个 JAR)

**APK 文件**:
- `minecraft_bedrock_1.20.60.apk`
- `miniworld_cn_1.53.1.apk`
- `miniworld_en_1.7.15.apk`

**分析报告** (50+ 份):
- SO 逆向分析报告
- 协议分析报告
- 安全审计报告
- 网络抓包分析

**工具脚本** (100+ 个):
- Python 解密/分析工具
- Frida Hook 脚本
- IDA Pro 脚本

#### 3. 现有项目结构

```
Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/
├── mnmcp-core/          # 核心库 (Python)
│   ├── crypto/          # 加密: ECDH, HKDF, AES-GCM
│   ├── network/         # 网络: UDP, RakNet, Session
│   ├── protocol/        # 协议: iLink, MNW, Protobuf
│   ├── mapping/         # 映射: 坐标, 方块, 实体
│   └── utils/           # 工具
├── mnmcp-server/        # 服务端 (未完成)
├── mnmcp-personal/      # 个人客户端 (Flutter)
├── mnmcp-streamer/      # 直播工具 (Electron)
└── mnmcp-website/       # 官网 (VitePress)
```

**问题**:
- ❌ 架构基于错误假设 (以为需要中心服务器)
- ❌ 代码中硬编码了大量敏感信息
- ❌ 模块耦合度高
- ❌ 缺少测试

---

## 🏗️ 新架构设计

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                  BlockConnect-MnMCP v2.0                     │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Minecraft 服务器 │
│  (Spigot/Paper)  │
│                  │
│  + Geyser        │ ← 基岩版协议支持
│  + Floodgate     │ ← 无验证登录
│  + MnMCP Plugin  │ ← 迷你世界桥接
└────────┬─────────┘
         │ 25565 (Java)
         │ 19132 (Bedrock)
         │
         ▼
┌──────────────────┐
│  MnMCP 桥接器    │
│                  │
│  ┌────────────┐  │
│  │ 协议转换器  │  │ ← MC ↔ MNW 协议转换
│  ├────────────┤  │
│  │ 本地服务端  │  │ ← 模拟迷你世界服务端
│  ├────────────┤  │
│  │ 穿透客户端  │  │ ← 内网穿透 (frp/ngrok)
│  ├────────────┤  │
│  │ 房间管理器  │  │ ← 房间注册/发现
│  └────────────┘  │
└────────┬─────────┘
         │
         ├─ 127.0.0.1:xxxxx (本地服务端)
         │
         ├─ frp.example.com:7000 (穿透服务器)
         │
         └─ openroom.mini1.cn (房间注册)
              │
              ▼
┌──────────────────┐
│  迷你世界客户端   │
│                  │
│  1. 获取房间列表  │
│  2. 选择房间      │
│  3. 连接穿透地址  │
└──────────────────┘
```

### 核心模块

#### 1. mnmcp-core (核心库)

```python
mnmcp/
├── __init__.py
├── crypto/                    # 加密模块
│   ├── __init__.py
│   ├── ecdh.py               # ECDH 密钥交换
│   ├── hkdf.py               # HKDF 密钥派生
│   ├── aesgcm.py             # AES-GCM 加密
│   └── keys.py               # 密钥管理 (从配置加载)
├── network/                   # 网络模块
│   ├── __init__.py
│   ├── udp.py                # UDP 通信
│   ├── tcp.py                # TCP 通信
│   ├── raknet.py             # RakNet 协议
│   └── session.py            # 会话管理
├── protocol/                  # 协议模块
│   ├── __init__.py
│   ├── ilink.py              # iLink 协议
│   ├── mnw.py                # 迷你世界协议
│   ├── protobuf/             # Protobuf 定义
│   │   ├── __init__.py
│   │   ├── common.proto
│   │   ├── room.proto
│   │   └── game.proto
│   └── minecraft.py          # Minecraft 协议
├── mapping/                   # 映射模块
│   ├── __init__.py
│   ├── coordinates.py        # 坐标转换
│   ├── blocks.py             # 方块映射
│   ├── entities.py           # 实体映射
│   └── items.py              # 物品映射
├── server/                    # 服务端模拟
│   ├── __init__.py
│   ├── local_server.py       # 本地游戏服务端
│   ├── world.py              # 世界管理
│   └── player.py             # 玩家管理
├── tunnel/                    # 内网穿透
│   ├── __init__.py
│   ├── frp.py                # frp 客户端
│   ├── ngrok.py              # ngrok 客户端
│   └── custom.py             # 自定义穿透
├── room/                      # 房间管理
│   ├── __init__.py
│   ├── registry.py           # 房间注册
│   ├── discovery.py          # 房间发现
│   └── api.py                # API 客户端
├── bridge/                    # 桥接器
│   ├── __init__.py
│   ├── core.py               # 核心桥接逻辑
│   ├── mc_adapter.py         # Minecraft 适配器
│   └── mnw_adapter.py        # 迷你世界适配器
└── utils/                     # 工具
    ├── __init__.py
    ├── config.py             # 配置管理
    ├── logging.py            # 日志
    └── errors.py             # 错误处理
```

#### 2. mnmcp-plugin (Minecraft 插件)

```
mnmcp-plugin/
├── src/main/java/
│   └── com/blockconnect/mnmcp/
│       ├── MnMCPPlugin.java          # 插件主类
│       ├── bridge/
│       │   ├── BridgeManager.java    # 桥接管理
│       │   └── PacketHandler.java    # 包处理
│       ├── player/
│       │   └── MnWPlayer.java        # 迷你世界玩家
│       └── config/
│           └── PluginConfig.java     # 配置
├── src/main/resources/
│   ├── plugin.yml
│   └── config.yml
└── pom.xml
```

#### 3. mnmcp-cli (命令行工具)

```python
mnmcp-cli/
├── __init__.py
├── main.py                    # 主入口
├── commands/
│   ├── __init__.py
│   ├── start.py              # 启动桥接器
│   ├── room.py               # 房间管理
│   └── config.py             # 配置管理
└── ui/
    ├── __init__.py
    └── console.py            # 控制台界面
```

---

## 🔐 敏感信息清理

### 清理清单

#### 1. 密钥材料
```python
# ❌ 删除硬编码
RSA_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCS..."
XXTEA_KEY = [0x12345678, 0x9ABCDEF0, ...]

# ✅ 使用配置
from mnmcp.utils.config import load_keys
keys = load_keys("keys.yaml")  # 从本地配置加载
```

#### 2. 服务器地址
```python
# ❌ 删除硬编码
GAME_SERVER = "116.205.254.229:19701"
API_SERVER = "117.89.177.75:8080"

# ✅ 使用配置
from mnmcp.utils.config import get_server_config
server = get_server_config("game_server")
```

#### 3. 用户凭证
```python
# ❌ 删除测试账号
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_pass"

# ✅ 从环境变量读取
import os
username = os.getenv("MNW_USERNAME")
password = os.getenv("MNW_PASSWORD")
```

#### 4. 代码注释
```python
# ❌ 删除敏感注释
# 从 116.205.254.229 抓包得到
# 使用 Annie 的密钥

# ✅ 通用描述
# 从网络分析得到
# 使用配置的密钥
```

### 清理脚本

```python
# workspace/clean_sensitive_info.py
import re
from pathlib import Path

SENSITIVE_PATTERNS = [
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP 地址
    r'-----BEGIN.*?-----END.*?-----',        # PEM 密钥
    r'0x[0-9A-Fa-f]{8,}',                    # 十六进制密钥
    r'username\s*=\s*["\'][^"\']+["\']',     # 用户名
    r'password\s*=\s*["\'][^"\']+["\']',     # 密码
]

def clean_file(file_path: Path):
    """清理文件中的敏感信息"""
    content = file_path.read_text(encoding='utf-8')
    
    for pattern in SENSITIVE_PATTERNS:
        content = re.sub(pattern, '[REDACTED]', content)
    
    file_path.write_text(content, encoding='utf-8')
```

---

## 📦 GitHub 仓库结构

```
BlockConnect-MnMCP/                    # 公开仓库
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                     # CI/CD
│   │   └── release.yml                # 发布
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/
│   ├── README.md                      # 文档首页
│   ├── getting-started.md             # 快速开始
│   ├── architecture.md                # 架构说明
│   ├── protocol.md                    # 协议文档
│   ├── api-reference.md               # API 参考
│   └── contributing.md                # 贡献指南
├── src/
│   └── mnmcp/                         # 核心库
│       └── (如上所述)
├── plugins/
│   └── mnmcp-plugin/                  # Minecraft 插件
├── cli/
│   └── mnmcp-cli/                     # 命令行工具
├── examples/
│   ├── basic_bridge.py                # 基础桥接示例
│   ├── custom_mapping.py              # 自定义映射
│   └── room_management.py             # 房间管理
├── tests/
│   ├── unit/                          # 单元测试
│   ├── integration/                   # 集成测试
│   └── fixtures/                      # 测试数据
├── tools/
│   ├── packet_analyzer.py             # 包分析工具
│   └── config_generator.py            # 配置生成器
├── .gitignore
├── .editorconfig
├── LICENSE                            # MIT License
├── README.md                          # 项目说明
├── CHANGELOG.md                       # 更新日志
├── CONTRIBUTING.md                    # 贡献指南
├── CODE_OF_CONDUCT.md                 # 行为准则
├── requirements.txt                   # Python 依赖
├── setup.py                           # 安装脚本
└── pyproject.toml                     # 项目配置
```

---

## 🚀 实施步骤

### Phase 1: 准备工作 (1-2 天)
- [x] 创建工作区结构
- [x] 编写资源整理脚本
- [ ] 运行资源整理 (实际执行)
- [ ] 创建 GitHub 仓库结构
- [ ] 编写清理脚本

### Phase 2: 代码迁移 (3-5 天)
- [ ] 复制现有代码到新结构
- [ ] 运行敏感信息清理
- [ ] 重构模块导入
- [ ] 更新配置系统
- [ ] 添加类型注解

### Phase 3: 架构重构 (5-7 天)
- [ ] 实现本地服务端模拟
- [ ] 集成内网穿透 (frp)
- [ ] 实现房间注册/发现
- [ ] 重构桥接器核心
- [ ] 更新 Minecraft 插件

### Phase 4: 测试和文档 (3-5 天)
- [ ] 编写单元测试
- [ ] 编写集成测试
- [ ] 完善 API 文档
- [ ] 编写使用教程
- [ ] 录制演示视频

### Phase 5: 发布准备 (2-3 天)
- [ ] 代码审查
- [ ] 性能优化
- [ ] 安全审计
- [ ] 准备发布说明
- [ ] 配置 CI/CD

### Phase 6: 发布 (1 天)
- [ ] 推送到 GitHub
- [ ] 发布到 PyPI
- [ ] 发布插件到 SpigotMC
- [ ] 宣传推广

**总计**: 约 15-23 天

---

## 📊 风险评估

### 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 协议变更 | 高 | 中 | 版本检测,向后兼容 |
| 性能问题 | 中 | 低 | 性能测试,优化 |
| 兼容性问题 | 中 | 中 | 多版本测试 |
| 安全漏洞 | 高 | 低 | 安全审计,代码审查 |

### 法律风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 版权问题 | 高 | 低 | 不包含原始资源 |
| 逆向工程 | 中 | 中 | 仅发布自研代码 |
| 服务条款 | 中 | 中 | 明确免责声明 |

---

## 📝 待办事项

### 立即执行
- [ ] 运行资源整理脚本 (实际执行)
- [ ] 创建 GitHub 仓库
- [ ] 编写敏感信息清理脚本

### 本周完成
- [ ] 迁移核心代码
- [ ] 清理敏感信息
- [ ] 重构配置系统

### 下周完成
- [ ] 实现新架构
- [ ] 编写测试
- [ ] 完善文档

---

## 🎯 成功标准

### 代码质量
- ✅ 无硬编码敏感信息
- ✅ 测试覆盖率 > 80%
- ✅ 类型注解完整
- ✅ 文档完善

### 功能完整性
- ✅ 支持 Minecraft ↔ 迷你世界联机
- ✅ 支持房间创建/加入
- ✅ 支持聊天/移动/方块同步
- ✅ 支持多玩家

### 用户体验
- ✅ 安装简单 (pip install)
- ✅ 配置简单 (YAML 文件)
- ✅ 文档清晰
- ✅ 示例丰富

---

**最后更新**: 2026-04-24  
**负责人**: AI Assistant  
**状态**: 规划完成，待执行
