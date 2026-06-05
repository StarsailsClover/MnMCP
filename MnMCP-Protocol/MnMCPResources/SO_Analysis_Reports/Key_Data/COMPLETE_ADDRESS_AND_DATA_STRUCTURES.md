# 完整地址映射与数据结构手册

## 1. 全局地址空间映射

### 1.1 代码段 (.text)

| 起始地址 | 结束地址 | 大小 | 所属SO | 功能描述 |
|----------|----------|------|--------|----------|
| 0x2EBF000 | 0x3EBEFFF | 16 MB | liblibGameApp.so | 游戏主逻辑代码 |
| 0x1000000 | 0x1020000 | 2 MB | libMiniTechLoader.so | 加载器代码 |
| 0x2000000 | 0x2020000 | 2 MB | libEncryptor.so | 加密算法代码 |
| 0x3000000 | 0x3020000 | 2 MB | libilink_network.so | 网络协议代码 |
| 0x4000000 | 0x4010000 | 1 MB | libInnoSecure.so | 安全防护代码 |
| 0x5000000 | 0x5010000 | 1 MB | libqmcheat.so | 作弊检测代码 |
| 0x6000000 | 0x6010000 | 1 MB | libtersafe2.so | 腾讯反作弊代码 |
| 0x7000000 | 0x7010000 | 1 MB | libsgcore.so | 腾讯安全核心代码 |

### 1.2 数据段 (.data/.bss)

| 起始地址 | 结束地址 | 大小 | 所属SO | 功能描述 |
|----------|----------|------|--------|----------|
| 0xA950000 | 0xA960000 | 64 KB | liblibGameApp.so | 全局变量区 |
| 0xA970000 | 0xA980000 | 64 KB | libilink_network.so | 网络数据区 |
| 0xA990000 | 0xA9A0000 | 64 KB | libEncryptor.so | 密钥存储区 |
| 0xA9B0000 | 0xA9C0000 | 64 KB | libInnoSecure.so | 安全数据区 |
| 0xA9D0000 | 0xA9E0000 | 64 KB | libqmcheat.so | 检测数据区 |

### 1.3 堆内存区

| 起始地址 | 大小 | 用途 |
|----------|------|------|
| 0xB0000000 | 256 MB | 游戏对象分配 |
| 0xC0000000 | 128 MB | 纹理资源 |
| 0xC8000000 | 128 MB | 音频资源 |
| 0xD0000000 | 256 MB | 网络缓冲区 |

---

## 2. 关键数据结构详细定义

### 2.1 玩家数据结构 (Player) - 地址: 0xA951000

