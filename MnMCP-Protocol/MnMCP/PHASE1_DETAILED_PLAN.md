# MnMCP 3 Phase 1 详细执行计划

**版本**: 2026-05-23-15  
**阶段**: Phase 1 - 基础重构与协议准备  
**预计工期**: 2天  
**基于**: 新发现的协议文档和密钥材料

---

## 🎯 Phase 1 目标

1. 修复所有P0级技术债务
2. 整合新发现的协议规范
3. 建立UDP/WPK协议处理基础
4. 完善密钥管理和配置系统

---

## 📚 新发现关键资源分析

### 1. 协议文档更新

**来源**: `开发资源文件/01-文档/`

| 文档 | 关键信息 | 影响 |
|------|----------|------|
| `20-Phase2-协议逆向分析报告.md` | 自研引擎（非Unity）、mmtls协议、ilink-network v2.3.2.f3 | 协议实现需参考微信Mars框架 |
| `udp_package_report.md` | **AES-128-GCM** (不是CBC!)、ECDH+HKDF密钥派生、WPKG包结构 | 必须修正加密实现 |
| `旧版登录说明.md` | WebSocket RPC格式、多分支登录流程 | 认证模块需重构 |

### 2. 密钥材料

**来源**: `开发资源文件/04-密钥材料/`

| 文件 | 内容 | 用途 |
|------|------|------|
| `found_keys.json` | 内存中提取的密钥偏移和上下文 | 调试参考 |
| `xxtea_contexts.json` | XXTEA使用场景：`{"serializeFlag":"json","compressFlag":"none","encrypFlag":"xxtea_64"}` | 确认XXTEA仅用于特定JSON |
| `rsa_public_keys.json` | RSA公钥（证书相关） | 初始握手验证 |

### 3. 数据文件

**来源**: `开发资源文件/03-数据文件/`

| 文件 | 内容 | 用途 |
|------|------|------|
| `Extracted_Proto_Definitions.txt` | Protobuf定义 | 协议解析 |
| `login_flow_export.json` | 登录流程数据 | 流程参考 |
| `udp_package.txt` | UDP包样本 | 逆向分析 |

### 4. 工具脚本

**来源**: `开发资源文件/02-工具脚本/`

| 脚本 | 功能 | 复用价值 |
|------|------|----------|
| `liblibGameApp_udp_decoder.py` | UDP包解码器 | **高** - 可直接参考 |
| `Universal_GameApp_Decryptor.py` | 通用解密器 | **高** - 加密逻辑参考 |
| `frida_blockid_hook.js` | Frida Hook脚本 | **中** - 调试参考 |
| `analyze_handshake.py` | 握手分析 | **高** - ECDH参考 |

---

## 🔧 WPKG/UDP协议规范（更新版）

基于新文档，修正之前的理解：

### 包结构（WPKG - WeChat Package?）

```
Offset  Len   Field                    说明
0       2     Magic/Version            魔数/版本
2       2     CmdID                    命令ID
4       4     SeqNo                    序列号
8       4     BodyLen                  负载长度
12      1     EncryptAlgo              0=HybridECDH, 1=AesGcm
13      1     CompressAlgo             0=none, 1/4=zlib, 2=lz4
14      1     CompressVersion          压缩版本
15      1     HeaderEnd/Flags          标志
16      12    Nonce (GCM IV, 96-bit)   随机数
28      N     Ciphertext               密文
28+N    16    GCM Tag                  认证标签
```

### 加密模式

| 模式 | ID | 算法 | 使用场景 |
|------|-----|------|----------|
| HybridECDH | 0 | 一次性ECDH握手 | 无现成会话的建连 |
| AesGcm | 1 | AES-128-GCM | 已建立会话后的数据 |

### 密钥派生流程

```python
# 1. ECDH握手
shared_secret = ECDH_compute_key(client_priv, server_pub)  # 32B

# 2. HKDF派生
prk = HKDF_Extract(salt=b'', ikm=shared_secret)
session_material = HKDF_Expand(prk, info=b'', length=48)  # 48B

# 3. 切分
aes_key = session_material[0:16]      # 16B
nonce_base = session_material[16:28]  # 12B
# 其余 [28:48] 保留/填充

# 4. GCM加密
# nonce = 12字节 (从session或header取)
# tag = 16字节 (GCM自动添加)
```

