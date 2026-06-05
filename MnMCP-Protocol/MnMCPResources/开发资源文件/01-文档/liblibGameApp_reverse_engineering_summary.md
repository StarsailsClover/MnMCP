# liblibGameApp.so 逆向工程完整汇总

> 目标文件: `liblibGameApp.so` (Android ARM64 ELF)
> 逆向工具: IDA Pro 9.3 + Hex-Rays
> 抓包验证: mini.pcapng + scapy + 自研 RakNet 解码器
> 总分析脚本: 87 个 IDA Python 脚本，63 份分析报告

---

## 一、总体架构

### 1.1 网络协议栈

```
┌──────────────────────────────────────────────────────────┐
│                    业务逻辑层 (Business Logic)             │
│  MpGameSurviveNetHandler / MpGameSurviveNetHandler_ver1  │
│  GameNetClientMsgHandler / GameNetHostMsgHandler          │
├──────────────────────────────────────────────────────────┤
│                   通知/分发层 (Notify/Dispatch)            │
│  m_notifySendToHost(this+40)                              │
│  m_notifySendBroadcast(this+56)                           │
│  m_notifySendToClient → sub_639424C                       │
│  m_notifySendToClientMulti → sub_7501F30                  │
├──────────────────────────────────────────────────────────┤
│                连接/传输绑定层 (Transport Binding)          │
│  sub_2F402E4: m_notifySendToHost.IsValid() → callback     │
│  sub_2F4088C: 实际发送触发                                 │
│  sub_2F40954: 发送后清理                                   │
├──────────────────────────────────────────────────────────┤
│                   RakPeer 发送层                           │
│  RakPeer::Send (sub_79BA7BC) — vtable slot 23 (+0xB8)     │
│  sub_79BA0E4: 远程系统查找                                 │
│  sub_79BA484: 内部发送（排队 BufferedCommand）              │
├──────────────────────────────────────────────────────────┤
│                   可靠性层 (Reliability Layer)             │
│  sub_79AFCE8: RunUpdateCycle (定时刷新)                    │
│  sub_79B0BF4: 可靠性层发送                                 │
│  sub_79B329C: 可靠包构建器                                 │
│  处理: 重传、排序、分片                                     │
├──────────────────────────────────────────────────────────┤
│                   Socket 发送层                            │
│  RNS2_Linux::SendTo (sub_79B4B20)                         │
│  sub_79B3ABC: sendto 包装器                                │
│  sendto(fd, buf, len, 0, sockaddr_in, 16)                 │
└──────────────────────────────────────────────────────────┘
```

### 1.2 游戏层不直接调用 RakPeer::Send

游戏层通过 **委托/通知模式** (Delegate/Notify) 间接调用 RakPeer::Send：

- 业务 handler 构造序列化消息后调用 `sub_63AB1F4`（统一分发核心）
- 分发核心根据目标选择 `sendToHost`(this+40) / `sendBroadcast`(this+56) / `sendToClient`
- 委托链最终通过 C++ vtable 虚调用到达 `RakPeer::Send`
- RakPeer::Send 在 IDA 中显示 0 个直接 caller（因为全部是间接调用）

---

## 二、线格式 (Wire Format)

### 2.1 RakNet 数据报层

```
┌─────────────────── UDP Payload ───────────────────┐
│                                                    │
│  [1 字节] 报头标志位                                │
│    bit 7: isValid (1=DATA, 区分 ACK/NACK)          │
│    bit 6: isACK                                    │
│    bit 5: isNACK                                   │
│    bit 4: packetPair                               │
│    bit 3: continuousSend                           │
│    bit 2: needsBAndAS                              │
│                                                    │
│  --- 若 isACK=1 ---                                │
│  [1B] hasBAndAS                                    │
│  [2B] ack range count (LE)                         │
│  [N×] ack ranges                                   │
│                                                    │
│  --- 若 isNACK=1 ---                               │
│  (同 ACK 格式)                                     │
│                                                    │
│  --- 若 DATA 包 ---                                │
│  [3B] datagram sequence number (LE)                │
│  [N×] 消息列表                                      │
│                                                    │
└────────────────────────────────────────────────────┘
```

### 2.2 RakNet 消息层

