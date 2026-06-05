# MnMCP 局域网测试指南

**版本**: 3.26.0.0-3100  
**日期**: 2026-06-03  
**状态**: ✅ 准备就绪

---

## 🚀 快速开始

### 环境要求

- **操作系统**: Windows 10/11 或 Linux
- **Python**: 3.11+
- **Minecraft**: Java Edition 1.19.2
- **网络**: 局域网 (同一 WiFi 或网段)

### 安装依赖

```bash
cd mnmcp-v2
pip install -r requirements.txt
```

---

## 🧪 测试流程

### 步骤 1: 启动服务器

在**主机**上运行:

```bash
python lan_test_server.py
```

**预期输出**:
```
============================================================
 MnMCP v2 - 局域网测试服务器
============================================================

[1] 初始化桥接器...
[2] 初始化服务器...
[3] 初始化发现服务...

[4] 启动服务...
  桥接器: ✓ 已启动
  服务器: ✓ 已启动
  发现服务: ✓ 已启动

============================================================
 服务器运行中...
============================================================

连接信息:
  地址: 127.0.0.1:25565
  端口: 25565

Minecraft 连接方式:
  1. 启动 Minecraft Java Edition 1.19.2
  2. 多人游戏 -> 直接连接
  3. 输入: 127.0.0.1:25565
```

**保持此窗口运行！**

---

### 步骤 2: 测试客户端连接

在**另一台电脑**上运行:

```bash
python lan_test_client.py
```

**预期输出**:
```
============================================================
 MnMCP v2 - 局域网测试客户端
============================================================

[1] 扫描局域网服务器...
    扫描中 (约 10 秒)...

    ✓ 发现 1 个服务器:

    [1] [MnMCP] MiniWorld <-> Minecraft Bridge
        地址: 192.168.1.100:25565
        版本: 1.19.2
        玩家: 0/20
        延迟: 2.5ms

[2] 连接到 192.168.1.100:25565...
    ✓ 已连接!

    连接测试完成
```

---

### 步骤 3: 使用 Minecraft 连接

#### 方法 A: 直接连接 (推荐)

1. 启动 Minecraft Java Edition 1.19.2
2. 点击 **多人游戏**
3. 点击 **直接连接**
4. 输入服务器地址:
   ```
   192.168.1.100:25565  # 替换为实际服务器IP
   ```
5. 点击 **加入服务器**

#### 方法 B: 局域网扫描

1. 启动 Minecraft Java Edition 1.19.2
2. 点击 **多人游戏**
3. 点击 **局域网游戏** (如果服务器开启发现服务)
4. 选择服务器并加入

---

## 📋 测试清单

### 基础连接测试

- [ ] 服务器启动成功
- [ ] 客户端扫描发现服务器
- [ ] 客户端可以 ping 通服务器
- [ ] Minecraft 可以连接服务器
- [ ] 服务器状态显示正确

### 游戏功能测试

- [ ] 玩家可以登录
- [ ] 玩家可以在世界中移动
- [ ] 方块放置/破坏同步
- [ ] 聊天消息转发
- [ ] 玩家断开连接正常

### 网络性能测试

- [ ] 延迟 < 50ms (局域网内)
- [ ] 数据包无丢失
- [ ] 多客户端同时连接
- [ ] 长时间运行稳定

---

## 🔧 故障排除

### 问题 1: 连接被拒绝

**症状**: `Connection refused`

**解决**:
1. 确认服务器已启动
2. 检查防火墙设置
3. 确认端口未被占用

```bash
# 检查端口占用 (Windows)
netstat -ano | findstr 25565

# 检查端口占用 (Linux)
sudo lsof -i :25565
```

### 问题 2: 发现不了服务器

**症状**: `未发现服务器`

**解决**:
1. 确认服务器和客户端在同一网络
2. 尝试直接 IP 连接
3. 检查 Windows 防火墙

```bash
# 手动测试连接
python lan_test_client.py --ping
```

### 问题 3: Minecraft 连接失败

**症状**: `无法连接至服务器`

**解决**:
1. 确认 Minecraft 版本 (1.19.2)
2. 检查服务器 IP 地址
3. 确认服务器状态响应

```bash
# 测试服务器状态
python -c "
import asyncio
from src.network import BridgeClient
from src.config import Config

async def test():
    client = BridgeClient(Config())
    info = await client.ping('127.0.0.1', 25565)
    if info:
        print(f'服务器响应: {info.description}')
    else:
        print('服务器无响应')

asyncio.run(test())
"
```

### 问题 4: 延迟过高

**症状**: 延迟 > 100ms

**解决**:
1. 使用有线连接替代 WiFi
2. 关闭其他网络应用
3. 检查网络设备负载

---

## 📊 网络配置

### 端口配置

| 服务 | 端口 | 协议 | 说明 |
|------|------|------|------|
| Minecraft | 25565 | TCP | 游戏连接 |
| 发现服务 | 25566 | UDP | 局域网发现 |

### 防火墙规则