---

## 🏗️ 新增/修改的模块

### 1. mn2mc/crypto/ (需重构)

```
crypto/
├── __init__.py
├── xxtea.py              # 现有，用于特定JSON
├── aes_gcm.py            # 【新增】AES-128-GCM实现
├── ecdh.py               # 【新增】ECDH密钥交换
├── hkdf.py               # 【新增】HKDF密钥派生
├── session.py            # 【新增】会话管理
└── wpkg.py               # 【新增】WPKG包加解密
```

**优先级**: P0 - 协议核心

### 2. mn2mc/protocol/ (需重构)

```
protocol/
├── __init__.py
├── wpkg/                 # 【新增】WPKG协议栈
│   ├── __init__.py
│   ├── header.py         # 协议头解析
│   ├── packet.py         # 包结构
│   └── codec.py          # 编解码器
├── mini/
│   └── (迁移现有)
└── mc/
    └── (迁移现有)
```

**优先级**: P0 - 协议核心

### 3. mn2mc/network/raknet/ (需新增)

```
network/
├── __init__.py
├── raknet/               # 【新增】RakNet协议
│   ├── __init__.py
│   ├── connection.py
│   ├── server.py
│   └── reliability.py    # 可靠传输
├── websocket/
│   └── (用于登录RPC)
└── http/
    └── (保持现有)
```

**优先级**: P1 - Phase 2重点

---

## 📋 修正后的Phase 1任务

### Day 1: 安全与配置 (2026-05-24)

#### 任务1.1: 清理硬编码密钥 (TD-001) - 2h

**文件修改**:
- `mn2mc/mini/auth.py` - 移除MD5签名密钥硬编码
- `mn2mc/mini/room.py` - 移除AUTH_KEY硬编码

**更新config.template.yaml**:
```yaml
mini:
  central_server:
    sign_key: ""           # MD5签名密钥
    auth_key: ""           # 房间认证密钥
    auth_url: "https://wskacchm.mini1.cn:14130"
    room_url: "http://openroom.mini1.cn:8080"
    
  crypto:
    xxtea_key: ""          # XXTEA密钥 (JSON加密)
    ecdh_private: ""       # ECDH私钥 (可选，通常临时生成)
    ecdh_public_server: "" # 服务器ECDH公钥
```

#### 任务1.2: 移除URL硬编码 (TD-002) - 1h

同上计划。

#### 任务1.3: 添加错误处理 (TD-003) - 3h

**网络调用添加try-catch**:
- `auth.py` 登录请求
- `room.py` 房间API请求
- `server.py` 网络操作

#### 任务1.4: 创建新加密模块 (高优先级!) - 4h

**创建 `mn2mc/crypto/aes_gcm.py`**:
```python
"""AES-128-GCM for WPKG protocol."""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Tuple

def aes_gcm_encrypt(key: bytes, nonce: bytes, plaintext: bytes, aad: bytes = None) -> Tuple[bytes, bytes]:
    """Encrypt and return (ciphertext, tag)."""
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, aad)
    # ciphertext_with_tag includes 16B tag at end
    ciphertext = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]
    return ciphertext, tag

def aes_gcm_decrypt(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes, aad: bytes = None) -> bytes:
    """Decrypt with tag verification."""
    aesgcm = AESGCM(key)
    ciphertext_with_tag = ciphertext + tag
    return aesgcm.decrypt(nonce, ciphertext_with_tag, aad)
```

**创建 `mn2mc/crypto/hkdf.py`**:
```python
"""HKDF-SHA256 for key derivation."""
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

def derive_session_keys(shared_secret: bytes, length: int = 48) -> bytes:
    """Derive session material from ECDH shared secret."""
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=None,  # salt=0 in original
        info=b''
    )
    return hkdf.derive(shared_secret)

def split_session_material(material: bytes) -> Tuple[bytes, bytes]:
    """Split into aes_key and nonce_base."""
    aes_key = material[0:16]
    nonce_base = material[16:28]
    return aes_key, nonce_base
```