```
┌────────────── 单条消息 ──────────────┐
│                                       │
│  [3 bits] reliability type            │
│    0 = UNRELIABLE                     │
│    2 = RELIABLE                       │
│    3 = RELIABLE_ORDERED               │
│    4 = RELIABLE_SEQUENCED             │
│    6 = UNRELIABLE_SEQUENCED           │
│                                       │
│  [1 bit] has_split_packet             │
│  [4 bits] padding                     │
│                                       │
│  [2B] data bit length (BE)            │
│                                       │
│  (若 reliability ≥ 2: RELIABLE)       │
│  [3B] reliable_message_number (LE)    │
│                                       │
│  (若 SEQUENCED)                       │
│  [3B] sequencing_index (LE)           │
│                                       │
│  (若 ORDERED 或 SEQUENCED)            │
│  [3B] ordering_index (LE)             │
│  [1B] ordering_channel                │
│                                       │
│  (若 has_split_packet=1)              │
│  [4B] split_packet_count (BE)         │
│  [2B] split_packet_id (BE)           │
│  [4B] split_packet_index (BE)         │
│                                       │
│  [N bytes] message data               │
│    第1字节 = message_id               │
│    后续 = payload                     │
│                                       │
└───────────────────────────────────────┘
```

### 2.3 应用层封装

```
┌────────── 应用层 Payload ──────────────┐
│                                         │
│  [1B] message_id                        │
│    0x00~0x85: RakNet 内部消息            │
│    0x86+: 用户自定义消息 (ID_USER_PACKET_ENUM 起) │
│                                         │
│  --- 用户自定义消息格式 ---              │
│  [2B] cmdid / 协议码 (LE)               │
│    范围: 0x7D3 ~ 0x7F3 (2003~2035)     │
│                                         │
│  [varint] protobuf 长度                  │
│  [N bytes] protobuf 编码的业务消息       │
│    外层: PB_PACKDATA_CLIENT 或 tagPackData│
│    内层: 具体业务 protobuf              │
│                                         │
└─────────────────────────────────────────┘
```

### 2.4 PB_PACKDATA_CLIENT 字段定义

| Protobuf Field | 类型 | 名称 | 说明 |
|---|---|---|---|
| field 1 | varint | uin | 用户唯一标识 |
| field 2 | bytes (length-delimited) | dataContent | 内层 protobuf 数据 |
| field 3 | varint | targetUin | 目标用户 UIN (可选) |
| field 4 | varint | protoId / msgCode | 协议号 / 消息码 |

### 2.5 tagPackData 字段定义 (C 结构体)

`tagPackData` 是 `PB_PACKDATA_CLIENT` 的 C 结构体等价物，用于 Host 侧：

```c
struct tagPackData {
    uint32_t uin;           // 用户 UIN
    void*    dataContent;   // 数据内容指针
    uint32_t dataLen;       // 数据长度
    uint32_t targetUin;     // 目标 UIN
    uint32_t protoId;       // 协议号
};
```

序列化: `sub_300D878`
反序列化: `sub_300DCCC`

---

## 三、协议码主表

### 3.1 已确认协议码 (17 个)

| 协议码 | 十进制 | 业务消息名 | 桥函数 | 置信度 |
|---|---|---|---|---|
| 0x7D3 | 2003 | (未解析) | sub_4451C54, sub_4455A50 | 低 |
| 0x7D8 | 2008 | (未解析) | sub_44516DC, sub_4451C54 | 低 |
| 0x7D9 | 2009 | (未解析) | sub_44516DC, sub_4451C54 | 低 |
| 0x7DB | 2011 | (未解析) | sub_4451C54, sub_44531B8, sub_44536E4 | 低 |
| 0x7DC | 2012 | (未解析) | sub_4451C54, sub_4454094 | 低 |
| 0x7DD | 2013 | (未解析) | sub_4451C54, sub_445451C | 低 |
| 0x7DE | 2014 | (未解析) | sub_4451C54, sub_4454A4C | 低 |
| **0x7E2** | **2018** | **cheat_move_protocal, switch_move_protocal** | sub_4451C54, sub_44558B8 | **中** |
| 0x7E7 | 2023 | (未解析) | sub_4451C54, sub_4454E08 | 低 |
| 0x7E8 | 2024 | (未解析) | sub_4451C54, sub_44550E0 | 低 |
| 0x7E9 | 2025 | (未解析) | sub_4451C54, sub_44553BC | 低 |
| 0x7EA | 2026 | (未解析) | sub_4451C54, sub_4455CEC, sub_4455F94 | 低 |
| 0x7ED | 2029 | (未解析) | sub_4451C54, sub_4456974 | 低 |
| 0x7EF | 2031 | (未解析) | sub_4451C54, sub_44572B0, sub_4457554 | 低 |
| **0x7F0** | **2032** | **switch_revive** (revive_type, revive_mode, revive_delay, dead_time, cheat_type) | sub_4451C54, sub_44578E8 | **中** |
| 0x7F2 | 2034 | PB_ROLE_ENTER_WORLD_CH (enter-world) | sub_2F7B8AC, sub_303FE90, sub_3055718 | 高 |
| **0x7F3** | **2035** | **switch_rotation** (pitch, yaw) | sub_4451C54, sub_445854C | **中** |

