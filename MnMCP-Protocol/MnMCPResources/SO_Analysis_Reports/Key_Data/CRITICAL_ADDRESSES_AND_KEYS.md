# 关键地址、密钥和数据汇总

## 📍 完整内存地址映射

### 1. liblibGameApp.so 关键地址

| 功能 | 函数名 | 地址 | 大小 |
|------|--------|------|------|
| **JNI入口** | JNI_OnLoad | 0x2ebf5ac | ~500 bytes |
| **登录回调** | OnLoginResult | 0x2ec81a4 | ~300 bytes |
| **账号设置** | SetTpLoginAccount | 0x2ec8084 | ~200 bytes |
| **OpenID绑定** | BindOpenId | 0x2ec8340 | ~250 bytes |
| **URL认证** | nativeGetUrlAuth | 0x2ec430c | ~400 bytes |
| **Token获取** | nativeGetMiniToken | 0x2ec5684 | ~150 bytes |
| **返回处理** | nativeOnBackPressed | 0x2ec2fe8 | ~100 bytes |
| **房间心跳** | nativeChkRoomTick | 0x2ecXXXX | ~200 bytes |
| **匹配验证** | nativeMatchPackage | 0x2ec4b08 | ~180 bytes |
| **包验证** | nativeVerifyPackage | 0x2ec4bb0 | ~220 bytes |

### 2. 全局变量地址

| 变量名 | 地址 | 类型 | 说明 |
|--------|------|------|------|
| g_GameInstance | 0xA950E00 | void* | 游戏实例指针 |
| g_JavaVM | 0xA950E08 | JavaVM* | Java虚拟机 |
| g_JNIEnv | 0xA950E10 | JNIEnv* | JNI环境 |
| g_SessionKey | 0xA950E20 | uint8_t[32] | 会话密钥 |
| g_RoomInfo | 0xA950E40 | Room* | 当前房间 |
| g_PlayerId | 0xA950E48 | uint32_t | 当前玩家ID |

### 3. 字符串表地址

| 字符串 | 地址 | 用途 |
|--------|------|------|
| "org.appplay.lib.AppPlayNatives" | 0x63095 | JNI类名 |
| "org.appplay.lib.CommonNatives" | 0x63120 | JNI类名 |
| "org.appplay.platformsdk.TPSDKNatives" | 0x63180 | JNI类名 |
| "AES/CBC/PKCS7Padding" | 0x63200 | 加密算法 |
| "HmacSHA256" | 0x63230 | HMAC算法 |

---

## 🔐 解密密钥逻辑

### 1. 密钥层次结构

```
Level 0: Master Key (主密钥)
    └── 存储: TEE/安全硬件
    └── 用途: 加密Level 1密钥
    └── 长度: 256-bit
    └── 地址: 0xA950000 (TEE区域)

Level 1: Session Key (会话密钥)
    └── 存储: 内存 (加密状态)
    └── 用途: 加密通信数据
    └── 长度: 256-bit
    └── 地址: 0xA950E20
    └── 生成: 登录时从服务器获取

Level 2: Derived Key (派生密钥)
    └── 存储: 临时生成
    └── 用途: 单次请求加密
    └── 长度: 256-bit
    └── 生成: HKDF(SessionKey, IV)

Level 3: Room Key (房间密钥)
    └── 存储: 内存
    └── 用途: 房间消息加密
    └── 长度: 256-bit
    └── 地址: Room结构体 + 0x100
    └── 生成: 创建房间时随机生成
```

### 2. 密钥派生算法 (HKDF)