```c
// 完整玩家结构体 - 256 bytes
struct Player {
    // === 基础信息 (64 bytes) ===
    uint32_t playerId;                    // 0x00: 玩家ID
    uint32_t accountId;                   // 0x04: 账号ID
    char nickname[32];                    // 0x08: 昵称
    uint8_t level;                        // 0x28: 等级
    uint8_t vipLevel;                     // 0x29: VIP等级
    uint16_t titleId;                     // 0x2A: 称号ID
    uint32_t exp;                         // 0x2C: 经验值
    uint32_t totalExp;                    // 0x30: 总经验
    uint32_t gold;                        // 0x34: 金币
    uint32_t diamond;                     // 0x38: 钻石
    uint32_t honor;                       // 0x3C: 荣誉点
    
    // === 位置信息 (48 bytes) ===
    float posX;                           // 0x40: X坐标
    float posY;                           // 0x44: Y坐标
    float posZ;                           // 0x48: Z坐标
    float rotX;                           // 0x4C: X旋转 (俯仰)
    float rotY;                           // 0x50: Y旋转 (偏航)
    float rotZ;                           // 0x52: Z旋转 (翻滚)
    float velX;                           // 0x54: X速度
    float velY;                           // 0x58: Y速度
    float velZ;                           // 0x5C: Z速度
    float scale;                          // 0x60: 缩放
    uint32_t mapId;                       // 0x64: 地图ID
    uint32_t instanceId;                  // 0x68: 副本ID
    uint8_t padding1[4];                  // 0x6C: 填充
    
    // === 战斗属性 (48 bytes) ===
    uint32_t hp;                          // 0x70: 当前生命
    uint32_t maxHp;                       // 0x74: 最大生命
    uint32_t mp;                          // 0x78: 当前魔法
    uint32_t maxMp;                       // 0x7C: 最大魔法
    uint32_t attack;                      // 0x80: 攻击力
    uint32_t defense;                     // 0x84: 防御力
    uint32_t magicAttack;                 // 0x88: 魔法攻击
    uint32_t magicDefense;                // 0x8C: 魔法防御
    uint32_t critRate;                    // 0x90: 暴击率
    uint32_t critDamage;                  // 0x94: 暴击伤害
    uint32_t moveSpeed;                   // 0x98: 移动速度
    uint32_t attackSpeed;                 // 0x9C: 攻击速度
    
    // === 状态标志 (16 bytes) ===
    uint32_t stateFlags;                  // 0xA0: 状态标志
    // Bit 0: 是否在线
    // Bit 1: 是否战斗中
    // Bit 2: 是否死亡
    // Bit 3: 是否眩晕
    // Bit 4: 是否沉默
    // Bit 5: 是否无敌
    // Bit 6: 是否隐身
    // Bit 7: 是否坐骑上
    // Bit 8-31: 保留
    
    uint32_t actionState;                 // 0xA4: 动作状态
    // 0=空闲, 1=移动, 2=攻击, 3=施法, 4=受伤, 5=死亡
    
    uint32_t buffFlags;                   // 0xA8: Buff标志
    uint32_t debuffFlags;                 // 0xAC: Debuff标志
    
    // === 网络信息 (16 bytes) ===
    uint32_t ping;                        // 0xB0: 延迟(ms)
    uint64_t lastHeartbeat;               // 0xB4: 最后心跳时间
    
    // === 背包信息 (16 bytes) ===
    uint32_t bagSize;                     // 0xBC: 背包大小
    uint32_t bagUsed;                     // 0xC0: 已用空间
    void *bagItems;                       // 0xC4: 物品数组指针
    
    // === 装备信息 (32 bytes) ===
    struct {
        uint32_t itemId;
        uint32_t enhanceLevel;
    } equipments[8];                      // 0xC8 - 0xE8
    // 0=武器, 1=头盔, 2=护甲, 3=护腿, 4=鞋子, 5=项链, 6=戒指, 7=饰品
    
    // === 技能信息 (16 bytes) ===
    void *skillList;                      // 0xE8: 技能列表指针
    uint32_t skillPoints;                 // 0xEC: 技能点
    
    // === 社交信息 (16 bytes) ===
    uint32_t guildId;                     // 0xF0: 公会ID
    uint32_t teamId;                      // 0xF4: 队伍ID
    uint32_t friendCount;                 // 0xF8: 好友数量
    uint8_t padding2[4];                  // 0xFC: 填充
};  // 总大小: 256 bytes (0x100)
```

### 2.2 房间数据结构 (Room) - 地址: 0xA952000

