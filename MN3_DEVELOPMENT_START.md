# MnMCP 3 开发启动清单

**版本**: v26.3-20260605  
**状态**: 🚀 准备就绪

---

## 阶段 0: 开发前准备 (必须完成)

### 0.1 安全修复 ✅

```bash
cd mnmcp-v3-integrated

# 1. 运行安全扫描
python scripts/fix_security.py

# 2. 创建环境变量文件
copy .env.template .env
# 编辑 .env 填写实际值

# 3. 加载环境变量 (PowerShell)
$env:MCP_MD5_SALT="your_actual_salt"
$env:MCP_DEVICE_ID="your_device_id"
$env:MCP_XXTEA_KEY="your_16byte_key"
```

### 0.2 配置系统 ✅

```python
# 测试配置系统
python src/mcp_config.py

# 预期输出:
# ✓ 已创建 config.template.yaml
# ✓ 配置加载成功
#   认证服务器: wskacchm.mini1.cn:14130
#   MC桥接地址: 127.0.0.1:25565
```

### 0.3 验证现有模块 ✅

```bash
# 运行整合验证
python verify_integration.py

# 预期输出:
# [测试] 方块映射系统
# ✓ 映射加载成功
#   总映射数: 844
# [测试] 加密模块
# ✓ 打包测试
# ✓ 加密测试
# ✓ 消息编码
# MnMCP v3 整合版验证完成
```

---

## 阶段 1: 网络客户端移植 (Week 1)

### 1.1 移植 MC 客户端

**目标**: `mcp_mc/client_mcp.py`

```python
# 待实现功能:
# TODO: 实现完整的 VarInt 长度读取
# TODO: 实现握手协议
# TODO: 实现登录流程
# TODO: 实现数据包解析
# TODO: 实现状态同步
```

**参考**:
- Minecraft 协议: https://wiki.vg/Protocol
- 现有框架: `mcp_mc/client_mcp.py` (已建框架)

**预计工时**: 16小时

### 1.2 移植 MNW 客户端

**目标**: `mcp_mini/client_mcp.py`

```python
# 待实现功能:
# TODO: 实现 MiniWorld 协议解析
# TODO: 实现房间进入流程
# TODO: 实现玩家控制
# TODO: 实现数据包转发
```

**参考**:
- MN2MC 原始代码
- 现有框架: `mcp_mini/client_mcp.py` (已建框架)

**预计工时**: 16小时

---

## 阶段 2: 桥接核心实现 (Week 2)

### 2.1 创建桥接核心

**目标**: `src/mcp_core/bridge.py`

```python
class MCPBridgeCore:
    """
    MnMCP 桥接核心
    
    功能:
    1. 双向数据包转发
    2. 状态同步
    3. 错误恢复
    4. 事件系统
    """
    
    async def start(self):
        """启动桥接服务"""
        pass
    
    async def forward_mc_to_mnw(self, packet):
        """MC → MNW 转发"""
        pass
    
    async def forward_mnw_to_mc(self, packet):
        """MNW → MC 转发"""
        pass
```

**预计工时**: 24小时

### 2.2 事件系统

**目标**: `src/mcp_core/events.py`

```python
class MCPEventBus:
    """事件总线"""
    
    async def emit(self, event: str, data: dict):
        """触发事件"""
        pass
    
    def on(self, event: str, handler: Callable):
        """注册处理器"""
        pass
```

**预计工时**: 8小时

---

## 阶段 3: 协议层实现 (Week 3)

### 3.1 ProtoBuf 协议

**目标**: `src/protocol/mini/` 和 `src/protocol/mc/`

```python
# MiniWorld ProtoBuf 定义
# Minecraft 数据包定义
```

**预计工时**: 16小时

### 3.2 数据包编解码

**目标**: `src/protocol/codec.py`

```python
class MCPPacketCodec:
    """数据包编解码器"""
    
    def encode(self, packet: dict) -> bytes:
        """编码数据包"""
        pass
    
    def decode(self, data: bytes) -> dict:
        """解码数据包"""
        pass
```

**预计工时**: 8小时

---

## 阶段 4: 测试与优化 (Week 4)

### 4.1 单元测试

```bash
# 创建测试目录结构
mkdir tests/unit tests/integration

# 测试文件
tests/
├── unit/
│   ├── test_mapping.py
│   ├── test_crypto.py
│   ├── test_mc_client.py
│   └── test_mnw_client.py
└── integration/
    └── test_bridge.py
```

**预计工时**: 8小时

### 4.2 局域网测试

```bash
# 启动测试服务器
python lan_test_server.py

# 启动测试客户端
python lan_test_client.py

# 使用 Minecraft 客户端连接
# localhost:25565
```

**预计工时**: 8小时

---

## 开发规范

### 命名规范

```python
# 模块: mcp_xxx
# 类: MCPXxx
# 函数: snake_case
# 常量: UPPER_CASE

from mcp_mapping import MCPBlockMapper
from mcp_crypto import MCPXXTEA

class MCPBridgeCore:
    def forward_packet(self, packet: dict) -> bool:
        MAX_RETRIES = 3
```

### 代码质量要求

- ✅ 类型注解覆盖率 100%
- ✅ 文档字符串完整
- ✅ 错误处理完善
- ✅ 单元测试 >80%
- ✅ 无硬编码敏感信息

### Git 提交规范

```
类型: 简短描述

详细说明

Fixes: #issue
```

类型:
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `test`: 测试
- `refactor`: 重构
- `security`: 安全修复

---

## 进度跟踪

| 阶段 | 任务 | 状态 | 工时 | 完成日期 |
|------|------|------|------|----------|
| 0 | 安全修复 | ⏳ | 2h | - |
| 0 | 配置系统 | ⏳ | 4h | - |
| 1 | MC 客户端 | ⏳ | 16h | - |
| 1 | MNW 客户端 | ⏳ | 16h | - |
| 2 | 桥接核心 | ⏳ | 24h | - |
| 2 | 事件系统 | ⏳ | 8h | - |
| 3 | ProtoBuf | ⏳ | 16h | - |
| 3 | 编解码 | ⏳ | 8h | - |
| 4 | 单元测试 | ⏳ | 8h | - |
| 4 | 集成测试 | ⏳ | 8h | - |

**总工时**: ~110小时 (~14天，每天8小时)

---

## 启动命令

```bash
# 1. 进入项目目录
cd mnmcp-v3-integrated

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境变量
$env:MCP_MD5_SALT="your_salt"
$env:MCP_DEVICE_ID="your_device_id"
$env:MCP_XXTEA_KEY="your_key"

# 4. 验证安装
python verify_integration.py

# 5. 开始开发！
```

---

**准备就绪！开始 MnMCP 3 开发 🚀**