### 3.2 协议码分发路径

所有协议码共用统一的桥分发函数 `sub_4451C54`，调用模式为：
```c
sub_4443CB8(&byte_AD465D0, packed_data);   // 构建打包数据
sub_4451C54(context, packed_data, 0x7XX);   // 分发到桥，第3参数为协议码
```

---

## 四、Handler 类体系

### 4.1 四个核心 Handler 类 (RTTI 恢复)

| 类名 | 消息类型 | 方向 |
|---|---|---|
| `MpGameSurviveNetHandler` | PB_PACKDATA_CLIENT / tagPackData | 主要生存玩法 handler |
| `MpGameSurviveNetHandler_ver1` | PB_PACKDATA_CLIENT / tagPackData | v1 版本兼容 |
| `GameNetClientMsgHandler` | PB_PACKDATA_CLIENT | 客户端消息处理 |
| `GameNetHostMsgHandler` | tagPackData | 主机消息处理 (uin 参数) |

### 4.2 Handler 注册绑定

- **Client 侧绑定锚点**: `sub_62B2564` — 注册 `GameNetClientMsgHandler` 回调
- **Host 侧绑定锚点**: `sub_62B2B80` — 注册 `GameNetHostMsgHandler` 回调
- **Client 类型锚点**: `sub_60160DC` — 65 项
- **Host 类型锚点**: `sub_6015FC8` — 65 项

### 4.3 Handler 签名差异

```
// Client 侧: 接收 PB_PACKDATA_CLIENT 引用
void handler(const PB_PACKDATA_CLIENT& packData);

// Host 侧: 接收 uin + tagPackData
void handler(uint32_t uin, const tagPackData& packData);
// 或
void handler(int uin, const tagPackData& packData);
```

### 4.4 关键 Handler 函数

| 函数地址 | 名称 | 说明 |
|---|---|---|
| `sub_2F7B8AC` | handleRoleEnterWorld2Client | 角色进入世界 (Client 侧) |
| `sub_2FF8BF4` | handleRoleEnterWorld2Host | 角色进入世界 (Host 侧)，含 uin/world 字段 |
| `sub_303FE90` | enterWorld 绑定 | enter-world 的绑定注册 |
| `sub_3055718` | enterWorld 回调链 | enter-world 的回调路径 |
| `sub_3041AF0` | tagPackData 处理 A | tagPackData 消费函数 |
| `sub_3041BA0` | PB_PACKDATA_CLIENT 处理 A | PB_PACKDATA_CLIENT 消费函数 |
| `sub_3041C54` | tagPackData 处理 B | tagPackData 消费函数 |
| `sub_3041D08` | PB_PACKDATA_CLIENT 处理 B | PB_PACKDATA_CLIENT 消费函数 |
| `sub_3056580` | tagPackData 处理 C | tagPackData 消费函数 |

---

## 五、RakNet 内部结构

### 5.1 RakPeer 虚函数表

- 虚表地址: `0xA7EBE38`
- 虚表大小: 93 个 slot
- Send 函数: slot 23 (偏移 +0xB8 / +184)
- Send 实现: `sub_79BA7BC`
- 内部发送: `sub_79BA484`

### 5.2 BufferedCommand 结构 (136 字节)

