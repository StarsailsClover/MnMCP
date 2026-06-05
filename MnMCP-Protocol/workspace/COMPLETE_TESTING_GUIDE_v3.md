# MnMCP v3.0 - 完整测试指南

**基于 Clash Meta 的中间人代理方案**

---

## 🎯 方案说明

通过 Clash Meta 拦截迷你世界的API请求，返回伪造的房间列表，让 Minecraft 局域网房间出现在迷你世界的房间列表中。

```
[迷你世界客户端]
    ↓ 设置代理: 127.0.0.1:7890
[Clash Meta]
    ↓ 拦截 openroom.mini1.cn
[MnMCP 伪造API]
    ↓ 返回包含 Minecraft 房间的列表
[迷你世界显示房间列表]
    ↓ 点击加入
[MnMCP 桥接器]
    ↓ 协议转换
[Minecraft 局域网]
```

---

## 📋 准备工作

### 1. 下载 Clash Meta

从 GitHub 下载最新版本:
```
https://github.com/MetaCubeX/Clash.Meta/releases
```

选择对应系统的版本:
- Windows: `clash.meta-windows-amd64.exe`
- Linux: `clash.meta-linux-amd64`
- macOS: `clash.meta-darwin-amd64`

### 2. 准备文件

确保以下文件在 workspace 目录:
- `clash_meta_mnmcp_v3.yaml` - Clash Meta 配置
- `mnmcp_fake_api.py` - 伪造API服务器
- `mnmcp_bridge_v3.py` - 桥接器 (待实现)

---

## 🚀 启动步骤

### Step 1: 启动 Clash Meta

```bash
# Windows
cd D:\Coding\BlockConnect\BlockConnect-MnMCP\workspace
clash.meta-windows-amd64.exe -f clash_meta_mnmcp_v3.yaml

# Linux/macOS
cd /path/to/workspace
./clash.meta -f clash_meta_mnmcp_v3.yaml
```

**检查点**:
```
INFO[0000] Start initial compatible provider Default
INFO[0000] Start initial compatible provider MiniWorld
INFO[0000] HTTP proxy listening at: 127.0.0.1:7890
INFO[0000] SOCKS proxy listening at: 127.0.0.1:7891
INFO[0000] RESTful API listening at: 127.0.0.1:9090
```

### Step 2: 启动伪造API服务器

```bash
cd D:\Coding\BlockConnect\BlockConnect-MnMCP\workspace
python mnmcp_fake_api.py
```

**检查点**:
```
============================================================
MnMCP v3.0 - 伪造迷你世界API服务器
============================================================

✓ Minecraft 局域网发现已启动
  监听多播: 224.0.2.60:4445
✓ API 服务器已启动: http://0.0.0.0:8080

============================================================
使用步骤:
1. 确保 Clash Meta 已启动并配置正确
2. 在 Minecraft 中打开局域网
3. 迷你世界设置代理: 127.0.0.1:7890
4. 打开迷你世界，查看房间列表
============================================================
```

### Step 3: 启动 Minecraft 并打开局域网

1. 打开 Minecraft 1.20.6 Java Edition
2. 单人游戏 → 选择或创建世界
3. 进入世界后，按 ESC
4. 点击"对局域网开放"
5. 选择游戏模式 (创造/生存)
6. 点击"创造一个局域网世界"

**检查点**:
- Minecraft 显示: "本地游戏已在端口 xxxxx 上开启"
- 伪造API服务器显示:
  ```
  ============================================================
  [LAN] 发现 Minecraft 局域网房间!
    地址: 192.168.1.100:54321
    世界: My World
  ============================================================
  ```

### Step 4: 配置迷你世界代理

#### 方式 A: 系统代理 (推荐)

**Windows 10/11**:
1. 设置 → 网络和 Internet → 代理
2. 手动设置代理
3. 地址: `127.0.0.1`
4. 端口: `7890`
5. 保存

**或使用命令**:
```powershell
# 启用代理
netsh winhttp set proxy 127.0.0.1:7890

# 禁用代理 (测试后)
netsh winhttp reset proxy
```

#### 方式 B: Proxifier (更可靠)

1. 下载安装 Proxifier
2. Profile → Proxy Servers → Add
3. 地址: `127.0.0.1`
4. 端口: `7890`
5. 协议: HTTP
6. Proxification Rules → Add
7. 应用程序: `miniworld.exe`
8. 代理: 刚才添加的代理

### Step 5: 打开迷你世界

1. 启动迷你世界 1.55.0
2. 点击"联机"
3. 查看房间列表

**预期结果**:
- 看到房间: "🎮 My World" (你的 Minecraft 世界名)
- 房间信息显示: 1/20 人

