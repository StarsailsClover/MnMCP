# MnMCP 技术债务清单

**版本**: MnMCP 3 (时间线版本)  
**创建日期**: 2026-05-23  
**状态**: 持续更新

---

## 🚨 严重问题 (P0 - 必须修复)

### TD-001: 硬编码安全密钥

**描述**: 代码中包含多个硬编码的加密密钥和认证密钥

| 位置 | 代码 | 风险 |
|------|------|------|
| `mn2mc/mini/auth.py:43` | `key=2ddb7619717147439c83ab022e9d4d38` | MD5签名密钥硬编码 |
| `mn2mc/mini/room.py:12` | `AUTH_KEY = "f5711eb1640712de051e5aedc35329c3"` | 房间认证密钥 |

**影响**:
- 密钥泄露风险
- 无法灵活更换密钥
- 违反安全最佳实践

**修复方案**:
```python
# 方案1: 环境变量
import os
SIGN_KEY = os.environ.get('MN_MCP_SIGN_KEY', '')

# 方案2: 配置文件
from mn2mc.config import config
SIGN_KEY = config.mini['central_server']['sign_key']
```

**工作量**: 2小时  
**负责人**: 待分配  
**截止日期**: 2026-05-24

---

### TD-002: 硬编码服务器地址

**描述**: 迷你世界服务器地址硬编码在代码中

| 位置 | 代码 |
|------|------|
| `auth.py:14` | `LOGIN_URL = "https://wskacchm.mini1.cn:14130/..."` |
| `room.py:10` | `CONFIG_URL = " http://openroom.mini1.cn:8080/..."` (注意空格) |

**影响**:
- 服务器地址变更需修改代码
- 无法切换测试/生产环境
- 代码复用性降低

**修复方案**:
```python
# 移至config.yaml
mini:
  central_server:
    auth_url: "https://wskacchm.mini1.cn:14130"
    room_url: "http://openroom.mini1.cn:8080"
```

**工作量**: 1小时  
**负责人**: 待分配  
**截止日期**: 2026-05-24

---

### TD-003: 缺少错误处理

**描述**: 网络调用和文件操作缺少try-catch块

| 位置 | 操作 | 风险 |
|------|------|------|
| `auth.py:45-52` | HTTP GET请求 | 网络超时崩溃 |
| `config.py:85-88` | 文件读取 | 文件不存在崩溃 |
| `room.py:147-152` | 异步HTTP请求 | 异常未捕获 |

**示例问题代码**:
```python
# auth.py (当前)
async with session.get(LOGIN_URL % (msg, msgsign), headers=...) as response:
    text = await response.text()
    data = json.loads(text)
```

**修复方案**:
```python
# 应该改为
try:
    async with session.get(...) as response:
        if response.status != 200:
            raise MiniAuthenticationError(f"HTTP {response.status}")
        text = await response.text()
        data = json.loads(text)
except aiohttp.ClientError as e:
    logger.error(f"Network error during login: {e}")
    raise MiniAuthenticationError(f"Network error: {e}")
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON response: {e}")
    raise MiniAuthenticationError(f"Invalid response: {e}")
```

**工作量**: 4小时  
**负责人**: 待分配  
**截止日期**: 2026-05-25

---

## 🔶 中等问题 (P1 - 应该修复)

### TD-004: 过度使用全局变量

**描述**: 多个模块使用全局变量存储状态

| 位置 | 全局变量 | 问题 |
|------|----------|------|
| `auth.py:17-23` | `uin`, `jwt`, `name`, etc. | 状态难以追踪 |
| `room.py:66-68` | `room_url`, `config`, `session_id` | 线程不安全 |

**影响**:
- 代码难以测试
- 并发安全问题
- 状态管理混乱

**修复方案**:
```python
# 改为类封装
class AuthManager:
    def __init__(self):
        self._uin = 0
        self._jwt = ""
        self._name = "Unknown"
    
    async def login(self) -> bool:
        # 实现登录逻辑
        pass
    
    @property
    def uin(self) -> int:
        return self._uin
```