```
偏移    大小    字段
0x00    8B      next 指针 (链表)
0x08    8B      data 指针
0x10    4B      numberOfBitsToSend
0x14    1B      priority
0x15    1B      reliability
0x16    1B      orderingChannel
0x18    20B     address (SystemAddress)
0x2C    4B      connectionMode
0x30    8B      receipt
...
0x88    结束 (136 字节)
```

### 5.3 SystemAddress 结构 (20 字节)

```
偏移    大小    字段
0x00    2B      address family (AF_INET=2)
0x02    2B      port (大端序)
0x04    4B      IPv4 address (网络字节序)
0x08    8B      padding
0x10    2B      debugPort
0x12    2B      systemIndex
```

### 5.4 RakNetGUID 结构 (10 字节)

```
偏移    大小    字段
0x00    8B      GUID (uint64)
0x08    2B      systemIndex
```

### 5.5 RemoteSystem 结构 (7136 字节)

```
偏移      字段
+0x04     SystemAddress (20B)
+0x1BC0   GUID (RakNetGUID, 10B) [偏移 +7104]
+0x1BE8   某个状态字段 [偏移 +7144]
```

每个 RemoteSystem 条目: 7136 字节

### 5.6 RakNet 消息 ID 完整映射 (0x00 ~ 0x86+)

| 范围 | 类别 |
|---|---|
| 0x00~0x04 | 连接管理 (PING/PONG/DETECT_LOST) |
| 0x05~0x08 | 连接握手 (OPEN_CONNECTION_REQUEST/REPLY 1&2) |
| 0x09~0x1E | 连接状态 (REQUEST/ACCEPTED/REJECTED/LOST 等) |
| 0x1F~0x21 | 远程通知 |
| 0x22~0x5C | 插件消息 (FileList/Replica/RakVoice/NAT/SQLite 等) |
| 0x86+ | 用户自定义消息 (ID_USER_PACKET_ENUM 起) |

---

## 六、分发核心路径

### 6.1 发送前检查

```
sub_63AB000 (send pre-check / proto lookup)
  ├─ sub_785F550: 协议描述符访问器 (检查 flags)
  ├─ sub_2ED9408: 序列化 (实际是 std::string assign)
  └─ 分发到:
     ├─ sub_63AB1F4(this+40, packet): sendToHost
     ├─ sub_63AB1F4(this+56, packet): sendBroadcast
     └─ sub_639424C: sendToClient
```

### 6.2 sendToHost 回调实现

```
sub_2F40A58 (sendToHost 实际实现)
  ├─ 遍历 16 字节 slot 数组
  ├─ 检查优先级阈值
  └─ 分发到:
     ├─ sub_2F40CB4
     └─ sub_2F40E84
         └─ (虚调用) RakPeer::Send
```

### 6.3 RakPeer::Send 内部流程

```
RakPeer::Send (sub_79BA7BC)
  ├─ 验证 BitStream
  ├─ 检查连接状态
  ├─ sub_79BA0E4: 远程系统查找
  │   ├─ sub_79BBE28: GetRemoteSystemFromAddress
  │   └─ sub_79BBFD0: GetRemoteSystemFromGUID
  └─ sub_79BA484: 内部发送 (入队 BufferedCommand)
```

### 6.4 刷新到线路

```
sub_79AFCE8: RunUpdateCycle (定时调用)
  ├─ 从 BufferedCommand 队列取出待发包
  ├─ sub_79B0BF4: 可靠性层发送
  │   └─ sub_79B329C: 可靠包构建器
  │       ├─ 添加序列号
  │       ├─ 添加排序索引
  │       └─ 处理分片 (split packet)
  └─ RNS2_Linux::SendTo (sub_79B4B20)
      └─ sub_79B3ABC → sendto(fd, buf, len, 0, &addr, 16)
```

---

## 七、桥分发系统 (Bridge Dispatch)

### 7.1 桥核心函数

| 函数 | 作用 |
|---|---|
| `sub_4451C54` | 通用桥分发核心，接收 (context, data, protocol_code) |
| `sub_4443CB8` | 打包数据构建器 |
| `sub_4443D9C` | 打包数据构建器变体 |
| `sub_44558B8` | 0x7E2 协议调用者 |
| `sub_44578E8` | 0x7F0 协议调用者 |
| `sub_445854C` | 0x7F3 协议调用者 |

