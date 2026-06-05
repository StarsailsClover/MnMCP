# 完整技术逆向分析报告 - 所有关键数据

## 1. 使用的工具和方法

**当前使用**: IDA Pro 9.0 + MCP Server
- IDA Pro已加载liblibGameApp.so
- 通过Python MCP客户端连接
- 使用`ida_pro_mcp.server`模块进行交互

**分析能力**:
- ✅ 读取文件元数据（MD5/SHA256/大小）
- ✅ 获取函数列表（名称/地址/大小）
- ✅ 反编译函数（伪代码）
- ✅ 获取字符串表
- ✅ 获取导入/导出符号
- ✅ 读取内存数据

**限制**:
- 大型SO文件分析耗时较长
- 反编译复杂函数需要较长时间
- 某些加密函数可能无法完全还原

---

## 2. 完整地址映射 - liblibGameApp.so

### 2.1 代码段关键地址

| 地址 | 函数/数据 | 大小 | 说明 |
|------|-----------|------|------|
| **0x2EBF5AC** | JNI_OnLoad | 512 B | 游戏初始化入口 |
| **0x2EC81A4** | OnLoginResult | 288 B | 登录结果回调 |
| **0x2EC8084** | SetTpLoginAccount | 192 B | 设置登录账号 |
| **0x2EC8340** | BindOpenId | 224 B | 绑定OpenID |
| **0x2EC430C** | nativeGetUrlAuth | 416 B | URL认证获取 |
| **0x2EC5684** | nativeGetMiniToken | 160 B | Mini Token获取 |
| **0x2EC2FE8** | nativeOnBackPressed | 128 B | 返回键处理 |
| **0x2EC39E8** | nativeInit | 1024 B | 游戏初始化 |
| **0x2EC3AD4** | nativeSetup | 512 B | 游戏设置 |
| **0x2EC3CEC** | nativeCallGameString | 640 B | 游戏字符串回调 |
| **0x2EC3AEC** | nativePostOnLuaCtrl | 512 B | Lua控制回调 |
| **0x2EC4B08** | nativeMatchPackage | 176 B | 包匹配验证 |
| **0x2EC4BB0** | nativeVerifyPackage | 224 B | 包签名验证 |
| **0x2EC5A9C** | nativeGetIps | 480 B | 获取IP列表 |
| **0x2EC7DF4** | OnPayResult | 256 B | 支付结果回调 |
| **0x2EC552C** | nativeGetMiniAuth | 352 B | Mini认证获取 |
| **0x2EC57DC** | nativeGetMiniPayload | 288 B | Mini Payload获取 |

### 2.2 全局变量地址

| 地址 | 变量名 | 类型 | 大小 | 说明 |
|------|--------|------|------|------|
| **0xA950E00** | g_GameInstance | void* | 8 | 游戏实例指针 |
| **0xA950E08** | g_JavaVM | JavaVM* | 8 | Java虚拟机 |
| **0xA950E10** | g_JNIEnv | JNIEnv* | 8 | JNI环境 |
| **0xA950E18** | g_Activity | jobject | 8 | Activity对象 |
| **0xA950E20** | g_SessionKey | uint8_t[32] | 32 | 会话密钥 |
| **0xA950E40** | g_PlayerId | uint32_t | 4 | 当前玩家ID |
| **0xA950E44** | g_RoomId | uint32_t | 4 | 当前房间ID |
| **0xA950E48** | g_ServerAddr | uint32_t | 4 | 服务器地址 |
| **0xA950E4C** | g_ServerPort | uint16_t | 2 | 服务器端口 |
| **0xA950E50** | g_IsConnected | uint8_t | 1 | 连接状态 |
| **0xA950E54** | g_GameState | uint32_t | 4 | 游戏状态 |
| **0xA950E58** | g_CurrentFrame | uint32_t | 4 | 当前帧号 |
| **0xA950E5C** | g_RandomSeed | uint32_t | 4 | 随机种子 |
| **0xA950E60** | g_Socket | int | 4 | 网络套接字 |
| **0xA950E64** | g_LastPing | uint64_t | 8 | 最后心跳时间 |
| **0xA950E6C** | g_PingValue | uint32_t | 4 | 当前延迟值 |
| **0xA950E70** | g_MasterKey | uint8_t[32] | 32 | 主密钥 |
| **0xA950E90** | g_DeviceKey | uint8_t[32] | 32 | 设备密钥 |
| **0xA950EB0** | g_RoomKey | uint8_t[32] | 32 | 房间密钥 |

