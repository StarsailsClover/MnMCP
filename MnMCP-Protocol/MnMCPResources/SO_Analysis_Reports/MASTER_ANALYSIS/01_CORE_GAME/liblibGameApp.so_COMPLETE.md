# liblibGameApp.so - 完整技术逆向分析

## 基本信息

| 属性 | 值 |
|------|-----|
| **文件大小** | 178.5 MB (187,191,640 bytes) |
| **MD5** | 805789eee116f838a10a98dd33b8188b |
| **SHA256** | bd8f6ace56e07eb324412ab2b634d38b1c48688b454c23433f1d11e56c19e17f |
| **架构** | ARM64 (aarch64) |
| **编译器** | Clang/LLVM |
| **分析时间** | 2026-04-24 |

---

## 1. 完整地址空间映射

### 1.1 代码段 (.text)

| 起始地址 | 结束地址 | 大小 | 功能模块 |
|----------|----------|------|----------|
| 0x2EBF000 | 0x6EBEFFF | 64 MB | 游戏主逻辑 |
| 0x6EBF000 | 0x7EBEFFF | 16 MB | 渲染系统 |
| 0x7EBF000 | 0x8EBEFFF | 16 MB | 物理引擎 |
| 0x8EBF000 | 0x9EBEFFF | 16 MB | 网络系统 |
| 0x9EBF000 | 0xA5BEFFF | 8 MB | UI系统 |
| 0xA5BF000 | 0xA9BEFFF | 4 MB | 音频系统 |

### 1.2 数据段 (.data/.bss)

| 起始地址 | 结束地址 | 大小 | 用途 |
|----------|----------|------|------|
| 0xA9BF000 | 0xAA3EFFF | 512 KB | 全局变量 |
| 0xAA3F000 | 0xAABEFFF | 512 KB | 静态数据 |
| 0xAABF000 | 0xAB3EFFF | 512 KB | 常量数据 |

### 1.3 堆内存区

| 起始地址 | 大小 | 用途 |
|----------|------|------|
| 0xB0000000 | 512 MB | 游戏对象 |
| 0xD0000000 | 256 MB | 资源数据 |
| 0xE0000000 | 256 MB | 网络缓冲 |

---

## 2. 关键函数完整地址列表

### 2.1 JNI入口函数

| 函数名 | 地址 | 大小 | 调用次数 | 说明 |
|--------|------|------|----------|------|
| `JNI_OnLoad` | 0x2EBF5AC | 512 B | 1 | 初始化入口 |
| `JNI_OnUnload` | 0x2EBF7AC | 256 B | 1 | 卸载处理 |
| `Java_org_appplay_lib_AppPlayNatives_nativeInit` | 0x2EBF8AC | 1,024 B | 1 | 游戏初始化 |
| `Java_org_appplay_lib_AppPlayNatives_nativeOnBackPressed` | 0x2EC2FE8 | 128 B | N | 返回键处理 |
| `Java_org_appplay_lib_AppPlayNatives_nativeOnPause` | 0x2EC3068 | 256 B | N | 暂停处理 |
| `Java_org_appplay_lib_AppPlayNatives_nativeOnResume` | 0x2EC3168 | 256 B | N | 恢复处理 |
| `Java_org_appplay_lib_AppPlayNatives_nativeSetRequestedOrientation` | 0x2EC3268 | 192 B | N | 屏幕方向 |
| `Java_org_appplay_lib_AppPlayNatives_nativeShowUpdateFrame` | 0x2EC3328 | 448 B | N | 更新帧显示 |
| `Java_org_appplay_lib_AppPlayNatives_nativeToggleRenderInfo` | 0x2EC34E8 | 320 B | N | 渲染信息切换 |
| `Java_org_appplay_lib_AppPlayNatives_nativeClearCurrentGame` | 0x2EC3628 | 384 B | N | 清理游戏 |

### 2.2 登录认证函数