```c
// 完整房间结构体 - 2048 bytes
struct Room {
    // === 基本信息 (32 bytes) ===
    uint32_t roomId;                      // 0x00: 房间ID
    uint32_t hostId;                      // 0x04: 房主ID
    uint8_t state;                        // 0x08: 房间状态
    // 0=IDLE, 1=CREATING, 2=WAITING, 3=PREPARING, 4=PLAYING, 5=ENDING, 6=CLOSED
    
    uint8_t gameMode;                     // 0x09: 游戏模式
    // 1=经典, 2=排位, 3=娱乐, 4=自定义
    
    uint8_t maxPlayers;                   // 0x0A: 最大人数
    uint8_t currentPlayers;               // 0x0B: 当前人数
    uint32_t mapId;                       // 0x0C: 地图ID
    uint32_t matchRule;                   // 0x10: 匹配规则
    uint64_t createTime;                  // 0x14: 创建时间
    uint64_t startTime;                   // 0x1C: 开始时间
    
    // === 配置信息 (32 bytes) ===
    uint8_t isPrivate;                    // 0x24: 是否私有
    uint8_t hasPassword;                  // 0x25: 是否有密码
    char password[16];                    // 0x26: 密码(MD5)
    uint16_t minLevel;                    // 0x36: 最低等级
    uint16_t maxLevel;                    // 0x38: 最高等级
    uint8_t allowSpectator;               // 0x3A: 允许观战
    uint8_t voiceChat;                    // 0x3B: 语音聊天
    
    // === 玩家信息 (1152 bytes = 36 * 32) ===
    struct RoomPlayer {
        uint32_t playerId;                // 玩家ID
        char nickname[24];                // 昵称
        uint8_t isHost;                   // 是否房主
        uint8_t isReady;                  // 是否准备
        uint8_t slot;                     // 位置
        uint8_t team;                     // 队伍
        uint32_t characterId;             // 角色ID
        uint32_t skinId;                  // 皮肤ID
        uint16_t level;                   // 等级
        uint16_t rank;                    // 段位
        uint32_t ping;                    // 延迟
        uint64_t joinTime;                // 加入时间
        uint8_t isBot;                    // 是否机器人
        uint8_t padding[7];               // 填充
    } players[32];                        // 0x40 - 0x4C0
    
    // === 游戏状态 (256 bytes) ===
    struct {
        uint32_t currentFrame;            // 当前帧
        uint32_t gameTime;                // 游戏时间(秒)
        uint32_t score[2];                // 双方分数
        uint8_t winner;                   // 获胜方
        uint8_t gamePhase;                // 游戏阶段
        uint16_t reserved;
        uint32_t randomSeed;              // 随机种子
        uint64_t lastSyncTime;            // 最后同步时间
        uint32_t syncFrame;               // 同步帧
    } gameState;                          // 0x4C0 - 0x5C0
    
    // === 网络信息 (64 bytes) ===
    int serverSocket;                     // 0x5C0: 服务器连接
    uint32_t serverAddr;                  // 0x5C4: 服务器地址
    uint16_t serverPort;                  // 0x5C8: 服务器端口
    uint8_t roomKey[32];                  // 0x5CA: 房间密钥
    uint8_t padding3[2];                  // 填充
    
    // === 统计信息 (64 bytes) ===
    uint32_t totalKills;                  // 0x5F0: 总击杀
    uint32_t totalDeaths;                 // 0x5F4: 总死亡
    uint32_t totalAssists;                // 0x5F8: 总助攻
    uint32_t totalDamage;                 // 0x5FC: 总伤害
    uint32_t totalHeal;                   // 0x600: 总治疗
    uint32_t matchDuration;               // 0x604: 对局时长
    uint8_t padding4[8];                  // 填充
    
    // === 消息队列 (512 bytes) ===
    struct {
        uint32_t head;                    // 队列头
        uint32_t tail;                    // 队列尾
        uint32_t count;                   // 消息数量
        uint32_t maxCount;                // 最大数量
        void *messages;                   // 消息数组指针
    } msgQueue;                           // 0x610 - 0x620
    uint8_t msgBuffer[496];               // 0x620 - 0x810
    
    // === 回调函数 (16 bytes) ===
    void (*onPlayerJoin)(uint32_t);       // 0x810
    void (*onPlayerLeave)(uint32_t);      // 0x818
    void (*onGameStart)();                // 0x820
    void (*onGameEnd)();                  // 0x828
    
    // === 互斥锁 (16 bytes) ===
    pthread_mutex_t lock;                 // 0x830
    
    // === 保留空间 (144 bytes) ===
    uint8_t reserved[144];                // 0x840 - 0x8D0
};  // 总大小: 2048 bytes (0x800)
```

### 2.3 游戏状态结构 (GameState) - 地址: 0xA953000