**工作量**: 6小时  
**负责人**: 待分配  
**截止日期**: 2026-05-26

---

### TD-005: 类型注解不完整

**描述**: 许多函数缺少类型注解

| 位置 | 函数 | 当前签名 |
|------|------|----------|
| `auth.py:29` | `encode` | `def encode(data):` |
| `server.py:53` | `broadcast_packet` | `def broadcast_packet(msgcode, data):` |
| `utils/xxtea.py:9` | `encrypt` | `def encrypt(data):` |

**修复方案**:
```python
# 添加完整类型注解
from typing import Dict, Any

def encode(data: Dict[str, Any]) -> str:
    ...

def broadcast_packet(msgcode: proto.common.ePBMsgCode, data: bytes) -> None:
    ...
```

**工作量**: 4小时 (可使用mypy自动检查)  
**负责人**: 待分配  
**截止日期**: 2026-05-26

---

### TD-006: 模块职责不清晰

**描述**: `server.py` 模块承担了过多职责

**当前职责**:
- 网络连接管理 (aiorak.Server)
- 房间状态管理
- 协议消息广播
- 日志转发

**应该拆分**:
```
mn2mc/
├── network/
│   ├── server.py        # 纯网络层
│   └── connection.py    # 连接管理
├── room/
│   ├── manager.py       # 房间管理
│   └── state.py         # 房间状态
└── bridge/
    ├── broadcaster.py   # 消息广播
    └── logger.py        # 日志转发
```

**工作量**: 8小时  
**负责人**: 待分配  
**截止日期**: 2026-05-27

---

## 🔷 低优先级问题 (P2 - 可选修复)

### TD-007: 缺少单元测试

**描述**: 整个项目没有单元测试

**测试覆盖率**: 0%

**建议测试框架**:
```bash
pip install pytest pytest-asyncio pytest-cov
```

**关键测试点**:
- [ ] 加密/解密模块
- [ ] 协议解析
- [ ] 坐标转换
- [ ] 配置加载

**工作量**: 8小时  
**负责人**: 待分配  
**截止日期**: 2026-05-30

---

### TD-008: 文档不完整

**描述**: 缺少API文档和开发文档

| 缺失文档 | 优先级 |
|----------|--------|
| API参考文档 | 高 |
| 架构设计文档 | 高 |
| 贡献指南 | 中 |
| 部署文档 | 中 |

**工作量**: 6小时  
**负责人**: 待分配  
**截止日期**: 2026-05-28

---

## 📊 债务统计

| 优先级 | 数量 | 预估总工时 | 截止日期 |
|--------|------|------------|----------|
| P0 (严重) | 3 | 7小时 | 2026-05-24 |
| P1 (中等) | 3 | 18小时 | 2026-05-27 |
| P2 (低) | 2 | 14小时 | 2026-05-30 |
| **总计** | **8** | **39小时** | **2026-05-30** |

---

## 🎯 偿还计划

### Sprint 1 (5/23-5/24) - 安全优先
- [ ] TD-001: 移除硬编码密钥
- [ ] TD-002: 移除硬编码服务器地址

### Sprint 2 (5/25-5/26) - 稳定性
- [ ] TD-003: 添加错误处理
- [ ] TD-004: 重构全局变量

### Sprint 3 (5/27-5/28) - 代码质量
- [ ] TD-005: 补充类型注解
- [ ] TD-006: 模块重构

### Sprint 4 (5/29-5/30) - 完善
- [ ] TD-007: 单元测试
- [ ] TD-008: 文档完善

---

## 📈 债务追踪

| 日期 | 剩余债务 | 已偿还 | 新增 |
|------|----------|--------|------|
| 2026-05-23 | 8 | 0 | 0 |
| 2026-05-24 | - | - | - |
| 2026-05-25 | - | - | - |

**目标**: 每周偿还50%债务，新增债务<10%