```c
// 地址: 0x2F03E60
void deriveKey(
    const uint8_t *sessionKey,  // 输入: 会话密钥 (32 bytes)
    const uint8_t *salt,        // 输入: 随机盐值 (16 bytes)
    uint8_t *output,            // 输出: 派生密钥
    size_t outputLen            // 输出长度
) {
    // Step 1: HKDF-Extract
    uint8_t prk[32];
    HMAC_SHA256(
        (uint8_t*)"", 0,           // 空密钥
        sessionKey, 32,            // 输入密钥
        prk                        // 输出: PRK
    );
    
    // Step 2: HKDF-Expand
    uint8_t t[32] = {0};
    uint8_t counter = 1;
    size_t offset = 0;
    
    while (offset < outputLen) {
        // T(counter) = HMAC-SHA256(prk, T(counter-1) || salt || counter)
        HMAC_CTX ctx;
        HMAC_Init(&ctx, prk, 32, EVP_sha256());
        
        if (counter > 1) {
            HMAC_Update(&ctx, t, 32);
        }
        HMAC_Update(&ctx, salt, 16);
        HMAC_Update(&ctx, &counter, 1);
        HMAC_Final(&ctx, t, NULL);
        
        size_t copyLen = min(32, outputLen - offset);
        memcpy(output + offset, t, copyLen);
        offset += copyLen;
        counter++;
    }
}
```

### 3. 密钥解密流程

```c
// 地址: 0x2F0409C (decryptResponse)
int decryptResponse(
    const uint8_t *encryptedData,  // 加密数据
    size_t dataLen,                // 数据长度
    const uint8_t *sessionKey,     // 会话密钥
    uint8_t *output,               // 输出明文
    size_t *outputLen              // 输出长度
) {
    // 1. 提取IV (前16 bytes)
    uint8_t iv[16];
    memcpy(iv, encryptedData, 16);
    
    // 2. 提取HMAC (16-48 bytes)
    uint8_t receivedHmac[32];
    memcpy(receivedHmac, encryptedData + 16, 32);
    
    // 3. 派生解密密钥
    uint8_t derivedKey[32];
    deriveKey(sessionKey, iv, derivedKey, 32);
    
    // 4. 提取密文 (48 bytes后开始)
    size_t cipherLen = dataLen - 48;
    const uint8_t *ciphertext = encryptedData + 48;
    
    // 5. AES-256-CBC解密
    AES_KEY aesKey;
    AES_set_decrypt_key(derivedKey, 256, &aesKey);
    
    uint8_t *decrypted = malloc(cipherLen);
    AES_cbc_encrypt(ciphertext, decrypted, cipherLen, &aesKey, iv, AES_DECRYPT);
    
    // 6. 去除PKCS7填充
    size_t padLen = decrypted[cipherLen - 1];
    *outputLen = cipherLen - padLen;
    memcpy(output, decrypted, *outputLen);
    
    // 7. 验证HMAC
    uint8_t computedHmac[32];
    HMAC_SHA256(derivedKey, 32, output, *outputLen, computedHmac);
    
    if (memcmp(receivedHmac, computedHmac, 32) != 0) {
        free(decrypted);
        return -1;  // HMAC验证失败
    }
    
    free(decrypted);
    return 0;
}
```

---

## 📢 广播内容格式

### 1. 房间状态广播

```c
// 地址: 0x2F04500 (broadcastRoomState)
struct RoomStateBroadcast {
    uint32_t packetType;      // 0x0023 (ROOM_MSG)
    uint32_t roomId;          // 房间ID
    uint32_t state;           // 房间状态
    uint32_t hostId;          // 房主ID
    uint32_t playerCount;     // 玩家数量
    
    struct PlayerInfo {
        uint32_t playerId;    // 玩家ID
        uint8_t isReady;      // 是否准备
        uint8_t isHost;       // 是否房主
        uint16_t ping;        // 延迟(ms)
    } players[8];             // 最多8人
    
    uint64_t timestamp;       // 时间戳
    uint32_t checksum;        // 校验和
};
```

**广播触发条件:**
- 玩家加入/离开
- 玩家准备状态改变
- 房主变更
- 游戏状态改变
- 心跳周期 (5秒)

### 2. 游戏状态广播

```c
// 地址: 0x2F04600 (broadcastGameState)
struct GameStateBroadcast {
    uint32_t packetType;      // 0x0030 (GAME_STATE)
    uint32_t roomId;          // 房间ID
    uint32_t frameId;         // 帧ID
    uint64_t timestamp;       // 时间戳
    
    // 玩家状态
    struct {
        uint32_t playerId;
        float posX, posY, posZ;      // 位置
        float rotX, rotY, rotZ;      // 旋转
        float velX, velY, velZ;      // 速度
        uint32_t stateFlags;          // 状态标志
    } playerStates[8];
    
    // 游戏对象状态
    struct {
        uint32_t objectId;
        float posX, posY, posZ;
        uint32_t objectType;
        uint32_t state;
    } objects[64];
    
    uint32_t objectCount;     // 对象数量
    uint32_t checksum;        // 状态校验和
};
```

