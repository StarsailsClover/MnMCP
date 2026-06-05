# MnMCP 3 快速启动指南

**版本**: MnMCP 3 (时间线版本: 2026-05-23)  
**适用**: 开发者接手项目

---

## 🚀 5分钟快速启动

### 1. 克隆/准备项目

```bash
# 进入项目目录
cd C:\Users\Sails\Documents\Workspace\NormalWorkplace\Coding\MnMCP-Protocol\MN2MC

# 确保Python 3.11+
python --version  # 应显示 3.11.x 或更高
```

### 2. 安装依赖

```bash
# 创建虚拟环境 (推荐)
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置文件

```bash
# 复制模板配置文件
copy config.template.yaml config.yaml

# 编辑配置 (使用你的编辑器)
notepad config.yaml
```

**最小配置要求**:
```yaml
mini:
  auth:
    uin: 123456789              # 你的迷你世界账号
    passwd: "your_password"     # 你的密码
    xxtea_key: "your_xxtea_key" # 从逆向分析获取

mc:
  ip: "127.0.0.1"               # MC服务器地址
  port: 25565                   # MC服务器端口
```

### 4. 创建日志目录

```bash
mkdir logs
```

### 5. 运行测试

```bash
# 运行主程序
python main.py
```

如果看到以下输出，说明启动成功:
```
2026-05-23 14:30:00.123 | INFO     | Preparing Node.js dependencies...
2026-05-23 14:30:05.456 | INFO     | Server started on 127.0.0.1:11155
```

---

## 📂 项目结构

```
MN2MC/
├── main.py                    # 程序入口
├── requirements.txt           # Python依赖
├── config.yaml                # 配置文件 (本地，不提交Git)
├── config.template.yaml       # 配置模板
├── DEV_READINESS_REPORT.md    # 开发准备报告
├── TECHNICAL_DEBT.md          # 技术债务清单
├── QUICK_START.md             # 本文件
│
├── mn2mc/                     # 核心包
│   ├── __init__.py
│   ├── config.py              # 配置加载
│   │
│   ├── mc/                    # Minecraft 相关
│   │   ├── client.py          # MC客户端
│   │   ├── packet.py          # 数据包处理
│   │   └── packetevents/      # 事件处理器
│   │
│   ├── mini/                  # 迷你世界相关
│   │   ├── server.py          # 迷你服务端
│   │   ├── auth.py            # 认证模块
│   │   ├── room.py            # 房间管理
│   │   ├── packet.py          # 数据包处理
│   │   ├── proto/             # 协议定义 (.proto)
│   │   └── packetevents/      # 事件处理器
│   │
│   ├── mapping/               # 数据映射
│   │   ├── blocks.py          # 方块映射
│   │   ├── items.py           # 物品映射
│   │   └── mobs.py            # 实体映射
│   │
│   └── utils/                 # 工具函数
│       ├── xxtea.py           # XXTEA加密
│       ├── protobuf_parser.py # Protobuf解析
│       └── ...
│
└── logs/                      # 日志目录
```

---

## 🧪 开发测试

### 测试映射系统

```python
# 启动Python解释器
python

# 测试代码
>>> from mn2mc import mapping
>>> mapping.get_block_mapping(100)  # 迷你世界方块ID 100
'minecraft:grass_block'
```

### 测试加密模块

```python
>>> from mn2mc.utils import xxtea
>>> xxtea.xxtea_key = b'your_key_here'
>>> encrypted = xxtea.encrypt_zip(b"Hello World")
>>> decrypted = xxtea.decrypt_unzip(encrypted)
>>> print(decrypted.decode())
Hello World
```

---

## 🔧 常见问题和解决方案

### Q1: `ModuleNotFoundError: No module named 'javascript'`

**解决**:
```bash
pip install javascript
# 如果失败，尝试:
pip install --pre javascript
```

### Q2: `Error: Cannot find module 'minecraft-protocol'`

**解决**:
```bash
# 需要Node.js
node --version  # 检查是否安装

# 安装Node.js依赖 (程序会自动尝试安装)
# 如果失败，手动安装:
npm install -g minecraft-protocol prismarine-chunk
```

### Q3: `xxtea_key is empty` 错误

**解决**:
1. 编辑 `config.yaml`
2. 填入 `mini.auth.xxtea_key`
3. 密钥需从逆向分析获取，格式: 16字节hex字符串

### Q4: 登录失败 `code: -1`

**可能原因**:
- 账号密码错误
- 网络连接问题
- 服务器维护

**排查步骤**:
1. 检查账号密码
2. 检查网络连接
3. 查看 `logs/` 目录下的日志文件

---

## 📚 开发资源

### 逆向工程文档

- `MnMCPResources/SO_Analysis_Reports/` - SO库分析报告
- `MnMCPResources/reverse-engineering/` - 逆向工程资源

### 关键文档

| 文档 | 说明 |
|------|------|
| `DEV_READINESS_REPORT.md` | 开发准备报告，含架构说明 |
| `TECHNICAL_DEBT.md` | 技术债务清单，待修复问题 |
| `WORKSPACE_STRUCTURE.md` | 工作区结构设计 |
| `RESTRUCTURE_PLAN.md` | 重构计划详细说明 |

---

## 🤝 贡献指南

### Git工作流

```bash
# 1. 创建功能分支
git checkout -b feature/your-feature-name

# 2. 提交更改 (使用时间线版本格式)
git commit -m "2026-05-23-15: 添加XXX功能"

# 3. 推送到远程
git push origin feature/your-feature-name

# 4. 创建Pull Request
```

### 代码规范

- 使用 `black` 格式化代码: `pip install black && black .`
- 使用 `mypy` 类型检查: `pip install mypy && mypy mn2mc/`
- 添加类型注解
- 编写清晰的commit消息

---

## 📞 联系方式

- **项目文档**: 查看 `workspace/docs/`
- **问题追踪**: 查看 `TECHNICAL_DEBT.md`
- **日志文件**: 查看 `logs/` 目录

---

## ✅ 检查清单

首次启动前确认:

- [ ] Python 3.11+ 已安装
- [ ] 依赖已安装 (`pip install -r requirements.txt`)
- [ ] `config.yaml` 已创建并配置
- [ ] `logs/` 目录已创建
- [ ] XXTEA密钥已填入

开发前确认:

- [ ] 已阅读 `DEV_READINESS_REPORT.md`
- [ ] 已了解 `TECHNICAL_DEBT.md` 中的问题
- [ ] 已理解架构设计

---

**最后更新**: 2026-05-23  
**MnMCP 3 时间线版本**: 2026-05-23-14
