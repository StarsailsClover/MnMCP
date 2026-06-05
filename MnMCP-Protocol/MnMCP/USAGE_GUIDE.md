# MnMCP 使用文档

**版本**: v3.0 Phase 5 Complete  
**开发者**: BlockConnect Studio  
**最后更新**: 2026-05-31

---

## 📖 目录

1. [项目简介](#项目简介)
2. [系统要求](#系统要求)
3. [安装步骤](#安装步骤)
4. [配置说明](#配置说明)
5. [启动服务](#启动服务)
6. [功能测试](#功能测试)
7. [常见问题](#常见问题)
8. [高级用法](#高级用法)

---

## 🎯 项目简介

**MnMCP (MiniWorld to Minecraft Protocol Bridge)** 是一个桥接器，允许：
- 迷你世界客户端连接到本地服务
- Minecraft 客户端同时连接到同一世界
- 实现双向协议转换和实时同步

### 核心功能

| 功能 | 说明 |
|------|------|
| 三端口架构 | 19132(迷你世界) / 19133(Minecraft) / 19134(后端) |
| 协议桥接 | 自动转换迷你世界和Minecraft协议 |
| 玩家同步 | 实时同步玩家位置和状态 |
| 方块同步 | 双向方块放置/破坏同步 |
| 聊天桥接 | 双向聊天消息转发 |
| 内网穿透 | 支持FRP隧道，外部可加入 |

---

## 💻 系统要求

### 必需

- **Python**: 3.11 或更高版本
- **Node.js**: 18+ (用于minecraft-protocol)
- **内存**: 至少 4GB RAM
- **网络**: 局域网环境（测试用）

### 推荐配置

- **Python**: 3.11.9
- **Node.js**: 20.x LTS
- **内存**: 8GB+ (大型地图)
- **网络**: 有线以太网（低延迟）

---

## 📦 安装步骤

### 1. 克隆或下载项目

```bash
# 如果使用Git
git clone <repository-url>
cd MnMCP

# 或直接解压项目压缩包
```

### 2. 安装Python依赖

```bash
# Windows (PowerShell)
py -m pip install -r requirements.txt

# 或手动安装
py -m pip install loguru cryptography msgpack pyyaml aiohttp websockets xxtea ormsgpack
```

### 3. 安装Node.js依赖

```bash
# 在项目根目录
npm install minecraft-protocol prismarine-chunk prismarine-block prismarine-registry vec3 msgpackr
```

### 4. 创建配置文件和目录

```bash
# 复制配置模板
copy config.template.yaml config.yaml

# 创建必要目录
mkdir logs
mkdir worlds\default
mkdir textures
```

---

## ⚙️ 配置说明

### 基础配置 (config.yaml)

```yaml
# ==========================================
# 迷你世界配置
# ==========================================
mini:
  auth:
    uin: 0                    # 你的迷你世界账号（仅创建房间时需要）
    passwd: ""                # 账号密码
    api_id: 110
    device_id: ""             # 设备ID（留空自动生成）
    xxtea_key: ""             # XXTEA加密密钥（登录需要）
  
  server:
    ip: 127.0.0.1             # 本地监听地址
    port: 11155               # 本地端口
    host_to_room_server: false # 是否创建迷你房间（true=创建房间，false=桥接模式）
  
  send_log_to_chat: false     # 是否发送日志到游戏聊天

# ==========================================
# Minecraft配置
# ==========================================
mc:
  ip: 127.0.0.1               # MC服务器地址
  port: 25565                 # MC服务器端口
  username: ""                # MC玩家名（留空使用迷你世界名称）
  version: "1.21.11"          # MC版本（当前仅支持1.21.11）
  use_new_chunk_parser: true  # 使用新版区块解析器
  chunk_parse_thread: 4       # 区块解析线程数
  log_message: false            # 是否记录聊天消息

# ==========================================
# 服务器配置 (Phase 5+)
# ==========================================
server:
  mode: "dual"                # dual/mini/mc - 服务器模式
  
  # 三端口架构
  mini_port: 19132            # 迷你世界客户端端口
  mc_port: 19133              # Minecraft客户端端口
  backend_port: 19134         # 后端服务端口
  
  # IP配置
  lan_ip: "auto"              # auto=自动检测，或指定IP如 192.168.1.100
  backend_host: "127.0.0.1"   # 后端服务地址
  
  # 用户配置
  guid: 0                     # 迷你世界UID（用于RakNet连接）

# ==========================================
# 地图配置
# ==========================================
world:
  map_path: "./worlds/default"     # 本地存档路径
  texture_path: "./textures"         # 材质目录
  auto_extract_textures: false       # 自动提取材质

# ==========================================
# 调试配置
# ==========================================
debug: false                  # 启用调试模式（输出更多日志）
```

### 配置说明

| 配置项 | 说明 | 必填 |
|--------|------|------|
| `mini.auth.uin` | 迷你世界账号 | 仅创建房间时需要 |
| `mini.auth.passwd` | 账号密码 | 仅创建房间时需要 |
| `mini.auth.xxtea_key` | 16字节加密密钥 | 登录必须 |
| `server.guid` | 迷你世界用户ID | 推荐填写 |
| `server.lan_ip` | 局域网IP | 留空自动检测 |
| `world.map_path` | 地图存档路径 | 推荐配置 |

---

## 🚀 启动服务

### 方式一：双端口模式（推荐）

**同时启动迷你世界和Minecraft服务**

```bash
# Terminal 1: 启动后端服务
python backend.py --map ./worlds/default

# Terminal 2: 启动MnMCP代理
python mnmcp.py --mode dual --guid 598340631 --lan-ip auto
```

### 方式二：仅迷你世界模式

```bash
python mnmcp.py --mode mini --port 19132 --guid 598340631
```

### 方式三：仅Minecraft模式

```bash
python mnmcp.py --mode mc --host-port 19133
```

### 启动参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--mode` | 运行模式 | dual |
| `--port` | 迷你世界端口 | 19132 |
| `--host-port` | Minecraft端口 | 19133 |
| `--backend-port` | 后端端口 | 19134 |
| `--lan-ip` | 局域网IP | auto |
| `--guid` | 迷你世界UID | 0 |
| `--backend` | 后端地址 | 127.0.0.1:19134 |
| `--config` | 配置文件路径 | config.yaml |
| `--debug` | 调试模式 | false |

---

## 🎮 客户端连接

### 迷你世界客户端

1. 打开迷你世界
2. 进入 **本地游戏** → **加入房间**
3. 输入服务器地址：
   ```
   192.168.1.x:19132
   ```
   （将192.168.1.x替换为你的实际IP）

4. 点击加入

### Minecraft客户端

1. 打开Minecraft 1.20.6
2. 多人游戏 → 添加服务器
3. 服务器地址：
   ```
   192.168.1.x:19133
   ```
4. 加入服务器

---

## ✅ 功能测试清单

### 基础连接测试

| 测试项 | 操作 | 预期结果 |
|--------|------|----------|
| 后端启动 | `python backend.py` | 看到"WorldService started" |
| 代理启动 | `python mnmcp.py --mode dual` | 看到三端口启动信息 |
| 迷你世界连接 | 客户端加入192.168.1.x:19132 | 成功加入MnMCP Bridge房间 |
| Minecraft连接 | 客户端连接192.168.1.x:19133 | 成功进入游戏 |

### 核心功能测试

| 测试项 | 操作 | 预期结果 |
|--------|------|----------|
| 玩家同步 | 迷你世界移动角色 | Minecraft中同步显示 |
| 方块放置 | 迷你世界放置方块 | Minecraft中同步显示 |
| 方块破坏 | 迷你世界破坏方块 | Minecraft中同步消失 |
| 聊天转发 | 迷你世界发送消息 | Minecraft聊天框显示[MW]前缀 |
| 区块渲染 | 进入游戏后等待 | 地形正常加载 |

### 高级功能测试

| 测试项 | 操作 | 预期结果 |
|--------|------|----------|
| 内网穿透 | 配置FRP后启动 | 外部可发现房间 |
| 房间注册 | 自动注册到中心服务器 | 房间列表可见 |
| 模式切换 | 聊天输入`/mnmcp minecraft` | 切换到MC模式 |

---

## 📊 验证测试

### 运行验证脚本

```bash
# 验证MnMCP与MN2MC路径一致性
python verify_mnmcp_path.py

# 运行完整功能测试
python tests/test_phase4_complete.py
```

### 预期输出

```
============================================================
MnMCP Path Verification (vs MN2MC)
============================================================
Checking core imports...
  ✓ config module
  ✓ mini modules (auth, room, server)
  ✓ mc modules (client, packet)
  ✓ server module
  ✓ bridge modules
  ✓ room modules
  ✓ tunnel modules
  ✓ mapping modules

✅ ALL CHECKS PASSED - MnMCP follows MN2MC core path
============================================================
```

---

## 🐛 常见问题

### Q1: 后端启动失败

**症状**: `python backend.py` 报错

**解决方案**:
1. 检查Python版本：`python --version` (需要3.11+)
2. 检查依赖：`pip install loguru`
3. 检查地图路径是否存在

### Q2: 迷你世界无法连接

**症状**: 客户端连接超时

**解决方案**:
1. 检查端口19132是否开放：
   ```bash
   # Windows防火墙
   控制面板 → Windows Defender防火墙 → 高级设置 → 入站规则 → 新建规则
   ```
2. 检查IP是否正确：`ipconfig` 查看本机IP
3. 确认代理已启动：查看终端输出

### Q3: Minecraft连接失败

**症状**: "无法连接服务器"

**解决方案**:
1. 确认Minecraft版本为1.20.6
2. 检查端口19133是否开放
3. 确认后端服务正在运行
4. 查看日志：`logs/` 目录

### Q4: 区块不显示

**症状**: Minecraft世界空白

**解决方案**:
1. 检查地图路径是否正确
2. 确认地图文件存在
3. 尝试减少 `chunk_parse_thread` 数量
4. 启用调试模式：`--debug`

### Q5: 玩家不显示

**症状**: 看不到其他玩家

**解决方案**:
1. 确认双方都已连接
2. 检查玩家同步是否启用
3. 查看日志中的同步信息

---

## 🔧 高级用法

### 1. 自定义地图

```bash
# 将迷你世界存档复制到 worlds/default/
# 或使用Minecraft地图转换工具

# 启动时指定地图
python backend.py --map ./my_custom_world
```

### 2. FRP内网穿透

```bash
# 1. 配置FRP服务器
# 2. 修改config.yaml中的tunnel配置

# 3. 启动隧道
python -c "
from mnmcp.tunnel import TunnelManager, TunnelConfig
import asyncio

async def main():
    config = TunnelConfig(
        enabled=True,
        frp_server="your-frp-server.com",
        frp_port=7000,
        frp_token="your-token"
    )
    manager = TunnelManager()
    await manager.initialize(config)
    await manager.create_mini_tunnel()
    await manager.create_mc_tunnel()
    
    # 保持运行
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
"
```

### 3. 调试模式

```bash
# 启用详细日志
python mnmcp.py --mode dual --debug

# 查看日志
tail -f logs/*.log
```

### 4. 房间注册（创建房间模式）

```yaml
# 修改 config.yaml
mini:
  auth:
    uin: 123456789          # 你的迷你世界账号
    passwd: "your_password"
    xxtea_key: "your_key"
  server:
    host_to_room_server: true  # 创建房间模式
```

---

## 📁 项目结构

```
MnMCP/
├── mnmcp.py                 # 主入口（推荐）
├── backend.py              # 后端服务入口
├── main.py                 # 原始入口
├── config.template.yaml    # 配置模板
├── config.yaml             # 你的配置（不提交Git）
│
├── mnmcp/
│   ├── server/             # 服务器层
│   │   ├── dual_server.py  # 三端口架构
│   │   └── mc_server.py    # MC服务端
│   ├── network/            # 网络层
│   │   └── raknet/         # RakNet协议
│   ├── bridge/             # 桥接层
│   │   ├── protocol_bridge.py
│   │   ├── player_sync.py
│   │   ├── block_bridge.py
│   │   └── chat_bridge.py
│   ├── room/               # 房间管理
│   │   ├── registry.py
│   │   └── discovery_client.py
│   ├── tunnel/             # 内网穿透
│   │   ├── frp_client.py
│   │   └── punch_client.py
│   └── mapping/            # 数据映射
│       ├── blocks.py       # 方块映射
│       └── mobs.py         # 实体映射
│
├── tests/                  # 测试脚本
├── logs/                   # 日志目录
├── worlds/                 # 地图目录
└── textures/               # 材质目录
```

---

## 📞 技术支持

### 日志位置

```
logs/
├── 2026-05-31_10-00-00.log
├── 2026-05-31_10-01-00.log
└── ...
```

### 调试步骤

1. **检查日志**
   ```bash
   # 查看最新日志
   Get-Content logs\*.log -Wait
   ```

2. **验证配置**
   ```bash
   python verify_mnmcp_path.py
   ```

3. **运行测试**
   ```bash
   python tests/test_phase4_complete.py
   ```

---

## 🎯 快速启动检查清单

- [ ] Python 3.11+ 已安装
- [ ] Node.js 18+ 已安装
- [ ] 依赖已安装 (`pip install -r requirements.txt`)
- [ ] `config.yaml` 已创建并配置
- [ ] `logs/` 目录已创建
- [ ] `worlds/default/` 目录已创建
- [ ] 防火墙已开放端口 19132, 19133, 19134

---

## 📝 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v3.0 Phase 5 | 2026-05-31 | 内网穿透、房间管理、测试指南 |
| v3.0 Phase 4 | 2026-05-31 | 协议桥接核心 |
| v3.0 Phase 6 | 2026-05-30 | 参考版本移植 |
| v3.0 Phase 1-3 | 2026-05-23 | 基础架构 |

---

**BlockConnect Studio**  
**MnMCP v3.0 - MiniWorld to Minecraft Bridge**