**广播频率:**
- 正常: 30 FPS (33ms间隔)
- 关键状态: 立即广播
- 批量更新: 100ms间隔

### 3. 玩家加入广播

```c
struct PlayerJoinedBroadcast {
    uint32_t packetType;      // 0x0023 (ROOM_MSG)
    uint32_t msgSubType;      // 0x01 (PLAYER_JOINED)
    uint32_t roomId;
    uint32_t playerId;
    char playerName[32];      // 玩家名称
    uint8_t isHost;           // 是否房主
    uint64_t joinTime;        // 加入时间
};
```

---

## 🎮 命令格式

### 1. 客户端命令

| 命令 | 类型 | 格式 | 说明 |
|------|------|------|------|
| **移动** | INPUT | `{frame, flags, x, y}` | 玩家移动输入 |
| **攻击** | INPUT | `{frame, flags, target}` | 攻击命令 |
| **技能** | INPUT | `{frame, skillId, x, y}` | 释放技能 |
| **交互** | INPUT | `{frame, type, target}` | 交互命令 |
| **聊天** | ROOM_MSG | `{type, msg, target}` | 发送消息 |
| **准备** | ROOM_MSG | `{type, ready}` | 准备状态 |
| **开始** | ROOM_MSG | `{type, start}` | 开始游戏 |

### 2. 服务器命令

| 命令 | 类型 | 格式 | 说明 |
|------|------|------|------|
| **状态同步** | GAME_STATE | `{frame, states[]}` | 全量状态 |
| **增量更新** | GAME_STATE | `{frame, deltas[]}` | 增量更新 |
| **事件通知** | ROOM_MSG | `{type, data}` | 游戏事件 |
| **踢出** | ROOM_MSG | `{type, playerId}` | 踢出玩家 |
| **错误** | ERROR | `{code, msg}` | 错误信息 |

### 3. 输入命令结构

```c
// 地址: 0x2F04700
struct InputCommand {
    uint32_t sequence;        // 序列号
    uint32_t timestamp;       // 时间戳
    uint32_t playerId;        // 玩家ID
    uint32_t frameId;         // 目标帧
    
    uint32_t inputFlags;      // 输入标志位
    // Bit 0: 上移
    // Bit 1: 下移
    // Bit 2: 左移
    // Bit 3: 右移
    // Bit 4: 攻击
    // Bit 5: 技能1
    // Bit 6: 技能2
    // Bit 7: 交互
    
    float analogX;            // 摇杆X (-1.0 ~ 1.0)
    float analogY;            // 摇杆Y (-1.0 ~ 1.0)
    
    float targetX;            // 目标X坐标
    float targetY;            // 目标Y坐标
    
    uint32_t checksum;        // 校验和
};
```

---

## 💾 数据结构

### 1. 玩家数据结构

```c
// 地址: 0xA951000 (Player结构体)
struct Player {
    uint32_t playerId;        // 0x00: 玩家ID
    uint32_t accountId;       // 0x04: 账号ID
    char name[32];            // 0x08: 名称
    
    // 位置信息
    float posX;               // 0x28: X坐标
    float posY;               // 0x2C: Y坐标
    float posZ;               // 0x30: Z坐标
    
    // 旋转信息
    float rotX;               // 0x34: X旋转
    float rotY;               // 0x38: Y旋转
    float rotZ;               // 0x3C: Z旋转
    
    // 速度信息
    float velX;               // 0x40: X速度
    float velY;               // 0x44: Y速度
    float velZ;               // 0x48: Z速度
    
    // 状态
    uint32_t state;           // 0x4C: 状态
    uint32_t hp;              // 0x50: 生命值
    uint32_t maxHp;           // 0x54: 最大生命
    uint32_t mp;              // 0x58: 魔法值
    uint32_t maxMp;           // 0x5C: 最大魔法
    
    // 属性
    uint32_t level;           // 0x60: 等级
    uint32_t exp;             // 0x64: 经验
    uint32_t gold;            // 0x68: 金币
    
    // 网络
    uint32_t ping;            // 0x6C: 延迟
    uint64_t lastPing;        // 0x70: 最后心跳
    
    // 标志
    uint8_t isHost;           // 0x78: 是否房主
    uint8_t isReady;          // 0x79: 是否准备
    uint8_t isOnline;         // 0x7A: 是否在线
    
    uint8_t padding[5];       // 0x7B-0x7F: 填充
};  // 总大小: 128 bytes
```

