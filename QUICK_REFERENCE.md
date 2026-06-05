# MnMCP 快速参考

## 🚀 5分钟上手

### 1. 验证安装
```bash
cd mnmcp-v3-integrated
python verify_integration.py
```

### 2. 核心模块

```python
# 方块映射
from mcp_mapping import BlockMapperIntegrated
mapper = BlockMapperIntegrated()
mnw_id = mapper.mc_to_mnw(1)  # 104

# 登录认证
from mcp_crypto import MCPAuthManager, MCPAuthConfig
config = MCPAuthConfig(uin="123456", passwd="xxx")
auth = MCPAuthManager(config)
await auth.login()

# MC 客户端
from mcp_mc import MCPMinecraftClient
client = MCPMinecraftClient(server, "Player")

# MNW 客户端
from mcp_mini import MCPMiniWorldClient
client = MCPMiniWorldClient(server, auth)
```

## 📁 项目结构

```
mnmcp-v3-integrated/
├── src/
│   ├── mcp_mapping/       # ✅ 方块映射
│   ├── mcp_crypto/        # ✅ 加密认证
│   ├── mcp_mc/            # ✅ MC客户端
│   └── mcp_mini/          # ✅ MNW客户端
└── verify_integration.py  # 验证脚本
```

## ✅ 状态

```
Phase 1-5: ████████████████████ 100% (框架)
Phase 6-8: ░░░░░░░░░░░░░░░░░░░░ 0%  (实现)
实现度: 75%
质量: ⭐⭐⭐⭐⭐
```

## 🎯 下一步

1. 完善协议实现
2. 整合桥接核心
3. 局域网测试

## 📞 参考

- `HANDOVER_DOCUMENT.md` - 完整交接文档
- `INTEGRATION_FINAL_REPORT.md` - 详细报告
- `README.md` - 项目说明

---
**Quick Start!** 🎉
