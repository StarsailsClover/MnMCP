# BlockConnect-MnMCP 工作区结构设计

**日期**: 2026-04-24  
**版本**: v2.0.0-restructure  
**状态**: 重构中

---

## 📁 工作区布局

```
D:\Coding\BlockConnect\BlockConnect-MnMCP\
│
├── BlockConnect-MnMCP/                    # GitHub 仓库 (公开)
│   ├── .github/                           # GitHub 配置
│   ├── docs/                              # 文档
│   ├── src/                               # 源代码
│   │   ├── mnmcp/                         # 核心库
│   │   │   ├── crypto/                    # 加密模块
│   │   │   ├── network/                   # 网络模块
│   │   │   ├── protocol/                  # 协议模块
│   │   │   ├── mapping/                   # 映射模块
│   │   │   └── bridge/                    # 桥接器
│   │   ├── server/                        # 服务端
│   │   └── client/                        # 客户端
│   ├── tests/                             # 测试
│   ├── examples/                          # 示例
│   ├── tools/                             # 工具脚本
│   ├── requirements.txt                   # 依赖
│   ├── setup.py                           # 安装脚本
│   ├── README.md                          # 说明文档
│   ├── LICENSE                            # 许可证
│   └── .gitignore                         # Git 忽略
│
├── workspace/                             # 本地工作区 (不上传)
│   ├── resources/                         # 开发资源
│   │   ├── reverse-engineering/           # 逆向工程
│   │   │   ├── so-files/                  # SO 库文件
│   │   │   ├── apk-files/                 # APK 文件
│   │   │   ├── decompiled/                # 反编译代码
│   │   │   └── analysis-reports/          # 分析报告
│   │   ├── minecraft/                     # Minecraft 资源
│   │   │   ├── plugins/                   # 插件 (Geyser, Floodgate)
│   │   │   ├── mods/                      # 模组
│   │   │   └── server/                    # 服务端
│   │   ├── miniworld/                     # 迷你世界资源
│   │   │   ├── client/                    # 客户端文件
│   │   │   ├── assets/                    # 资源文件
│   │   │   └── data/                      # 数据文件
│   │   ├── tools/                         # 开发工具
│   │   │   ├── jadx/                      # 反编译工具
│   │   │   ├── ida/                       # IDA Pro 脚本
│   │   │   └── frida/                     # Frida 脚本
│   │   └── docs/                          # 内部文档
│   │       ├── protocol-specs/            # 协议规范
│   │       ├── crypto-analysis/           # 加密分析
│   │       └── network-analysis/          # 网络分析
│   │
│   ├── builds/                            # 构建输出
│   ├── logs/                              # 日志文件
│   ├── cache/                             # 缓存
│   └── temp/                              # 临时文件
│
└── MnMCPResources/                        # 原始资源库 (保持不动)
    └── (保持原样，作为备份)

```

---

## 🎯 文件分类规则

### GitHub 仓库 (公开上传)
**包含**:
- ✅ 源代码 (自研实现)
- ✅ 文档和教程
- ✅ 测试代码
- ✅ 示例代码
- ✅ 工具脚本 (通用)
- ✅ 配置模板

**排除**:
- ❌ 逆向工程产物 (.so, .apk, 反编译代码)
- ❌ 商业软件 (IDA Pro, JADX)
- ❌ 密钥材料 (RSA keys, XXTEA keys)
- ❌ 抓包文件 (.pcapng)
- ❌ 个人信息 (用户名, 密码, Token)
- ❌ 第三方插件/模组 (Geyser, Floodgate)

### 工作区 (本地开发)
**包含**:
- 所有开发资源
- 逆向工程文件
- 第三方工具
- 测试数据
- 构建产物

---

## 🔐 敏感信息清理规则

### 1. 密钥材料
```python
# ❌ 禁止硬编码
RSA_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----..."
XXTEA_KEY = "0x12345678..."

# ✅ 使用配置文件
config = load_config("config.yaml")
key = config.get("encryption.key")
```

### 2. 服务器地址
```python
# ❌ 禁止硬编码真实地址
SERVER_HOST = "116.205.254.229"

# ✅ 使用配置或环境变量
SERVER_HOST = os.getenv("MNW_SERVER_HOST", "localhost")
```

