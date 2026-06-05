# 网络协议规范文档

## 1. 协议概述

### 1.1 协议栈

```
┌─────────────────────────────────────────┐
│ 应用层 - 游戏协议                         │
│ (房间管理/状态同步/游戏逻辑)               │
├─────────────────────────────────────────┤
│ 安全层 - 加密/签名                        │
│ (AES-256/HMAC-SHA256)                   │
├─────────────────────────────────────────┤
│ 传输层 - TCP/UDP/WebSocket               │
├─────────────────────────────────────────┤
│ 网络层 - IP                              │
└─────────────────────────────────────────┘
```

### 1.2 端口分配

| 服务 | 协议 | 端口 | 说明 |
|------|------|------|------|
| HTTP API | TCP | 80/443 | 平台接口 |
| 游戏服务器 | TCP | 10000-11000 | 动态分配 |
| 实时通信 | UDP | 20000-21000 | 状态同步 |
| WebSocket | TCP | 443 | 双向通信 |

---

## 2. 协议头格式

### 2.1 基础协议头 (24 bytes)

```c
struct ProtocolHeader {
    uint16_t magic;          // 0x4B47 ('KG')
    uint16_t version;        // 协议版本
    uint32_t packetId;       // 包序列号
    uint32_t timestamp;      // 时间戳 (ms)
    uint16_t packetType;     // 包类型
    uint16_t flags;          // 标志位
    uint32_t payloadLen;     // 负载长度
    uint32_t checksum;       // 校验和
};
```

**字段说明:**

| 字段 | 大小 | 说明 |
|------|------|------|
| magic | 2 | 魔数 'KG' = 0x4B47 |
| version | 2 | 当前版本 = 1 |
| packetId | 4 | 递增序列号，防重放 |
| timestamp | 4 | 毫秒时间戳 |
| packetType | 2 | 见包类型定义 |
| flags | 2 | 加密/压缩标志 |
| payloadLen | 4 | 负载数据长度 |
| checksum | 4 | CRC32校验和 |

### 2.2 标志位定义

```c
#define FLAG_ENCRYPTED   0x0001  // 数据已加密
#define FLAG_COMPRESSED  0x0002  // 数据已压缩
#define FLAG_ACK         0x0004  // 确认包
#define FLAG_RELIABLE    0x0008  // 可靠传输
#define FLAG_BROADCAST   0x0010  // 广播包
```

---

## 3. 包类型定义

### 3.1 系统包 (0x0000-0x00FF)

| 类型 | 值 | 说明 |
|------|-----|------|
| PKT_HANDSHAKE | 0x0001 | 握手请求/响应 |
| PKT_HEARTBEAT | 0x0002 | 心跳包 |
| PKT_DISCONNECT | 0x0003 | 断开连接 |
| PKT_ACK | 0x0004 | 确认包 |
| PKT_ERROR | 0x0005 | 错误包 |

### 3.2 登录包 (0x0100-0x01FF)

| 类型 | 值 | 说明 |
|------|-----|------|
| PKT_LOGIN_REQ | 0x0100 | 登录请求 |
| PKT_LOGIN_RES | 0x0101 | 登录响应 |
| PKT_LOGOUT | 0x0102 | 登出 |
| PKT_TOKEN_REFRESH | 0x0103 | Token刷新 |

### 3.3 房间包 (0x0200-0x02FF)

| 类型 | 值 | 说明 |
|------|-----|------|
| PKT_ROOM_CREATE | 0x0200 | 创建房间 |
| PKT_ROOM_JOIN | 0x0201 | 加入房间 |
| PKT_ROOM_LEAVE | 0x0202 | 离开房间 |
| PKT_ROOM_KICK | 0x0203 | 踢出玩家 |
| PKT_ROOM_READY | 0x0204 | 准备状态 |
| PKT_ROOM_START | 0x0205 | 开始游戏 |
| PKT_ROOM_LIST | 0x0206 | 房间列表 |
| PKT_ROOM_INFO | 0x0207 | 房间信息 |
| PKT_ROOM_MSG | 0x0208 | 房间消息 |