**Windows 防火墙**:
```powershell
# 添加入站规则
New-NetFirewallRule -DisplayName "MnMCP-Minecraft" -Direction Inbound -Protocol TCP -LocalPort 25565 -Action Allow
New-NetFirewallRule -DisplayName "MnMCP-Discovery" -Direction Inbound -Protocol UDP -LocalPort 25566 -Action Allow
```

**Linux (iptables)**:
```bash
# 允许 Minecraft 连接
iptables -A INPUT -p tcp --dport 25565 -j ACCEPT
iptables -A INPUT -p udp --dport 25566 -j ACCEPT
```

---

## 🎮 测试场景

### 场景 1: 单机测试

```
[同一台电脑]
┌─────────────────┐
│   服务器端       │
│  lan_test_      │
│   server.py     │
│     :25565      │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Minecraft │
    │  客户端   │
    └─────────┘
```

**步骤**:
1. 启动服务器
2. 启动 Minecraft
3. 连接 `127.0.0.1:25565`

---

### 场景 2: 局域网双机测试

```
[网络拓扑]
┌──────────────┐      WiFi/有线      ┌──────────────┐
│   服务器主机  │ ←─────────────────→ │   客户端主机  │
│  (Windows)   │                      │  (任意系统)   │
│ 192.168.1.100│                      │ 192.168.1.101│
│   :25565     │                      │              │
└──────┬───────┘                      └──────┬───────┘
       │                                    │
  ┌────┴────┐                          ┌───┴────┐
  │ Minecraft│                          │ Minecraft│
  │  (可选)  │                          │  (主要)  │
  └─────────┘                          └─────────┘
```

**步骤**:
1. 主机 A 启动服务器
2. 主机 B 运行客户端测试
3. 主机 B 使用 Minecraft 连接

---

### 场景 3: 多客户端测试

```
            [路由器]
              │
      ┌───────┼───────┐
      │       │       │
  ┌───┴───┐┌──┴──┐┌───┴───┐
  │服务器 ││客户端1││客户端2│
  │:25565 ││      ││       │
  └───────┘└──────┘└───────┘
```

**步骤**:
1. 启动服务器
2. 多个客户端连接
3. 观察服务器状态输出

---

## 📈 性能基准

### 预期性能指标

| 指标 | 期望值 | 说明 |
|------|--------|------|
| 启动时间 | < 3s | 服务器启动完成 |
| 连接延迟 | < 5ms | 局域网内 |
| 登录时间 | < 2s | 玩家登录过程 |
| 数据包处理 | < 1ms | 单个数据包 |
| 内存占用 | < 100MB | 单服务器实例 |
| CPU 占用 | < 5% | 空闲状态 |

### 压力测试

```bash
# 模拟 10 个并发连接
python -c "
import asyncio
from src.network import BridgeClient
from src.config import Config

async def stress_test():
    config = Config()
    clients = []
    
    for i in range(10):
        client = BridgeClient(config)
        success = await client.connect('127.0.0.1', 25565)
        if success:
            clients.append(client)
            print(f'连接 {i+1}: 成功')
        else:
            print(f'连接 {i+1}: 失败')
    
    print(f'\\n总连接数: {len(clients)}/10')
    
    # 断开
    for client in clients:
        await client.disconnect()

asyncio.run(stress_test())
"
```

---

## 🐛 调试工具

### 1. 网络抓包

使用 Wireshark 监控端口 25565:

```
过滤器: tcp.port == 25565
```

### 2. 日志级别

```python
# 在代码中启用调试日志
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### 3. 性能分析

```bash
# Python 性能分析
python -m cProfile -o profile.stats lan_test_server.py

# 查看结果
python -m pstats profile.stats
```

---

## ✅ 测试完成标准

### 基础要求

- [ ] 服务器启动无错误
- [ ] 客户端可以发现服务器
- [ ] Minecraft 可以成功连接
- [ ] 玩家可以登录和移动

### 性能要求

- [ ] 延迟 < 50ms
- [ ] 内存占用 < 200MB
- [ ] CPU 占用 < 10%
- [ ] 连续运行 1 小时无崩溃

### 兼容性要求

- [ ] Windows 10/11 正常运行
- [ ] Linux 正常运行
- [ ] Minecraft 1.19.2 兼容
- [ ] 支持至少 5 个并发连接

---

## 📞 问题反馈

### 收集信息

遇到问题时，请收集:

1. **错误信息**: 完整的错误堆栈
2. **环境信息**: Python 版本、操作系统
3. **网络信息**: IP 地址、防火墙状态
4. **日志文件**: 启用 DEBUG 级别的日志

### 测试报告模板

```markdown
## 测试报告

- 日期: 2026-XX-XX
- 版本: 3.26.0.0-3100
- 环境: Windows 11 / Python 3.11

### 测试项目
- [ ] 服务器启动
- [ ] 客户端连接
- [ ] Minecraft 连接

### 结果
- 状态: 成功 / 失败
- 问题描述: (如果有)
- 日志: (关键日志片段)
```

---

**祝测试顺利！** 🎉