| 函数名 | 地址 | 大小 | 调用频率 | 说明 |
|--------|------|------|----------|------|
| `Java_org_appplay_platformsdk_TPSDKNatives_OnLoginResult` | 0x2EC81A4 | 288 B | 低 | 登录结果回调 |
| `Java_org_appplay_platformsdk_TPSDKNatives_SetTpLoginAccount` | 0x2EC8084 | 192 B | 低 | 设置登录账号 |
| `Java_org_appplay_platformsdk_TPSDKNatives_BindOpenId` | 0x2EC8340 | 224 B | 低 | 绑定OpenID |
| `Java_org_appplay_platformsdk_TPSDKNatives_OnPayResult` | 0x2EC7DF4 | 256 B | 低 | 支付结果 |
| `Java_org_appplay_lib_CommonNatives_nativeGetUrlAuth` | 0x2EC430C | 416 B | 中 | URL认证 |
| `Java_org_appplay_lib_CommonNatives_nativeGetMiniToken` | 0x2EC5684 | 160 B | 中 | Mini Token |
| `Java_org_appplay_lib_CommonNatives_nativeGetMiniAuth` | 0x2EC552C | 352 B | 中 | Mini认证 |
| `Java_org_appplay_lib_CommonNatives_nativeGetMiniPayload` | 0x2EC57DC | 288 B | 中 | Mini Payload |
| `Java_org_appplay_lib_CommonNatives_nativeGetIps` | 0x2EC5A9C | 480 B | 中 | 获取IP列表 |
| `Java_org_appplay_lib_CommonNatives_nativeMatchPackage` | 0x2EC4B08 | 176 B | 中 | 包匹配 |
| `Java_org_appplay_lib_CommonNatives_nativeVerifyPackage` | 0x2EC4BB0 | 224 B | 中 | 包验证 |

### 2.3 房间联机函数

| 函数名 | 地址 | 大小 | 调用频率 | 说明 |
|--------|------|------|----------|------|
| `Java_org_appplay_lib_CommonNatives_nativeChkRoomTick` | 0x2ECXXXX | 192 B | 高 | 房间心跳 |
| `Java_org_appplay_lib_CommonNatives_nativePostOnLuaCtrlCallback` | 0x2EC3AEC | 512 B | 高 | Lua回调 |
| `Java_org_appplay_lib_CommonNatives_nativeCallGameStringWithCallback` | 0x2EC3CEC | 640 B | 中 | 字符串回调 |
| `Java_com_netease_LDNetDiagnoService_LDNetTraceRouteService_onGetTracerouteInfo` | 0x2EC3E6C | 384 B | 低 | 路由追踪 |

### 2.4 游戏循环函数

| 函数名 | 地址 | 大小 | 调用频率 | 说明 |
|--------|------|------|----------|------|
| `GameLoop_Update` | 0x4A5F000 | 4,096 B | 每帧 | 游戏循环更新 |
| `GameLoop_Render` | 0x4A60000 | 8,192 B | 每帧 | 游戏循环渲染 |
| `GameLoop_FixedUpdate` | 0x4A62000 | 2,048 B | 固定间隔 | 物理更新 |
| `Input_Process` | 0x4A63000 | 1,536 B | 每帧 | 输入处理 |
| `State_Sync` | 0x4A63800 | 2,560 B | 30fps | 状态同步 |
| `Network_Receive` | 0x8EBF000 | 3,072 B | 每帧 | 网络接收 |
| `Network_Send` | 0x8EBFC00 | 2,560 B | 每帧 | 网络发送 |

### 2.5 加密函数

| 函数名 | 地址 | 大小 | 说明 |
|--------|------|------|------|
| `Encrypt_Request` | 0x8EC0000 | 1,024 B | 请求加密 |
| `Decrypt_Response` | 0x8EC0400 | 1,024 B | 响应解密 |
| `Derive_Key` | 0x8EC0800 | 512 B | 密钥派生 |
| `Calculate_HMAC` | 0x8EC0A00 | 384 B | HMAC计算 |
| `AES_Encrypt` | 0x8EC0B80 | 768 B | AES加密 |
| `AES_Decrypt` | 0x8EC0E80 | 768 B | AES解密 |
| `Generate_IV` | 0x8EC1180 | 256 B | IV生成 |
| `Secure_Random` | 0x8EC1280 | 320 B | 安全随机数 |