### 3.4 游戏包 (0x0300-0x03FF)

| 类型 | 值 | 说明 |
|------|-----|------|
| PKT_GAME_STATE | 0x0300 | 游戏状态 |
| PKT_GAME_INPUT | 0x0301 | 玩家输入 |
| PKT_GAME_EVENT | 0x0302 | 游戏事件 |
| PKT_GAME_SYNC | 0x0303 | 状态同步请求 |
| PKT_GAME_RESULT | 0x0304 | 游戏结果 |

---

## 4. 详细包格式

### 4.1 握手包 (0x0001)

**请求:**
```c
struct HandshakeRequest {
    uint32_t protocolVersion;    // 协议版本
    uint32_t clientVersion;      // 客户端版本
    char deviceId[32];           // 设备ID
    char token[256];             // 认证Token
    uint64_t timestamp;          // 时间戳
};
```

**响应:**
```c
struct HandshakeResponse {
    uint32_t result;             // 结果码 (0=成功)
    uint32_t sessionId;          // 会话ID
    uint64_t serverTime;         // 服务器时间
    uint32_t heartbeatInterval;  // 心跳间隔(ms)
    char sessionKey[32];         // 会话密钥
};
```

### 4.2 心跳包 (0x0002)

```c
struct HeartbeatPacket {
    uint32_t sessionId;          // 会话ID
    uint32_t clientTime;         // 客户端时间
    uint16_t ping;               // 延迟(ms)
    uint8_t status;              // 状态 (0=正常)
};
```

### 4.3 登录请求 (0x0100)

```c
struct LoginRequest {
    uint8_t loginType;           // 登录类型
    // 1=账号密码, 2=Token, 3=第三方
    
    union {
        struct {
            char account[64];    // 账号
            char password[64];   // 密码 (MD5)
        } account;
        
        struct {
            char token[256];     // 登录Token
        } token;
        
        struct {
            uint8_t platform;    // 平台类型
            char openId[64];     // OpenID
            char authToken[256]; // 平台Token
        } thirdParty;
    };
    
    char deviceInfo[256];        // 设备信息(JSON)
};
```

**登录响应 (0x0101):**
```c
struct LoginResponse {
    uint32_t result;             // 结果码
    // 0=成功, 1=账号错误, 2=密码错误, 3=Token过期...
    
    uint32_t playerId;           // 玩家ID
    char token[256];             // 会话Token
    uint32_t expireTime;         // 过期时间
    
    struct {
        uint32_t level;
        uint32_t exp;
        uint32_t gold;
        char name[32];
    } playerInfo;
};
```

### 4.4 创建房间 (0x0200)

**请求:**
```c
struct CreateRoomRequest {
    uint8_t gameMode;            // 游戏模式
    uint8_t maxPlayers;          // 最大人数 (2-8)
    uint8_t isPrivate;           // 是否私有
    char password[16];           // 密码 (可选)
    uint32_t mapId;              // 地图ID
    char roomName[32];           // 房间名
};
```

**响应:**
```c
struct CreateRoomResponse {
    uint32_t result;             // 结果码
    uint32_t roomId;             // 房间ID
    uint8_t roomKey[32];         // 房间密钥
    uint64_t createTime;         // 创建时间
};
```

### 4.5 加入房间 (0x0201)

**请求:**
```c
struct JoinRoomRequest {
    uint32_t roomId;             // 房间ID
    char password[16];           // 密码 (私有房间)
};
```

**响应:**
```c
struct JoinRoomResponse {
    uint32_t result;             // 结果码
    // 0=成功, 1=房间不存在, 2=已满, 3=密码错误...
    
    struct {
        uint32_t roomId;
        uint32_t hostId;
        uint8_t state;
        uint8_t maxPlayers;
        uint8_t currentPlayers;
    } roomInfo;
    
    struct {
        uint32_t playerId;
        char name[32];
        uint8_t isHost;
        uint8_t isReady;
    } players[8];
    
    uint8_t roomKey[32];         // 房间密钥
};
```

