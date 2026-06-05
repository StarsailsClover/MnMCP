# MnMCP v2.1 - 实用测试指南

**基于 Geyser 的实际可行方案**

---

## 🎯 架构说明

```
[迷你世界客户端] (1.55.0)
    │ 迷你世界协议
    ▼
[MnMCP 适配器] (端口 19133) ← 你运行这个
    │ 转换为 Bedrock 协议
    ▼
[Geyser 插件] (端口 19132) ← Minecraft 服务器插件
    │ 转换为 Java 协议
    ▼
[Minecraft 服务器] (端口 25565) ← Fabric 1.20.6
    │
    ├─ Minecraft Java 玩家
    └─ 迷你世界玩家 (通过适配器)
```

**关键点**:
- ✅ 不需要迷你世界官方API
- ✅ 不需要房间注册
- ✅ 直接输入IP连接
- ✅ 利用 Geyser 现有功能

---

## 📋 准备工作

### 1. 下载 Geyser

从 MnMCPResources 中复制或下载:

```
MnMCPResources\reverse-engineering\plugins\Geyser-Spigot.jar
```

或从官网下载:
```
https://geysermc.org/download
```

### 2. 安装 Geyser

```bash
# 复制到 Minecraft 服务器的 plugins 目录
cp Geyser-Spigot.jar <MC服务器>/plugins/
```

### 3. 配置 Geyser

编辑 `plugins/Geyser-Spigot/config.yml`:

```yaml
bedrock:
  # 监听地址
  address: 0.0.0.0
  # Bedrock 端口
  port: 19132
  
remote:
  # Minecraft 服务器地址
  address: 127.0.0.1
  # Minecraft 服务器端口
  port: 25565
```

---

## 🚀 启动步骤

### Step 1: 启动 Minecraft 服务器

```bash
cd <你的MC服务器目录>
java -Xmx2G -Xms2G -jar fabric-server-launch.jar nogui
```

**检查点**:
```
[Geyser-Spigot] Listening on 0.0.0.0:19132
[Server] Done! For help, type "help"
```

### Step 2: 启动 MnMCP 适配器

```bash
cd D:\Coding\BlockConnect\BlockConnect-MnMCP\workspace
python mnmcp_adapter.py
```

**检查点**:
```
============================================================
MnMCP v2.1 - 协议适配器
============================================================
✓ Geyser 连接正常: 127.0.0.1:19132
✓ MnMCP 适配器已启动
  监听端口: 19133
  Geyser 地址: 127.0.0.1:19132
============================================================
迷你世界玩家连接方式:
  1. 打开迷你世界 1.55.0
  2. 点击'联机' → '加入房间'
  3. 输入地址: <服务器IP>:19133
============================================================
```

### Step 3: 迷你世界连接

#### 本机测试

1. 打开迷你世界 1.55.0
2. 点击"联机"
3. 选择"加入房间"
4. 输入地址: `127.0.0.1:19133`
5. 点击"连接"

#### 局域网测试

1. 查看服务器IP: `ipconfig` (Windows) 或 `ifconfig` (Linux)
2. 假设服务器IP是 `192.168.1.100`
3. 在迷你世界中输入: `192.168.1.100:19133`

#### 公网测试 (需要端口转发)

1. 配置路由器端口转发: 19133 → 服务器IP:19133
2. 查看公网IP: `https://ip.sb`
3. 在迷你世界中输入: `<公网IP>:19133`

### Step 4: Minecraft 连接

1. 打开 Minecraft 1.20.6
2. 多人游戏 → 添加服务器
3. 服务器地址: `127.0.0.1:25565`
4. 加入服务器

---

## 📊 预期结果

### 成功连接

**MnMCP 适配器日志**:
```
============================================================
[连接 #1] 迷你世界玩家: 192.168.1.101:54321
[连接 #1] 正在连接到 Geyser...
[连接 #1] ✓ 已连接到 Geyser
[连接 #1] 开始数据转发...
[MNW→BE] 192.168.1.101 已转发 100 个数据包
[BE→MNW] 192.168.1.101 已转发 100 个数据包
```

**Minecraft 服务器日志**:
```
[Server] <玩家名> joined the game
```

### 当前限制

由于协议转换尚未完全实现，当前版本:

- ✅ 可以建立连接
- ✅ 可以转发数据包
- ⚠️ 协议格式不匹配，可能无法正常游戏
- ⚠️ 需要实现完整的协议转换

---

## 🐛 故障排查

### 问题 1: Geyser 未启动

**症状**:
```
✗ Geyser 连接失败: Connection refused
```

**解决**:
1. 确认 Minecraft 服务器已启动
2. 确认 Geyser 插件已加载
3. 检查 Geyser 配置中的端口 (默认 19132)
4. 查看服务器日志中的 Geyser 启动信息

### 问题 2: 端口被占用

**症状**:
```
OSError: [WinError 10048] 通常每个套接字地址只允许使用一次
```

**解决**:
```bash
# 查看端口占用
netstat -ano | findstr "19133"

# 结束占用进程
taskkill /PID <进程ID> /F
```

### 问题 3: 迷你世界无法连接

**症状**:
- 迷你世界显示"连接失败"
- 适配器没有"新连接"日志

**解决**:
1. 检查防火墙设置
2. 确认IP地址正确
3. 确认端口号正确 (19133)
4. 尝试使用 telnet 测试: `telnet <IP> 19133`

### 问题 4: 连接后立即断开

**症状**:
```
[连接 #1] 迷你世界玩家: ...
[断开] ... (剩余连接: 0)
```

**原因**:
- 协议格式不匹配
- 握手失败

**下一步**:
- 需要实现完整的协议转换
- 需要分析迷你世界的握手流程

---

## 📝 下一步开发

### 优先级 P0: 协议转换

1. **分析迷你世界握手流程**
   - 捕获握手数据包
   - 分析数据包格式
   - 实现握手响应

2. **实现基础数据包转换**
   - 玩家登录
   - 玩家移动
   - 聊天消息

3. **测试连接稳定性**
   - 保持连接
   - 心跳包
   - 错误处理

### 优先级 P1: 游戏功能

1. **方块操作**
   - 方块放置
   - 方块破坏
   - 方块映射

2. **实体同步**
   - 实体生成
   - 实体移动
   - 实体映射

3. **物品交互**
   - 物品拾取
   - 物品使用
   - 物品映射

---

## 🔧 开发工具

### 抓包分析

```bash
# 使用 Wireshark 捕获迷你世界数据包
# 过滤器: tcp.port == 19133

# 或使用 tcpdump
tcpdump -i any -w mnw_packets.pcap port 19133
```

### 调试模式

```bash
# 启用详细日志
python mnmcp_adapter.py --debug

# 指定 Geyser 地址
python mnmcp_adapter.py --geyser-host 192.168.1.100 --geyser-port 19132

# 指定监听端口
python mnmcp_adapter.py --listen-port 19134
```

---

## ✅ 测试清单

### 环境测试

- [ ] Minecraft 服务器启动成功
- [ ] Geyser 插件加载成功
- [ ] Geyser 监听 19132 端口
- [ ] MnMCP 适配器启动成功
- [ ] MnMCP 监听 19133 端口
- [ ] MnMCP 可以连接到 Geyser

### 连接测试

- [ ] 迷你世界可以连接到 MnMCP
- [ ] MnMCP 可以连接到 Geyser
- [ ] 数据包可以双向转发
- [ ] 连接可以保持稳定

### 功能测试 (待协议实现)

- [ ] 玩家可以登录
- [ ] 玩家可以移动
- [ ] 玩家可以聊天
- [ ] 玩家可以放置方块
- [ ] 玩家可以破坏方块

---

## 📞 需要帮助？

### 查看日志

```bash
# 实时查看适配器日志
python mnmcp_adapter.py

# 查看 Minecraft 服务器日志
tail -f logs/latest.log

# 查看 Geyser 日志
tail -f plugins/Geyser-Spigot/logs/latest.log
```

### 报告问题

请提供:
1. 完整的错误日志
2. Minecraft 服务器版本
3. Geyser 版本
4. 迷你世界版本
5. 操作系统

---

**当前状态**: 基础框架完成，等待协议转换实现

**下一步**: 分析迷你世界握手流程，实现协议转换

---

**文档版本**: v2.1  
**最后更新**: 2026-04-24 14:00  
**负责人**: AI Assistant