### 7.2 状态管理 (ctx+0x620)

- Host 对象偏移 +0x620 存储目标状态指针
- `sub_62E4680`: rakpeerInterface 访问器
- 多个写入器函数在初始化阶段设置此指针

---

## 八、序列化路径

### 8.1 发送方向 (序列化)

```
业务逻辑
  └─ 构造 PB_DYNAMIC_PROTO_CH / PB_ROLE_ENTER_WORLD_CH 消息
      └─ protobuf SerializeToString
          └─ 构建 48 字节发送描述符: {flags, proto_id, data_ptr, ...}
              └─ 包装为 PB_PACKDATA_CLIENT
                  └─ tagPackData::serialize (sub_300D878)
                      └─ 写入 BitStream
                          └─ RakPeer::Send
```

### 8.2 接收方向 (反序列化)

```
RakPeer::Receive
  └─ 解析 RakNet reliability 头部
      └─ 提取 message data
          └─ 第一字节 = message_id
              └─ 若 ≥ 0x86: 用户消息
                  └─ 读取 cmdid (2B LE)
                      └─ tagPackData::deserialize (sub_300DCCC)
                          └─ protobuf 解码 PB_PACKDATA_CLIENT
                              └─ 分发到对应 Handler
```

---

## 九、pcap 抓包验证

### 9.1 验证环境

- 抓包文件: `mini.pcapng` (20237 总包)
- 解码工具: `liblibGameApp_udp_decoder.py` + `pcap_raknet_scan.py`

### 9.2 流量统计

| 流 | 包数 | 字节数 | 说明 |
|---|---|---|---|
| 192.168.1.7:60009 ↔ 129.211.227.69:60021 | 260 | ~6176 | RakNet 游戏连接 A |
| 192.168.1.7:60009 ↔ 222.95.9.122:51001 | 258 | ~6281 | RakNet 游戏连接 B |
| 192.168.1.7:56437 → 58.212.179.76:8081 | 10 | ~3120 | 疑似加密流量 |
| (其他 QUIC/DNS/mDNS) | ~340 | — | 非游戏流量 |

### 9.3 解码结果

- RakNet 候选包: **528**
- 成功解码: **528 (100%)**
- 解码失败: **0**
- 含应用层 payload: **9** (全部为握手阶段的 offline 消息误识别)

### 9.4 已观测的 RakNet 消息类型

| 消息 ID | 名称 | 数量 | 说明 |
|---|---|---|---|
| 0x00 | ID_CONNECTED_PING | ~200 | 心跳请求 |
| 0x03 | ID_CONNECTED_PONG | ~200 | 心跳响应 |
| 0x05 | ID_OPEN_CONNECTION_REQUEST_1 | 2 | 握手第1步 |
| 0x06 | ID_OPEN_CONNECTION_REPLY_1 | 2 | 握手第2步 |
| 0x07 | ID_OPEN_CONNECTION_REQUEST_2 | 2 | 握手第3步 |
| 0x08 | ID_OPEN_CONNECTION_REPLY_2 | 2 | 握手第4步 |
| 0x09 | ID_CONNECTION_REQUEST | 2 | 连接请求 |
| 0x10 | ID_CONNECTION_REQUEST_ACCEPTED | 2 | 连接接受 |
| 0x13 | ID_NEW_INCOMING_CONNECTION | 4 | 新入连接 |
| 0x5C | ID_SQLLITE_LOGGER | 2 | 日志消息 |
| ACK | — | ~80 | 确认包 |
| NACK | — | ~10 | 否认包 |

### 9.5 连接建立序列 (验证正确)

```
Client → Server:  0x05 OPEN_CONNECTION_REQUEST_1     (1464 bytes, 含 RakNet magic)
Server → Client:  0x06 OPEN_CONNECTION_REPLY_1       (28 bytes)
Client → Server:  0x07 OPEN_CONNECTION_REQUEST_2     (34 bytes)
Server → Client:  0x08 OPEN_CONNECTION_REPLY_2       (35 bytes)
------- 以上为 offline 握手，以下为 online 连接 -------
Client → Server:  0x09 CONNECTION_REQUEST            (18 bytes, RELIABLE)
Server → Client:  0x10 CONNECTION_REQUEST_ACCEPTED   (96 bytes, RELIABLE_ORDERED)
Client → Server:  0x13 NEW_INCOMING_CONNECTION       (94 bytes, RELIABLE_ORDERED)
Client → Server:  0x00 CONNECTED_PING               (9 bytes, UNRELIABLE)
Server → Client:  0x03 CONNECTED_PONG               (17 bytes, UNRELIABLE)
... (心跳保活循环)
```

