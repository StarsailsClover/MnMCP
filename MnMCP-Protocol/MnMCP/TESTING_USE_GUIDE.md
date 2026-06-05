# MnMCP 功能测试使用文档

**版本**: v3.0 (改进版)  
**测试类型**: 实际联机测试  
**日期**: 2026-05-31

---

## 🎯 测试目标

验证 MnMCP 在真实网络环境下的功能：
- 迷你世界客户端能加入桥接房间
- Minecraft 客户端能连接服务器
- 双向数据同步正常（玩家、方块、聊天）
- 区块渲染正常

---

## 📋 测试前准备

### 1. 环境确认

```bash
# Python 版本
python --version  # 需要 3.11+

# Node.js 版本
node --version    # 需要 18+

# 确认依赖已安装
pip list | findstr "loguru cryptography msgpack pyyaml aiohttp websockets xxtea ormsgpack"
```

### 2. 网络确认

```bash
# Windows 查看本机IP
ipconfig

# 确认防火墙允许以下端口
# - 19132 (迷你世界)
# - 19133 (Minecraft)
# - 19134 (后端)
```

### 3. 配置文件确认

编辑 `config.yaml`：

```yaml
mini:
  auth:
    uin: 0              # 测试时可填0
    passwd: ""
    api_id: 110
    device_id: ""
    xxtea_key: ""       # 测试时可留空（非创建房间模式）
  server:
    ip: 127.0.0.1
    port: 11155
    host_to_room_server: false  # 关键：false=桥接模式
  send_log_to_chat: false

mc:
  ip: 127.0.0.1
  port: 25565
  username: ""
  version: "1.21.11"
  use_new_chunk_parser: true
  chunk_parse_thread: 4
  log_message: false

server:
  mode: "dual"
  mini_port: 19132
  mc_port: 19133
  backend_port: 19134
  lan_ip: "auto"        # 自动检测，或手动填你的IP如 192.168.1.100
  backend_host: "127.0.0.1"
  guid: 0               # 测试时可填0

world:
  map_path: "./worlds/default"
  texture_path: "./textures"

debug: true              # 测试时建议开启debug
```

### 4. 准备地图

```bash
# 创建地图目录（如果不存在）
mkdir worlds\default

# 可选：放入测试地图文件
# 将迷你世界导出或Minecraft地图放入该目录
```

---

## 🚀 启动步骤

### Terminal 1: 启动后端服务

```bash
cd C:\Users\Sails\Documents\Workspace\NormalWorkplace\Coding\MnMCP-Protocol\MnMCP

python backend.py --map ./worlds/default
```

**预期输出**：
```
2026-05-31 10:00:00.000 | INFO | Starting WorldService on 127.0.0.1:19134
2026-05-31 10:00:00.000 | INFO | WorldService started
```

**确认点**：
- [ ] 后端服务启动成功
- [ ] 监听端口 19134
- [ ] 无报错

---

### Terminal 2: 启动MnMCP代理

```bash
cd C:\Users\Sails\Documents\Workspace\NormalWorkplace\Coding\MnMCP-Protocol\MnMCP

python mnmcp.py --mode dual --guid 0 --lan-ip auto
```

**预期输出**：
```
2026-05-31 10:00:00.000 | INFO | MnMCP - MiniWorld to Minecraft Bridge
2026-05-31 10:00:00.000 | INFO | Mode: dual
2026-05-31 10:00:00.000 | INFO | MiniWorld Port: 19132
2026-05-31 10:00:00.000 | INFO | Minecraft Port: 19133
2026-05-31 10:00:00.000 | INFO | Backend: 127.0.0.1:19134
2026-05-31 10:00:00.000 | INFO | Auto-detected LAN IP: 192.168.1.100
2026-05-31 10:00:00.000 | INFO | DualServer started successfully
2026-05-31 10:00:00.000 | INFO | Server Info:
2026-05-31 10:00:00.000 | INFO |   MiniWorld: 192.168.1.100:19132
2026-05-31 10:00:00.000 | INFO |   Minecraft: 192.168.1.100:19133
2026-05-31 10:00:00.000 | INFO |   Backend:   127.0.0.1:19134
```

**确认点**：
- [ ] 代理启动成功
- [ ] 检测到LAN IP（如192.168.1.100）
- [ ] 三端口都显示启动
- [ ] 无报错

---

## 🎮 客户端连接测试

### 测试1: 迷你世界客户端连接

**操作步骤**：
1. 打开迷你世界客户端
2. 进入 **本地游戏** → **加入房间**
3. 输入服务器地址：
   ```
   192.168.1.100:19132
   ```
   （替换为你的实际IP）
4. 点击加入

**预期结果**：
- [ ] 能发现房间（如果房间已注册到中心服务器）
- [ ] 或直接输入IP:端口能加入
- [ ] 成功进入游戏世界
- [ ] 能看到地形

**验证方法**：
- 查看Terminal 2的输出，应有客户端连接日志
- 游戏内应能正常移动

---

### 测试2: Minecraft客户端连接