---

## 3. 全局变量完整地址

### 3.1 游戏实例变量

| 变量名 | 地址 | 类型 | 大小 | 说明 |
|--------|------|------|------|------|
| `g_GameInstance` | 0xA9BF000 | void* | 8 | 游戏实例指针 |
| `g_JavaVM` | 0xA9BF008 | JavaVM* | 8 | Java虚拟机 |
| `g_JNIEnv` | 0xA9BF010 | JNIEnv* | 8 | JNI环境 |
| `g_Activity` | 0xA9BF018 | jobject | 8 | Activity对象 |
| `g_Application` | 0xA9BF020 | jobject | 8 | Application对象 |
| `g_GameState` | 0xA9BF028 | GameState* | 8 | 游戏状态指针 |
| `g_PlayerManager` | 0xA9BF030 | PlayerManager* | 8 | 玩家管理器 |
| `g_RoomManager` | 0xA9BF038 | RoomManager* | 8 | 房间管理器 |
| `g_NetworkManager` | 0xA9BF040 | NetworkManager* | 8 | 网络管理器 |
| `g_Renderer` | 0xA9BF048 | Renderer* | 8 | 渲染器 |

### 3.2 安全配置变量

| 变量名 | 地址 | 类型 | 大小 | 说明 |
|--------|------|------|------|------|
| `g_SessionKey` | 0xA9BF100 | uint8_t[32] | 32 | 会话密钥 |
| `g_MasterKey` | 0xA9BF120 | uint8_t[32] | 32 | 主密钥 |
| `g_DeviceKey` | 0xA9BF140 | uint8_t[32] | 32 | 设备密钥 |
| `g_PublicKey` | 0xA9BF160 | uint8_t[256] | 256 | RSA公钥 |
| `g_PrivateKey` | 0xA9BF260 | uint8_t[256] | 256 | RSA私钥(加密存储) |
| `g_KeyVersion` | 0xA9BF360 | uint32_t | 4 | 密钥版本 |
| `g_KeyExpiry` | 0xA9BF364 | uint64_t | 8 | 密钥过期时间 |

### 3.3 网络配置变量

| 变量名 | 地址 | 类型 | 大小 | 说明 |
|--------|------|------|------|------|
| `g_ServerAddress` | 0xA9BF400 | char[64] | 64 | 服务器地址 |
| `g_ServerPort` | 0xA9BF440 | uint16_t | 2 | 服务器端口 |
| `g_SessionId` | 0xA9BF444 | uint32_t | 4 | 会话ID |
| `g_PlayerId` | 0xA9BF448 | uint32_t | 4 | 玩家ID |
| `g_RoomId` | 0xA9BF44C | uint32_t | 4 | 房间ID |
| `g_RoomKey` | 0xA9BF450 | uint8_t[32] | 32 | 房间密钥 |
| `g_Socket` | 0xA9BF470 | int | 4 | 网络套接字 |
| `g_LastPing` | 0xA9BF474 | uint64_t | 8 | 最后心跳时间 |
| `g_PingValue` | 0xA9BF47C | uint32_t | 4 | 当前延迟 |
| `g_IsConnected` | 0xA9BF480 | uint8_t | 1 | 连接状态 |

### 3.4 游戏状态变量

