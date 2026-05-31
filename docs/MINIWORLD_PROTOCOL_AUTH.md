# 迷你世界登录验证与开房间协议文档

> 基于 liblibGameApp.so (Android ARM64) 逆向分析 + Lua 脚本反编译 + 实际抓包验证
>
> 客户端版本: 1.55.0 (cltversion=79617)

---

## 1. 密钥汇总

| Key | Value | 用途 | 来源 |
|-----|-------|------|------|
| **xxtea_key** | `b48e6ef44ed13eee606141750e729cf4` | 登录数据编码: msgpack → xxtea加密 → zip → base64url | `liblibGameApp.so` @ `0x8ADB465` (16字节 raw bytes) |
| **sign_key** | `2ddb7619717147439c83ab022e9d4d38` | HTTP 登录请求签名 `md5("msg=...&key=" + sign_key)` | `client.lua:20` `client_M.http_authkey` |
| **auth_key** | `f5711eb1640712de051e5aedc35329c3` | 房间 API 签名 `md5(sorted_params + auth_key)` | `liblibGameApp.so` `sub_62D1F48` → `sub_358D0A0` |
| **appsecret** (apiid=110) | `1942b40fab9856240d9e4525042e04fe` | 防沉迷认证 `md5(secret + time + uin)` | `account.lua:1913` |
| **appsecret** (其他apiid) | `4167658d815d3595cfc30b91c6b21736` | 防沉迷认证（非 110 apiid） | `account.lua:1907` |
| **chatpush_key** | `#Chat@Push.99#` | WebSocket 聊天推送加密 | `container.lua:1347` |

### xxtea_key 详细信息

```
地址:    0x8ADB465
Hex:     b4 8e 6e f4 4e d1 3e ee 60 61 41 75 0e 72 9c f4
uint32 LE:
  k[0] = 0xF46E8EB4
  k[1] = 0xEE3ED14E
  k[2] = 0x75416160
  k[3] = 0xF49C720E
```

XXTEA 算法使用标准 DELTA = `0x9E3779B9`（代码中以 `-1640531527` 即 `0x61C88647` 取负形式出现）。加密函数位于 `sub_65B19F8`，解密函数位于 `sub_65B18C4`，key 由 `sub_65B18B8` 返回（直接返回硬编码地址）。

---

## 2. API 端点

| 端点 | 地址 | 协议 | 用途 |
|------|------|------|------|
| 登录 | `https://wskacchm.mini1.cn:14130/man_machine/login_v3` | HTTPS GET | 账号密码登录，获取 JWT + sign |
| WS 配置 | `http://wskacchm.mini1.cn:4000/update/?` | HTTP GET | 获取 WebSocket 服务器地址 |
| WS 心跳 | `ws://cn-logicN.mini1.cn:PORT/` (动态) | WebSocket | 心跳换取真实 s2/s2t |
| 房间服务器配置 | `http://openroom.mini1.cn:8080/server/room?` | HTTP GET | 获取 proxy/punch/room 服务器 IP |
| 房间管理 | `http://{config.room.ip}:{config.room.port}/server/room?` | HTTP GET | 创建/更新/关闭房间 |
| 房间发现 | `http://cs-gsmgr.mini1.cn/v2/room/get` | HTTP POST | 客户端搜索加入房间 |

### 公共 Header

```
User-Agent: Rainbow/1.0 (Windows_RT; U; Linux 6.2; zh)
```

---

## 3. 登录流程

### Step 1: HTTP 登录

**编码过程:**

```python
# 1. 构造登录参数
login_data = {
    "source": "client",
    "juhe_auth": "",
    "passwd_auth": '{"passwd":"用户密码"}',
    "DeviceID": "32位UUID",
    "is_url": True,
    "geetest": "blending",
    "target": "login",
    "apiid": 110,
    "juhe_strong_auth": "",
    "svrTime": unix_timestamp,
    "login_type": "passwd",
    "version": 79617,          # cltversion
    "time": unix_timestamp,
    "uin": 用户UID,
}

# 2. 编码: msgpack → xxtea_encrypt_zip → base64url
packed = msgpack.pack(login_data)
compressed = zlib.compress(packed)
padded = struct.pack('>I', len(compressed)) + compressed  # 4字节大端长度前缀
padded += b'\x00' * ((4 - len(padded) % 4) % 4)          # 4字节对齐
encrypted = xxtea_encrypt(padded, xxtea_key)              # 标准 XXTEA
b64 = base64.urlsafe_b64encode(encrypted)
msg = b64.replace(b'=', b':').decode()                    # = 替换为 :

# 3. 签名
sign = md5(f"msg={msg}&key={sign_key}")
```