**操作步骤**：
1. 打开Minecraft 1.20.6
2. 多人游戏 → 添加服务器
3. 服务器名称：`MnMCP Bridge`
4. 服务器地址：
   ```
   192.168.1.100:19133
   ```
5. 完成 → 加入服务器

**预期结果**：
- [ ] 能ping通服务器
- [ ] 能成功加入
- [ ] 能看到地形
- [ ] 游戏正常运行

---

## 🔄 功能同步测试

### 测试3: 玩家位置同步

**操作**：
1. 迷你世界客户端移动角色（前后左右、跳跃）
2. 观察Minecraft客户端

**预期**：
- [ ] Minecraft中能看到迷你世界玩家
- [ ] 位置实时同步（延迟<100ms）
- [ ] 旋转角度同步
- [ ] 无明显卡顿

---

### 测试4: 方块操作同步

**操作**：
1. 迷你世界放置一个方块
2. 观察Minecraft世界
3. Minecraft破坏一个方块
4. 观察迷你世界

**预期**：
- [ ] 迷你世界放置 → Minecraft显示
- [ ] Minecraft破坏 → 迷你世界消失
- [ ] 方块类型映射正确（草地→草地，石头→石头）

---

### 测试5: 聊天消息桥接

**操作**：
1. 迷你世界发送聊天消息："Hello from MiniWorld"
2. 观察Minecraft聊天框
3. Minecraft发送聊天消息："Hello from Minecraft"
4. 观察迷你世界聊天栏

**预期**：
- [ ] 迷你世界消息在MC显示为 `[MW] 玩家名: Hello from MiniWorld`
- [ ] MC消息在迷你世界显示为 `[MC] 玩家名: Hello from Minecraft`
- [ ] 双向通信正常

---

### 测试6: 区块渲染

**操作**：
1. 进入游戏后等待10秒
2. 观察周围地形

**预期**：
- [ ] 区块正常加载
- [ ] 地形可见（草地、树木、石头等）
- [ ] 无崩溃或白屏

---

## 📊 测试记录模板

```
测试日期: ___________
测试人员: ___________
MnMCP版本: v3.0 (改进版)
MN2MC参考: v 3.26.0.0_dev

环境信息:
- Python版本: ___________
- Node.js版本: ___________
- 本机IP: ___________
- 操作系统: ___________

测试结果:

[ ] 后端服务启动成功
[ ] 代理服务启动成功
[ ] 迷你世界客户端连接成功
[ ] Minecraft客户端连接成功
[ ] 玩家位置同步正常
[ ] 方块操作同步正常
[ ] 聊天消息桥接正常
[ ] 区块渲染正常

问题记录:
1. _________________________________
2. _________________________________
3. _________________________________

与MN2MC对比:
- 功能一致性: _______%
- 性能感受: _______
- 需要改进: _______
```

---

## 🐛 常见问题排查

### 问题1: 后端启动失败

**症状**: `python backend.py` 报错

**检查**：
```bash
# 检查Python版本
python --version

# 检查依赖
pip install loguru

# 检查地图路径
dir worlds\default
```

---

### 问题2: 代理启动失败

**症状**: `python mnmcp.py` 报错

**常见原因**：
- 端口被占用（19132/19133/19134）
- 配置文件错误
- 依赖缺失

**解决**：
```bash
# 检查端口占用
netstat -ano | findstr "19132"
netstat -ano | findstr "19133"
netstat -ano | findstr "19134"

# 更换端口测试
python mnmcp.py --port 19135 --host-port 19136
```

---

### 问题3: 迷你世界无法连接

**症状**: 客户端连接超时

**排查步骤**：
1. 确认代理已启动（查看Terminal 2输出）
2. 确认IP地址正确（`ipconfig`查看）
3. 关闭防火墙测试
4. 尝试ping本机IP

---

### 问题4: Minecraft连接失败

**症状**: "无法连接服务器"

**排查**：
1. 确认Minecraft版本为1.20.6
2. 确认后端服务正在运行
3. 检查端口19133是否开放
4. 查看后端日志

---

### 问题5: 同步延迟高

**症状**: 玩家移动有明显延迟

**优化建议**：
1. 使用有线网络代替WiFi
2. 减少 `chunk_parse_thread` 数量
3. 关闭debug模式
4. 检查CPU/内存占用

---

## 📈 性能指标参考

| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| 连接延迟 | < 500ms | ping测试 |
| 玩家同步延迟 | < 100ms | 移动观察 |
| 方块操作延迟 | < 200ms | 放置/破坏测试 |
| 内存占用 | < 2GB | 任务管理器 |
| CPU占用 | < 50% | 任务管理器 |

---

## ✅ 测试完成确认

所有测试通过后：

1. **截图保存**：
   - 客户端连接成功的截图
   - 游戏内截图（显示地形和玩家）

2. **日志备份**：
   ```bash
   copy logs\*.log logs\test_backup\
   ```

3. **提交报告**：
   - 填写测试记录模板
   - 记录问题和改进建议

---

## 🎯 下一步

测试通过后：
- 如需内网穿透，配置FRP隧道
- 如需创建房间，配置 `host_to_room_server: true`
- 如需优化，调整 `chunk_parse_thread` 等参数

---

**祝测试顺利！**