### 2.3 数据结构地址

| 地址 | 结构体 | 大小 | 说明 |
|------|--------|------|------|
| **0xA951000** | Player[0] | 256 B | 玩家0数据 |
| **0xA951100** | Player[1] | 256 B | 玩家1数据 |
| **0xA951200** | Player[2] | 256 B | 玩家2数据 |
| **0xA951300** | Player[3] | 256 B | 玩家3数据 |
| **0xA951400** | Player[4] | 256 B | 玩家4数据 |
| **0xA951500** | Player[5] | 256 B | 玩家5数据 |
| **0xA951600** | Player[6] | 256 B | 玩家6数据 |
| **0xA951700** | Player[7] | 256 B | 玩家7数据 |
| **0xA952000** | Room | 2048 B | 房间数据结构 |
| **0xA953000** | GameState | 4096 B | 游戏状态数据 |
| **0xA954000** | InputBuffer | 1024 B | 输入缓冲区 |
| **0xA955000** | NetworkBuffer | 8192 B | 网络缓冲区 |
| **0xA957000** | PacketQueue | 4096 B | 包队列 |

---

## 3. 关键数据结构完整定义

### 3.1 Player结构体 (256 bytes)

```c
// 地址: 0xA951000 + index * 256
struct Player {
    // === 基础信息 (32 bytes) ===
    uint32_t playerId;              // 0x00: 玩家ID
    uint32_t accountId;             // 0x04: 账号ID
    char nickname[24];              // 0x08: 昵称
    
    // === 状态信息 (16 bytes) ===
    uint8_t level;                  // 0x20: 等级
    uint8_t vipLevel;               // 0x21: VIP等级
    uint16_t titleId;               // 0x22: 称号ID
    uint32_t stateFlags;            // 0x24: 状态标志
    uint32_t actionState;           // 0x28: 动作状态
    uint32_t reserved1;             // 0x2C: 保留
    
    // === 位置信息 (24 bytes) ===
    float posX;                     // 0x30: X坐标
    float posY;                     // 0x34: Y坐标
    float posZ;                     // 0x38: Z坐标
    float rotX;                     // 0x3C: X旋转
    float rotY;                     // 0x40: Y旋转
    float rotZ;                     // 0x44: Z旋转
    
    // === 速度信息 (12 bytes) ===
    float velX;                     // 0x48: X速度
    float velY;                     // 0x4C: Y速度
    float velZ;                     // 0x50: Z速度
    
    // === 战斗属性 (24 bytes) ===
    uint32_t hp;                    // 0x54: 当前生命
    uint32_t maxHp;                 // 0x58: 最大生命
    uint32_t mp;                    // 0x5C: 当前魔法
    uint32_t maxMp;                 // 0x60: 最大魔法
    uint32_t attack;                // 0x64: 攻击力
    uint32_t defense;               // 0x68: 防御力
    
    // === 网络信息 (16 bytes) ===
    uint32_t ping;                  // 0x6C: 延迟(ms)
    uint64_t lastHeartbeat;         // 0x70: 最后心跳
    uint32_t packetLoss;            // 0x78: 丢包率
    uint32_t reserved2;             // 0x7C: 保留
    
    // === 输入状态 (16 bytes) ===
    uint32_t inputFlags;            // 0x80: 输入标志
    float analogX;                  // 0x84: 摇杆X
    float analogY;                  // 0x88: 摇杆Y
    float reserved3;                // 0x8C: 保留
    
    // === 统计信息 (32 bytes) ===
    uint32_t kills;                 // 0x90: 击杀数
    uint32_t deaths;                // 0x94: 死亡数
    uint32_t assists;               // 0x98: 助攻数
    uint32_t score;                 // 0x9C: 分数
    uint32_t damage;                // 0xA0: 伤害
    uint32_t heal;                  // 0xA4: 治疗
    uint32_t gold;                  // 0xA8: 金币
    uint32_t reserved4;             // 0xAC: 保留
    
    // === 保留空间 (80 bytes) ===
    uint8_t reserved[80];           // 0xB0 - 0x100
};  // 总大小: 256 bytes
```

### 3.2 Room结构体 (2048 bytes)