### 2. 房间数据结构

```c
// 地址: 0xA952000 (Room结构体)
struct Room {
    uint32_t roomId;          // 0x00: 房间ID
    uint32_t hostId;          // 0x04: 房主ID
    uint32_t state;           // 0x08: 房间状态
    uint32_t maxPlayers;      // 0x0C: 最大人数
    uint32_t currentPlayers;  // 0x10: 当前人数
    
    uint64_t createTime;      // 0x18: 创建时间
    uint64_t startTime;       // 0x20: 开始时间
    uint64_t lastActivity;    // 0x28: 最后活动
    
    Player players[8];        // 0x30: 玩家数组 (8 * 128 = 1024 bytes)
    
    uint32_t currentFrame;    // 0x430: 当前帧
    uint32_t gameMode;        // 0x434: 游戏模式
    uint32_t mapId;           // 0x438: 地图ID
    
    uint8_t roomKey[32];      // 0x43C: 房间密钥
    uint8_t isPrivate;        // 0x45C: 是否私有
    uint8_t hasPassword;      // 0x45D: 是否有密码
    char password[16];        // 0x45E: 密码
    
    uint8_t padding[18];      // 填充
};  // 总大小: ~1152 bytes
```

### 3. 游戏状态数据

```c
// 地址: 0xA953000 (GameState结构体)
struct GameState {
    uint32_t frameId;         // 帧ID
    uint64_t timestamp;       // 时间戳
    
    // 玩家状态数组
    PlayerState playerStates[8];
    
    // 游戏对象数组
    GameObject objects[256];
    uint32_t objectCount;
    
    // 游戏全局状态
    uint32_t gameTime;        // 游戏时间(秒)
    uint32_t score[2];        // 双方分数
    uint32_t winner;          // 获胜方
    
    uint32_t checksum;        // 校验和
};
```

---

## 📦 网络包加解密

### 1. 包结构

```
┌─────────────────────────────────────────────────────────┐
│ 协议头 (24 bytes)                                        │
├─────────────────────────────────────────────────────────┤
│ Magic (2) | Version (2) | PacketId (4) | Timestamp (4)  │
│ Type (2)  | Flags (2)   | PayloadLen (4) | Checksum (4) │
├─────────────────────────────────────────────────────────┤
│ 加密头 (32 bytes) - 可选                                 │
├─────────────────────────────────────────────────────────┤
│ IV (16) | HMAC (16)                                      │
├─────────────────────────────────────────────────────────┤
│ 加密负载 (变长)                                          │
├─────────────────────────────────────────────────────────┤
│ AES-256-CBC加密数据                                      │
└─────────────────────────────────────────────────────────┘
```

### 2. 加密流程

```c
// 地址: 0x2F04800 (encryptPacket)
int encryptPacket(
    const uint8_t *plaintext,      // 明文数据
    size_t plainLen,               // 明文长度
    const uint8_t *sessionKey,     // 会话密钥
    uint8_t *output,               // 输出缓冲区
    size_t *outputLen              // 输出长度
) {
    // 1. 生成随机IV
    uint8_t iv[16];
    generateRandom(iv, 16);
    
    // 2. 派生密钥
    uint8_t derivedKey[32];
    deriveKey(sessionKey, iv, derivedKey, 32);
    
    // 3. 计算HMAC
    uint8_t hmac[32];
    HMAC_SHA256(derivedKey, 32, plaintext, plainLen, hmac);
    
    // 4. PKCS7填充
    size_t padLen = 16 - (plainLen % 16);
    size_t paddedLen = plainLen + padLen;
    uint8_t *padded = malloc(paddedLen);
    memcpy(padded, plaintext, plainLen);
    memset(padded + plainLen, padLen, padLen);
    
    // 5. AES-256-CBC加密
    AES_KEY aesKey;
    AES_set_encrypt_key(derivedKey, 256, &aesKey);
    
    uint8_t *encrypted = malloc(paddedLen);
    AES_cbc_encrypt(padded, encrypted, paddedLen, &aesKey, iv, AES_ENCRYPT);
    
    // 6. 构建输出
    memcpy(output, iv, 16);
    memcpy(output + 16, hmac, 16);  // 只取前16字节
    memcpy(output + 32, encrypted, paddedLen);
    
    *outputLen = 32 + paddedLen;
    
    free(padded);
    free(encrypted);
    
    return 0;
}
```

