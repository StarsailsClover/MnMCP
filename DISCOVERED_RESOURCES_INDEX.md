# MnMCP 3 新发现资源索引

**检查日期**: 2026-05-23  
**版本**: 2026-05-23-15  
**位置**: `MnMCPResources/开发资源文件/` 和 `未分类/`

---

## 📁 资源总览

| 类别 | 数量 | 关键价值 |
|------|------|----------|
| 文档 | 11 | **协议规范、加密算法、登录流程** |
| 工具脚本 | 15 | **UDP解码器、解密器、分析工具** |
| 数据文件 | 5 | **Protobuf定义、包样本、登录流** |
| 密钥材料 | 4 | **密钥偏移、RSA公钥、XXTEA上下文** |
| 压缩包 | 5 | **Lua源码、RakNet实现** |
| **总计** | **44** | - |

---

## 📖 一、文档类资源

### 1.1 协议分析文档（高优先级）

| 文档名 | 路径 | 关键内容 | 开发影响 |
|--------|------|----------|----------|
| **udp_package_report.md** | `01-文档/` | **WPKG协议完整规范**、AES-128-GCM、ECDH+HKDF | **必须实现WPKG协议栈** |
| **20-Phase2-协议逆向分析报告.md** | `01-文档/` | 自研引擎架构、mmtls协议、ilink-network v2.3.2.f3 | 需参考微信Mars框架 |
| **旧版登录说明（可能通用）.md** | `未分类/` | **WebSocket RPC格式**、多分支登录流程 | **认证模块需重构** |
| **liblibGameApp_reverse_engineering_summary.md** | `01-文档/` | DLL逆向总结 | 架构参考 |
| **liblibGameApp_current_findings_summary_report.md** | `01-文档/` | 当前发现总结 | 快速参考 |
| **COMPREHENSIVE_FINAL_REPORT.md** | `01-文档/` | 综合最终报告 | 全景参考 |

### 1.2 网络协议文档

| 文档名 | 关键信息 |
|--------|----------|
| **Network_Protocol_Final_Report.md** | 网络协议最终报告 |
| **Protobuf_Protocol_Final_Report.md** | Protobuf协议规范 |
| **final_security_audit_report.md** | 安全审计报告 |
| **GRAND_MASTER_DECREE_FINAL.md** | 总体规范 |
| **MEMORY.md** | 内存分析笔记 |

---

## 🛠️ 二、工具脚本（可直接复用/适配）

### 2.1 核心工具（必须复用）

| 脚本名 | 路径 | 功能 | 复用方式 |
|--------|------|------|----------|
| **liblibGameApp_udp_decoder.py** | `02-工具脚本/` | **RakNet UDP包完整解码** | 适配到`mn2mc/protocol/wpkg/` |
| **Universal_GameApp_Decryptor.py** | `02-工具脚本/` | **TCP/UDP统一解密**、msgpack解析 | 适配到`mn2mc/crypto/` |
| **miniworld_signature_analyzer.py** | `02-工具脚本/` | 签名分析 | 参考签名计算 |
| **memory_signature_scanner.py** | `02-工具脚本/` | 内存签名扫描 | 调试工具 |
| **analyze_handshake.py** | `02-工具脚本/` | 握手分析 | ECDH参考 |

### 2.2 数据提取工具

| 脚本名 | 功能 | 输出 |
|--------|------|------|
| `extract_block_item_ids.py` | 方块/物品ID提取 | 映射数据 |
| `extract_dex.py` | DEX提取 | 反编译源码 |
| `extract_pkg_data.py` | PKG数据提取 | 资源文件 |
| `extract_pkg_zip.py` | PKG解压 | ZIP内容 |
| `parse_pkg_format.py` | PKG格式解析 | 结构化数据 |
| `parse_go_mapping.py` | Go映射解析 | 数据映射 |
| `pkg_unpacker.py` | PKG解包器 | 通用解包 |

### 2.3 其他工具

| 脚本名 | 功能 |
|--------|------|
| `ace_bypass.py` | ACE反作弊绕过（研究用） |
| `analyze_global_apk.py` | 全球APK分析 |
| `setup_geyser.py` | Geyser设置 |
| `frida_blockid_hook.js` | Frida方块ID Hook |

---

## 📊 三、数据文件（测试/验证用）

| 文件名 | 路径 | 内容 | 用途 |
|--------|------|------|------|
| **udp_package.txt** | `03-数据文件/` | **UDP包原始样本** | **WPKG协议测试** |
| **Extracted_Proto_Definitions.txt** | `03-数据文件/` | **Protobuf定义** | 协议解析实现 |
| **login_flow_export.json** | `03-数据文件/` | 登录流程JSON | 认证流程参考 |
| **miniworld_strings.json** | `03-数据文件/` | 字符串表 | 符号识别 |
| **filter_1.pcapng** | `03-数据文件/` | 抓包文件 | 流量分析 |
| **all_pe_images.json** | `03-数据文件/` | PE镜像信息 | 逆向参考 |

---

## 🔐 四、密钥材料（高敏感）

| 文件名 | 路径 | 内容 | 说明 |
|--------|------|------|------|
| **found_keys.json** | `04-密钥材料/` | 内存中提取的密钥偏移 | 调试参考，**不要硬编码** |
| **xxtea_contexts.json** | `04-密钥材料/` | XXTEA使用场景 | 确认XXTEA仅用于JSON序列化 |
| **rsa_public_keys.json** | `04-密钥材料/` | RSA公钥 | 初始握手验证 |
| **ssl_keys.log** | `04-密钥材料/` | SSL密钥日志 | TLS分析 |

### XXTEA使用场景确认

```json
// 来自xxtea_contexts.json
{"serializeFlag":"json","compressFlag":"none","encrypFlag":"xxtea_64","version":"0"}
```

