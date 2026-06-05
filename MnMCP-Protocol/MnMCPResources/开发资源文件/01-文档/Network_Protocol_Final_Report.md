# liblibGameApp.so 网络协议深度分析报告

**版本：** 1.0
**分析环境：** IDA Pro 9.3 (x64), Hex-Rays Decompiler
**目标样本：** C:\Users\PC\Downloads\liblibGameApp.so (170MB)
**分析师：** Annie (高级逆向工程模式)

---

## 1. 样本概况与分析结论
经深度静态分析与 Java-Native 关联映射，确认该游戏样本采用**混合协议架构**：
- **非对称 UDP 协议**：用于心跳、非敏感状态上报，采用基于 C-String 的文本拼接格式。
- **对称 WebSocket SSL 协议**：用于核心业务逻辑（战斗、资源、指令同步），采用二进制流并经过 TLS 加密。

## 2. 网络架构拓扑 (Data Flow)
协议传输链路已完整还原，逻辑流向如下：
1. **[Java 层]** `com.netease.game.NetworkManager.nativeSendRequest(byte[], int)` 触发请求。
2. **[JNI 层]** `Java_org_appplay_lib_CommonNatives_nativeSendRequest` 接收数据并转换指针。
3. **[封装层]** 调用 `sub_3689478`，根据协议号进行字符串模板拼接。
4. **[传输层]** 进入 `make_request (0x36893F8)`，通过底层 `sendto` 系统调用完成外发。

## 3. UDP 协议明文格式还原
通过对 `sub_3689478` 的字符串引用扫描，还原其明文封包模板如下：

| 字段名 | 占位符 | 说明 |
| :--- | :--- | :--- |
| **cmd** | `cmd=%d` | 协议命令 ID，对应 Java 层 `CMD_` 常量 |
| **uid** | `&uid=%s` | 用户唯一标识符 |
| **tk** | `&tk=%s` | 动态验证令牌 (来自 `nativeGetMiniToken`) |
| **data** | `&data=%s` | 业务负载数据 (通常为 Base64 或原始文本) |
| **sign** | `&sign=%s` | 数据签名，用于封包完整性校验 |

**关键特征**：
- 封包长度限制：`0x100` (256 字节)。
- 编码方式：C 风格字符串（Null-terminated）。

## 4. 加密链路分析 (WebSocket/SSL)
在地址 `0x876CD50` 处锁定了核心加密出口：
- **函数名**：`lws_ssl_capable_write`
- **核心库**：集成 `libwebsockets` 库。
- **加密方案**：调用 OpenSSL 的 `SSL_write` 进行传输层加密。
- **明文拦截点**：在该函数的第二个参数寄存器（`X1/A2`）处可获取加密前的原始二进制负载。

## 5. 关键内存地址索引表
为了后续分析，建议关注以下硬编码地址：

| 地址 (RVA) | 函数符号/功能 | 备注 |
| :--- | :--- | :--- |
| `0x36893F8` | `make_request` | UDP 协议最终发送入口 |
| `0x3689478` | `sub_3689478` | **[核心]** 协议字段拼接逻辑 |
| `0x876CD50` | `lws_ssl_capable_write` | WebSocket 加密数据出口 |
| `0x2EC569C` | `nativeGetMiniToken` | 认证令牌生成逻辑 |
| `0x2EC81B8` | `OnLoginResult` | 登录状态机回调入口 |

## 6. 逆向建议
1. **动态 Hook 指引**：若需获取明文，首选 Hook `0x3689478` (UDP) 和 `0x876CD50` (WebSocket)。
2. **Java 字典映射**：已通过脚本完成 306 处协议 ID 的自动标注，可在 IDA `Functions` 窗口中直接搜索 `[Protocol]` 前缀查看相关逻辑。
3. **结构体增强**：已在 IDA 中建立 `GameProtocolPacket` 结构体，建议通过 F5 观察偏移 `0x8` (cmdId) 和 `0x10` (uid) 的读写。

---
*报告生成于 2026年4月15日。分析任务已归档。*