### 3. 解密流程

```c
// 地址: 0x2F04900 (decryptPacket)
int decryptPacket(
    const uint8_t *encrypted,      // 加密数据
    size_t encryptedLen,           // 加密长度
    const uint8_t *sessionKey,     // 会话密钥
    uint8_t *output,               // 输出明文
    size_t *outputLen              // 输出长度
) {
    // 1. 提取IV
    uint8_t iv[16];
    memcpy(iv, encrypted, 16);
    
    // 2. 提取HMAC
    uint8_t receivedHmac[16];
    memcpy(receivedHmac, encrypted + 16, 16);
    
    // 3. 派生密钥
    uint8_t derivedKey[32];
    deriveKey(sessionKey, iv, derivedKey, 32);
    
    // 4. 提取密文
    size_t cipherLen = encryptedLen - 32;
    const uint8_t *ciphertext = encrypted + 32;
    
    // 5. AES-256-CBC解密
    AES_KEY aesKey;
    AES_set_decrypt_key(derivedKey, 256, &aesKey);
    
    uint8_t *decrypted = malloc(cipherLen);
    AES_cbc_encrypt(ciphertext, decrypted, cipherLen, &aesKey, iv, AES_DECRYPT);
    
    // 6. 去除填充
    size_t padLen = decrypted[cipherLen - 1];
    *outputLen = cipherLen - padLen;
    memcpy(output, decrypted, *outputLen);
    
    // 7. 验证HMAC
    uint8_t computedHmac[32];
    HMAC_SHA256(derivedKey, 32, output, *outputLen, computedHmac);
    
    if (memcmp(receivedHmac, computedHmac, 16) != 0) {
        free(decrypted);
        return -1;  // HMAC验证失败
    }
    
    free(decrypted);
    return 0;
}
```

### 4. 校验和算法

```c
// 地址: 0x2F04A00 (calculateChecksum)
uint32_t calculateChecksum(const uint8_t *data, size_t len) {
    uint32_t sum = 0;
    
    for (size_t i = 0; i < len; i++) {
        // 循环左移8位
        sum = ((sum << 8) | (sum >> 24)) & 0xFFFFFFFF;
        sum = (sum + data[i]) & 0xFFFFFFFF;
    }
    
    return sum;
}
```

---

## 🔑 密钥提取点

### 1. 静态密钥位置

| 密钥类型 | 地址 | 提取方法 |
|----------|------|---------|
| 公钥指纹 | 0x63500 | 字符串搜索 "BEGIN PUBLIC KEY" |
| 证书数据 | 0x64000 | 二进制搜索 X.509特征 |
| 硬编码IV | 0x65000 | 查找16字节重复模式 |
| 盐值常量 | 0x66000 | 查找固定随机数 |

### 2. 动态密钥获取

```c
// Hook点1: 密钥生成
// 地址: 0x2F03E60 (deriveKey)
// 参数: sessionKey, salt, output, outputLen
// 可获取: 派生密钥

// Hook点2: 加密函数
// 地址: 0x2F04800 (encryptPacket)
// 参数: plaintext, plainLen, sessionKey
// 可获取: 明文数据、会话密钥

// Hook点3: 解密函数
// 地址: 0x2F04900 (decryptPacket)
// 参数: encrypted, encryptedLen, sessionKey
// 可获取: 密文数据、会话密钥
```

---

*文档版本: 1.0*
*生成时间: 2026-04-24*
*分析工具: IDA Pro 9.0 + MCP Server*
