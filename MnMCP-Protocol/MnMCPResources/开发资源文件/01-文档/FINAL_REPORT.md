# 迷你世界内存提取 - 最终分析报告

## 环境
- VMware vmem: `52EB1-90b07d16.vmem` (4.0 GB)
- 客户端版本: 79105
- UIN: 2056826320
- 设备ID: WIN9e40eedc04a71931ece88472bb778bc4

---

## 1. 认证体系

### JWT Token
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aW4iOiIyMDU2ODI2MzIwIiwidGltZSI6MTc3MzQxODM0NywiZmxhZyI6MSwiZXhwIjoxNzc2MDEwMzQ3LCJpc3MiOiJpbXNlcnZlciJ9.9XgDXNS9kvyDQghl9j0aUdPKYSGyT-pZNZdGemRT-Vc
```
- **算法**: HS256
- **签发者**: imserver
- **UIN**: 2056826320
- **签发时间**: 1773418347
- **过期时间**: 1776010347 (约30天有效期)
- **Signature (hex)**: `f578035cd4bd92fc83420865f63d1a51d3ca6121b24fea593597467a6453f957`

### 微信登录
- **WeChat AppID**: `wx0344e7ba7bfcacaf`
- **OAuth Scope**: `snsapi_login`
- **回调URL**: `https://mnlogin.mini1.cn/thirdconnect/callback/login`
- **授权码**: `0819OQll2R6Dkh4IJtnl2fvUsy39OQl6`

---

## 2. API签名体系

### Sign 格式
```
sign = md5(参数拼接 + appkey) + "_" + timestamp
```

### 已捕获的 Sign 值
| Sign MD5 | Timestamp | 用途 |
|---|---|---|
| `61bee5fa0e7f2c7a8039bbbee5cfd35f` | 1773418346 | 登录签名 |
| `9c84b5e61e5fb8a6ef82f4d3cc24c5be` | 1773418348 | API请求 |
| `664c958f5711353945579c41248ae718` | 1638758234 | 旧缓存 |

### genApiServerQueryStr 函数参数
```lua
-- 从内存中提取的函数签名:
function genApiServerQueryStr(self, sub, postData, callback, headers, appid, appkey)
  local curtime = ...
  local poststr = ...
  local md5 = ...
  local params = ...
  local querystr = ...
  local baseUrl = ...
  local url = ...
  -- signType: "md5" 或 "client_ext" 或 "client"
end
```

### Sign 类型
1. **signType=md5** - 标准 MD5 签名 (appkey参与)
2. **signType=client_ext** - 客户端扩展签名
3. **signType=client** - 客户端签名
4. **signType=1** - QQ好友列表等接口

### 已知 AppID
- **游戏内部 appid**: `1835` (从 Lua 常量)
- **微信 appid**: `wx0344e7ba7bfcacaf`

### Auth 值示例
```
auth=4dc7171fb1b69633a5df805092483cef  (avatar接口)
auth=8dfaa4807de4cce18701dddcb18b47b1  (anti_addiction接口)
```

---

## 3. 加密体系

### UDP 通信加密
- **算法**: AES-128-CBC (国服)
- **密钥交换**: ECDH (DHKeyMgr)
- **Lua 接口**:
  - `GenerateClientDHKey()`
  - `GetClientPublicKey()`
  - `SetServerPublicKey()`
  - `GetServerPublicKey()`
  - `GetDHKey()` → 最终 AES 密钥
  - `GetLoginDhp()` / `GetLoginDhg()` → DH 参数

### AES 密钥管理 (AES_CONST Lua模块)
```
字段结构 (0x764f2dd4):
  aes_iv          → 当前会话 IV
  aes_key         → 当前会话 Key
  hex_num         → hex 编码的数值
  secretKey       → DH 协商后的密钥
  serverPublicKey → 服务器公钥
  commonTask      → 通用任务密钥
  common_task_key → 任务加密 key
  common_task_iv  → 任务加密 iv
```

