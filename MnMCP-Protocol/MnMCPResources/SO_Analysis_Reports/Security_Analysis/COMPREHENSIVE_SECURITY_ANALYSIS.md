# 综合安全分析报告

## 1. 安全架构总览

### 1.1 防御层次

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 5: 应用层安全                                          │
│ ├── 游戏逻辑校验                                             │
│ ├── 数据完整性检查                                           │
│ └── 异常行为检测                                             │
├─────────────────────────────────────────────────────────────┤
│ Layer 4: 反作弊层                                            │
│ ├── libqmcheat.so (作弊检测)                                 │
│ ├── libtersafe2.so (腾讯反作弊)                              │
│ └── 风险评分系统                                             │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: 安全防护层                                          │
│ ├── libInnoSecure.so (反调试/反注入)                         │
│ ├── libsgcore.so (腾讯安全核心)                              │
│ └── 完整性校验                                               │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: 加密通信层                                          │
│ ├── libEncryptor.so (AES/RSA加密)                            │
│ ├── libEncryptorP.so (平台加密)                              │
│ └── 安全通信通道                                             │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: 加载器层                                            │
│ ├── libMiniTechLoader.so (安全加载)                          │
│ └── 签名验证                                                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 关键安全组件

| 组件 | 功能 | 风险等级 |
|------|------|---------|
| libMiniTechLoader.so | 加载器安全 | LOW ✅ |
| libEncryptor.so | 数据加密 | LOW ✅ |
| libInnoSecure.so | 运行时防护 | LOW ✅ |
| libqmcheat.so | 作弊检测 | LOW ✅ |
| libtersafe2.so | 反作弊核心 | LOW ✅ |
| libilink_network.so | 网络安全 | LOW ✅ |

---

## 2. 密钥管理系统

### 2.1 密钥层次

```
Level 0: Root Key (根密钥)
├── 存储位置: 服务器安全模块 (HSM)
├── 用途: 签发所有子密钥
├── 生命周期: 永久 (定期轮换)
└── 访问控制: 仅密钥管理员

Level 1: Master Key (主密钥)
├── 存储位置: TEE/安全硬件
├── 用途: 加密Level 2密钥
├── 派生方式: HKDF(RootKey, "master")
└── 轮换周期: 90天

Level 2: Session Key (会话密钥)
├── 存储位置: 客户端内存 (加密)
├── 用途: 加密通信数据
├── 派生方式: ECDH密钥交换
├── 有效期: 单次会话
└── 地址: 0xA950E20

Level 3: Room Key (房间密钥)
├── 存储位置: 客户端内存
├── 用途: 房间消息加密
├── 生成方式: 随机生成 (32 bytes)
├── 分发方式: RSA加密传输
└── 有效期: 房间生命周期
```

### 2.2 密钥派生详细流程

```c
// 完整密钥派生流程
void fullKeyDerivation() {
    // Step 1: 从服务器获取加密的MasterKey
    EncryptedMasterKey encryptedMK = receiveFromServer();
    
    // Step 2: 使用设备私钥解密
    uint8_t masterKey[32];
    RSA_decrypt(devicePrivateKey, encryptedMK.data, masterKey);
    
    // Step 3: 派生SessionKey (HKDF)
    uint8_t sessionSalt[16] = generateRandom(16);
    uint8_t sessionKey[32];
    HKDF(masterKey, 32, sessionSalt, 16, "session", sessionKey, 32);
    
    // Step 4: 存储SessionKey (加密存储)
    uint8_t encryptedSessionKey[32];
    encryptWithDeviceKey(sessionKey, encryptedSessionKey);
    storeSecurely(0xA950E20, encryptedSessionKey, 32);
    
    // Step 5: 派生PacketKey (每次请求)
    uint8_t packetIV[16] = generateRandom(16);
    uint8_t packetKey[32];
    HKDF(sessionKey, 32, packetIV, 16, "packet", packetKey, 32);
    
    // Step 6: 使用PacketKey加密数据
    uint8_t encryptedData[...];
    AES_encrypt(plaintext, packetKey, packetIV, encryptedData);
}
```