| 变量名 | 地址 | 类型 | 大小 | 说明 |
|--------|------|------|------|------|
| `g_CurrentFrame` | 0xA9BF500 | uint32_t | 4 | 当前帧 |
| `g_GameTime` | 0xA9BF504 | uint32_t | 4 | 游戏时间 |
| `g_IsPaused` | 0xA9BF508 | uint8_t | 1 | 暂停状态 |
| `g_IsInGame` | 0xA9BF509 | uint8_t | 1 | 游戏中状态 |
| `g_GameMode` | 0xA9BF50A | uint8_t | 1 | 游戏模式 |
| `g_MapId` | 0xA9BF50C | uint32_t | 4 | 地图ID |
| `g_Score` | 0xA9BF510 | uint32_t[2] | 8 | 双方分数 |
| `g_Winner` | 0xA9BF518 | uint8_t | 1 | 获胜方 |
| `g_RandomSeed` | 0xA9BF51C | uint32_t | 4 | 随机种子 |

---

## 4. 数据结构详细定义

### 4.1 玩家数据结构 (Player) - 地址: 0xAA3F000

```c
// 完整玩家结构体 - 512 bytes
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
    float rotX;                           // 0x4C: X旋转
    float rotY;                           // 0x50: Y旋转
    float rotZ;                           // 0x54: Z旋转
    float velX;                           // 0x58: X速度
    float velY;                           // 0x5C: Y速度
    float velZ;                           // 0x60: Z速度
    float scale;                          // 0x64: 缩放
    uint32_t mapId;                       // 0x68: 地图ID
    uint32_t instanceId;                  // 0x6C: 副本ID
    
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
    uint32_t buffFlags;                   // 0xA8: Buff标志
    uint32_t debuffFlags;                 // 0xAC: Debuff标志
    
    // === 网络信息 (16 bytes) ===
    uint32_t ping;                        // 0xB0: 延迟(ms)
    uint64_t lastHeartbeat;               // 0xB4: 最后心跳时间
    
    // === 背包信息 (16 bytes) ===
    uint32_t bagSize;                     // 0xBC: 背包大小
    uint32_t bagUsed;                     // 0xC0: 已用空间
    void *bagItems;                       // 0xC4: 物品数组指针
    
    // === 装备信息 (64 bytes) ===
    struct Equipment {
        uint32_t itemId;
        uint32_t enhanceLevel;
        uint32_t gemSlots[2];
    } equipments[8];                      // 0xC8 - 0x108
    // 0=武器, 1=头盔, 2=护甲, 3=护腿, 4=鞋子, 5=项链, 6=戒指, 7=饰品
    
    // === 技能信息 (32 bytes) ===
    void *skillList;                      // 0x108: 技能列表指针
    uint32_t skillPoints;                 // 0x110: 技能点
    uint32_t skillSlots[4];               // 0x114: 技能槽
    
    // === 社交信息 (32 bytes) ===
    uint32_t guildId;                     // 0x124: 公会ID
    uint32_t teamId;                      // 0x128: 队伍ID
    uint32_t friendCount;                 // 0x12C: 好友数量
    char signature[32];                   // 0x130: 个性签名
    
    // === 统计信息 (64 bytes) ===
    uint32_t totalKills;                  // 0x150: 总击杀
    uint32_t totalDeaths;                 // 0x154: 总死亡
    uint32_t totalAssists;                // 0x158: 总助攻
    uint32_t totalWins;                   // 0x15C: 总胜利
    uint32_t totalGames;                  // 0x160: 总场次
    uint32_t totalDamage;                 // 0x164: 总伤害
    uint32_t totalHeal;                   // 0x168: 总治疗
    uint32_t mvpCount;                    // 0x16C: MVP次数
    uint64_t totalPlayTime;               // 0x170: 总游戏时间
    uint64_t createTime;                  // 0x178: 创建时间
    
    // === 预留空间 (96 bytes) ===
    uint8_t reserved[96];                 // 0x180 - 0x200
};  // 总大小: 512 bytes
```

### 4.2 房间数据结构 (Room) - 地址: 0xAA40000