### 9.6 RakNet Magic 签名

offline 握手包前 16 字节固定为:
```
00 FF FF 00 FE FE FE FE FD FD FD FD 12 34 56 78
```

### 9.7 验证结论

| 验证项 | 结果 |
|---|---|
| RakNet 报头解码 (DATA/ACK/NACK) | ✅ 正确 |
| Reliability 层 (UNRELIABLE/RELIABLE/RELIABLE_ORDERED) | ✅ 正确 |
| 消息 ID 映射 (100+ 种) | ✅ 正确 |
| Datagram sequence number | ✅ 递增正确 |
| Reliable message number | ✅ 递增正确 |
| Ordering index | ✅ 正确 |
| 连接建立 4-way handshake | ✅ 完整 |
| 业务数据包解码 | ⚠️ 未验证 (pcap 中无业务交互数据) |

### 9.8 待验证项

当前 pcap 仅包含连接建立阶段和心跳保活，**没有实际业务交互数据**。需要更长的抓包（进入游戏对局后的流量）来验证：
- cmdid 提取是否正确
- PB_PACKDATA_CLIENT protobuf 解码是否正确
- 协议码 0x7D3~0x7F3 是否出现在真实流量中

### 9.9 8081 端口流量

`192.168.1.7:56437 → 58.212.179.76:8081` 和 `→ 114.222.112.81:8081` 的流量：
- 数据高熵（看起来随机），可能已加密
- 解码器可以解析但 ACK range 值异常大（33610、50429），说明不是标准 RakNet
- 可能是另一种协议或加密后的 RakNet

---

## 十、工具产物清单

### 10.1 解码器

| 文件 | 说明 |
|---|---|
| `liblibGameApp_udp_decoder.py` | RakNet UDP 完整解码器 (~700行)，支持 `--protobuf`/`--packdata`/`--command`/`--address` 模式 |
| `pcap_raknet_scan.py` | pcap 批量扫描器，基于 scapy 提取 UDP 并调用解码器 |

### 10.2 IDA 分析脚本 (按阶段分类)

**阶段 1-3: 基础探索** (23 个脚本)
- `liblibGameApp_packet_analysis.py` — 发包分析入口
- `liblibGameApp_deep_paths.py` — 深路径追踪
- `liblibGameApp_callchains.py` — 调用链分析
- `liblibGameApp_udp_send_chain.py` — UDP 发送链
- `liblibGameApp_proto_to_send.py` — 协议到发送追踪
- `liblibGameApp_gamenet_chain.py` — GameNet 业务链
- `liblibGameApp_udp_buffer_builder.py` — UDP 缓冲构建器
- `liblibGameApp_udp_builder_chain.py` — 构建器链
- `liblibGameApp_udp_descriptor_export.py` — 描述符导出
- `liblibGameApp_udp_x1_source_trace.py` — X1 结构追踪
- `liblibGameApp_online_protocol.py` — 联机协议
- `liblibGameApp_cmdid_trace.py` — CMDID 追踪
- `liblibGameApp_multiplayer_core_trace.py` — 多人核心追踪
- `liblibGameApp_cmd_register_map.py` — CMD 注册映射
- `liblibGameApp_cmd_dispatch_focus.py` — CMD 分发聚焦
- `liblibGameApp_cmd_dispatch_narrow.py` — CMD 分发窄化
- `liblibGameApp_pb_packdata_client_focus.py` — PB_PACKDATA 聚焦
- `liblibGameApp_client_msgcode_bind_trace.py` — msgcode 绑定追踪
- `liblibGameApp_client_msgcode_runtime_path.py` — msgcode 运行时路径
- `liblibGameApp_client_msgcode_dispatch_bridge.py` — 分发桥
- `liblibGameApp_internal_event_bridge.py` — 内部事件桥
- ... (更多)