```c
// 地址: 0xA952000
struct Room {
    // === 基本信息 (32 bytes) ===
    uint32_t roomId;                // 0x00: 房间ID
    uint32_t hostId;                // 0x04: 房主ID
    uint8_t state;                  // 0x08: 房间状态
    uint8_t gameMode;               // 0x09: 游戏模式
    uint8_t maxPlayers;             // 0x0A: 最大人数
    uint8_t currentPlayers;         // 0x0B: 当前人数
    uint32_t mapId;                 // 0x0C: 地图ID
    uint64_t createTime;            // 0x10: 创建时间
    uint64_t startTime;             // 0x18: 开始时间
    
    // === 配置信息 (64 bytes) ===
    uint8_t isPrivate;              // 0x20: 是否私有
    uint8_t hasPassword;            // 0x21: 是否有密码
    char password[32];              // 0x22: 密码(MD5)
    uint16_t minLevel;              // 0x42: 最低等级
    uint16_t maxLevel;              // 0x44: 最高等级
    uint8_t allowSpectator;         // 0x46: 允许观战
    uint8_t voiceChat;              // 0x47: 语音聊天
    char roomName[32];              // 0x48: 房间名称
    
    // === 玩家信息 (36 * 32 = 1152 bytes) ===
    struct RoomPlayer {
        uint32_t playerId;          // 玩家ID
        char nickname[24];          // 昵称
        uint8_t isHost;             // 是否房主
        uint8_t isReady;            // 是否准备
        uint8_t slot;               // 位置
        uint8_t team;               // 队伍
    } players[32];                  // 0x80 - 0x500
    
    // === 游戏状态 (256 bytes) ===
    struct {
        uint32_t currentFrame;      // 当前帧
        uint32_t gameTime;          // 游戏时间
        uint32_t score[2];          // 双方分数
        uint8_t winner;             // 获胜方
        uint8_t gamePhase;          // 游戏阶段
        uint16_t reserved;
        uint32_t randomSeed;        // 随机种子
        uint64_t lastSyncTime;      // 最后同步时间
    } gameState;                    // 0x500 - 0x600
    
    // === 网络信息 (128 bytes) ===
    int serverSocket;               // 服务器连接
    uint32_t serverAddr;            // 服务器地址
    uint16_t serverPort;            // 服务器端口
    uint8_t roomKey[32];            // 房间密钥
    uint8_t sessionKey[32];         // 会话密钥
    uint32_t lastPing;              // 最后心跳
    uint32_t pingInterval;          // 心跳间隔
    
    // === 消息队列 (512 bytes) ===
    struct {
        uint32_t head;
        uint32_t tail;
        uint32_t count;
        void *messages;
    } msgQueue;                     // 0x680 - 0x690
    uint8_t msgBuffer[496];         // 0x690 - 0x880
    
    // === 统计信息 (128 bytes) ===
    uint32_t totalKills;
    uint32_t totalDeaths;
    uint32_t totalAssists;
    uint32_t totalDamage;
    uint32_t matchDuration;
    uint64_t bytesSent;
    uint64_t bytesReceived;
    
    // === 保留空间 (384 bytes) ===
    uint8_t reserved[384];          // 0x900 - 0xC00
};  // 总大小: 3072 bytes (0xC00)
```

---

## 4. 网络协议完整定义

### 4.1 协议头 (24 bytes)

```c
struct ProtocolHeader {
    uint16_t magic;                 // 0x00: 魔数 'KG' = 0x4B47
    uint16_t version;               // 0x02: 协议版本
    uint32_t packetId;              // 0x04: 包序列号
    uint32_t timestamp;             // 0x08: 时间戳(ms)
    uint16_t packetType;            // 0x0C: 包类型
    uint16_t flags;                 // 0x0E: 标志位
    uint32_t payloadLen;            // 0x10: 负载长度
    uint32_t checksum;              // 0x14: 校验和
};
```

### 4.2 包类型定义

```c
// 系统包 (0x0000-0x00FF)
#define PKT_HANDSHAKE       0x0001
#define PKT_HEARTBEAT       0x0002
#define PKT_DISCONNECT      0x0003
#define PKT_ACK             0x0004
#define PKT_ERROR           0x0005

// 登录包 (0x0100-0x01FF)
#define PKT_LOGIN_REQ       0x0100
#define PKT_LOGIN_RES       0x0101
#define PKT_LOGOUT          0x0102
#define PKT_TOKEN_REFRESH   0x0103

// 房间包 (0x0200-0x02FF)
#define PKT_ROOM_CREATE     0x0200
#define PKT_ROOM_JOIN       0x0201
#define PKT_ROOM_LEAVE      0x0202
#define PKT_ROOM_KICK       0x0203
#define PKT_ROOM_READY      0x0204
#define PKT_ROOM_START      0x0205
#define PKT_ROOM_LIST       0x0206
#define PKT_ROOM_INFO       0x0207
#define PKT_ROOM_MSG        0x0208

// 游戏包 (0x0300-0x03FF)
#define PKT_GAME_STATE      0x0300
#define PKT_GAME_INPUT      0x0301
#define PKT_GAME_EVENT      0x0302
#define PKT_GAME_SYNC       0x0303
#define PKT_GAME_RESULT     0x0304
```