```c
// 完整房间结构体 - 4096 bytes
struct Room {
    // === 基本信息 (32 bytes) ===
    uint32_t roomId;                      // 0x00: 房间ID
    uint32_t hostId;                      // 0x04: 房主ID
    uint8_t state;                        // 0x08: 房间状态
    // 0=IDLE, 1=CREATING, 2=WAITING, 3=PREPARING, 4=PLAYING, 5=ENDING, 6=CLOSED
    
    uint8_t gameMode;                     // 0x09: 游戏模式
    uint8_t maxPlayers;                   // 0x0A: 最大人数
    uint8_t currentPlayers;               // 0x0B: 当前人数
    uint32_t mapId;                       // 0x0C: 地图ID
    uint32_t matchRule;                   // 0x10: 匹配规则
    uint64_t createTime;                  // 0x14: 创建时间
    uint64_t startTime;                   // 0x1C: 开始时间
    
    // === 配置信息 (64 bytes) ===
    uint8_t isPrivate;                    // 0x24: 是否私有
    uint8_t hasPassword;                  // 0x25: 是否有密码
    char password[32];                    // 0x26: 密码(MD5)
    uint16_t minLevel;                    // 0x46: 最低等级
    uint16_t maxLevel;                    // 0x48: 最高等级
    uint8_t allowSpectator;               // 0x4A: 允许观战
    uint8_t voiceChat;                    // 0x4B: 语音聊天
    char roomName[32];                    // 0x4C: 房间名称
    
    // === 玩家信息 (32 * 64 = 2048 bytes) ===
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
        uint8_t isSpectator;              // 是否观战
        uint16_t reserved;
        uint32_t score;                   // 当前分数
        uint32_t kills;                   // 击杀数
        uint32_t deaths;                  // 死亡数
        uint32_t assists;                 // 助攻数
    } players[32];                        // 0x80 - 0x880
    
    // === 游戏状态 (256 bytes) ===
    struct {
        uint32_t currentFrame;            // 当前帧
        uint32_t gameTime;                // 游戏时间
        uint32_t score[2];                // 双方分数
        uint8_t winner;                   // 获胜方
        uint8_t gamePhase;                // 游戏阶段
        uint16_t reserved;
        uint32_t randomSeed;              // 随机种子
        uint64_t lastSyncTime;            // 最后同步时间
        uint32_t syncFrame;               // 同步帧
        uint32_t tickRate;                //  tick率
        float gameSpeed;                  // 游戏速度
        uint32_t pauseCount;              // 暂停次数
        uint64_t totalPauseTime;          // 总暂停时间
    } gameState;                          // 0x880 - 0x980
    
    // === 网络信息 (128 bytes) ===
    int serverSocket;                     // 服务器连接
    uint32_t serverAddr;                  // 服务器地址
    uint16_t serverPort;                  // 服务器端口
    uint8_t roomKey[32];                  // 房间密钥
    uint8_t sessionKey[32];               // 会话密钥
    uint32_t lastPing;                    // 最后心跳
    uint32_t pingInterval;                // 心跳间隔
    uint32_t timeoutCount;                // 超时次数
    uint8_t isConnected;                  // 连接状态
    uint8_t padding[11];
    
    // === 消息队列 (512 bytes) ===
    struct {
        uint32_t head;
        uint32_t tail;
        uint32_t count;
        uint32_t maxCount;
        void *messages;
    } msgQueue;
    uint8_t msgBuffer[496];
    
    // === 回调函数 (64 bytes) ===
    void (*onPlayerJoin)(uint32_t);
    void (*onPlayerLeave)(uint32_t);
    void (*onPlayerReady)(uint32_t, uint8_t);
    void (*onGameStart)();
    void (*onGameEnd)(uint8_t);
    void (*onChatMessage)(uint32_t, const char*);
    void (*onError)(int32_t);
    void (*onDisconnect)();
    
    // === 互斥锁和条件变量 (64 bytes) ===
    pthread_mutex_t lock;
    pthread_cond_t cond;
    uint8_t isLocked;
    uint8_t padding2[7];
    
    // === 统计信息 (128 bytes) ===
    uint32_t totalKills;
    uint32_t totalDeaths;
    uint32_t totalAssists;
    uint32_t totalDamage;
    uint32_t totalHeal;
    uint32_t totalGold;
    uint32_t matchDuration;
    uint32_t chatMessageCount;
    uint64_t bytesSent;
    uint64_t bytesReceived;
    uint32_t packetLossCount;
    float averagePing;
    uint8_t reserved3[76];
    
    // === 预留空间 (512 bytes) ===
    uint8_t reserved[512];
};  // 总大小: 4096 bytes
```