### 2.3 关键密钥地址

| 密钥 | 地址 | 大小 | 说明 |
|------|------|------|------|
| MasterKey | 0xA950000 | 32 bytes | 主密钥 (TEE) |
| SessionKey | 0xA950E20 | 32 bytes | 会话密钥 |
| RoomKey | Room+0x100 | 32 bytes | 房间密钥 |
| PacketKey | 栈变量 | 32 bytes | 包密钥 (临时) |
| HMACKey | 派生 | 32 bytes | HMAC密钥 |

---

## 3. 加密算法详解

### 3.1 AES-256-CBC实现

```c
// 地址: 0x2F04800
struct AES_Context {
    uint8_t key[32];
    uint8_t iv[16];
    AES_KEY encryptKey;
    AES_KEY decryptKey;
};

// 加密流程
int AES_256_CBC_Encrypt(
    const uint8_t *plaintext,
    size_t plainLen,
    const uint8_t *key,
    const uint8_t *iv,
    uint8_t *ciphertext
) {
    // 1. 初始化密钥
    AES_KEY aesKey;
    AES_set_encrypt_key(key, 256, &aesKey);
    
    // 2. PKCS7填充
    size_t padLen = 16 - (plainLen % 16);
    size_t paddedLen = plainLen + padLen;
    uint8_t *padded = malloc(paddedLen);
    memcpy(padded, plaintext, plainLen);
    memset(padded + plainLen, padLen, padLen);
    
    // 3. CBC加密
    uint8_t ivCopy[16];
    memcpy(ivCopy, iv, 16);
    
    AES_cbc_encrypt(
        padded,           // 输入
        ciphertext,       // 输出
        paddedLen,        // 长度
        &aesKey,          // 密钥
        ivCopy,           // IV (会被修改)
        AES_ENCRYPT       // 加密模式
    );
    
    free(padded);
    return paddedLen;
}
```

### 3.2 HMAC-SHA256实现

```c
// 地址: 0x2F04A00
void HMAC_SHA256(
    const uint8_t *key, size_t keyLen,
    const uint8_t *data, size_t dataLen,
    uint8_t *output
) {
    // 1. 处理密钥
    uint8_t k[32];
    if (keyLen > 64) {
        SHA256(key, keyLen, k);
    } else {
        memcpy(k, key, keyLen);
        memset(k + keyLen, 0, 64 - keyLen);
    }
    
    // 2. 内层哈希: H(K XOR ipad || data)
    uint8_t inner[64 + dataLen];
    for (int i = 0; i < 64; i++) {
        inner[i] = k[i] ^ 0x36;  // ipad
    }
    memcpy(inner + 64, data, dataLen);
    
    uint8_t innerHash[32];
    SHA256(inner, 64 + dataLen, innerHash);
    
    // 3. 外层哈希: H(K XOR opad || innerHash)
    uint8_t outer[64 + 32];
    for (int i = 0; i < 64; i++) {
        outer[i] = k[i] ^ 0x5c;  // opad
    }
    memcpy(outer + 64, innerHash, 32);
    
    SHA256(outer, 64 + 32, output);
}
```

### 3.3 RSA加密实现

```c
// 地址: 0x2F04C00
// RSA-2048 OAEP加密
int RSA_Encrypt_OAEP(
    const RSA *publicKey,
    const uint8_t *plaintext,
    size_t plainLen,
    uint8_t *ciphertext
) {
    // 1. 生成随机种子
    uint8_t seed[32];
    generateRandom(seed, 32);
    
    // 2. 数据块编码 (MGF1 + OAEP)
    uint8_t encoded[256];  // RSA-2048 = 256 bytes
    OAEP_encode(plaintext, plainLen, seed, encoded);
    
    // 3. RSA加密: c = m^e mod n
    BN_mod_exp(ciphertext, encoded, publicKey->e, publicKey->n, ctx);
    
    return 256;
}
```

---

## 4. 网络包加解密详细流程

### 4.1 加密包结构

