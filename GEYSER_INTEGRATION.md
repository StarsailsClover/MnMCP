# ============================================================
# MnMCP v3 - Geyser 集成配置指南
# MiniWorld <-> MC JE <-> Geyser <-> MC BE 联机架构
# ============================================================

# 架构说明:
#   MiniWorld 客户端 (RakNet)
#       ↓ Port 19132
#   MnMCP ProxyServerV2 (run_proxy.py)
#       ↓ Port 25565 (TCP)
#   Minecraft JE Server (Paper/Spigot)
#       ↓ Geyser 插件
#   Minecraft BE 客户端 (通过 Geyser)
#
# 部署步骤:
#   1. 安装 MC JE 服务器 (Paper 1.20.6 推荐)
#   2. 安装 Geyser 插件到 MC JE 服务器
#   3. 启动 MnMCP ProxyServerV2
#   4. 修改 MiniWorld 客户端连接到代理地址

# ============================================================
# Geyser 配置 (plugins/Geyser/config.yml)
# ============================================================

# 克隆此配置到你的 MC JE 服务器 plugins/Geyser/config.yml
# 或在已有 Geyser 配置中修改以下关键项:

bedrock:
  # Bedrock 客户端连接的端口
  port: 19132        # 默认 19132，但 MnMCP 也占用此端口
                     # 建议改为 19133 避免冲突
  
  # 如果使用同一个端口，需要修改 run_proxy.py 的端口
  # python run_proxy.py --port 19134

remote:
  # Java 服务器地址 (Geyser 连接目标)
  address: 127.0.0.1
  port: 25565
  
  # 认证类型: offline (离线模式), online (正版), floodgate
  auth-type: offline

# 通用设置
general:
  # 允许密码认证
  allow-password-authentication: true
  
  # 调试模式
  debug-mode: false

# ============================================================
# 部署步骤
# ============================================================

# 步骤 1: 安装 MC JE 服务器
#   下载 Paper 1.20.6: https://papermc.io/downloads/paper
#   运行: java -jar paper-1.20.6-xxx.jar
#   (首次运行后会生成 eula.txt，改为 eula=true，再运行)

# 步骤 2: 安装 Geyser
#   下载: https://geysermc.org/download
#   将 Geyser.jar 放入 plugins/ 目录
#   启动服务器让 Geyser 生成配置文件
#   修改 plugins/Geyser/config.yml 按上述配置
#   重启服务器

# 步骤 3: 启动 MnMCP 代理
#   python run_proxy.py --mc-host 127.0.0.1 --mc-port 25565

# 步骤 4: MiniWorld 客户端连接
#   修改 MiniWorld 客户端连接地址为代理服务器 IP:端口
#   默认端口: 19132

# ============================================================
# 端口规划
# ============================================================

# 选项 A: 不同端口 (推荐)
#   MnMCP RakNet:         19132
#   Geyser Bedrock:       19133
#   MC JE Server:         25565
#
#   启动: python run_proxy.py --port 19132 --mc-port 25565

# 选项 B: 同一台机器，分离端口
#   MnMCP RakNet:         19134
#   Geyser Bedrock:       19132
#   MC JE Server:         25565
#
#   启动: python run_proxy.py --port 19134 --mc-port 25565

# ============================================================
# 快速启动命令
# ============================================================

# MC JE 服务器 + Geyser:
#   java -jar paper-1.20.6-xxx.jar nogui

# MnMCP 代理:
#   python run_proxy.py --debug

# 全部一起启动 (Windows PowerShell):
#   Start-Process java -ArgumentList "-jar paper-1.20.6-xxx.jar nogui"
#   Start-Sleep -Seconds 10
#   python run_proxy.py --debug
# 全部一起启动 (Linux/Mac):
#   java -jar paper-1.20.6-xxx.jar nogui &
#   sleep 10
#   python run_proxy.py --debug