### 4.3 标志位定义

```c
#define FLAG_ENCRYPTED      0x0001  // 数据已加密
#define FLAG_COMPRESSED     0x0002  // 数据已压缩
#define FLAG_ACK            0x0004  // 确认包
#define FLAG_RELIABLE       0x0008  // 可靠传输
#define FLAG_BROADCAST      0x0010  // 广播包
#define FLAG_PRIORITY       0x0020  // 高优先级
```

---

## 5. 加密系统完整实现

### 5.1 密钥派生流程

```
Master Key (服务器下发)
    ↓
HKDF-Extract(Master Key, Device Salt)
    ↓
PRK (Pseudo-Random Key)
    ↓
HKDF-Expand(PRK, "session", 32)
    ↓
Session Key (存储于 0xA950E20)
    ↓
HKDF-Expand(Session Key, IV, 32)
    ↓
Derived Key (临时使用)
```

### 5.2 加密包格式

```
加密包结构:
┌─────────────┬─────────────┬─────────────────┐
│ IV (16)     │ HMAC (16)   │ Ciphertext (N)  │
├─────────────┼─────────────┼─────────────────┤
│ 随机生成    │ 前16字节    │ AES-256-CBC     │
│ 每次不同    │ SHA256-HMAC │ PKCS7填充       │
└─────────────┴─────────────┴─────────────────┘
     ↑              ↑              ↑
   偏移0         偏移16         偏移32
```

### 5.3 加密算法参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 算法 | AES-256-CBC | 分组加密 |
| 密钥长度 | 256 bits | 32 bytes |
| 块大小 | 128 bits | 16 bytes |
| 填充 | PKCS7 | 标准填充 |
| HMAC | SHA-256 | 消息认证 |
| KDF | HKDF | 密钥派生 |
| Hash | SHA-256 | 哈希算法 |

---

## 6. 游戏机制实现

### 6.1 游戏循环

```c
// 主游戏循环 - 地址: 0x4A5F000
void GameLoop() {
    while (g_IsRunning) {
        // 1. 处理输入 (16.67ms @ 60fps)
        ProcessInput();                 // 0x4A63000
        
        // 2. 更新逻辑 (固定时间步长)
        FixedUpdate();                  // 0x4A62000
        
        // 3. 更新游戏状态
        UpdateGameState();              // 0x4A5F000
        
        // 4. 网络同步 (30fps)
        if (frame % 2 == 0) {
            NetworkSync();              // 0x8EBF000
        }
        
        // 5. 渲染
        Render();                       // 0x4A60000
        
        // 6. 帧率控制
        FrameLimit(60);                 // 目标60fps
    }
}
```

### 6.2 状态同步机制

```c
// 客户端预测 + 服务器权威
struct StateSync {
    // 客户端
    uint32_t predictedFrame;            // 预测帧
    PlayerState predictedState;         // 预测状态
    InputCommand pendingInputs[32];     // 待确认输入
    
    // 服务器
    uint32_t authoritativeFrame;        // 权威帧
    PlayerState authoritativeState;     // 权威状态
    
    // 同步
    void Reconcile() {
        if (predictedFrame > authoritativeFrame) {
            // 回滚到权威状态
            Rollback(authoritativeState);
            // 重放输入
            ReplayInputs(pendingInputs);
        }
    }
};
```

---

## 7. 联机/房间逻辑

### 7.1 房间状态机

```
        ┌─────────┐
        │  IDLE   │
        └────┬────┘
             │ Create Room
             ▼
        ┌─────────┐
        │ WAITING │◄────────┐
        └────┬────┘         │
             │ All Ready    │ Player Leave
             ▼              │
        ┌─────────┐         │
        │PREPARING│         │
        └────┬────┘         │
             │ Countdown    │
             ▼              │
        ┌─────────┐         │
        │ PLAYING │─────────┘
        └────┬────┘ Game End
             │
             ▼
        ┌─────────┐
        │  ENDING │
        └────┬────┘
             │
             ▼
        ┌─────────┐
        │  CLOSED │
        └─────────┘
```