**阶段 4: 桥分发系统深挖** (20+ 个脚本)
- `liblibGameApp_bridge_core_focus.py` — 桥核心聚焦
- `liblibGameApp_bridge_arg_node.py` — 桥参数节点
- `liblibGameApp_bridge_node_layout_keys.py` — 节点布局
- `liblibGameApp_bridge_key_registrar.py` — 键注册器
- `liblibGameApp_bridge_upstream_keys_templates.py` — 上游键模板
- `liblibGameApp_bridge_triple_slot_cluster.py` — 三槽聚类
- `liblibGameApp_route_semantics_followup.py` — 路由语义
- `liblibGameApp_route_activation_selector_trace.py` — 路由激活选择器
- `liblibGameApp_route_decompile_bridge.py` — 路由反编译
- `liblibGameApp_route_bridge_closure.py` — 路由桥闭合
- `liblibGameApp_route_620_writer_trace.py` — +0x620 写入追踪
- `liblibGameApp_target_state_shape_trace.py` — 目标状态形状
- `liblibGameApp_ctx620_attach_closure.py` — ctx620 附加闭合
- ... (更多)

**阶段 5: 协议恢复** (10+ 个脚本)
- `liblibGameApp_protocol_definition_recover.py` — 协议定义恢复
- `liblibGameApp_protocol_binding_recover.py` — 协议绑定恢复
- `liblibGameApp_enter_world_protocol_recover.py` — enter-world 恢复
- `liblibGameApp_enter_world_field_recover.py` — enter-world 字段恢复
- `liblibGameApp_packdata_field_recover.py` — packdata 字段恢复
- `liblibGameApp_full_protocol_definition_recover.py` — 完整协议定义恢复
- `liblibGameApp_protocol_7e2_7f0_7f3_recover.py` — 三协议码窄追
- `liblibGameApp_true_network_candidate_recover.py` — 真网络候选恢复
- `liblibGameApp_unknown_protocol_hunter.py` — 未知协议猎手
- `liblibGameApp_unknown_protocol_hunter_narrow.py` — 窄化猎手

**阶段 6: UDP 完整链路反编译** (6 个脚本)
- `liblibGameApp_udp_full_chain_decompile.py` — 完整链反编译
- `liblibGameApp_udp_deep_chain.py` — 深链反编译
- `liblibGameApp_udp_chain_phase2.py` — Phase 2
- `liblibGameApp_udp_chain_phase3.py` — Phase 3
- `liblibGameApp_udp_chain_phase4.py` — Phase 4
- `liblibGameApp_udp_chain_phase5.py` — Phase 5 (最终)

---

## 十一、核心地址索引

### 11.1 关键函数速查

| 地址 | 名称 / 作用 |
|---|---|
| `0x63AB1F4` | 通知分发核心 (sendToHost/sendBroadcast 入口) |
| `0x63AB000` | 发送前检查 / 协议查找 |
| `0x639424C` | sendToClient 分发 |
| `0x7501F30` | sendToClientMulti 分发 |
| `0x2F402E4` | m_notifySendToHost.IsValid() 检查 |
| `0x2F4088C` | sendToHost 回调 (实际发送触发) |
| `0x2F40954` | sendToHost 发送后清理 |
| `0x2F40A58` | sendToHost 真实实现 |
| `0x79BA7BC` | RakPeer::Send (vtable slot 23) |
| `0x79BA484` | RakPeer 内部发送 (排队) |
| `0x79BA0E4` | 远程系统查找 |
| `0x79BBE28` | GetRemoteSystemFromAddress |
| `0x79BBFD0` | GetRemoteSystemFromGUID |
| `0x79AFCE8` | RunUpdateCycle (刷新到线路) |
| `0x79B0BF4` | 可靠性层发送 |
| `0x79B329C` | 可靠包构建器 |
| `0x79B4B20` | RNS2_Linux::SendTo |
| `0x79B3ABC` | sendto 包装器 |
| `0x785F550` | 协议描述符访问器 |
| `0x300D878` | tagPackData 序列化 |
| `0x300DCCC` | tagPackData 反序列化 |
| `0x2ED9408` | std::string assign (曾误识为 protobuf serialize) |
| `0x4451C54` | 桥分发核心 |
| `0x4443CB8` | 打包数据构建器 |
| `0x62B2564` | Client handler 绑定锚点 |
| `0x62B2B80` | Host handler 绑定锚点 |
| `0x6015FC8` | Host handler 类型锚点 (65 项) |
| `0x60160DC` | Client handler 类型锚点 (65 项) |
| `0x62E4680` | rakpeerInterface 访问器 |
| `0x2F7B8AC` | handleRoleEnterWorld2Client |
| `0x2FF8BF4` | handleRoleEnterWorld2Host |
| `0x303FE90` | enterWorld 绑定注册 |
| `0x3055718` | enterWorld 回调链 |

