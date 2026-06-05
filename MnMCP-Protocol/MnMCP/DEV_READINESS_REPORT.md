# MnMCP 开发准备报告

**检查日期**: 2026-05-23  
**目标版本**: MnMCP 3 (时间线版本管理)  
**状态**: 准备就绪，可以接手开发

---

## 📊 项目概览

### 发现的关键架构

根据逆向工程和文档分析，迷你世界采用 **"本地服务端 + 内网穿透"** 的P2P架构：

```
房主流程:
1. 本地启动游戏服务端 (127.0.0.1:随机端口)
2. 启动内网穿透客户端，建立隧道到公网
3. 向中心服务器注册房间 (房间号 + 穿透地址)

加入者流程:
1. 从中心服务器获取房间列表
2. 选择房间，获取穿透地址
3. 直接连接到房主的本地服务端
```

**重要**: 中心服务器只返回元数据，游戏数据通过P2P直连。

---

## 🔒 代码审查结果 (Critical Issues)

### 1. 安全漏洞 - 硬编码密钥

| 位置 | 问题 | 严重程度 |
|------|------|----------|
| `mn2mc/mini/auth.py:15` | 硬编码MD5签名密钥 | **CRITICAL** |
| `mn2mc/mini/room.py:11` | 硬编码AUTH_KEY | **CRITICAL** |
| `mn2mc/config.py:30` | 默认空xxtea_key需用户填充 | **HIGH** |

**修复建议**:
```python
# 当前 (不安全)
msgsign = hashlib.md5(
    f"msg={msg}&key=2ddb7619717147439c83ab022e9d4d38".encode()
).hexdigest()

# 应该改为配置读取
msgsign = hashlib.md5(
    f"msg={msg}&key={config.auth['sign_key']}".encode()
).hexdigest()
```

### 2. 硬编码服务器地址

| 位置 | 硬编码地址 | 风险 |
|------|------------|------|
| `auth.py:14` | `wskacchm.mini1.cn:14130` | 域名变更风险 |
| `room.py:10` | `openroom.mini1.cn:8080` | 配置不灵活 |

### 3. 代码质量问题

| 维度 | 问题 | 位置 |
|------|------|------|
| **Maintainability** | 大量使用全局变量 | `auth.py`, `room.py` |
| **Correctness** | 缺少错误处理 | 多处网络调用 |
| **Testing** | 无单元测试 | 整个项目 |
| **Documentation** | 缺少API文档 | 核心模块 |
| **Type Safety** | 类型注解不完整 | 多处函数 |

### 4. 架构耦合

```
问题: mn2mc.mini.server 模块同时处理:
- 网络连接 (aiorak)
- 房间管理
- 协议转换
- 配置读取

应该拆分为:
- server/connection.py - 连接管理
- room/manager.py - 房间管理
- protocol/bridge.py - 协议转换
```

---

## 🏗️ MnMCP 3 时间线版本管理

### 版本命名规则

放弃传统语义化版本，采用**时间线版本**:

```
格式: YYYY-MM-DD-HH[-hotfix]

示例:
- 2026-05-23-14       # 2026年5月23日 14:00版本
- 2026-05-23-14-1     # 同日14:00版本的第1个热修复
- 2026-05-23          # 当日最终稳定版
```

### 版本文件

```python
# mnmcp/version.py
from datetime import datetime

def get_version():
    return datetime.now().strftime("%Y-%m-%d-%H")

VERSION = get_version()  # 编译时确定
BUILD_TIME = "2026-05-23-14"
```

### Git工作流

```bash
# 每日开发分支
git checkout -b dev/2026-05-23

# 小时级提交
git commit -m "2026-05-23-14: 完成协议解析优化"

# 每日合并到main
git checkout main
git merge dev/2026-05-23
git tag 2026-05-23
```

---

## 📋 技术债务清单

| 优先级 | 债务项 | 预估工作量 | 修复建议 |
|--------|--------|------------|----------|
| 🔴 P0 | 移除硬编码密钥 | 2h | 改为从环境变量读取 |
| 🔴 P0 | 添加错误处理 | 4h | 所有网络调用添加try-catch |
| 🟡 P1 | 重构全局变量 | 6h | 改为依赖注入模式 |
| 🟡 P1 | 补充类型注解 | 4h | 使用mypy检查 |
| 🟢 P2 | 添加单元测试 | 8h | pytest框架 |
| 🟢 P2 | 文档补全 | 6h | docstrings + README |

---

## 🚀 开发准备清单

### 已完成 ✅

- [x] 项目结构理解
- [x] 代码审查完成
- [x] 架构设计熟悉
- [x] 资源文件清单
- [x] 版本管理机制定义

### 待完成 📝

- [ ] 安装依赖: `pip install -r requirements.txt`
- [ ] 配置config.yaml (复制config.template.yaml)
- [ ] 创建logs目录
- [ ] 测试MN2MC是否能启动

### 环境要求

```
Python: 3.11+
Node.js: 18+ (for javascript模块)
依赖: 见requirements.txt
```

---

## 🔄 下一步行动计划

### 立即执行 (今天)

1. **清理敏感信息**
   - 从代码中提取所有硬编码值到config.yaml
   - 添加config.template.yaml作为模板

2. **创建安全配置模板**
   ```yaml
   # config.template.yaml
   mini:
     auth:
       uin: 0  # 填入迷你世界账号
       passwd: ""  # 填入密码
       api_id: 110
       device_id: ""  # 生成UUID
       xxtea_key: ""  # 从逆向分析获取
   ```

### 本周目标

1. 完成MN2MC模块重构
2. 实现时间线版本管理
3. 添加基础错误处理
4. 编写单元测试框架

### 长期目标

1. 实现完整的桥接功能
2. 优化性能 (chunk解析速度)
3. 支持更多MC版本
4. 生产环境测试

---

## 📚 关键资源

### 逆向工程成果

- **SO分析**: 69,672个文件已扫描
- **关键库**: libilink_network.so (网络通信)
- **密钥结构**: 4层密钥层次 (Master → Session → Derived → Room)
- **协议文档**: Protocol Specification完整

### 可用工具

- JADX: APK反编译
- Frida: 动态Hook
- IDA Pro: 静态分析
- Wireshark: 流量分析
- Clash Meta: 代理测试

---

## ✅ 结论

**状态**: MnMCP项目已准备好接手开发。

**核心优势**:
1. 完整的逆向工程基础
2. 清晰的架构理解
3. 丰富的资源文件
4. 时间线版本管理机制

**需要关注**:
1. 敏感信息清理
2. 错误处理完善
3. 测试覆盖增加

**推荐启动方式**:
1. 先清理config.py中的硬编码值
2. 创建config.template.yaml
3. 运行MN2MC测试基本功能
4. 逐步重构和优化
