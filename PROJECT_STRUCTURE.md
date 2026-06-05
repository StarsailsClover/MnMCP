# MnMCP 项目结构整理方案

## 目标
创建清晰、可维护的项目结构

## 新结构

```
MnMCP/
├── 📁 mnmcp-v3-integrated/          # ✅ 主项目 (整合版)
│   ├── src/
│   │   ├── mcp_core/               # 核心桥接
│   │   ├── mcp_mapping/           # ✅ 方块映射 (844个)
│   │   ├── mcp_crypto/            # ✅ 加密认证
│   │   ├── mcp_mc/                # MC 客户端
│   │   ├── mcp_mini/              # MNW 客户端
│   │   └── mcp_config/            # 统一配置
│   ├── tests/
│   └── main.py
│
├── 📁 archive/                      # 归档旧版本
│   ├── mnmcp-v2-original/         # MnMCP 3 原始版
│   ├── mn2mc-official/            # MN2MC 官方版
│   └── mnmcp-mn2mc-legacy/        # MnMCP-MN2MC 旧版
│
├── 📁 docs/                         # 文档
│   ├── integration/               # 整合文档
│   ├── api/                       # API文档
│   └── guides/                    # 使用指南
│
├── 📁 tools/                        # 工具脚本
│   ├── extract-mappings.py
│   └── test-scripts/
│
└── 📄 README.md                     # 项目说明
```

## 整理步骤

1. 创建 archive/ 目录
2. 移动旧版本到 archive/
3. 整理 mnmcp-v3-integrated/
4. 创建 docs/ 目录
5. 更新 README.md

## 命名规范

- 模块: `mcp_xxx` (统一前缀)
- 类: `MCPXxx` (PascalCase)
- 函数: `xxx_xxx` (snake_case)
- 常量: `UPPER_CASE`