### 4.6 房间消息 (0x0208)

```c
struct RoomMessage {
    uint8_t msgType;             // 消息类型
    // 1=聊天, 2=系统, 3=准备, 4=开始...
    
    uint32_t senderId;           // 发送者ID
    uint64_t timestamp;          // 时间戳
    
    union {
        struct {
            char content[256];   // 聊天内容
        } chat;
        
        struct {
            uint8_t ready;       // 准备状态
        } ready;
        
        struct {
            uint32_t targetId;   // 目标玩家ID
        } kick;
    };
};
```

### 4.7 游戏状态 (0x0300)

```c
struct GameStatePacket {
    uint32_t frameId;            // 帧ID
    uint64_t timestamp;          // 时间戳
    uint32_t gameTime;           // 游戏时间(秒)
    
    // 玩家状态
    struct PlayerState {
        uint32_t playerId;
        float posX, posY, posZ;      // 位置
        float rotX, rotY, rotZ;      // 旋转
        float velX, velY, velZ;      // 速度
        uint32_t hp;                  // 生命值
        uint32_t stateFlags;          // 状态标志
    } players[8];
    uint8_t playerCount;
    
    // 游戏对象
    struct ObjectState {
        uint32_t objectId;
        uint32_t objectType;
        float posX, posY, posZ;
        uint32_t state;
    } objects[64];
    uint8_t objectCount;
    
    // 游戏全局状态
    uint32_t score[2];           // 双方分数
    uint8_t gamePhase;           // 游戏阶段
};
```

### 4.8 玩家输入 (0x0301)

```c
struct InputPacket {
    uint32_t sequence;           // 序列号
    uint32_t frameId;            // 目标帧
    uint64_t timestamp;          // 时间戳
    
    uint32_t inputFlags;         // 输入标志
    // Bit 0: 上移
    // Bit 1: 下移
    // Bit 2: 左移
    // Bit 3: 右移
    // Bit 4: 跳跃
    // Bit 5: 攻击
    // Bit 6: 技能1
    // Bit 7: 技能2
    // Bit 8: 交互
    
    float analogX;               // 摇杆X (-1.0 ~ 1.0)
    float analogY;               // 摇杆Y (-1.0 ~ 1.0)
    
    float targetX;               // 目标X
    float targetY;               // 目标Y
    float targetZ;               // 目标Z
};
```

---

## 5. 加密规范

### 5.1 加密流程

```
明文数据
    │
    ▼
┌─────────────────┐
│ 1. 添加序列号    │
│ 2. 添加时间戳    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. 计算HMAC     │
│ HMAC-SHA256     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. AES-256加密  │
│ CBC模式 + PKCS7 │
└────────┬────────┘
         │
         ▼
密文数据 (IV + HMAC + Ciphertext)
```

### 5.2 加密头格式

```c
struct EncryptionHeader {
    uint8_t iv[16];              // 初始化向量
    uint8_t hmac[16];            // HMAC前16字节
    uint8_t encryptedData[];     // 加密数据
};
```

### 5.3 密钥派生

```
Master Key (服务器下发)
    │
    ▼ HKDF-Extract
PRK (Pseudo-Random Key)
    │
    ▼ HKDF-Expand + Session Salt
Session Key (32 bytes)
    │
    ▼ HKDF-Expand + Packet IV
Packet Key (32 bytes)
```

---

## 6. 状态码定义

### 6.1 通用状态码

| 码值 | 名称 | 说明 |
|------|------|------|
| 0 | SUCCESS | 成功 |
| 1 | ERROR_UNKNOWN | 未知错误 |
| 2 | ERROR_INVALID_PARAM | 参数错误 |
| 3 | ERROR_NETWORK | 网络错误 |
| 4 | ERROR_TIMEOUT | 超时 |
| 5 | ERROR_SERVER_BUSY | 服务器繁忙 |