**请求:**

```
GET https://wskacchm.mini1.cn:14130/man_machine/login_v3?msg={msg}&sign={sign}
```

**响应 (code=0 成功):**

```json
{
    "code": 0,
    "baseinfo": {
        "RoleInfo": {
            "NickName": "玩家昵称",
            "Uin": 2056826320
        }
    },
    "authinfo": {
        "sign": "s2值_s2t值",
        "token": "JWT令牌"
    }
}
```

**提取:**

```python
uin = config.uin
name = data["baseinfo"]["RoleInfo"]["NickName"]
jwt = data["authinfo"]["token"]
s2, s2t = data["authinfo"]["sign"].split("_")
```

---

### Step 2: WebSocket 心跳获取真实 sign

> **关键**: 登录返回的 s2/s2t 不是最终值。必须通过 WS 心跳获取真实的 s2/s2t，后续所有房间操作使用心跳返回的值。

**获取 WS 地址:**

```
GET http://wskacchm.mini1.cn:4000/update/?cltversion=79617&clttype=0&uin={uin}&game_env=0&ver=1.55.0&apiid=110&lang=0&country=CN
```

```json
{"conn": "ws://cn-logic2.mini1.cn:4014/"}
```

**WS 心跳:**

```python
# 连接
ws = websocket.connect(ws_url, user_agent="Rainbow/1.0 ...")

# 发送心跳: xxtea 加密的 msgpack([0, seq, jwt])
seq = int(time.time() * 1000) % 10000000
heartbeat = xxtea_encrypt(msgpack.pack([0, seq, jwt]))
ws.send(heartbeat)

# 接收响应: xxtea 解密 → msgpack → [1, seq, code, sign_value]
raw = ws.recv()
data = msgpack.unpack(xxtea_decrypt(raw))
# data = [1, seq, 0, "real_s2_real_s2t"]

real_s2, real_s2t = str(data[3]).split("_", 1)
```

> 注意: WS 加密用的是 `xxtea_encrypt`（不带 zip），不是 `encrypt_zip`。

---

## 4. 创建房间流程

### Step 3: 获取房间服务器配置

**签名算法:**

```python
params = {"cmd": "server_config", "uin": str(uin)}
body = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
# body = "cmd=server_config&uin=2056826320"
auth = md5(body + auth_key)
```

**请求:**

```
GET http://openroom.mini1.cn:8080/server/room?cmd=server_config&uin={uin}&auth={auth}
```

**响应:**

```json
{
    "result": 0,
    "config": {
        "room": {"ip": "1.13.213.183", "port": 8080},
        "proxy": {"ip": "222.95.9.73", "port": 51001},
        "punch": {"ip": "129.211.227.69", "port": 60021},
        "network_type": 1,
        "room_name": "hd_room_ct-10"
    }
}
```

**保存:**

```python
room_url = f"http://{config.room.ip}:{config.room.port}/server/room?"
# 后续 create_room / update_room / close_room 都用这个 URL
```

---

### Step 4: 创建房间

**构造 room_token:**

```python
session_id = random_hex(32)  # 32字符随机hex
room_token = f"{uin:0>12}{timestamp:0>12}{session_id}"
# 例: "002056826320001716854400a1b2c3d4e5f6..."
```

**构造 token:**

```python
token = md5(f"{timestamp}{real_s2}{uin}")
```

**请求参数 (参与签名):**