```c
// 游戏状态结构体 - 4096 bytes
struct GameState {
    // === 帧信息 (16 bytes) ===
    uint32_t frameId;                     // 0x00: 帧ID
    uint64_t timestamp;                   // 0x04: 时间戳
    uint32_t deltaTime;                   // 0x0C: 帧间隔(ms)
    
    // === 玩家状态数组 (1024 bytes = 8 * 128) ===
    struct GamePlayerState {
        uint32_t playerId;                // 玩家ID
        uint32_t team;                    // 队伍
        
        // 位置 (24 bytes)
        float posX, posY, posZ;           // 位置
        float rotX, rotY, rotZ;           // 旋转
        float velX, velY, velZ;           // 速度
        
        // 状态 (16 bytes)
        uint32_t hp;                      // 生命值
        uint32_t maxHp;                   // 最大生命
        uint32_t mp;                      // 魔法值
        uint32_t stateFlags;              // 状态标志
        
        // 动画 (8 bytes)
        uint32_t animState;               // 动画状态
        float animTime;                   // 动画时间
        
        // 输入 (16 bytes)
        uint32_t inputFlags;              // 输入标志
        float analogX, analogY;           // 摇杆
        
        // 目标 (16 bytes)
        float targetX, targetY, targetZ;  // 目标位置
        uint32_t targetId;                // 目标ID
        
        // 技能 (16 bytes)
        uint32_t skillId;                 // 当前技能
        float skillTime;                  // 技能时间
        uint32_t cooldowns[2];            // 冷却时间
        
        // 统计 (8 bytes)
        uint32_t killCount;               // 击杀数
        uint32_t score;                   // 分数
    } players[8];                         // 0x10 - 0x410
    uint8_t playerCount;                  // 0x410: 玩家数量
    uint8_t padding1[15];                 // 填充
    
    // === 游戏对象数组 (1536 bytes = 64 * 24) ===
    struct GameObject {
        uint32_t objectId;                // 对象ID
        uint32_t objectType;              // 对象类型
        float posX, posY, posZ;           // 位置
        float rotX, rotY, rotZ;           // 旋转
        uint32_t state;                   // 状态
        uint32_t ownerId;                 // 所有者ID
    } objects[64];                        // 0x420 - 0xA20
    uint8_t objectCount;                  // 0xA20: 对象数量
    uint8_t padding2[15];                 // 填充
    
    // === 技能效果数组 (512 bytes = 32 * 16) ===
    struct SkillEffect {
        uint32_t effectId;                // 效果ID
        uint32_t skillId;                 // 技能ID
        uint32_t casterId;                // 施法者ID
        uint32_t targetId;                // 目标ID
        float posX, posY, posZ;           // 位置
        float duration;                   // 持续时间
        float elapsed;                    // 已持续时间
    } effects[32];                        // 0xA30 - 0xC30
    uint8_t effectCount;                  // 0xC30: 效果数量
    uint8_t padding3[15];                 // 填充
    
    // === 伤害事件数组 (512 bytes = 32 * 16) ===
    struct DamageEvent {
        uint32_t attackerId;              // 攻击者ID
        uint32_t victimId;                // 受害者ID
        uint32_t damage;                  // 伤害值
        uint32_t damageType;              // 伤害类型
        float posX, posY, posZ;           // 位置
        uint32_t flags;                   // 标志
    } damageEvents[32];                   // 0xC40 - 0xE40
    uint8_t damageEventCount;             // 0xE40: 事件数量
    uint8_t padding4[15];                 // 填充
    
    // === 全局状态 (64 bytes) ===
    uint32_t gameTime;                    // 0xE50: 游戏时间
    uint32_t timeLimit;                   // 0xE54: 时间限制
    uint32_t score[2];                    // 0xE58: 双方分数
    uint8_t gamePhase;                    // 0xE60: 游戏阶段
    uint8_t winner;                       // 0xE61: 获胜方
    uint16_t reserved1;                   // 保留
    uint32_t randomSeed;                  // 0xE64: 随机种子
    uint32_t frameCount;                  // 0xE68: 帧计数
    float gameSpeed;                      // 0xE6C: 游戏速度
    uint64_t startTime;                   // 0xE70: 开始时间
    uint64_t endTime;                     // 0xE78: 结束时间
    uint8_t reserved2[8];                 // 保留
    
    // === 校验和 (4 bytes) ===
    uint32_t checksum;                    // 0xE80: 状态校验和
    
    // === 保留空间 (376 bytes) ===
    uint8_t reserved3[376];               // 0xE84 - 0x1000
};  // 总大小: 4096 bytes (0x1000)
```