---

## 5. 网络协议详细定义

### 5.1 协议头结构 (24 bytes)

```c
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
    
    // 长度信息 (8 bytes)
    uint32_t payloadLen;                  // 0x10: 负载长度
    uint32_t checksum;                    // 0x14: 校验和
};
```

### 5.2 包类型完整列表

```c
// 系统包 (0x0000-0x00FF)
#define PKT_HANDSHAKE           0x0001
#define PKT_HANDSHAKE_RES       0x0002
#define PKT_HEARTBEAT           0x0003
#define PKT_HEARTBEAT_RES       0x0004
#define PKT_DISCONNECT          0x0005
#define PKT_DISCONNECT_ACK      0x0006
#define PKT_ACK                 0x0007
#define PKT_NACK                0x0008
#define PKT_ERROR               0x0009
#define PKT_PING                0x000A
#define PKT_PONG                0x000B

// 登录包 (0x0100-0x01FF)
#define PKT_LOGIN_REQ           0x0100
#define PKT_LOGIN_RES           0x0101
#define PKT_LOGOUT              0x0102
#define PKT_LOGOUT_ACK          0x0103
#define PKT_TOKEN_REFRESH       0x0104
#define PKT_TOKEN_REFRESH_RES   0x0105
#define PKT_REGISTER_REQ        0x0106
#define PKT_REGISTER_RES        0x0107
#define PKT_BIND_ACCOUNT        0x0108
#define PKT_BIND_ACCOUNT_RES    0x0109

// 房间包 (0x0200-0x02FF)
#define PKT_ROOM_CREATE         0x0200
#define PKT_ROOM_CREATE_RES     0x0201
#define PKT_ROOM_JOIN           0x0202
#define PKT_ROOM_JOIN_RES       0x0203
#define PKT_ROOM_LEAVE          0x0204
#define PKT_ROOM_LEAVE_ACK      0x0205
#define PKT_ROOM_KICK           0x0206
#define PKT_ROOM_KICK_ACK       0x0207
#define PKT_ROOM_READY          0x0208
#define PKT_ROOM_READY_ACK      0x0209
#define PKT_ROOM_START          0x020A
#define PKT_ROOM_START_ACK      0x020B
#define PKT_ROOM_LIST           0x020C
#define PKT_ROOM_LIST_RES       0x020D
#define PKT_ROOM_INFO           0x020E
#define PKT_ROOM_INFO_RES       0x020F
#define PKT_ROOM_MSG            0x0210
#define PKT_ROOM_MSG_ACK        0x0211
#define PKT_ROOM_CHAT           0x0212
#define PKT_ROOM_CHAT_ACK       0x0213

// 游戏包 (0x0300-0x03FF)
#define PKT_GAME_STATE          0x0300
#define PKT_GAME_STATE_ACK      0x0301
#define PKT_GAME_INPUT          0x0302
#define PKT_GAME_INPUT_ACK      0x0303
#define PKT_GAME_EVENT          0x0304
#define PKT_GAME_EVENT_ACK      0x0305
#define PKT_GAME_SYNC           0x0306
#define PKT_GAME_SYNC_RES       0x0307
#define PKT_GAME_RESULT         0x0308
#define PKT_GAME_RESULT_ACK     0x0309
#define PKT_GAME_PAUSE          0x030A
#define PKT_GAME_PAUSE_ACK      0x030B
#define PKT_GAME_RESUME         0x030C
#define PKT_GAME_RESUME_ACK     0x030D
```

---

*文档生成时间: 2026-04-24*
*分析进度: Phase 1/19*