**创建 `mn2mc/crypto/wpkg.py`**:
```python
"""WPKG (WeChat Package) protocol handler."""
import struct
from dataclasses import dataclass
from typing import Optional

@dataclass
class WPKGHeader:
    magic: int           # 2 bytes
    cmd_id: int          # 2 bytes  
    seq_no: int          # 4 bytes
    body_len: int        # 4 bytes
    encrypt_algo: int    # 1 byte (0=HybridECDH, 1=AesGcm)
    compress_algo: int   # 1 byte (0=none, 1/4=zlib, 2=lz4)
    compress_ver: int     # 1 byte
    flags: int           # 1 byte
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'WPKGHeader':
        return cls(
            magic=struct.unpack('>H', data[0:2])[0],
            cmd_id=struct.unpack('>H', data[2:4])[0],
            seq_no=struct.unpack('>I', data[4:8])[0],
            body_len=struct.unpack('>I', data[8:12])[0],
            encrypt_algo=data[12],
            compress_algo=data[13],
            compress_ver=data[14],
            flags=data[15]
        )
    
    def to_bytes(self) -> bytes:
        return struct.pack('>HHIIBBBBB',
            self.magic, self.cmd_id, self.seq_no, self.body_len,
            self.encrypt_algo, self.compress_algo, self.compress_ver, self.flags, 0)

class WPKGPacket:
    def __init__(self, header: WPKGHeader, nonce: bytes, ciphertext: bytes, tag: bytes):
        self.header = header
        self.nonce = nonce
        self.ciphertext = ciphertext
        self.tag = tag
    
    @classmethod
    def decrypt(cls, data: bytes, session_key: bytes) -> 'WPKGPacket':
        """Decrypt WPKG packet."""
        header = WPKGHeader.from_bytes(data[:16])
        nonce = data[16:28]
        ciphertext = data[28:-16] if header.encrypt_algo == 1 else data[28:28+header.body_len-16]
        tag = data[-16:]
        # ... decrypt logic
        return cls(header, nonce, ciphertext, tag)
```

---

### Day 2: 全局变量重构与类型注解 (2026-05-24)

#### 任务2.1: 重构全局变量 (TD-004) - 6h

**auth.py重构为类**:
```python
class AuthManager:
    def __init__(self, config: dict):
        self._uin: int = 0
        self._jwt: str = ""
        self._name: str = "Unknown"
        self._s2: str = ""
        self._s2t: str = ""
        self._config = config
    
    async def login(self) -> bool:
        """Perform login with error handling."""
        try:
            # ... login logic
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    @property
    def uin(self) -> int:
        return self._uin
    
    @property
    def is_authenticated(self) -> bool:
        return bool(self._jwt)
```

#### 任务2.2: 补充类型注解 (TD-005) - 4h

使用mypy检查并修复所有类型问题。

---

## 🔄 集成新资源到开发流程

### 1. 复用已有工具

```python
# 在mn2mc/utils/下创建adapters/
utils/
├── adapters/
│   ├── __init__.py
│   ├── udp_decoder.py        # 适配liblibGameApp_udp_decoder.py
│   └── gameapp_decryptor.py  # 适配Universal_GameApp_Decryptor.py
```

### 2. 密钥提取脚本

```python
# tools/extract_keys.py
import json
from pathlib import Path

def load_found_keys():
    """Load keys from reverse engineering results."""
    keys_path = Path("../MnMCPResources/开发资源文件/04-密钥材料/found_keys.json")
    with open(keys_path) as f:
        return json.load(f)

def extract_xxtea_contexts():
    """Extract XXTEA usage contexts."""
    contexts_path = Path("../MnMCPResources/开发资源文件/04-密钥材料/xxtea_contexts.json")
    with open(contexts_path) as f:
        return json.load(f)
```

### 3. 协议验证测试

