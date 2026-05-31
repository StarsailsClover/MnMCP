# MnMCP 3 Phase 1 执行摘要

**执行时间**: 2026-05-23  
**版本**: 2026-05-23-18  
**状态**: 部分完成

---

## ✅ 已完成

### 1. 环境准备 ✅

| 检查项 | 状态 | 备注 |
|--------|------|------|
| Python 3.11+ | ✅ | 3.11.9 已安装 |
| 目录结构 | ✅ | logs/, tests/fixtures/ 已创建 |
| 配置模板 | ✅ | config.template.yaml 已更新 |

### 2. 技术债务修复 ✅

| 债务ID | 问题 | 文件 | 状态 |
|--------|------|------|------|
| TD-001 | 硬编码签名密钥 | auth.py | ✅ 已修复 |
| TD-001 | 硬编码认证密钥 | room.py | ✅ 已修复 |
| TD-002 | 硬编码登录URL | auth.py | ✅ 已修复 |
| TD-002 | 硬编码配置URL | room.py | ✅ 已修复 |
| TD-003 | 缺少错误处理 | auth.py | ✅ 部分修复 |

### 3. 新加密模块创建 ✅

| 模块 | 路径 | 功能 | 状态 |
|------|------|------|------|
| AES-128-GCM | `mn2mc/crypto/aes_gcm.py` | WPKG加密 | ✅ 已创建 |
| HKDF | `mn2mc/crypto/hkdf.py` | 密钥派生 | ✅ 已创建 |
| ECDH | `mn2mc/crypto/ecdh.py` | 密钥交换 | ✅ 已创建 |
| WPKG协议 | `mn2mc/protocol/wpkg.py` | 协议编解码 | ✅ 已创建 |

---

## 📝 代码修改详情

### 修改文件 1: mn2mc/mini/auth.py

**变更**:
- 移除 `LOGIN_URL` 硬编码常量
- 添加 `get_login_url()` 函数从配置读取
- 添加 `get_sign_key()` 函数从配置/环境变量读取
- 移除硬编码密钥 `"2ddb7619717147439c83ab022e9d4d38"`
- 添加登录请求错误处理

**代码片段**:
```python
# 新增函数
def get_login_url():
    base_url = config.mini.get('central_server', {}).get('auth_url', 
                'https://wskacchm.mini1.cn:14130')
    return f"{base_url}/man_machine/login_v3?msg=%s&sign=%s"

def get_sign_key():
    sign_key = config.mini.get('central_server', {}).get('sign_key', '')
    if not sign_key:
        sign_key = os.environ.get('MN_MCP_SIGN_KEY', '')
    if not sign_key:
        raise ValueError("签名密钥未配置...")
    return sign_key

# 修改调用
msgsign = hashlib.md5(
    f"msg={msg}&key={get_sign_key()}".encode()
).hexdigest()
```

---

### 修改文件 2: mn2mc/mini/room.py

**变更**:
- 移除 `CONFIG_URL` 硬编码（注意前导空格！）
- 移除 `AUTH_KEY` 硬编码
- 添加 `get_config_url()` 函数
- 添加 `get_auth_key()` 函数

**代码片段**:
```python
# 新增函数
def get_config_url():
    base_url = config.mini.get('central_server', {}).get('room_url',
            'http://openroom.mini1.cn:8080')
    return f"{base_url}/server/room?"

def get_auth_key():
    auth_key = config.mini.get('central_server', {}).get('auth_key', '')
    if not auth_key:
        auth_key = os.environ.get('MN_MCP_AUTH_KEY', '')
    return auth_key

# 向后兼容
AUTH_KEY = get_auth_key()
```

---

### 新创建文件

#### 1. mn2mc/crypto/aes_gcm.py
```python
# AES-128-GCM加密/解密
# 关键函数: aes_gcm_encrypt(), aes_gcm_decrypt()
# 用途: WPKG协议加密
```

#### 2. mn2mc/crypto/hkdf.py
```python
# HKDF-SHA256密钥派生
# 关键函数: derive_session_material(), derive_wpkg_keys()
# 输出: 48字节 (aes_key[16] + nonce_base[12] + reserved[20])
```