```
┌─────────────────────────────────────────────────────────────┐
│ 加密包格式 (总长度 = 48 + paddedLen)                          │
├─────────────────────────────────────────────────────────────┤
│ IV (16 bytes)                                               │
│ ├─ Offset: 0                                                │
│ └─ 随机生成，每次请求不同                                     │
├─────────────────────────────────────────────────────────────┤
│ HMAC (16 bytes)                                             │
│ ├─ Offset: 16                                               │
│ ├─ 计算: HMAC-SHA256(DerivedKey, Plaintext)                 │
│ └─ 只取前16字节                                             │
├─────────────────────────────────────────────────────────────┤
│ Ciphertext (paddedLen bytes)                                │
│ ├─ Offset: 32                                               │
│ ├─ 算法: AES-256-CBC                                        │
│ ├─ 密钥: DerivedKey (HKDF生成)                              │
│ ├─ IV: 包IV                                                 │
│ └─ 填充: PKCS7                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 完整加密流程

```c
// 地址: 0x2F05000
int encryptNetworkPacket(
    const void *plaintext,       // 明文数据
    size_t plainLen,             // 明文长度
    const uint8_t *sessionKey,   // 会话密钥
    uint8_t *output,             // 输出缓冲区
    size_t *outputLen            // 输出长度
) {
    // Step 1: 生成随机IV
    uint8_t iv[16];
    generateSecureRandom(iv, 16);  // 地址: 0x2F05100
    
    // Step 2: 派生加密密钥
    // DerivedKey = HKDF(SessionKey, IV, "encryption", 32)
    uint8_t derivedKey[32];
    HKDF_sha256(
        sessionKey, 32,           // 主密钥
        iv, 16,                   // 盐值
        (uint8_t*)"encryption", 10,  // 上下文信息
        derivedKey, 32            // 输出
    );  // 地址: 0x2F05200
    
    // Step 3: 计算HMAC
    // HMAC = HMAC-SHA256(DerivedKey, Plaintext)
    uint8_t hmac[32];
    HMAC_SHA256(
        derivedKey, 32,           // 密钥
        plaintext, plainLen,      // 数据
        hmac                      // 输出
    );  // 地址: 0x2F04A00
    
    // Step 4: PKCS7填充
    size_t padLen = 16 - (plainLen % 16);
    size_t paddedLen = plainLen + padLen;
    uint8_t *padded = alloca(paddedLen);
    memcpy(padded, plaintext, plainLen);
    memset(padded + plainLen, padLen, padLen);
    
    // Step 5: AES-256-CBC加密
    AES_KEY aesKey;
    AES_set_encrypt_key(derivedKey, 256, &aesKey);  // 地址: 0x2F05300
    
    uint8_t *encrypted = output + 32;  // 密文位置
    uint8_t ivCopy[16];
    memcpy(ivCopy, iv, 16);
    
    AES_cbc_encrypt(
        padded,                   // 输入
        encrypted,                // 输出
        paddedLen,                // 长度
        &aesKey,                  // 密钥
        ivCopy,                   // IV
        AES_ENCRYPT               // 模式
    );  // 地址: 0x2F05400
    
    // Step 6: 组装输出
    memcpy(output, iv, 16);           // IV
    memcpy(output + 16, hmac, 16);    // HMAC (前16字节)
    // encrypted 已在正确位置
    
    *outputLen = 32 + paddedLen;
    
    // Step 7: 清理敏感数据
    secureZeroMemory(derivedKey, 32);
    secureZeroMemory(padded, paddedLen);
    
    return 0;
}
```

### 4.3 完整解密流程

```c
// 地址: 0x2F05500
int decryptNetworkPacket(
    const uint8_t *encrypted,    // 加密数据
    size_t encryptedLen,         // 加密长度
    const uint8_t *sessionKey,   // 会话密钥
    void *output,                // 输出明文
    size_t *outputLen            // 输出长度
) {
    // Step 1: 提取IV
    uint8_t iv[16];
    memcpy(iv, encrypted, 16);
    
    // Step 2: 提取HMAC
    uint8_t receivedHmac[16];
    memcpy(receivedHmac, encrypted + 16, 16);
    
    // Step 3: 派生解密密钥 (与加密相同)
    uint8_t derivedKey[32];
    HKDF_sha256(sessionKey, 32, iv, 16, 
                (uint8_t*)"encryption", 10, derivedKey, 32);
    
    // Step 4: 提取密文
    size_t cipherLen = encryptedLen - 32;
    const uint8_t *ciphertext = encrypted + 32;
    
    // Step 5: AES-256-CBC解密
    AES_KEY aesKey;
    AES_set_decrypt_key(derivedKey, 256, &aesKey);
    
    uint8_t *decrypted = alloca(cipherLen);
    uint8_t ivCopy[16];
    memcpy(ivCopy, iv, 16);
    
    AES_cbc_encrypt(
        ciphertext,
        decrypted,
        cipherLen,
        &aesKey,
        ivCopy,
        AES_DECRYPT
    );
    
    // Step 6: 去除PKCS7填充
    size_t padLen = decrypted[cipherLen - 1];
    *outputLen = cipherLen - padLen;
    memcpy(output, decrypted, *outputLen);
    
    // Step 7: 验证HMAC
    uint8_t computedHmac[32];
    HMAC_SHA256(derivedKey, 32, output, *outputLen, computedHmac);
    
    if (memcmp(receivedHmac, computedHmac, 16) != 0) {
        // HMAC验证失败，数据被篡改
        secureZeroMemory(output, *outputLen);
        *outputLen = 0;
        return ERROR_HMAC_VERIFICATION_FAILED;
    }
    
    // Step 8: 清理
    secureZeroMemory(derivedKey, 32);
    secureZeroMemory(decrypted, cipherLen);
    
    return 0;
}
```

---

## 5. 广播内容详细格式

### 5.1 房间状态广播 (0x0207)

```c
struct RoomStateBroadcast {
    // 协议头 (24 bytes)
    ProtocolHeader header;
    #define header.packetType 0x0207
    