| 参数 | 值 | 说明 |
|------|-----|------|
| `cmd` | `create_room` | 命令 |
| `connect_mode` | `1` | 连接模式 |
| `country` | `CN` | 国家 |
| `desc` | `""` | 描述 |
| `device` | `110` | api_id |
| `extra_data` | `{json}` | 房间额外信息 |
| `game_label` | `3` | 游戏标签 |
| `has_avatar` | `1` | 有头像 |
| `map_id` | `193fdcb8...` | 地图ID |
| `map_type` | `10260950510809` | 地图类型 |
| `map_version` | `0` | 地图版本 |
| `max_count` | `40` | 最大人数 |
| `net_area` | `0` | 网络区域 |
| `net_isp` | `0` | 运营商 |
| `net_status` | `2` | 网络状态 |
| `passwd` | `""` | 房间密码 |
| `proxy_ip` | `{config.proxy.ip}` | 代理IP |
| `proxy_port` | `{config.proxy.port}` | 代理端口 |
| `punch_ip` | `{config.punch.ip}` | 打洞IP |
| `punch_port` | `{config.punch.port}` | 打洞端口 |
| `right` | `1` | 权限 |
| `room_name` | `"MN2MC 0.0.6"` | 房间名 |
| `room_type` | `4` | 房间类型 |
| `s2t` | `{real_s2t}` | WS心跳获取的s2t |
| `time` | `{timestamp}` | 时间戳 |
| `token` | `{md5(time+s2+uin)}` | 认证令牌 |
| `uicon` | `645` | 用户图标 |
| `uicon_box` | `33279` | 图标框 |
| `uin` | `{uin}` | 用户ID |
| `uname` | `""` | 用户名 |
| `use_proxy` | `0` | 是否用代理 |
| `version` | `1.55.0` | 版本 |

**扩展参数 (不参与签名):**

| 参数 | 值 |
|------|-----|
| `public_type` | `0` |
| `prei_room_name_idx` | `0` |
| `regapiid` | `6` |
| `cltapiid` | `110` |
| `cltversion` | `79617` |
| `lang` | `0` |
| `game_session_id` | `""` |
| `session_id` | `{session_id}` |
| `room_token` | `{room_token}` |

**签名:**

```python
# 对参与签名的参数按 key 排序，拼接为 k=v&k=v，再加 auth_key 做 MD5
sorted_body = "&".join(f"{k}={v}" for k, v in sorted(sign_params.items()) if v is not None)
auth = md5(sorted_body + auth_key)
```

**请求:**

```
GET {room_url}?{sign_params_encoded}&{extend_params_encoded}&auth={auth}
```

**响应:**

```json
{"result": 0}
```

---

### Step 5: 启动 RakNet 服务器

```python
import aiorak

server = await aiorak.create_server(
    ("0.0.0.0", 19132),
    connection_handler,
    guid=uin  # guid 设为登录的 uin
)
```

---

### Step 6: 房间心跳维持 (每 15 秒)

**签名参数 (参与auth计算):**

| 参数 | 值 |
|------|-----|
| `cmd` | `host_update_room` |
| `locked` | `0` |
| `members` | `{uin}` |
| `ping` | `89` |
| `aiPlayerCounts` | `""` |
| `ready` | `1` |
| `stage` | `0` |
| `uin` | `{uin}` |
| `umpire` | `0` |

**附加参数 (不参与签名):**

```
pause=0, can_trace=9323, public_type=0, max_count=10, passwd=, is_empty_night=0
```

**签名同 create_room:**

```python
auth = md5("&".join(f"{k}={v}" for k,v in sorted(auth_params.items()) if v is not None) + auth_key)
```

---

### Step 7: 关闭房间

**签名参数:**

```python
auth = md5("cmd=close_room&uin={uin}" + auth_key)
```

**请求:**

```
GET {room_url}?cmd=close_room&uin={uin}&apiid=110&country=CN&lang=0&ver=1.55.0
    &regapiid=6&cltapiid=110&cltversion=79617&game_session_id=
    &session_id={session_id}&room_token={room_token}&auth={auth}
```

---

## 5. 客户端连接流程

### 客户端搜索房间

客户端通过 `POST http://cs-gsmgr.mini1.cn/v2/room/get` 搜索房间，服务端返回房间的 `ip:port`。

### RakNet 握手

```
Client → Server: 0x05 ID_OPEN_CONNECTION_REQUEST_1 (MTU discovery)
Server → Client: 0x06 ID_OPEN_CONNECTION_REPLY_1
Client → Server: 0x07 ID_OPEN_CONNECTION_REQUEST_2
Server → Client: 0x08 ID_OPEN_CONNECTION_REPLY_2
```

