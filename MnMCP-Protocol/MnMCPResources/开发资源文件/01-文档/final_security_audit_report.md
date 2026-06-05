# libilink_network.so 静态安全审计报告（最终版）

## 1. 执行摘要
本次审计针对 `libilink_network.so`（迷你世界 1.53.1）开展了**纯静态分析**，目标是梳理 UDP 协议通信链路、加密实现结构及硬编码密钥材料风险。  
审计未进行运行时注入、内存读取、反调试绕过或会话密钥提取。

核心结论如下：
- 已识别完整通信与加解密链路：组包、收发、协议解析、加密/解密均有明确函数落点。
- 现有证据支持协议采用 **ECDH + HKDF + AES-GCM**，并含压缩分支（ZLIB/LZ4）。
- 在 `.rodata` 中发现高风险硬编码公钥材料（PEM/EC 点形态），并确认被 `sub_1011C8`、`sub_92E8C` 引用加载。
- 下游大量 `BLR` 间接调用表明存在函数表/虚表分发，部分目标可恢复，但最终密钥导入调用点仍未完全显式化。

---

## 2. 分析范围与方法

### 2.1 目标范围
- 目标 SO：`E:\TEMP_SHARE\Miniworld_pkg_unpack\迷你世界_1.53.1\lib\arm64-v8a\libilink_network.so`
- 关联输入：前序 Java 层/Native 层多轮脚本输出文件

### 2.2 方法与工具
- 工具：IDA Pro 9.3 + 多个自研 IDAPython 脚本
- 方法：函数枚举、字符串/交叉引用、调用图、常量提取与格式验证、间接调用恢复（BLR）

### 2.3 合规约束
- 仅静态分析
- 未运行程序
- 未做内存读取/Hook/绕过
- 未提取实际会话密钥，未执行流量解密

---

## 3. 主要发现

## 3.1 协议架构与关键链路
基于函数行为、字符串证据与调用关系，识别到以下核心链路：
- `sub_B696C`：请求组包（头部/负载组织）
- `sub_B716C`：发送/接收主流程
- `sub_B3F94`：协议解析与算法字段分支
- `sub_AC6C4`：加密核心
- `sub_ADB14`：解密核心
- `sub_BBDA0`：Socket 准备相关流程

结论：UDP 通信基于自定义封装，包结构与算法选择由协议头字段驱动。

## 3.2 加密机制证据
来自函数命名线索、字符串与包装函数映射结果：
- 命中 `AesGcmEncrypt` / `AesGcmDecrypt` 类证据
- 命中 `Ecdh ... failed`、`HKDF ... failed` 类证据
- 压缩分支出现 ZLIB/LZ4 相关证据

结论：静态证据一致支持 **ECDH 协商 + HKDF 派生 + AES-GCM**，并带可选压缩分支。

## 3.3 硬编码密钥材料证据链（高风险）
在 `.rodata` 发现并验证了以下高价值常量：
- `0x6418BA`（Base64, 240）  
  解码后为 PEM 公钥文本（证据见附录 A）
- `0x641861`（Base64, 88）  
  解码后为 65 字节未压缩 EC 点（`0x04 + 64字节坐标`）
- 关联封装类常量：`0x680058`、`0x67FED0`、`0x67FF94`（Hex）

引用关系：
- `0x6418BA` / `0x641861` -> `sub_1011C8`
- `0x680058` / `0x67FED0` / `0x67FF94` -> `sub_92E8C`

函数内字符串证据：
- `Base64 Decode ecdh pubkey failed!!`
- `Decode ecdsa pubkey failed!!`

结论：已形成“硬编码常量 -> 关键函数加载/复制 -> 解码相关字符串证据”的高置信链路。

## 3.4 间接调用链（BLR）现状
- 下游存在大量 `BLR Xn` 间接调用，符合函数表/虚表分发模式。
- 部分轮次可恢复出目标函数（如 `0x105EE4`、`0x1061B0`、`0x106800` 等）。
- 最新轮次中仍有较多“base address unresolved”，说明二级解引用链未完全闭合。

结论：间接分发机制明确存在；最终密钥导入函数（如显式 OpenSSL 导入点）仍需更深层静态恢复。

---

## 4. 风险评估

### 4.1 风险结论
- **硬编码公钥材料风险：高**
  - 公钥材料以可提取形式存在于 `.rodata`
  - 被关键路径函数直接引用并处理
  - 增加逆向与协议仿真门槛下降风险

### 4.2 影响分析
- 协议原语本身（ECDH/HKDF/AES-GCM）并不弱，但静态密钥资产暴露会降低攻击者分析成本。
- 在供应链/逆向对抗场景下，硬编码材料可被用于协议行为建模与高保真模拟。

---

## 5. 修复建议

1. 移除静态公钥硬编码，改为可信通道动态下发与轮换。  
2. 对密钥加载/导入路径增加完整性保护与反篡改校验。  
3. 提升代码混淆与控制流保护，重点强化函数表/虚表分发路径保护。  
4. 建立密钥/证书轮换机制（版本化、灰度、失效策略）。  
5. 在日志中避免暴露过强语义（如直白解码失败文案），减少逆向线索。

---

## 6. 附录

## A. 硬编码公钥示例（静态证据）
- 地址：`0x6418BA`（Base64，240 字节）  
  解码示例：
  ```text
  -----BEGIN PUBLIC KEY-----
  MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAElsQBff9Ng3kBHy/H+EH4c86qn/iS
  0zRmO0XcMQJdxeATvpBKd0BtdhSdPAvYkB/b/ho5Z4o5wwEJW94vlAFCag==
  -----END PUBLIC KEY-----
  ```

- 地址：`0x641861`（Base64，88 字节）  
  解码后：65 字节未压缩 EC 公钥点（首字节 `0x04`）。

## B. 关键函数列表
- `sub_AC6C4`：加密核心  
- `sub_ADB14`：解密核心  
- `sub_B3F94`：协议解析与算法选择  
- `sub_B696C`：SendRequest 组包  
- `sub_B716C`：网络发送/接收主流程  
- `sub_BBDA0`：Socket 准备流程  
- `sub_1011C8`：公钥加载与解码相关入口  
- `sub_92E8C`：封装公钥材料入口  

## C. 脚本输出清单（主要）
- `libilink_network_static.txt`
- `deeper_analysis.txt`
- `target_callgraph.dot`
- `crypto_network_details.txt`
- `crypto_network_callgraph.dot`
- `crypto_network_details_v2.txt`
- `algorithm_mapping_final.txt`
- `packet_layout_final.txt`
- `wrapper_mapping_final.txt`
- `summary_final.txt`
- `public_key_candidate_blocks.txt`
- `pubkey_deep_static_report.txt`
- `pubkey_low_noise_report.txt`
- `hex_base64_candidates.txt`
- `key_candidates_audit.txt`
- `key_candidates_export.json`
- `key_usage_audit.txt`
- `downstream_crypto_audit.txt`
- `final_audit_evidence.txt`
- `resolved_indirect_calls.txt`
- `final_static_audit_report.md`

---

**声明**：本报告全部结论基于静态证据（字符串、指令、交叉引用、调用关系、常量格式验证）得出，不包含运行时行为验证与密钥实提取。