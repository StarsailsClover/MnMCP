# UDP 包加解密逻辑提炼报告（基于 `E:\TEMP_SHARE\udp_package.txt`）

## 1. 总体结论

- `libilink_network.so` 属于 ilink-network（ARM64）实现，网络框架与 Mars/mmtls 体系相关。
- `libilink_network.so 是腾讯 ilink-network v2.3.2.f3 的 ARM64 编译产物，基于微信 Mars 网络框架，底层使用 mmtls
    协议（微信自研 TLS-like 协议）`****注：此为原文****
- UDP 安全通道存在两类模式：
  - `kIlinkSession (id=1)`：`ECDH + HKDF -> AES-128-GCM`，用于已建立会话后的数据包。
  - `kIlinkHybridEcdh (id=0)`：一次性 Hybrid-ECDH 握手加密，用于无现成 Session 的建连场景。
- 当前文档主结论：协议并非 AES-CBC，而是 **AES-128-GCM + 动态密钥派生**。

## 2. 密钥生成与使用链路

1. ECDH 握手阶段  
   - 客户端生成临时 EC 密钥对。  
   - 服务端持有静态 ECDH 公钥（文档提到 `mmtls_g_ecdh_key_0/1`）。  
   - 计算共享秘密 `shared_secret`（约 32B）。
2. HKDF 派生阶段  
   - `HKDF_Extract(salt=0, IKM=shared_secret)` 得到 PRK。  
   - `HKDF_Expand(..., length=48)` 得到会话材料 48B。  
   - 切分（文档给出的候选）：
     - `aes_key`：`[0:16]`（16B）
     - `nonce_base`：`[16:28]`（12B）
     - 其余保留/填充：`[28:48]`
3. Session 持久化  
   - 结果保存到会话对象（App/Device Session），发送时按会话取 `aes_key + nonce`。
4. 加解密执行  
   - 加密：`AesGcmEncrypt`（wrapper 链）  
   - 解密：`AesGcmDecrypt`（wrapper 链）  
   - 参数语义：`key=16B, nonce=12B, aad=header, plaintext/ciphertext body`，并带 `16B GCM tag`。

## 3. UDP/WPKG 包结构（文档中的候选还原）

> 以下为文档给出的结构化推断：

```text
offset  len  field
0       2    Magic/Version
2       2    CmdID
4       4    SeqNo
8       4    BodyLen
12      1    EncryptAlgo (0=HybridEcdh, 1=AesGcm)
13      1    CompressAlgo (0=none, 1/4=zlib, 2=lz4)
14      1    CompressVersion
15      1    HeaderEnd/Flags
16      12   Nonce (GCM IV, 96-bit)
28      N    Ciphertext
28+N    16   GCM Tag
```

补充说明（文档原意）：

- 在 `HybridEcdh` 路径下，`16~28` 区域可能承载临时公钥而非普通 nonce（需按分支确认）。

## 4. 解包逻辑（文档伪代码要点）

- 解析头字段（magic/cmd/seq/body_len/enc_algo/comp_algo）。
- 提取 `nonce(12B)`、`ciphertext`、`tag(16B)`。
- 从 Session 取 `aes_key`。
- `AAD = header(通常前16字节)`。
- 执行 `AES-GCM decrypt_and_verify`。
- 再按 `comp_algo` 解压（none/zlib/lz4）。
- 最后解析业务体（如 protobuf）。

## 5. 为什么此前 AES-CBC 方案失败

文档给出的原因可归纳为：

- 包结构理解错误（真实是 WPKG Header + GCM nonce/tag 体系，不是 CBC 常见布局）。
- 加密模式错误（实际是 GCM，不是 CBC）。
- 密钥来源错误（密钥是 ECDH+HKDF 动态派生，不是固定静态 AES key）。
- 头部字段被误当作 protobuf/tag 数据。

## 6. 下一步验证重点（静态/离线）

- 锁定并确认服务端静态 ECDH 公钥来源（`mmtls_g_ecdh_key_0/1` 相关字符串与引用点）。
- 验证文档中 Base64 公钥样本是否为真实握手公钥材料（文档示例解码长度约 57B，需结合曲线与编码格式判断）。
- 分支化确认 `kIlinkSession` 与 `kIlinkHybridEcdh` 在 `offset 16~28` 区域语义是否一致。