### 游戏包格式

**客户端→服务端 (C2S):**

```
0x89 | UIN(4B BE) | PLACEHOLDER(8B) | MsgCode(2B LE) | Length(2B LE) | ProtobufData
```

**服务端→客户端 (S2C):**

```
0x89 | MsgCode(2B LE) | Length(2B LE) | ProtobufData
```

### 进入世界序列 (从实际抓包)

```
1.  S→C  PB_SYNC_ROOM_EXTRA_HC      (5205)  房间信息、地图URL、MD5
2.  S→C  PB_SS_SYNC_TASK_HC          (6025)  任务同步
3.  S→C  PB_PLAYERS_UPDATEINFO_HC    (4013)  在线玩家列表
4.  S→C  PB_GROUP_WEATHER_HC         (7019)  x7 各区域天气
5.  C→S  PB_ROLE_ENTER_WORLD_CH      (1001)  客户端进入世界 (含Auth字段)
6.  C→S  PB_HEARTBEAT_CH             (11)    x4 心跳
7.  S→C  PB_HEARTBEAT_HC             (12)    x4 心跳回复
8.  S→C  PB_CUSTOM_MSG               (7000)  SDBRemoteBin 沙盒版本协商
9.  S→C  PB_VEHICLE_ALL_ITEMID_HC    (5081)  载具物品
10. S→C  PB_CUSTOM_MODELCLASS_HC     (5055)  自定义模型分类
11. S→C  PB_CUSTOM_ITEMIDS_HC        (5051)  自定义物品ID (123项)
12. S→C  PB_PACKING_FCMDATA_HC       (6051)  打包FCM数据
13. S→C  PB_IMPORT_MODEL_HC          (6075)  导入模型
14. S→C  PB_PLAYER_SETATTR_HC        (5096)  玩家属性 (HP=100等)
15. S→C  PB_SYNC_CHUNK_DATA_HC       (102)   x326 区块数据 (最大量)
16. S→C  PB_GENERAL_ENTER_AOI_HC     (2001)  实体进入视野
17.      ... 正常游戏循环 ...
```

### 高频包统计 (60秒实测)

| 消息 | 方向 | 次数 | 说明 |
|------|------|------|------|
| `PB_ACTOR_MOVEV3_HC` | S→C | 813 | 实体移动 |
| `PB_PLAYEFFECT_HC` | S→C | 459 | 特效播放 |
| `PB_SYNC_CHUNK_DATA_HC` | S→C | 326 | 区块数据 |
| `PB_SYNC_MOVE_CH` | C→S | 246 | 玩家移动 |
| `PB_PHYSICS_ASYNC_TIMESTAMP` | 双向 | 190 | 物理时间戳 |
| `PB_GENERAL_ENTER_AOI_HC` | S→C | 124 | 实体进入AOI |
| `PB_BLOCK_PUNCH_HC` | S→C | 115 | 方块交互 |
| `PB_ACTOR_LEAVE_AOI_HC` | S→C | 109 | 实体离开AOI |
| `PB_SS_SYNC_TASK_HC` | S→C | 108 | 任务同步 |
| `PB_SYNC_CHUNK_DATA_CH` | C→S | 108 | 区块请求 |

---

## 6. Protobuf 注册表

共 660 个 ePBMsgCode 枚举值，659 个已映射到 protobuf 消息类（唯一缺少的 `PB_MAX_MSG_CODE` 是哨兵值）。

消息类分布:

| 模块 | 消息数 | 说明 |
|------|--------|------|
| `common.py` | 179 msg + 8 enum | 公共类型、ePBMsgCode 枚举 |
| `ch.py` | 223 | Client→Host 消息 |
| `hc.py` | 350 | Host→Client 消息 |
| `ch_ver2.py` | — | CH v2 扩展 |
| `hc_ver2.py` | — | HC v2 扩展 |
| `common_ver1.py` | 86 | 公共类型 v1 |
| `hc_ver1.py` | 242 | HC v1 扩展 |
| `gs2ds.py` | 40 | 游戏服→数据服 |
| `room.py` | 6 | 房间管理 |
| `stub_ch.py` | 10 | CH 空壳补全 |
| `stub_hc.py` | 15 | HC 空壳补全 |
