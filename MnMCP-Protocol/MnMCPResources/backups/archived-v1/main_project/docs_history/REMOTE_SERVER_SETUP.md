# MnMCP 远程服务器连接指南

**版本**: v0.3.1  
**日期**: 2026-03-04

---

## 🔴 常见问题: "远程服务器拒绝访问"

### 问题原因

1. **默认配置使用本地地址** (`127.0.0.1`)
2. **防火墙阻止连接**
3. **中继服务器未启动**
4. **端口未开放**

---

## ✅ 解决方案

### 方案1: 本地测试 (单机)

所有组件运行在同一台机器上：

```yaml
# multiplayer_config.yaml
relay_server:
  host: "127.0.0.1"  # 本地地址
  mc_port: 25565
  mnw_port: 19132
```

**启动顺序**:
1. 启动 Relay Server: `python start_relay_server.py`
2. 启动 MnMCP GUI: `MnMCP_GUI.bat` 或 `mnmcp_client.exe`
3. 配置中继地址为 `127.0.0.1`
4. 启动 VPN/连接

### 方案2: 局域网测试

**Relay Server (主机)**:
```yaml
relay_server:
  host: "0.0.0.0"  # 监听所有接口
  mc_port: 25565
  mnw_port: 19132
```

**客户端配置**:
```yaml
relay_server:
  host: "192.168.1.100"  # 主机的局域网IP
  mc_port: 25565
  mnw_port: 19132
```

### 方案3: 远程服务器 (公网)

**服务器端 (Linux/Windows Server)**:

1. 开放防火墙端口:
```bash
# Linux (iptables)
iptables -A INPUT -p tcp --dport 25565 -j ACCEPT
iptables -A INPUT -p udp --dport 19132 -j ACCEPT

# Windows (PowerShell)
New-NetFirewallRule -DisplayName "MnMCP-MC" -Direction Inbound -Protocol TCP -LocalPort 25565 -Action Allow
New-NetFirewallRule -DisplayName "MnMCP-MNW" -Direction Inbound -Protocol UDP -LocalPort 19132 -Action Allow
```

2. 配置中继服务器:
```yaml
relay_server:
  host: "0.0.0.0"  # 监听所有接口
  mc_port: 25565
  mnw_port: 19132
```

3. 启动中继服务器:
```bash
python start_relay_server.py
```

**客户端配置**:
```yaml
relay_server:
  host: "your-server.com"  # 或公网IP
  mc_port: 25565
  mnw_port: 19132
```

---

## 🔧 故障排除

### 检查1: 中继服务器是否运行

```bash
# 检查端口监听
netstat -an | findstr 25565
netstat -an | findstr 19132
```

### 检查2: 防火墙设置

```powershell
# Windows 检查防火墙规则
Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*MnMCP*" }
```

### 检查3: 网络连通性

```bash
# 从客户端测试连接
telnet your-server.com 25565
nc -vu your-server.com 19132
```

### 检查4: 日志查看

```bash
# 中继服务器日志
tail -f logs/mnmcp_*.log

# Android日志
adb logcat -s MnMCP-VPN:D
```

---

## 📝 配置示例

### 场景A: 迷你世界房主 (Android) + MC玩家 (PC)

**Android (房主)**:
1. 打开 MnMCP App
2. 设置中继服务器: `your-server.com:19132`
3. 点击 "Connect VPN"
4. 打开迷你世界，创建房间

**PC (玩家)**:
1. 启动 Minecraft
2. 添加服务器: `your-server.com:25565`
3. 加入游戏

### 场景B: MC房主 (PC) + 迷你世界玩家 (Android)

**PC (房主)**:
1. 启动 Minecraft 服务器
2. 启动 MnMCP Personal 模式 B

**Android (玩家)**:
1. 打开 MnMCP App
2. 设置中继服务器: `your-server.com:19132`
3. 点击 "Connect VPN"
4. 打开迷你世界，进入联机大厅

---

## 🌐 云服务器部署

### 推荐配置

| 配置项 | 最低 | 推荐 |
|--------|------|------|
| CPU | 2核 | 4核 |
| 内存 | 4GB | 8GB |
| 带宽 | 5Mbps | 10Mbps |
| 系统 | Ubuntu 22.04 | Ubuntu 22.04 |

### 快速部署脚本

```bash
#!/bin/bash
# deploy_relay_server.sh

# 安装依赖
apt update
apt install -y python3 python3-pip

# 克隆项目
git clone https://github.com/your-repo/MnMCP.git
cd MnMCP

# 安装Python依赖
pip3 install -r requirements.txt

# 开放端口
ufw allow 25565/tcp
ufw allow 19132/udp

# 启动服务
python3 start_relay_server.py
```

---

## 🔒 安全建议

1. **使用SSL/TLS** (远程部署)
```yaml
relay_server:
  use_ssl: true
  ssl_cert: "/path/to/cert.pem"
  ssl_key: "/path/to/key.pem"
```

2. **限制连接数**
```yaml
relay_server:
  max_clients: 40
```

3. **使用防火墙限制IP**
```bash
# 只允许特定IP
iptables -A INPUT -p tcp --dport 25565 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 25565 -j DROP
```

---

## 📞 获取帮助

如果遇到问题：
1. 查看日志文件 `logs/mnmcp_*.log`
2. 检查防火墙设置
3. 验证网络连通性
4. 提交Issue到项目仓库