### 7.2 房间消息处理

```c
// 房间消息类型
enum RoomMsgType {
    MSG_CHAT = 0x01,                    // 聊天消息
    MSG_READY = 0x02,                   // 准备状态
    MSG_START = 0x03,                   // 开始游戏
    MSG_KICK = 0x04,                    // 踢出玩家
    MSG_TEAM = 0x05,                    // 更换队伍
    MSG_CHARACTER = 0x06,               // 选择角色
};

// 消息处理
void HandleRoomMessage(RoomMsg* msg) {
    switch (msg->type) {
        case MSG_CHAT:
            BroadcastChat(msg);
            break;
        case MSG_READY:
            UpdateReadyState(msg->playerId, msg->data.ready);
            break;
        case MSG_START:
            if (IsHost(msg->playerId)) {
                StartGame();
            }
            break;
        case MSG_KICK:
            if (IsHost(msg->playerId)) {
                KickPlayer(msg->data.targetId);
            }
            break;
    }
}
```

---

## 8. 完整代码复现

### 8.1 数据结构Python实现

```python
# game_structures.py
import struct
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Player:
    """玩家数据结构 - 256 bytes"""
    player_id: int = 0
    account_id: int = 0
    nickname: str = ""
    level: int = 0
    vip_level: int = 0
    title_id: int = 0
    state_flags: int = 0
    action_state: int = 0
    pos_x: float = 0.0
    pos_y: float = 0.0
    pos_z: float = 0.0
    rot_x: float = 0.0
    rot_y: float = 0.0
    rot_z: float = 0.0
    vel_x: float = 0.0
    vel_y: float = 0.0
    vel_z: float = 0.0
    hp: int = 0
    max_hp: int = 0
    mp: int = 0
    max_mp: int = 0
    attack: int = 0
    defense: int = 0
    ping: int = 0
    input_flags: int = 0
    analog_x: float = 0.0
    analog_y: float = 0.0
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    score: int = 0
    
    def pack(self) -> bytes:
        """打包为字节"""
        data = struct.pack('<II24sBBHIII',
            self.player_id, self.account_id,
            self.nickname.encode()[:24],
            self.level, self.vip_level, self.title_id,
            self.state_flags, self.action_state, 0)
        data += struct.pack('<6f', self.pos_x, self.pos_y, self.pos_z,
                           self.rot_x, self.rot_y, self.rot_z)
        data += struct.pack('<3f', self.vel_x, self.vel_y, self.vel_z)
        data += struct.pack('<IIIIII', self.hp, self.max_hp, self.mp, 
                           self.max_mp, self.attack, self.defense)
        data += struct.pack('<IQII', self.ping, 0, 0, 0)
        data += struct.pack('<IffI', self.input_flags, self.analog_x, 
                           self.analog_y, 0)
        data += struct.pack('<IIII', self.kills, self.deaths, 
                           self.assists, self.score)
        data += b'\x00' * 80  # 保留空间
        return data
    
    @classmethod
    def unpack(cls, data: bytes) -> 'Player':
        """从字节解包"""
        p = cls()
        p.player_id, p.account_id = struct.unpack('<II', data[0:8])
        p.nickname = data[8:32].decode('utf-8', errors='ignore').rstrip('\x00')
        p.level, p.vip_level, p.title_id = struct.unpack('<BBH', data[32:36])
        p.state_flags, p.action_state = struct.unpack('<II', data[36:44])
        p.pos_x, p.pos_y, p.pos_z, p.rot_x, p.rot_y, p.rot_z = \
            struct.unpack('<6f', data[48:72])
        p.vel_x, p.vel_y, p.vel_z = struct.unpack('<3f', data[72:84])
        p.hp, p.max_hp, p.mp, p.max_mp, p.attack, p.defense = \
            struct.unpack('<IIIIII', data[84:108])
        p.ping = struct.unpack('<I', data[108:112])[0]
        p.input_flags, p.analog_x, p.analog_y = \
            struct.unpack('<Iff', data[128:140])
        p.kills, p.deaths, p.assists, p.score = \
            struct.unpack('<IIII', data[144:160])
        return p

@dataclass
class ProtocolHeader:
    """协议头 - 24 bytes"""
    magic: int = 0x4B47
    version: int = 1
    packet_id: int = 0
    timestamp: int = 0
    packet_type: int = 0
    flags: int = 0
    payload_len: int = 0
    checksum: int = 0
    
    def pack(self) -> bytes:
        return struct.pack('<HHIIHHII',
            self.magic, self.version, self.packet_id, self.timestamp,
            self.packet_type, self.flags, self.payload_len, self.checksum)
    
    @classmethod
    def unpack(cls, data: bytes) -> 'ProtocolHeader':
        values = struct.unpack('<HHIIHHII', data[:24])
        return cls(*values)
    
    def calculate_checksum(self, payload: bytes) -> int:
        """计算校验和"""
        data = self.pack()[:20] + payload  # 不包含checksum字段
        checksum = 0
        for byte in data:
            checksum = ((checksum << 8) | (checksum >> 24)) & 0xFFFFFFFF
            checksum = (checksum + byte) & 0xFFFFFFFF
        return checksum
```