### RSA 公钥 (1024-bit, 握手用)
```
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCsAxNCSLyNUCOP1QqYStE8ZeiU
v4afaMqEmoLCKb0mUZYvYOoVN7LPMi2IVY2MRaFJvuND3glVw1RDm2VJJtjQkwUd
3kpR9TrHAf7UQOVTpNo3Vi7pXTOqZ6bh3ZA/fs56jDCCKV6+wT/pCeu8N6vVnPrD
z3SdHIeNeWb/woazCwIDAQAB
-----END PUBLIC KEY-----
```

### 资源加密
- **算法**: XXTEA (g_DevEncrypt)
- **相关模块**: `encrypt`, `decrypt`, `encrypt_zip`, `decrypt_unzip`

### Byted SDK 密钥
```
byted-publicb: d7899c72e6510cc171283c5cb61bf7cc
byted-sign:    9308276afc81ac9f0e53
byted-$32b:    (32字节密钥, 用于加密)
```

### QQ 相关密钥
```
b2b850658de2ee4eff1bf3439f5b394d  (QQ OpenProxy key 1)
f189c95b1f31d472bb0065ec0909017e  (QQ OpenProxy key 2)
```

---

## 4. API 端点

| 域名 | 用途 |
|---|---|
| `mnlogin.mini1.cn` | 登录认证 |
| `shequ.mini1.cn:8081` | 社区/游戏数据 API |
| `credit-api.mini1.cn` | 积分/经验 API |
| `cdk.mini1.cn` | CDK兑换/迷你币 |
| `kfz.mini1.cn` | 开发者中心/活动 |
| `course.miniaixue.com` | 教育课程 |
| `graph.qq.com` | QQ社交 |
| `124.70.174.136:8080` | 内网/测试服务器 |

### 关键 API 路径
```
/miniw/anti_addiction  - 防沉迷
/miniw/map             - 地图数据
/miniw/map_shop        - 地图商店
/miniw/group           - 群组
/miniw/skill           - 技能
/miniw/profile         - 用户资料
/miniw/php_cmd         - PHP命令
/miniw/recux           - 推荐
/miniw/kfz_shop        - 开发者商店
/miniw/cm              - 通用消息
/avatar/v1/get         - 头像
/api/v1/action/exp_map - 经验地图
/api/config            - 配置
/api/flow/user/get     - 用户流量
/api/minicoin_revice   - 迷你币
```

---

## 5. Lua 模块清单

### 核心管理器
```
ClientAccountMgr / AccountManager
ClientBuddyMgr / BuddyManager
AchievementManager / AchievementMgr
HttpReportMgr / ReportMgr
ModManager / ModMgr / ModEditorManager
PlatformSdkManager / SdkManager
SnapshotMgr / SnapshotForShare / SnapshotForGame
UIEditorManager / UIProjectLibManager
DevEncrypt / g_DevEncrypt
RoomSyncResMgr
MicroUpdateMgr
SpringFestivalActivityMgr
```

### 加密相关
```
AES_CONST          - AES 常量和密钥管理
DHKeyMgr           - DH 密钥交换
g_DevEncrypt       - XXTEA 资源加密
g_recharge_md5_related - 充值 MD5 校验
genApiServerQueryStr   - API 签名生成
genApiQueryStr         - API 查询字符串
```

---

## 6. 关键发现总结

1. **Sign 算法**: `md5(排序参数 + appkey)_timestamp`, appkey 在 Lua 中通过 `genApiServerQueryStr` 传入
2. **appid=1835** 是游戏内部 API 的 appid
3. **byted-publicb** 密钥 `d7899c72e6510cc171283c5cb61bf7cc` 用于字节跳动 SDK 通信
4. **shequ.mini1.cn** 使用 s7 参数进行请求签名 (自定义编码)
5. **auth 值** 是基于 uin + time + s2t 计算的 MD5
6. **内网测试服务器** `124.70.174.136:8080` 暴露在内存中