    // 房间信息 (20 bytes)
    uint32_t roomId;              // 房间ID
    uint32_t hostId;              // 房主ID
    uint8_t state;                // 房间状态
    uint8_t maxPlayers;           // 最大人数
    uint8_t currentPlayers;       // 当前人数
    uint8_t gameMode;             // 游戏模式
    uint32_t mapId;               // 地图ID
    uint64_t elapsedTime;         // 已进行时间
    
    // 玩家信息 (每个36 bytes，最多8人)
    struct PlayerInfo {
        uint32_t playerId;        // 玩家ID
        char name[24];            // 玩家名称
        uint8_t isReady;          // 准备状态
        uint8_t isHost;           // 是否房主
        uint16_t ping;            // 延迟(ms)
        uint32_t score;           // 分数
    } players[8];
    
    // 校验 (4 bytes)
    uint32_t stateChecksum;       // 状态校验和
};
// 总大小: 24 + 20 + 36*8 + 4 = 336 bytes
```

**广播触发条件:**

| 事件 | 延迟 | 优先级 |
|------|------|--------|
| 玩家加入 | 立即 | 高 |
| 玩家离开 | 立即 | 高 |
| 准备状态改变 | 立即 | 中 |
| 房主变更 | 立即 | 高 |
| 游戏状态改变 | 立即 | 高 |
| 心跳周期 | 5秒 | 低 |

### 5.2 游戏状态广播 (0x0300)

```c
struct GameStateBroadcast {
    // 协议头 (24 bytes)
    ProtocolHeader header;
    #define header.packetType 0x0300
    
    // 帧信息 (16 bytes)
    uint32_t frameId;             // 帧ID
    uint64_t timestamp;           // 时间戳
    uint32_t gameTime;            // 游戏时间(秒)
    
    // 玩家状态 (每个64 bytes，最多8人)
    struct PlayerState {
        uint32_t playerId;        // 玩家ID
        
        // 位置 (12 bytes)
        float posX;               // X坐标
        float posY;               // Y坐标
        float posZ;               // Z坐标
        
        // 旋转 (12 bytes)
        float rotX;               // X旋转
        float rotY;               // Y旋转
        float rotZ;               // Z旋转
        