### 3. 用户凭证
```python
# ❌ 禁止硬编码
username = "real_username"
password = "real_password"

# ✅ 从环境变量或配置读取
username = os.getenv("MNW_USERNAME")
password = os.getenv("MNW_PASSWORD")
```

### 4. 代码注释
```python
# ❌ 包含敏感信息的注释
# 从 116.205.254.229:19701 抓包得到

# ✅ 通用描述
# 从网络抓包分析得到
```

---

## 📦 迁移计划

### Phase 1: 创建新结构
1. 创建 `BlockConnect-MnMCP/` 目录
2. 创建 `workspace/` 目录
3. 设置 `.gitignore`

### Phase 2: 迁移代码
1. 复制现有项目代码到新结构
2. 清理敏感信息
3. 重构模块结构

### Phase 3: 整理资源
1. 分类 SO 文件到 `workspace/resources/reverse-engineering/so-files/`
2. 分类 JAR 文件到对应目录
3. 整理分析报告

### Phase 4: 准备 GitHub
1. 初始化 Git 仓库
2. 配置 `.gitignore`
3. 准备 README 和文档

---

## 🚀 新架构设计

基于用户提示：**迷你世界采用本地服务端 + 内网穿透**

```
┌─────────────────────────────────────────────────────────────┐
│                   新架构设计 v2.0                            │
└─────────────────────────────────────────────────────────────┘

[迷你世界客户端]
    │
    ├─ 本地服务端 (127.0.0.1:xxxxx)
    │   ├─ 游戏逻辑处理
    │   ├─ 世界数据管理
    │   └─ 玩家状态同步
    │
    ├─ 内网穿透客户端
    │   ├─ 建立隧道到公网
    │   └─ 转发外部连接
    │
    └─ 连接到中心服务器
        ├─ 注册房间信息
        │   ├─ 房间号
        │   ├─ 房间名
        │   └─ 穿透地址
        ├─ 同步房间状态
        └─ 接收玩家加入请求

[中心服务器] (mini1.cn)
    │
    ├─ 房间注册服务
    │   └─ 存储: 房间号 → 穿透地址映射
    │
    ├─ 房间列表服务
    │   └─ 返回: 可用房间列表
    │
    └─ 玩家匹配服务
        └─ 返回: 目标房间的穿透地址

[MnMCP 桥接器]
    │
    ├─ 模拟迷你世界客户端
    │   ├─ 创建本地服务端
    │   ├─ 建立内网穿透
    │   └─ 注册到中心服务器
    │
    ├─ 连接 Minecraft 服务器
    │   └─ 使用 Geyser/Floodgate
    │
    └─ 双向数据转发
        ├─ MNW → MC
        └─ MC → MNW

[Minecraft 服务器]
    │
    ├─ Geyser 插件
    │   └─ 基岩版协议支持
    │
    ├─ Floodgate 插件
    │   └─ 无需正版验证
    │
    └─ MnMCP 插件
        └─ 迷你世界协议桥接
```

---

## 📝 开发优先级

### P0 (立即执行)
1. ✅ 创建工作区结构
2. ⏳ 迁移和清理代码
3. ⏳ 整理资源文件

### P1 (本周完成)
1. 重构核心模块
2. 实现本地服务端模拟
3. 实现内网穿透集成

### P2 (下周完成)
1. 完善文档
2. 编写测试
3. 准备发布

---

## 🔧 技术栈

### 核心技术
- **Python 3.8+**: 主要开发语言
- **asyncio**: 异步网络编程
- **cryptography**: 加密实现
- **protobuf**: 协议序列化

### 网络穿透
- **frp**: Fast Reverse Proxy
- **ngrok**: 备选方案
- **自建隧道**: 长期方案

### Minecraft 集成
- **Geyser**: 基岩版协议桥接
- **Floodgate**: 无验证登录
- **Spigot/Paper**: 服务端

---

## 📊 进度追踪

- [x] 扫描现有项目
- [x] 扫描资源文件
- [x] 设计新结构
- [ ] 创建目录结构
- [ ] 迁移代码
- [ ] 清理敏感信息
- [ ] 整理资源
- [ ] 重构架构
- [ ] 编写文档
- [ ] 准备发布

---

**最后更新**: 2026-04-24  
**负责人**: AI Assistant  
**状态**: 进行中