---

## 3. 网络协议数据结构

### 3.1 协议头结构 (24 bytes)

```c
// 协议头 - 地址: 协议包偏移0
struct ProtocolHeader {
    // 魔数和版本 (4 bytes)
    uint16_t magic;                       // 0x00: 魔数 'KG' = 0x4B47
    uint16_t version;                     // 0x02: 协议版本
    
    // 序列和时间 (8 bytes)
    uint32_t packetId;                    // 0x04: 包序列号
    uint32_t timestamp;                   // 0x08: 时间戳(ms)
    
    // 类型和标志 (4 bytes)
    uint16_t packetType;                  // 0x0C: 包类型
    uint16_t flags;                       // 0x0E: 标志位
    // Bit 0: FLAG_ENCRYPTED - 已加密
    // Bit 1: FLAG_COMPRESSED - 已压缩
    // Bit 2: FLAG_ACK - 确认包
    // Bit 3: FLAG_RELIABLE - 可靠传输
    // Bit 4: FLAG_BROADCAST - 广播包
    // Bit 5-15: 保留
    
    // 长度信息 (8 bytes)
    uint32_t payloadLen;                  // 0x10: 负载长度
    uint32_t checksum;                    // 0x14: 校验和
};  // 总大小: 24 bytes (0x18)
```

### 3.2 加密头结构 (32 bytes)

```c
// 加密头 - 地址: 加密包偏移0
struct EncryptionHeader {
    uint8_t iv[16];                       // 0x00: 初始化向量
    uint8_t hmac[16];                     // 0x10: HMAC前16字节
};  // 总大小: 32 bytes (0x20)

// 完整加密包格式
struct EncryptedPacket {
    EncryptionHeader header;              // 0x00: 加密头
    uint8_t ciphertext[];                 // 0x20: 密文数据
};
```

### 3.3 输入命令结构 (72 bytes)

```c
// 输入命令 - 地址: 游戏输入缓冲区
struct InputCommand {
    // 序列信息 (16 bytes)
    uint32_t sequence;                    // 0x00: 序列号
    uint32_t frameId;                     // 0x04: 目标帧
    uint64_t timestamp;                   // 0x08: 时间戳
    
    // 输入标志 (4 bytes)
    uint32_t inputFlags;                  // 0x10: 输入标志
    // Bit 0: UP - 上移
    // Bit 1: DOWN - 下移
    // Bit 2: LEFT - 左移
    // Bit 3: RIGHT - 右移
    // Bit 4: JUMP - 跳跃
    // Bit 5: ATTACK - 攻击
    // Bit 6: SKILL1 - 技能1
    // Bit 7: SKILL2 - 技能2
    // Bit 8: SKILL3 - 技能3
    // Bit 9: INTERACT - 交互
    // Bit 10: RELOAD - 换弹
    // Bit 11: CROUCH - 蹲下
    // Bit 12: SPRINT - 冲刺
    // Bit 13: AIM - 瞄准
    // Bit 14: FIRE - 开火
    // Bit 15-31: 保留
    
    // 模拟输入 (8 bytes)
    float analogX;                        // 0x14: 摇杆X (-1.0 ~ 1.0)
    float analogY;                        // 0x18: 摇杆Y (-1.0 ~ 1.0)
    
    // 目标位置 (12 bytes)
    float targetX;                        // 0x1C: 目标X
    float targetY;                        // 0x20: 目标Y
    float targetZ;                        // 0x24: 目标Z
    
    // 视角方向 (8 bytes)
    float viewYaw;                        // 0x28: 水平视角 (0 ~ 360)
    float viewPitch;                      // 0x2C: 垂直视角 (-90 ~ 90)
    
    // 额外数据 (16 bytes)
    uint32_t extraFlags;                  // 0x30: 额外标志
    float extraFloat1;                    // 0x34: 额外浮点1
    float extraFloat2;                    // 0x38: 额外浮点2
    float extraFloat3;                    // 0x3C: 额外浮点3
    
    // 校验和 (4 bytes)
    uint32_t checksum;                    // 0x40: 校验和
    
    // 填充 (8 bytes)
    uint8_t padding[8];                   // 0x44 - 0x48
};  // 总大小: 72 bytes (0x48)
```

