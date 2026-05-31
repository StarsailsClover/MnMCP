# MnMCP 3 - 今日执行计划

**日期**: 2026-05-23  
**版本**: 2026-05-23-14  
**状态**: 准备启动开发

---

## 🎯 今日目标 (2026-05-23-14)

完成开发环境准备，启动Phase 1 - 基础重构

---

## ⏰ 时间表

### 当前时间: 2026-05-23 14:00

| 时间 | 任务 | 产出 |
|------|------|------|
| 14:00-15:00 | 验证开发环境 | 环境检查报告 |
| 15:00-16:00 | 清理硬编码密钥 (TD-001) | auth.py, room.py 更新 |
| 16:00-17:00 | 修复HTTP URL硬编码 (TD-002) | 配置文件更新 |
| 17:00-17:30 | 测试验证 | 启动测试报告 |
| 17:30-18:00 | 日终总结 | 进度更新到DEV_PROGRESS.md |

---

## 📝 任务详情

### 任务1: 环境验证

**检查清单**:
```bash
# Python版本
python --version  # 应 >= 3.11.0

# 依赖安装
pip install -r requirements.txt

# Node.js (用于javascript模块)
node --version  # 应 >= 18.0.0

# 目录检查
dir logs  # 应存在
```

**如果缺失**:
```bash
# 创建logs目录
mkdir logs

# 安装Python依赖
pip install -r requirements.txt

# 安装Node.js依赖 (如果需要)
npm install -g minecraft-protocol prismarine-chunk
```

---

### 任务2: 清理硬编码密钥 (TD-001)

**文件**: `mn2mc/mini/auth.py`

**当前问题代码** (line 43):
```python
msgsign = hashlib.md5(
    f"msg={msg}&key=2ddb7619717147439c83ab022e9d4d38".encode()
).hexdigest()
```

**修复后**:
```python
# 从配置文件读取
from mn2mc.config import config

# ...

sign_key = config.mini.get('central_server', {}).get('sign_key', '')
if not sign_key:
    sign_key = os.environ.get('MN_MCP_SIGN_KEY', '')
    
if not sign_key:
    raise ValueError("签名密钥未配置: 请在config.yaml中设置mini.central_server.sign_key")

msgsign = hashlib.md5(
    f"msg={msg}&key={sign_key}".encode()
).hexdigest()
```

**文件**: `mn2mc/mini/room.py`

**当前问题代码** (line 12):
```python
AUTH_KEY = "f5711eb1640712de051e5aedc35329c3"
```

**修复后**:
```python
import os
from mn2mc.config import config

# 从配置文件读取，允许环境变量覆盖
def get_auth_key():
    auth_key = config.mini.get('central_server', {}).get('auth_key', '')
    if not auth_key:
        auth_key = os.environ.get('MN_MCP_AUTH_KEY', '')
    return auth_key

AUTH_KEY = get_auth_key()
```

**更新config.template.yaml**:
```yaml
mini:
  central_server:
    sign_key: ""  # 迷你世界登录签名密钥
    auth_key: ""  # 迷你世界房间认证密钥
```

---

### 任务3: 修复HTTP URL硬编码 (TD-002)

**文件**: `mn2mc/mini/auth.py`

**当前问题代码** (line 14):
```python
LOGIN_URL = "https://wskacchm.mini1.cn:14130/man_machine/login_v3?msg=%s&sign=%s"
```

**修复后**:
```python
from mn2mc.config import config

def get_login_url():
    base_url = config.mini.get('central_server', {}).get('auth_url', 
                'https://wskacchm.mini1.cn:14130')
    return f"{base_url}/man_machine/login_v3?msg=%s&sign=%s"
```

**文件**: `mn2mc/mini/room.py`

**当前问题代码** (line 10):
```python
CONFIG_URL = " http://openroom.mini1.cn:8080/server/room?"
# 注意: 这里有前导空格!
```

**修复后**:
```python
def get_config_url():
    base_url = config.mini.get('central_server', {}).get('room_url',
                'http://openroom.mini1.cn:8080')
    return f"{base_url}/server/room?"
```

**更新config.template.yaml**:
```yaml
mini:
  central_server:
    auth_url: "https://wskacchm.mini1.cn:14130"
    room_url: "http://openroom.mini1.cn:8080"
```

---

### 任务4: 测试验证

**步骤1: 创建测试配置**
```bash
copy config.template.yaml config.yaml
notepad config.yaml  # 填入最小配置
```

**最小测试配置**:
```yaml
mini:
  auth:
    uin: 0
    passwd: ""
    api_id: 110
    device_id: ""
    xxtea_key: ""
  server:
    ip: "127.0.0.1"
    port: 11155
    host_to_room_server: false

debug: true
```

**步骤2: 运行启动测试**
```bash
python -c "from mn2mc.config import config; config.load(); print('Config loaded OK')"
```

**步骤3: 运行模块测试**
```bash
python -c "from mn2mc.mini import auth; print('Auth module imports OK')"
python -c "from mn2mc.mini import room; print('Room module imports OK')"
```

**预期输出**:
```
Config loaded OK
Auth module imports OK
Room module imports OK
```

---

## ✅ 完成标准

### 检查清单

- [ ] Python 3.11+ 已验证
- [ ] 依赖已安装
- [ ] `config.template.yaml` 已更新包含服务器配置
- [ ] `auth.py` 中的硬编码密钥已移除
- [ ] `room.py` 中的硬编码密钥已移除
- [ ] `auth.py` 中的硬编码URL已移除
- [ ] `room.py` 中的硬编码URL已移除
- [ ] 模块导入测试通过
- [ ] 配置文件加载测试通过
- [ ] 日志目录已创建

### 提交信息

```bash
git add -A
git commit -m "2026-05-23-15: 清理硬编码密钥和URL，添加配置模板"
git tag 2026-05-23-15
```

---

## 🐛 已知问题

### 问题1: xxtea_key 未设置
**症状**: `ValueError: xxtea_key is empty`
**解决**: 这是预期行为，需要用户提供密钥

### 问题2: Node.js依赖
**症状**: `Error: Cannot find module 'minecraft-protocol'`
**解决**: 安装Node.js并运行 `npm install -g minecraft-protocol`

---

## 📊 进度跟踪

| 任务 | 状态 | 开始 | 完成 | 备注 |
|------|------|------|------|------|
| 环境验证 | 🔴 待开始 | - | - | |
| TD-001 硬编码密钥 | 🔴 待开始 | - | - | |
| TD-002 硬编码URL | 🔴 待开始 | - | - | |
| 测试验证 | 🔴 待开始 | - | - | |
| 日终总结 | 🔴 待开始 | - | - | |

---

## 🚀 下一步

今日完成后，明天开始:
- **TD-003**: 添加错误处理
- **TD-004**: 重构全局变量

查看完整计划: `DEVELOPMENT_ROADMAP.md`