### 11.2 关键数据地址

| 地址 | 说明 |
|---|---|
| `0xA7EBE38` | RakPeer vtable (93 entries) |
| `0xAD465D0` | 打包数据全局缓冲区 (byte_AD465D0) |

### 11.3 RTTI 字符串地址

| 地址 | 字符串 |
|---|---|
| `0x8A81834` | `GameNetClientMsgHandler` |
| `0x8A815BE` | `GameNetHostMsgHandler` |
| `0x8865FE0+` | `MpGameSurviveNetHandler` 系列 RTTI |
| `0x88668CD+` | `MpGameSurviveNetHandler_ver1` 系列 RTTI |
| `0x8952348` | `MNSandbox::SandboxParamData<PB_PACKDATA_CLIENT>` |

---

## 十二、已知局限与待解决问题

1. **业务数据包未在真实流量中验证** — pcap 仅含连接建立阶段，需要更长的抓包
2. **17 个协议码中有 12 个业务消息名未解析** — 仅 0x7E2/0x7F0/0x7F2/0x7F3 有名称
3. **加密问题** — 8081 端口流量疑似加密，未确认是否游戏主流量使用加密
4. **sub_2ED9408 误识别** — 曾被识别为 protobuf serialize，实际是 std::string assign
5. **sub_5FC8DE4 误识别** — 曾被识别为 getConnection，实际是 Lua 类型注册
6. **从 sub_2F40E84 到 RakPeer::Send 的最后一跳** — 委托到虚调用的精确路径未完全追踪
7. **协议码完整范围** — 0x7D3~0x7F3 范围内可能还有未发现的协议码（0x7D4~0x7D7, 0x7DF~0x7E1, 0x7E3~0x7E6, 0x7EB~0x7EC, 0x7EE, 0x7F1 均未在代码中发现引用）

---

## 十三、RakNet 源码路径

从二进制中恢复的源码路径字符串:
```
F:/minichina/MiniGameAd/Source/External/Game/RakNet/Source/
```
涉及的源文件:
- `BitStream.cpp` / `BitStream.h`
- `ReliabilityLayer.cpp`
- 以及其他 RakNet 标准源文件

---

## 附录: 解码器使用方法

```python
from liblibGameApp_udp_decoder import decode_raknet_packet

# 解码 RakNet UDP payload (不含 IP/UDP 头部)
result = decode_raknet_packet(raw_bytes)

# result 结构:
# {
#   "datagram_header": {
#     "type": "DATA" / "ACK" / "NACK",
#     "datagram_sequence_number": int,
#     ...
#   },
#   "messages": [
#     {
#       "reliability_name": "RELIABLE_ORDERED",
#       "message_id": 0x86,
#       "message_name": "ID_USER_PACKET_ENUM",
#       "application_payload": {
#         "cmdid": 0x7F2,
#         "cmdid_hex": "0x7F2",
#         "cmdid_name": "PROTO_2034",
#         "protobuf_len": 128,
#         "PB_PACKDATA_CLIENT": {
#           "uin": 12345,
#           "dataContent": b"...",
#           "targetUin": 67890,
#           "protoId": 2034,
#         },
#       },
#       ...
#     },
#   ],
# }
```

```bash
# CLI 用法
python liblibGameApp_udp_decoder.py --hex "840000006003..."
python liblibGameApp_udp_decoder.py --protobuf "0a0c0801..."
python liblibGameApp_udp_decoder.py --packdata "0a0c0801..."
python liblibGameApp_udp_decoder.py --address "020017010a0001..."
```