**结论**: XXTEA仅用于特定JSON数据的序列化，**不是主协议加密**。

---

## 📦 五、压缩包资源

| 文件名 | 路径 | 内容推测 | 优先级 |
|--------|------|----------|--------|
| **Miniworld_RAINBOW_TRUE_SOURCE.rar** | `未分类/` | **迷你世界源码**（Rainbow引擎） | **极高** |
| **ljd-miniworld-alg.zip** | `未分类/` | LuaJIT反编译算法 | 高 |
| **ljd-miniworld.zip** | `未分类/` | LuaJIT反编译结果 | 高 |
| **raknet_miniworld.rar** | `未分类/` | **RakNet协议实现** | **极高** |
| **mihomo-windows-amd64-...** | `未分类/` | Mihomo代理工具 | 中 |

### 建议解压检查

```bash
# 需要检查的内容
1. Miniworld_RAINBOW_TRUE_SOURCE.rar - 寻找网络通信相关源码
2. raknet_miniworld.rar - RakNet协议实现细节
3. ljd-miniworld.zip - Lua脚本中的网络逻辑
```

---

## 📝 六、其他文件

| 文件名 | 路径 | 内容 | 价值 |
|--------|------|------|------|
| **网络工程师对话线索.txt** | `未分类/` | 技术人员对话记录 | UDP 8081加密确认 |
| **serverrentroom_deco.lua** | `未分类/` | Lua装饰脚本 | 房间逻辑参考 |
| **scriptapi.csv** | `未分类/` | API清单 | 功能对照 |
| **mitmproxy_console.txt** | `未分类/` | MITM代理日志 | 流量样本 |
| **rainbow_truth_unpacker.py** | `未分类/` | Rainbow解包器 | 资源提取 |

---

## 🎯 对Phase 1的影响

### 高优先级更新（必须实现）

1. **WPKG协议栈** (P0)
   - 来源: `udp_package_report.md`
   - 实现: `mn2mc/protocol/wpkg/`
   - 复用: `liblibGameApp_udp_decoder.py`

2. **AES-128-GCM模块** (P0)
   - 来源: `udp_package_report.md`
   - 实现: `mn2mc/crypto/aes_gcm.py`
   - 错误: 之前以为是AES-CBC

3. **ECDH+HKDF模块** (P0)
   - 来源: `udp_package_report.md`
   - 实现: `mn2mc/crypto/ecdh.py`, `hkdf.py`

4. **WebSocket RPC认证** (P1)
   - 来源: `旧版登录说明.md`
   - 实现: 重构`mn2mc/auth/`

### 中优先级（Phase 2准备）

5. **RakNet协议层**
   - 来源: `liblibGameApp_udp_decoder.py`
   - 参考: `raknet_miniworld.rar`

6. **Msgpack解析**
   - 来源: `Universal_GameApp_Decryptor.py`
   - 用于TCP 19701端口

---

## 📋 复用计划

### 工具脚本复用方案

```
开发资源文件/02-工具脚本/  →  MN2MC/mn2mc/utils/adapters/

liblibGameApp_udp_decoder.py → adapters/udp_decoder.py (适配)
Universal_GameApp_Decryptor.py → adapters/gameapp_decryptor.py (适配)
miniworld_signature_analyzer.py → crypto/signature.py (提取签名算法)
analyze_handshake.py → crypto/handshake.py (提取ECDH逻辑)
```

### 数据文件使用

```
开发资源文件/03-数据文件/  →  MN2MC/tests/fixtures/

udp_package.txt → tests/fixtures/wpkg_samples/ (测试样本)
Extracted_Proto_Definitions.txt → protocol/proto/ (Protobuf定义)
login_flow_export.json → tests/fixtures/login_flow.json (测试数据)
```

### 密钥材料管理

```
开发资源文件/04-密钥材料/  →  仅参考，不提交Git

found_keys.json → 密钥位置参考，不硬编码
xxtea_contexts.json → 确认XXTEA使用场景
```

---

## ✅ 检查清单

Phase 1实施前确认:

- [ ] 已阅读`udp_package_report.md`（WPKG协议）
- [ ] 已阅读`旧版登录说明.md`（登录流程）
- [ ] 已复用`liblibGameApp_udp_decoder.py`
- [ ] 已复用`Universal_GameApp_Decryptor.py`
- [ ] 已提取`found_keys.json`中的密钥偏移（仅参考）
- [ ] 已确认XXTEA使用场景
- [ ] 已解压`raknet_miniworld.rar`检查
- [ ] 已解压`Miniworld_RAINBOW_TRUE_SOURCE.rar`检查

---

## 📚 快速参考

### WPKG协议速查

```python
# Header (16 bytes)
magic       = 2 bytes  # 'KG' = 0x4B47
cmd_id      = 2 bytes
seq_no      = 4 bytes
body_len    = 4 bytes
encrypt_algo = 1 byte   # 0=HybridECDH, 1=AesGcm
compress_algo = 1 byte  # 0=none, 1/4=zlib, 2=lz4
compress_ver = 1 byte
flags       = 1 byte

# Nonce + Ciphertext + Tag
nonce       = 12 bytes
ciphertext  = N bytes
tag         = 16 bytes
```

### 加密算法速查

| 场景 | 算法 | 密钥来源 |
|------|------|----------|
| WPKG数据包 | AES-128-GCM | ECDH+HKDF派生 |
| JSON序列化 | XXTEA | 配置密钥 |
| 初始握手 | ECDH | 临时密钥对 |
| 密钥派生 | HKDF-SHA256 | shared_secret → 48B material |

---

**更新时间**: 2026-05-23 15:30  
**版本**: 2026-05-23-15