---

## 4. 密钥数据结构

### 4.1 密钥层次结构

```c
// 主密钥结构 - 地址: 0xA02000
struct MasterKey {
    uint8_t key[32];                      // 密钥数据
    uint32_t version;                     // 密钥版本
    uint64_t createTime;                  // 创建时间
    uint64_t expireTime;                  // 过期时间
    uint8_t algorithm;                    // 算法类型
    // 1=AES-128, 2=AES-192, 3=AES-256
    uint8_t status;                       // 状态
    // 0=无效, 1=有效, 2=过期, 3=撤销
    uint8_t padding[6];                   // 填充
};  // 总大小: 56 bytes

// 会话密钥结构 - 地址: 0xA950E20
struct SessionKey {
    uint8_t key[32];                      // 密钥数据
    uint32_t sessionId;                   // 会话ID
    uint64_t createTime;                  // 创建时间
    uint64_t lastUsed;                    // 最后使用时间
    uint32_t useCount;                    // 使用次数
    uint8_t status;                       // 状态
    uint8_t padding[3];                   // 填充
};  // 总大小: 56 bytes

// 派生密钥结构 (临时)
struct DerivedKey {
    uint8_t key[32];                      // 密钥数据
    uint8_t salt[16];                     // 盐值
    uint8_t context[32];                  // 上下文信息
    uint32_t iteration;                   // 迭代次数
};  // 总大小: 84 bytes

// 房间密钥结构 - 地址: Room结构体 + 0x5CA
struct RoomKey {
    uint8_t key[32];                      // 密钥数据
    uint32_t roomId;                      // 房间ID
    uint64_t createTime;                  // 创建时间
    uint8_t status;                       // 状态
    uint8_t padding[3];                   // 填充
};  // 总大小: 44 bytes
```

### 4.2 密钥派生参数

```c
// HKDF参数
struct HKDFParams {
    const char *algorithm;                // "sha256"
    uint8_t *salt;                        // 盐值指针
    size_t saltLen;                       // 盐值长度 (16)
    uint8_t *info;                        // 上下文信息
    size_t infoLen;                       // 信息长度
    size_t outputLen;                     // 输出长度 (32)
};

// 标准派生路径
// MasterKey -> SessionKey: HKDF(master, device_salt, "session", 32)
// SessionKey -> DerivedKey: HKDF(session, packet_iv, "encryption", 32)
// SessionKey -> RoomKey: HKDF(session, room_salt, "room", 32)
```

---

## 5. 广播数据结构

### 5.1 房间状态广播 (0x0207)

```c
// 房间状态广播 - 336 bytes
struct RoomStateBroadcast {
    ProtocolHeader header;                // 24 bytes
    
    // 房间信息 (20 bytes)
    uint32_t roomId;                      // 房间ID
    uint32_t hostId;                      // 房主ID
    uint8_t state;                        // 状态
    uint8_t maxPlayers;                   // 最大人数
    uint8_t currentPlayers;               // 当前人数
    uint8_t gameMode;                     // 游戏模式
    uint32_t mapId;                       // 地图ID
    uint64_t elapsedTime;                 // 已进行时间
    
    // 玩家信息 (每个36 bytes，最多8人 = 288 bytes)
    struct BroadcastPlayerInfo {
        uint32_t playerId;                // 玩家ID
        char name[24];                    // 名称
        uint8_t isReady;                  // 准备状态
        uint8_t isHost;                   // 是否房主
        uint16_t ping;                    // 延迟
        uint32_t score;                   // 分数
    } players[8];
    
    // 校验 (4 bytes)
    uint32_t stateChecksum;               // 状态校验和
};  // 总大小: 336 bytes
```