### 6.2 登录状态码

| 码值 | 名称 | 说明 |
|------|------|------|
| 100 | LOGIN_SUCCESS | 登录成功 |
| 101 | LOGIN_ACCOUNT_NOT_EXIST | 账号不存在 |
| 102 | LOGIN_WRONG_PASSWORD | 密码错误 |
| 103 | LOGIN_TOKEN_EXPIRED | Token过期 |
| 104 | LOGIN_ACCOUNT_BANNED | 账号被封禁 |
| 105 | LOGIN_DEVICE_LIMIT | 设备数量限制 |

### 6.3 房间状态码

| 码值 | 名称 | 说明 |
|------|------|------|
| 200 | ROOM_SUCCESS | 操作成功 |
| 201 | ROOM_NOT_EXIST | 房间不存在 |
| 202 | ROOM_FULL | 房间已满 |
| 203 | ROOM_WRONG_PASSWORD | 密码错误 |
| 204 | ROOM_ALREADY_IN | 已在房间中 |
| 205 | ROOM_NOT_IN | 不在房间中 |
| 206 | ROOM_NO_PERMISSION | 无权限 |
| 207 | ROOM_GAME_STARTED | 游戏已开始 |

---

## 7. 通信流程

### 7.1 登录流程

```
客户端                              服务器
  │                                   │
  │ ─────── 1. Handshake ───────────▶ │
  │      {version, deviceId, token}   │
  │                                   │
  │ ◀────── 2. Handshake Response ─── │
  │      {sessionId, sessionKey}      │
  │                                   │
  │ ─────── 3. Login Request ───────▶ │
  │      {account, password}          │
  │      (encrypted with sessionKey)  │
  │                                   │
  │ ◀────── 4. Login Response ─────── │
  │      {playerId, token}            │
  │                                   │
  │ ═══════ 5. Heartbeat (定期) ═════ │
  │                                   │
```

### 7.2 房间流程

```
客户端A (房主)                      服务器                      客户端B
    │                               │                           │
    │ ───── 1. Create Room ───────▶ │                           │
    │                               │                           │
    │ ◀──── 2. Room Created ─────── │                           │
    │                               │                           │
    │                               │ ◀──── 3. Join Room ───────│
    │                               │                           │
    │ ◀──── 4. Player Joined ──────│                           │
    │                               │─────▶ 5. Join Success ────│
    │                               │                           │
    │ ───── 6. Ready ─────────────▶ │                           │
    │                               │─────▶ 7. Player Ready ────│
    │                               │                           │
    │ ───── 8. Start Game ────────▶ │                           │
    │                               │─────▶ 9. Game Started ────│
```

### 7.3 游戏同步流程

```
客户端                              服务器
  │                                   │
  │ ═══════ 输入采集 (每帧) ═════════ │
  │                                   │
  │ ─────── Input Packet ───────────▶ │
  │      {frame, flags, analog}       │
  │                                   │
  │         [服务器计算权威状态]        │
  │                                   │
  │ ◀────── Game State (30fps) ────── │
  │      {frame, playerStates}        │
  │                                   │
  │         [客户端预测+插值]          │
  │                                   │
```

---

## 8. 数据校验

### 8.1 校验和算法

```c
uint32_t calculateChecksum(const void *data, size_t len) {
    const uint8_t *bytes = (const uint8_t*)data;
    uint32_t sum = 0;
    
    for (size_t i = 0; i < len; i++) {
        sum = ((sum << 8) | (sum >> 24)) + bytes[i];
    }
    
    return sum;
}
```

### 8.2 HMAC计算

```c
void calculateHMAC(
    const uint8_t *key, size_t keyLen,
    const void *data, size_t dataLen,
    uint8_t *output
) {
    HMAC_SHA256(key, keyLen, data, dataLen, output);
}
```

---

*文档版本: 1.0*
*最后更新: 2026-04-24*