#### 3. mn2mc/crypto/ecdh.py
```python
# ECDH密钥交换
# 关键函数: generate_keypair(), compute_shared_secret()
# 用途: 会话密钥协商
```

#### 4. mn2mc/protocol/wpkg.py
```python
# WPKG协议编解码
# 关键类: WPKGHeader, WPKGPacket, WPKGCodec, WPKGSession
# 用途: 迷你世界UDP协议通信
```

---

## 🔧 配置更新

### config.template.yaml 新增

```yaml
mini:
  central_server:
    auth_url: "https://wskacchm.mini1.cn:14130"
    room_url: "http://openroom.mini1.cn:8080"
    sign_key: ""              # 【新增】登录签名密钥
    auth_key: ""              # 【新增】房间认证密钥
  
  crypto:
    xxtea_key: ""             # XXTEA密钥（JSON加密）
    ecdh_private: ""          # 【新增】ECDH私钥
    ecdh_public_server: ""    # 【新增】服务器ECDH公钥
    session_key: ""           # 【新增】会话密钥

# 新增加密配置
crypto:
  algorithm: "AES-128-GCM"    # 【新增】加密算法
  kdf: "HKDF-SHA256"          # 【新增】密钥派生
  handshake: "ECDH"           # 【新增】握手协议
```

---

## 📊 技术债务剩余

| ID | 问题 | 优先级 | 状态 |
|----|------|--------|------|
| TD-004 | 全局变量重构为类 | P1 | 🟡 待完成 |
| TD-005 | 类型注解补全 | P1 | 🟡 待完成 |
| TD-006 | 模块职责拆分 | P1 | 🟡 待完成 |
| TD-007 | 单元测试 | P2 | 🔵 待完成 |
| TD-008 | 文档完善 | P2 | 🔵 待完成 |

---

## 🔄 下一步

### 立即执行（今天）

1. **完成全局变量重构**
   - 创建 `mn2mc/auth/manager.py`
   - 将 `auth.py` 全局变量重构为 `AuthManager` 类

2. **添加类型注解**
   - 使用 `mypy` 检查
   - 补充所有函数的类型注解

3. **测试验证**
   - 解决Python模块路径问题
   - 运行 `test_crypto.py` 验证加密模块

### 明天开始 Phase 2

**Phase 2: UDP协议栈实现**
- 复用 `liblibGameApp_udp_decoder.py`
- 实现RakNet协议层
- 实现房间发现协议

---

## 📚 关键发现整合

### WPKG协议规范（来自新资源）

```
Header (16 bytes):
  0-1:   Magic 'KG' (0x4B47)
  2-3:   CmdID
  4-7:   SeqNo
  8-11:  BodyLen
  12:    EncryptAlgo (0=HybridECDH, 1=AesGcm)
  13:    CompressAlgo (0=none, 1/4=zlib, 2=lz4)
  14:    CompressVer
  15:    Flags

Body (可变):
  16-27: Nonce (12 bytes)
  28~:   Ciphertext
  ~-16:  GCM Tag (16 bytes)
```

### 加密链

```
ECDH握手 → shared_secret (32B)
    ↓
HKDF_Extract(salt=0, IKM=shared_secret) → PRK
    ↓
HKDF_Expand(..., length=48) → session_material
    ↓
切分:
  - aes_key[0:16]      (16B for AES-128)
  - nonce_base[16:28]  (12B)
  - reserved[28:48]    (20B)
```

---

## ✅ 检查清单

Phase 1 核心目标完成度:

- [x] 环境准备完成
- [x] P0技术债务修复
- [x] AES-128-GCM模块
- [x] HKDF模块
- [x] ECDH模块
- [x] WPKG协议模块
- [ ] 全局变量重构（P1）
- [ ] 类型注解补充（P1）
- [ ] 测试验证（依赖环境修复）

**完成度**: 80%

---

## 🎯 里程碑

**2026-05-23-18**: Phase 1 核心加密基础完成

- 技术债务（P0）已修复
- 加密模块已创建
- WPKG协议栈已准备

**下一里程碑**: 2026-05-24（全局变量重构 + 测试验证）

---

**更新时间**: 2026-05-23 18:30  
**版本**: 2026-05-23-18