### 5.2 游戏状态广播 (0x0300)

```c
// 游戏状态广播 - 最大2154 bytes
struct GameStateBroadcast {
    ProtocolHeader header;                // 24 bytes
    
    // 帧信息 (16 bytes)
    uint32_t frameId;                     // 帧ID
    uint64_t timestamp;                   // 时间戳
    uint32_t gameTime;                    // 游戏时间
    
    // 玩家状态 (每个64 bytes，最多8人 = 512 bytes)
    struct BroadcastPlayerState {
        uint32_t playerId;                // 玩家ID
        float posX, posY, posZ;           // 位置
        float rotX, rotY, rotZ;           // 旋转
        float velX, velY, velZ;           // 速度
        uint32_t hp;                      // 生命值
        uint32_t maxHp;                   // 最大生命
        uint32_t mp;                      // 魔法值
        uint32_t stateFlags;              // 状态标志
        uint8_t actionState;              // 动作状态
        uint8_t padding[3];
    } players[8];
    uint8_t playerCount;                  // 玩家数量
    uint8_t padding1[7];
    
    // 游戏对象 (每个24 bytes，最多64个 = 1536 bytes)
    struct BroadcastObjectState {
        uint32_t objectId;                // 对象ID
        uint32_t objectType;              // 对象类型
        float posX, posY, posZ;           // 位置
        uint32_t state;                   // 状态
        uint32_t ownerId;                 // 所有者ID
    } objects[64];
    uint8_t objectCount;                  // 对象数量
    uint8_t padding2[7];
    
    // 全局状态 (16 bytes)
    uint32_t score[2];                    // 双方分数
    uint8_t gamePhase;                    // 游戏阶段
    uint8_t winner;                       // 获胜方
    uint16_t reserved;
    uint32_t randomSeed;                  // 随机种子
    
    // 校验 (4 bytes)
    uint32_t stateChecksum;               // 状态校验和
};  // 最大大小: 2154 bytes
```

---

## 6. 校验和算法

### 6.1 协议校验和

```c
// 地址: 0x2F04A00
uint32_t calculateProtocolChecksum(const void *data, size_t len) {
    const uint8_t *bytes = (const uint8_t*)data;
    uint32_t checksum = 0;
    
    for (size_t i = 0; i < len; i++) {
        // 循环左移8位 + 加法
        checksum = ((checksum << 8) | (checksum >> 24)) & 0xFFFFFFFF;
        checksum = (checksum + bytes[i]) & 0xFFFFFFFF;
    }
    
    return checksum;
}
```

### 6.2 状态校验和

```c
// 地址: 0x2F04B00
uint32_t calculateStateChecksum(const GameState *state) {
    uint32_t checksum = 0;
    
    // 校验帧信息
    checksum ^= state->frameId;
    checksum ^= (uint32_t)(state->timestamp >> 32);
    checksum ^= (uint32_t)state->timestamp;
    
    // 校验玩家状态
    for (int i = 0; i < state->playerCount; i++) {
        const GamePlayerState *player = &state->players[i];
        checksum ^= player->playerId;
        checksum ^= *(uint32_t*)&player->posX;
        checksum ^= *(uint32_t*)&player->posY;
        checksum ^= player->hp;
    }
    
    // 校验游戏对象
    for (int i = 0; i < state->objectCount; i++) {
        const GameObject *obj = &state->objects[i];
        checksum ^= obj->objectId;
        checksum ^= *(uint32_t*)&obj->posX;
    }
    
    // 校验全局状态
    checksum ^= state->score[0];
    checksum ^= state->score[1];
    checksum ^= state->gamePhase;
    
    return checksum;
}
```

---

*文档版本: 1.0*
*生成时间: 2026-04-24*
*分类: 机密*