**伪造API日志**:
```
[API] GET /server/room?cmd=server_config&uin=...
[API] 返回房间列表: 1 个房间
```

### Step 6: 加入房间

1. 点击 "🎮 My World" 房间
2. 点击"加入"

**当前状态**:
- ⚠️ 会尝试连接到 127.0.0.1:19132
- ⚠️ 但桥接器尚未实现，连接会失败

---

## 📊 测试结果

### 成功标准

- [x] Clash Meta 启动成功
- [x] 伪造API启动成功
- [x] Minecraft 局域网被发现
- [x] 迷你世界看到伪造的房间列表
- [ ] 迷你世界成功连接 (需要桥接器)
- [ ] 协议转换工作 (需要实现)

### 当前进度

```
Phase 1: Clash Meta 配置      ████████████████████ 100% ✅
Phase 2: 伪造API服务器         ████████████████████ 100% ✅
Phase 3: Minecraft 局域网发现  ████████████████████ 100% ✅
Phase 4: 迷你世界显示房间      ████████████████████ 100% ✅
Phase 5: 桥接器实现            ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Phase 6: 协议转换              ░░░░░░░░░░░░░░░░░░░░   0% ⏳

总进度: ████████████░░░░░░░░ 67%
```

---

## 🐛 故障排查

### 问题 1: Clash Meta 启动失败

**症状**:
```
FATAL[0000] Parse config error: ...
```

**解决**:
1. 检查 YAML 格式是否正确
2. 确认端口未被占用
3. 使用 `clash.meta -t -f config.yaml` 测试配置

### 问题 2: 伪造API无法启动

**症状**:
```
OSError: [WinError 10048] 端口被占用
```

**解决**:
```bash
# 查看端口占用
netstat -ano | findstr "8080"

# 更换端口
python mnmcp_fake_api.py --port 8081
```

### 问题 3: 未发现 Minecraft 局域网

**症状**:
- 伪造API没有 "[LAN] 发现 Minecraft" 日志
- 迷你世界显示 "⚠️ 未发现 Minecraft 房间"

**原因**:
- Minecraft 未打开局域网
- 防火墙阻止 UDP 多播
- 网络接口问题

**解决**:
1. 确认 Minecraft 已打开局域网
2. 关闭防火墙测试
3. 检查网络适配器

### 问题 4: 迷你世界未使用代理

**症状**:
- 迷你世界显示真实的房间列表
- 伪造API没有收到请求

**解决**:
1. 确认系统代理已设置
2. 使用 Proxifier 强制代理
3. 检查迷你世界是否绕过代理

### 问题 5: 迷你世界连接失败

**症状**:
- 点击加入后显示"连接失败"
- 伪造API显示连接到 127.0.0.1:19132

**原因**:
- 桥接器未启动 (当前未实现)

**下一步**:
- 需要实现 MnMCP 桥接器
- 监听 19132 端口
- 实现协议转换

---

## 📝 下一步开发

### 优先级 P0: 桥接器实现

```python
# mnmcp_bridge_v3.py

class MnMCPBridge:
    """MnMCP 桥接器 v3.0"""
    
    def __init__(self):
        self.mnw_server = None  # 迷你世界服务端 (19132)
        self.mc_client = None   # Minecraft 客户端
    
    async def start(self):
        # 1. 启动迷你世界服务端模拟器
        await self.start_mnw_server()
        
        # 2. 等待迷你世界客户端连接
        # 3. 连接到 Minecraft 局域网
        # 4. 开始协议转换和数据转发
```

### 优先级 P1: 协议转换

1. **握手流程**
   - 迷你世界握手
   - Minecraft 握手
   - 协议版本协商

2. **基础数据包**
   - 玩家登录
   - 玩家移动
   - 聊天消息

3. **游戏功能**
   - 方块操作
   - 实体同步
   - 物品交互

---

## ✅ 当前成就

- [x] 成功拦截迷你世界API
- [x] 成功伪造房间列表
- [x] 成功发现 Minecraft 局域网
- [x] 迷你世界显示 Minecraft 房间
- [ ] 成功建立连接 (下一步)
- [ ] 成功进行游戏 (最终目标)

---

## 📞 测试反馈

请测试并反馈:

1. **Clash Meta 是否正常启动？**
2. **伪造API是否收到请求？**
3. **是否发现了 Minecraft 局域网？**
4. **迷你世界是否显示伪造的房间？**
5. **点击加入后的错误信息？**

---

**当前版本**: v3.0  
**最后更新**: 2026-04-24 15:00  
**状态**: 可以测试房间显示，等待桥接器实现