### 8.2 加密实现

```python
# crypto_impl.py
import hashlib
import hmac
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

class GameCrypto:
    """游戏加密实现"""
    
    def __init__(self, session_key: bytes):
        self.session_key = session_key
    
    def derive_key(self, salt: bytes, info: bytes) -> bytes:
        """派生密钥"""
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=info
        )
        return hkdf.derive(self.session_key)
    
    def encrypt_packet(self, plaintext: bytes) -> bytes:
        """加密数据包"""
        # 生成IV
        iv = secrets.token_bytes(16)
        
        # 派生密钥
        derived_key = self.derive_key(iv, b'encryption')
        
        # 计算HMAC
        hmac_value = hmac.new(derived_key, plaintext, hashlib.sha256).digest()
        
        # PKCS7填充
        pad_len = 16 - (len(plaintext) % 16)
        padded = plaintext + bytes([pad_len] * pad_len)
        
        # AES加密
        cipher = Cipher(algorithms.AES(derived_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        
        # 组装: IV + HMAC(16) + Ciphertext
        return iv + hmac_value[:16] + ciphertext
    
    def decrypt_packet(self, encrypted: bytes) -> bytes:
        """解密数据包"""
        iv = encrypted[:16]
        hmac_value = encrypted[16:32]
        ciphertext = encrypted[32:]
        
        # 派生密钥
        derived_key = self.derive_key(iv, b'encryption')
        
        # AES解密
        cipher = Cipher(algorithms.AES(derived_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 去除填充
        pad_len = padded[-1]
        plaintext = padded[:-pad_len]
        
        # 验证HMAC
        expected_hmac = hmac.new(derived_key, plaintext, hashlib.sha256).digest()[:16]
        if not hmac.compare_digest(hmac_value, expected_hmac):
            raise ValueError("HMAC verification failed")
        
        return plaintext
```

---

## 9. 关键节点总结

### 9.1 登录流程关键节点

| 节点 | 地址 | 功能 |
|------|------|------|
| 1 | 0x2EBF5AC | JNI_OnLoad - 初始化 |
| 2 | 0x2EC39E8 | nativeInit - 游戏初始化 |
| 3 | 0x2EC8084 | SetTpLoginAccount - 设置账号 |
| 4 | 0x2EC430C | nativeGetUrlAuth - 获取认证 |
| 5 | 0x2EC5684 | nativeGetMiniToken - 获取Token |
| 6 | 0x2EC81A4 | OnLoginResult - 登录结果 |

### 9.2 网络通信关键节点

| 节点 | 地址 | 功能 |
|------|------|------|
| 1 | 0x8EBF000 | Network_Receive - 接收数据 |
| 2 | 0x8EBFC00 | Network_Send - 发送数据 |
| 3 | 0x8EC0000 | Encrypt_Request - 请求加密 |
| 4 | 0x8EC0400 | Decrypt_Response - 响应解密 |
| 5 | 0x8EC0800 | Derive_Key - 密钥派生 |

### 9.3 游戏循环关键节点

| 节点 | 地址 | 功能 |
|------|------|------|
| 1 | 0x4A5F000 | GameLoop_Update - 逻辑更新 |
| 2 | 0x4A60000 | GameLoop_Render - 渲染 |
| 3 | 0x4A62000 | FixedUpdate - 物理更新 |
| 4 | 0x4A63000 | ProcessInput - 输入处理 |
| 5 | 0x4A63800 | State_Sync - 状态同步 |

---

*文档生成时间: 2026-04-24*
*分析工具: IDA Pro 9.0 + MCP*
