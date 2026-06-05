# MnMCP 项目重构说明

**重构时间**: 2026-05-30  
**版本**: Phase 6 → Phase 4  
**变更**: MN2MC → MnMCP

---

## 🔄 重构完成

### 目录结构变更

**之前**:
```
MnMCP-Protocol/
└── MN2MC/
    ├── mn2mc/
    │   └── ...
    ├── mn2mc.py
    └── backend.py
```

**之后**:
```
MnMCP-Protocol/
└── MnMCP/
    ├── mnmcp/
    │   └── ...
    ├── mnmcp.py
    └── backend.py
```

### 已完成修改

1. ✅ 目录重命名: `MN2MC` → `MnMCP`
2. ✅ 包名重命名: `mn2mc` → `mnmcp`
3. ✅ 主入口重命名: `mn2mc.py` → `mnmcp.py`
4. ✅ 文档更新: `PHASE4_EXECUTION_PLAN.md`

### 需要继续修改的文件

以下文件中的 `mn2mc` 需要替换为 `mnmcp`:

```bash
# 使用 PowerShell 批量替换
Get-ChildItem -Recurse -Filter "*.py" | ForEach-Object {
    (Get-Content $_.FullName) -replace 'mn2mc', 'mnmcp' | Set-Content $_.FullName
}

Get-ChildItem -Recurse -Filter "*.md" | ForEach-Object {
    (Get-Content $_.FullName) -replace 'MN2MC', 'MnMCP' -replace 'mn2mc', 'mnmcp' | Set-Content $_.FullName
}
```

---

## 🎯 当前状态

**Phase 6**: ✅ 100% 完成
- 三端口架构
- RakNetServer
- MinecraftServer
- DualServer

**Phase 4**: 🔄 准备开始
- 协议桥接核心
- 玩家同步
- 区块转换

---

## 🚀 下一步

**立即执行**:
1. 批量替换所有文件中的 `mn2mc` → `mnmcp`
2. 创建桥接模块 `mnmcp/bridge/`
3. 开始 ProtocolBridge 实现

**文件**: `PHASE4_EXECUTION_PLAN.md`