```python
# tests/test_wpkg_protocol.py
import pytest
from mn2mc.crypto.wpkg import WPKGHeader, WPKGPacket

def test_wpkg_header_parsing():
    # 使用从udp_package.txt提取的样本
    sample = bytes.fromhex("...")
    header = WPKGHeader.from_bytes(sample[:16])
    assert header.magic == 0x4B47  # 'KG'

def test_aes_gcm_encryption():
    from mn2mc.crypto.aes_gcm import aes_gcm_encrypt, aes_gcm_decrypt
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    nonce = bytes.fromhex("000102030405060708090a0b")
    plaintext = b"Hello WPKG!"
    
    ciphertext, tag = aes_gcm_encrypt(key, nonce, plaintext)
    decrypted = aes_gcm_decrypt(key, nonce, ciphertext, tag)
    assert decrypted == plaintext
```

---

## 📝 更新后的技术债务清单

| ID | 问题 | 优先级 | 状态 | 新增/更新 |
|----|------|--------|------|-----------|
| TD-001 | 硬编码安全密钥 | P0 | 🔴 待修复 | 新增更多密钥类型 |
| TD-002 | 硬编码服务器地址 | P0 | 🔴 待修复 | - |
| TD-003 | 缺少错误处理 | P0 | 🔴 待修复 | - |
| TD-004 | 全局变量重构 | P1 | 🟡 待修复 | - |
| TD-005 | 类型注解补全 | P1 | 🟡 待修复 | - |
| TD-006 | 模块职责不清晰 | P1 | 🟡 待修复 | - |
| TD-009 | **加密算法错误** | **P0** | **🔴 紧急** | **新发现：使用AES-CBC而非AES-GCM** |
| TD-010 | **WPKG协议未实现** | **P0** | **🔴 紧急** | **新发现：需要完整WPKG协议栈** |
| TD-011 | **缺少ECDH支持** | **P1** | **🟡 待修复** | **新发现：需要ECDH+HKDF** |

---

## 🎯 立即执行任务

### 紧急修复 (今天完成)

1. **修正加密算法理解** (30分钟)
   - 更新所有文档：协议使用AES-128-GCM，不是CBC
   - 标记现有xxtea.py为"仅用于JSON特定场景"

2. **创建新加密模块** (4小时)
   - `mn2mc/crypto/aes_gcm.py`
   - `mn2mc/crypto/hkdf.py`
   - `mn2mc/crypto/wpkg.py`

3. **更新配置文件** (30分钟)
   - 添加新的密钥配置项
   - 添加加密算法选择配置

4. **复用逆向工程工具** (1小时)
   - 创建适配器复用`liblibGameApp_udp_decoder.py`
   - 提取测试样本

---

## 📚 参考文档

| 文档 | 路径 | 用途 |
|------|------|------|
| Phase2协议分析报告 | `开发资源文件/01-文档/20-Phase2-协议逆向分析报告.md` | 引擎架构、mmtls |
| UDP包报告 | `开发资源文件/01-文档/udp_package_report.md` | **WPKG协议核心** |
| 登录说明 | `开发资源文件/未分类/旧版登录说明.md` | 登录流程 |
| 密钥材料 | `开发资源文件/04-密钥材料/` | 密钥提取参考 |
| UDP解码器 | `开发资源文件/02-工具脚本/liblibGameApp_udp_decoder.py` | 复用参考 |

---

## ✅ Phase 1 完成标准

- [ ] 所有硬编码密钥已移除 (TD-001, TD-009)
- [ ] AES-128-GCM模块已实现 (TD-009)
- [ ] HKDF密钥派生已实现 (TD-011)
- [ ] WPKG协议头解析已实现 (TD-010)
- [ ] 配置文件模板已更新 (所有密钥类型)
- [ ] 错误处理已添加 (TD-003)
- [ ] 全局变量已重构为类 (TD-004)
- [ ] 类型注解已补充 (TD-005)
- [ ] 逆向工程工具已复用适配

---

**下一步**: 完成Phase 1后，进入Phase 2 - UDP协议栈实现