        // 速度 (12 bytes)
        float velX;               // X速度
        float velY;               // Y速度
        float velZ;               // Z速度
        
        // 状态 (20 bytes)
        uint32_t hp;              // 生命值
        uint32_t maxHp;           // 最大生命
        uint32_t mp;              // 魔法值
        uint32_t stateFlags;      // 状态标志
        uint8_t actionState;      // 动作状态
        uint8_t padding[3];
    } players[8];
    uint8_t playerCount;          // 玩家数量
    
    // 游戏对象 (每个24 bytes，最多64个)
    struct ObjectState {
        uint32_t objectId;        // 对象ID
        uint32_t objectType;      // 对象类型
        float posX, posY, posZ;   // 位置
        uint32_t state;           // 状态
        uint32_t ownerId;         // 所有者ID
    } objects[64];
    uint8_t objectCount;          // 对象数量
    
    // 全局状态 (16 bytes)
    uint32_t score[2];            // 双方分数
    uint8_t gamePhase;            // 游戏阶段
    uint8_t winner;               // 获胜方
    uint16_t reserved;
    uint32_t randomSeed;          // 随机种子
    
    // 校验 (4 bytes)
    uint32_t stateChecksum;       // 状态校验和
};
// 最大大小: 24 + 16 + 64*8 + 1 + 24*64 + 1 + 16 + 4 = 2154 bytes
```

**广播频率:**

| 场景 | 频率 | 带宽估算 |
|------|------|---------|
| 正常游戏 | 30 FPS | ~64 KB/s |
| 激烈战斗 | 60 FPS | ~128 KB/s |
| 休闲状态 | 10 FPS | ~21 KB/s |
| 关键状态 | 立即 | 突发 |

### 5.3 玩家加入广播 (0x0208 subtype 0x01)

```c
struct PlayerJoinedBroadcast {
    // 协议头 (24 bytes)
    ProtocolHeader header;
    #define header.packetType 0x0208
    
    // 消息类型 (1 byte)
    uint8_t msgSubType;           // 0x01 = PLAYER_JOINED
    
    // 玩家信息 (68 bytes)
    uint32_t roomId;              // 房间ID
    uint32_t playerId;            // 玩家ID
    char playerName[32];          // 玩家名称
    uint8_t isHost;               // 是否房主
    uint16_t level;               // 等级
    uint32_t rank;                // 段位
    uint64_t joinTime;            // 加入时间
    
    // 设备信息 (可选，32 bytes)
    char deviceModel[16];         // 设备型号
    char osVersion[16];           // 系统版本
};
```

---

## 6. 命令格式详细说明

### 6.1 输入命令 (0x0301)

```c
struct InputCommand {
    // 协议头 (24 bytes)
    ProtocolHeader header;
    #define header.packetType 0x0301
    
    // 命令序列 (12 bytes)
    uint32_t sequence;            // 序列号 (递增)
    uint32_t frameId;             // 目标帧
    uint64_t clientTimestamp;     // 客户端时间戳
    
    // 输入状态 (4 bytes)
    uint32_t inputFlags;          // 输入标志位
    /*
    Bit 0 (0x0001): UP - 上移
    Bit 1 (0x0002): DOWN - 下移
    Bit 2 (0x0004): LEFT - 左移
    Bit 3 (0x0008): RIGHT - 右移
    Bit 4 (0x0010): JUMP - 跳跃
    Bit 5 (0x0020): ATTACK - 攻击
    Bit 6 (0x0040): SKILL1 - 技能1
    Bit 7 (0x0080): SKILL2 - 技能2
    Bit 8 (0x0100): SKILL3 - 技能3
    Bit 9 (0x0200): INTERACT - 交互
    Bit 10 (0x0400): RELOAD - 换弹
    Bit 11 (0x0800): CROUCH - 蹲下
    Bit 12 (0x1000): SPRINT - 冲刺
    Bit 13-31: 保留
    */
    
    // 模拟输入 (8 bytes)
    float analogX;                // 摇杆X (-1.0 ~ 1.0)
    float analogY;                // 摇杆Y (-1.0 ~ 1.0)
    
