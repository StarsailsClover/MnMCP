# MnMCP 二次开发资源包

**版本**: v0.6.0  
**日期**: 2026-02-28  
**用途**: 开发者资源、API文档、扩展工具

---

## 资源包内容

### 1. API文档
- 模块接口文档
- 配置项详细说明
- 扩展开发指南

### 2. 开发工具
- 代码生成器
- 调试工具
- 测试模板

### 3. 资源文件
- 方块ID映射表
- 协议定义文件
- 抓包样本

### 4. 示例代码
- 插件示例
- 自定义协议处理器
- 扩展模块示例

---

## 快速开始

### 环境准备
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行开发环境检查
python check_dev_env.py
```

### 开发流程
1. 阅读 API文档/
2. 参考 示例代码/
3. 使用 开发工具/
4. 测试并提交

---

## 目录结构

```
MnMCP_DevResources/
├── README.md                 # 本文件
├── API文档/                  # API文档
│   ├── core_api.md          # 核心模块API
│   ├── protocol_api.md      # 协议模块API
│   └── crypto_api.md        # 加密模块API
├── 开发工具/                 # 开发工具
│   ├── code_generator.py    # 代码生成器
│   ├── debug_helper.py      # 调试助手
│   └── test_template.py     # 测试模板
├── 资源文件/                 # 资源文件
│   ├── block_mappings/      # 方块映射
│   ├── protocol_defs/       # 协议定义
│   └── packet_samples/      # 抓包样本
├── 示例代码/                 # 示例代码
│   ├── plugin_example/      # 插件示例
│   ├── custom_handler/      # 自定义处理器
│   └── extension_demo/      # 扩展示例
└── 测试数据/                 # 测试数据
    ├── test_packets/        # 测试数据包
    └── mock_servers/        # 模拟服务器
```

---

## 贡献指南

1. Fork 主项目
2. 创建特性分支
3. 参考本资源包开发
4. 提交Pull Request

---

## 联系方式

- GitHub: https://github.com/starsailsclover/MnMCP
- QQ群: 1084172731
- 邮箱: SailsHuang@gmail.com