    // 目标位置 (12 bytes)
    float targetX;                // 目标X
    float targetY;                // 目标Y
    float targetZ;                // 目标Z
    
    // 视角方向 (8 bytes)
    float viewYaw;                // 水平视角 (0 ~ 360)
    float viewPitch;              // 垂直视角 (-90 ~ 90)
    
    // 校验 (4 bytes)
    uint32_t checksum;            // 输入校验和
};
// 总大小: 72 bytes
```

**输入处理流程:**

```
客户端采集输入
    │
    ▼
┌─────────────────┐
│ 1. 本地预测      │
│ 立即应用到本地状态 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. 发送服务器    │
│ 带序列号和时间戳  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. 服务器处理    │
│ 验证并计算权威状态 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. 广播状态      │
│ 所有客户端同步    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. 客户端校正    │
│ 如有差异则回滚    │
└─────────────────┘
```

### 6.2 房间管理命令

```c
// 创建房间命令 (0x0200)
struct CreateRoomCommand {
    ProtocolHeader header;
    
    uint8_t gameMode;             // 游戏模式
    // 1=经典, 2=排位, 3=娱乐, 4=自定义
    
    uint8_t maxPlayers;           // 最大人数 (2-8)
    uint8_t isPrivate;            // 是否私有 (0/1)
    char password[16];            // 密码 (MD5)
    uint32_t mapId;               // 地图ID
    uint32_t matchRule;           // 匹配规则
    char roomName[32];            // 房间名称
};

// 准备命令 (0x0204)
struct ReadyCommand {
    ProtocolHeader header;
    
    uint8_t isReady;              // 准备状态 (0/1)
    uint8_t characterId;          // 选择角色
    uint32_t loadoutId;           // 装备配置
};

// 开始游戏命令 (0x0205)
struct StartGameCommand {
    ProtocolHeader header;
    
    uint32_t hostId;              // 房主ID (验证)
    uint8_t forceStart;           // 强制开始 (0/1)
};
```

---

## 7. 安全检测点

### 7.1 内存检测点

| 地址 | 检测内容 | 检测频率 |
|------|---------|---------|
| 0xA951000 | 玩家数据完整性 | 每秒 |
| 0xA952000 | 房间数据完整性 | 每秒 |
| 0xA953000 | 游戏状态完整性 | 每帧 |
| 0x2EBF000 | 代码段完整性 | 每5秒 |
| 0xA950E20 | 密钥数据保护 | 实时 |

### 7.2 网络检测点

| 检测项 | 阈值 | 响应 |
|--------|------|------|
| 包频率异常 | >100包/秒 | 限流 |
| 包大小异常 | >2KB | 丢弃 |
| 序列号跳跃 | >10 | 断连 |
| 时间戳异常 | >5秒偏差 | 校正 |
| HMAC失败 | >3次 | 踢出 |

### 7.3 行为检测点

| 检测项 | 阈值 | 响应 |
|--------|------|------|
| 移动速度 | >150% | 标记 |
| 瞄准精度 | >99% | 标记 |
| 操作频率 | >20次/秒 | 限流 |
| 透视嫌疑 | >5次 | 观察 |
| 自动化 | 标准差<5ms | 标记 |

---

## 8. 安全建议

### 8.1 客户端加固

1. **代码混淆**
   - 使用OLLVM进行控制流平坦化
   - 字符串加密
   - 反符号化

2. **完整性保护**
   - 代码段签名验证
   - 运行时完整性检查
   - SO加载白名单

3. **反调试增强**
   - 多线程交叉检测
   - 调试寄存器监控
   - 时间异常检测

### 8.2 服务器加固

1. **输入验证**
   - 速度限制检查
   - 物理可行性验证
   - 历史行为对比

2. **状态同步**
   - 权威服务器模型
   - 客户端预测限制
   - 异常状态回滚

3. **风控系统**
   - 实时风险评分
   - 行为模式分析
   - 设备指纹识别

---

*文档版本: 1.0*
*最后更新: 2026-04-24*
*分类: 机密*
