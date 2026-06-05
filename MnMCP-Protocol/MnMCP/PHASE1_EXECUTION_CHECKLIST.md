# MnMCP 3 Phase 1 执行检查清单

**版本**: 2026-05-23-15  
**阶段**: Phase 1 - 基础重构与协议准备  
**状态**: 准备执行

---

## 🎯 Phase 1 核心目标

1. ✅ 修复所有P0技术债务
2. ✅ 整合新发现的WPKG协议规范
3. ✅ 建立加密基础模块（AES-128-GCM、ECDH、HKDF）
4. ✅ 准备Phase 2的协议开发基础

---

## 📋 执行步骤（按顺序执行）

### 阶段 1.1: 环境确认 (15分钟)

#### 1.1.1 验证Python版本
```bash
# 在MN2MC目录下执行
cd C:\Users\Sails\Documents\Workspace\NormalWorkplace\Coding\MnMCP-Protocol\MN2MC
python --version
# 预期输出: Python 3.11.x 或更高
```

**检查点**: ☐ Python版本 >= 3.11

#### 1.1.2 安装依赖
```bash
pip install -r requirements.txt
# 新增加密依赖
pip install cryptography msgpack
```

**检查点**: ☐ 依赖安装成功

#### 1.1.3 创建日志目录
```bash
mkdir logs
mkdir tests\fixtures
```

**检查点**: ☐ logs目录已创建

---

### 阶段 1.2: 安全配置模板更新 (30分钟)

#### 1.2.1 更新 config.template.yaml

在现有基础上添加：

```yaml
mini:
  # 原有配置...
  
  central_server:
    auth_url: "https://wskacchm.mini1.cn:14130"
    room_url: "http://openroom.mini1.cn:8080"
    sign_key: ""              # 【新增】MD5签名密钥
    auth_key: ""              # 【新增】房间认证密钥
  
  crypto:
    xxtea_key: ""             # XXTEA密钥（JSON加密）
    ecdh_private: ""          # 【新增】ECDH私钥（可选）
    ecdh_public_server: ""    # 【新增】服务器ECDH公钥
    session_key: ""           # 【新增】会话密钥（运行时生成）

# 新增加密配置
crypto:
  algorithm: "AES-128-GCM"   # 【新增】加密算法
  kdf: "HKDF-SHA256"           # 【新增】密钥派生
  handshake: "ECDH"            # 【新增】握手协议
```

**检查点**: ☐ config.template.yaml已更新

#### 1.2.2 复制配置文件
```bash
copy config.template.yaml config.yaml
```

**警告**: 不要将config.yaml提交到Git!

**检查点**: ☐ config.yaml已创建

---

### 阶段 1.3: 技术债务修复 (4小时)

#### 1.3.1 修复硬编码密钥 (TD-001, P0) - 1小时

**修改文件**: `mn2mc/mini/auth.py`

**步骤**:
1. 打开`mn2mc/mini/auth.py`
2. 找到第43行硬编码密钥
3. 替换为：

```python
# 修改前（不安全）
msgsign = hashlib.md5(
    f"msg={msg}&key=2ddb7619717147439c83ab022e9d4d38".encode()
).hexdigest()

# 修改后（安全）
import os
from mn2mc.config import config

sign_key = config.mini.get('central_server', {}).get('sign_key', '')
if not sign_key:
    sign_key = os.environ.get('MN_MCP_SIGN_KEY', '')
    
if not sign_key:
    raise ValueError(
        "签名密钥未配置\n"
        "请执行以下操作之一：\n"
        "1. 在config.yaml中设置: mini.central_server.sign_key\n"
        "2. 设置环境变量: MN_MCP_SIGN_KEY"
    )

msgsign = hashlib.md5(
    f"msg={msg}&key={sign_key}".encode()
).hexdigest()
```

**修改文件**: `mn2mc/mini/room.py`

**步骤**:
1. 找到第12行硬编码AUTH_KEY
2. 替换为：

```python
# 修改前（不安全）
AUTH_KEY = "f5711eb1640712de051e5aedc35329c3"

# 修改后（安全）
def get_auth_key():
    """从配置或环境变量获取认证密钥."""
    auth_key = config.mini.get('central_server', {}).get('auth_key', '')
    if not auth_key:
        auth_key = os.environ.get('MN_MCP_AUTH_KEY', '')
    return auth_key

AUTH_KEY = get_auth_key()
```

**检查点**: ☐ 硬编码密钥已移除
**测试**: 运行`python -c "from mn2mc.mini import auth"`，应提示密钥未配置

---

#### 1.3.2 修复硬编码URL (TD-002, P0) - 30分钟

**修改文件**: `mn2mc/mini/auth.py`

```python
# 修改前
LOGIN_URL = "https://wskacchm.mini1.cn:14130/man_machine/login_v3?msg=%s&sign=%s"

# 修改后
def get_login_url():
    base = config.mini.get('central_server', {}).get('auth_url', 
            'https://wskacchm.mini1.cn:14130')
    return f"{base}/man_machine/login_v3?msg=%s&sign=%s"
```

**修改文件**: `mn2mc/mini/room.py`

```python
# 修改前（注意前导空格!）
CONFIG_URL = " http://openroom.mini1.cn:8080/server/room?"

# 修改后
def get_config_url():
    base = config.mini.get('central_server', {}).get('room_url',
            'http://openroom.mini1.cn:8080')
    return f"{base}/server/room?"
```

**检查点**: ☐ 硬编码URL已移除

---

#### 1.3.3 添加错误处理 (TD-003, P0) - 1.5小时

**修改文件**: `mn2mc/mini/auth.py` 的login函数

添加try-catch：

```python
async def login():
    """执行登录，带完整错误处理."""
    global uin, name, full_sign, s2, jwt, s2t, api_id
    
    try:
        logger.info(f"Logging in {config.mini['auth']['uin']}...")
        
        # 1. 准备登录参数
        try:
            server_time = int(time.time())
            msg = encode({
                # ... 原有参数
            })
        except Exception as e:
            logger.error(f"Failed to encode login message: {e}")
            raise MiniAuthenticationError(f"Message encoding failed: {e}")
        
        # 2. 计算签名
        try:
            msgsign = hashlib.md5(
                f"msg={msg}&key={get_sign_key()}".encode()
            ).hexdigest()
        except ValueError as e:
            logger.error(f"Missing sign key: {e}")
            raise MiniAuthenticationError(f"Configuration error: {e}")
        
        # 3. 发送请求
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    get_login_url() % (msg, msgsign),
                    headers=mn2mc.mini.HEADERS,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status != 200:
                        raise MiniAuthenticationError(
                            f"HTTP error: {response.status}"
                        )
                    
                    text = await response.text()
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error during login: {e}")
            raise MiniAuthenticationError(f"Network error: {e}")
        
        # 4. 解析响应
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            logger.debug(f"Raw response: {text[:200]}")
            raise MiniAuthenticationError(f"Invalid server response")
        
        # 5. 处理结果
        if data.get("code") != 0:
            error_msg = data.get("msg", "Unknown error")
            logger.error(f"Login failed: {error_msg}")
            raise MiniAuthenticationError(f"Server error: {error_msg}")
        
        # ... 原有成功逻辑
        
    except MiniAuthenticationError:
        raise
    except Exception as e:
        logger.exception("Unexpected error during login")
        raise MiniAuthenticationError(f"Unexpected error: {e}")
```

**检查点**: ☐ auth.login已添加错误处理

---

#### 1.3.4 重构全局变量 (TD-004, P1) - 1小时

**创建新文件**: `mn2mc/auth/manager.py`

```python
"""认证管理器 - 替代全局变量."""
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import time
import hashlib
import json
import aiohttp
from loguru import logger

from mn2mc.config import config
from mn2mc.crypto.xxtea import encrypt as xxtea_encode
from mn2mc.utils.exceptions import MiniAuthenticationError


@dataclass
class AuthSession:
    """认证会话数据."""
    uin: int = 0
    api_id: int = 110
    jwt: str = ""
    full_sign: str = ""
    s2: str = ""
    s2t: str = ""
    name: str = "Unknown"
    token: str = field(default="")
    expires_at: float = field(default=0.0)
    
    @property
    def is_valid(self) -> bool:
        """检查会话是否有效."""
        return bool(self.jwt) and time.time() < self.expires_at


class AuthManager:
    """认证管理器 - 替代全局变量."""
    
    def __init__(self):
        self._session: Optional[AuthSession] = None
        self._config: Dict[str, Any] = config.mini.get('auth', {})
        self._central_config: Dict[str, Any] = config.mini.get('central_server', {})
    
    @property
    def session(self) -> AuthSession:
        """获取当前会话，如不存在则创建空会话."""
        if self._session is None:
            self._session = AuthSession()
        return self._session
    
    @property
    def is_authenticated(self) -> bool:
        """检查是否已认证."""
        return self.session.is_valid
    
    def _get_sign_key(self) -> str:
        """获取签名密钥."""
        key = self._central_config.get('sign_key', '')
        if not key:
            import os
            key = os.environ.get('MN_MCP_SIGN_KEY', '')
        if not key:
            raise ValueError("签名密钥未配置")
        return key
    
    def _get_login_url(self) -> str:
        """获取登录URL."""
        base = self._central_config.get('auth_url', 
                'https://wskacchm.mini1.cn:14130')
        return f"{base}/man_machine/login_v3?msg=%s&sign=%s"
    
    def _encode_login_params(self, server_time: int) -> str:
        """编码登录参数."""
        import mn2mc.mini
        
        msg_data = {
            "source": "client",
            "juhe_auth": "",
            "passwd_auth": json.dumps({
                "passwd": self._config.get('passwd', '')
            }),
            "DeviceID": self._config.get('device_id', ''),
            "is_url": True,
            "geetest": "blending",
            "target": "login",
            "apiid": self._config.get('api_id', 110),
            "juhe_strong_auth": "",
            "svrTime": server_time,
            "login_type": "passwd",
            "version": mn2mc.mini.cltversion,
            "time": server_time,
            "uin": self._config.get('uin', 0),
        }
        
        return xxtea_encode(msg_data)
    
    async def login(self) -> bool:
        """执行登录."""
        try:
            server_time = int(time.time())
            msg = self._encode_login_params(server_time)
            
            msgsign = hashlib.md5(
                f"msg={msg}&key={self._get_sign_key()}".encode()
            ).hexdigest()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self._get_login_url() % (msg, msgsign),
                    headers=...,  # 从mn2mc.mini.HEADERS获取
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status != 200:
                        raise MiniAuthenticationError(
                            f"HTTP error: {response.status}"
                        )
                    
                    text = await response.text()
                    data = json.loads(text)
                    
                    if data.get("code") != 0:
                        raise MiniAuthenticationError(
                            data.get("msg", "Login failed")
                        )
                    
                    # 更新会话
                    self._session = AuthSession(
                        uin=int(self._config.get('uin', 0)),
                        api_id=self._config.get('api_id', 110),
                        jwt=data['data'].get('jwt', ''),
                        full_sign=data['data'].get('full_sign', ''),
                        s2=data['data'].get('s2', ''),
                        s2t=data['data'].get('s2t', ''),
                        name=data['data'].get('name', 'Unknown'),
                        token=data['data'].get('token', ''),
                        expires_at=time.time() + 3600  # 假设1小时过期
                    )
                    
                    logger.info(f"Login success: {self.session.name}")
                    return True
                    
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    async def refresh(self) -> bool:
        """刷新会话."""
        if not self.session.is_valid:
            return await self.login()
        return True


# 全局实例（取代全局变量）
auth_manager = AuthManager()
```

**检查点**: ☐ AuthManager类已创建

---

### 阶段 1.4: 新加密模块创建 (4小时)

#### 1.4.1 创建 AES-128-GCM 模块 - 1小时

**创建文件**: `mn2mc/crypto/aes_gcm.py`

```python
"""AES-128-GCM for WPKG protocol.

Based on udp_package_report.md:
- Algorithm: AES-128-GCM (NOT CBC!)
- Key size: 16 bytes
- Nonce size: 12 bytes
- Tag size: 16 bytes
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Tuple, Optional


def aes_gcm_encrypt(
    key: bytes, 
    nonce: bytes, 
    plaintext: bytes, 
    aad: Optional[bytes] = None
) -> Tuple[bytes, bytes]:
    """
    Encrypt with AES-128-GCM.
    
    Args:
        key: 16 bytes encryption key
        nonce: 12 bytes nonce (IV)
        plaintext: data to encrypt
        aad: optional additional authenticated data
    
    Returns:
        Tuple of (ciphertext, tag)
    """
    if len(key) != 16:
        raise ValueError(f"Key must be 16 bytes, got {len(key)}")
    if len(nonce) != 12:
        raise ValueError(f"Nonce must be 12 bytes, got {len(nonce)}")
    
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, aad)
    
    # Split ciphertext and tag (tag is last 16 bytes)
    ciphertext = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]
    
    return ciphertext, tag


def aes_gcm_decrypt(
    key: bytes, 
    nonce: bytes, 
    ciphertext: bytes, 
    tag: bytes,
    aad: Optional[bytes] = None
) -> bytes:
    """
    Decrypt with AES-128-GCM.
    
    Args:
        key: 16 bytes encryption key
        nonce: 12 bytes nonce (IV)
        ciphertext: encrypted data
        tag: 16 bytes authentication tag
        aad: optional additional authenticated data
    
    Returns:
        Decrypted plaintext
    
    Raises:
        InvalidTag: if authentication fails
    """
    if len(key) != 16:
        raise ValueError(f"Key must be 16 bytes, got {len(key)}")
    if len(nonce) != 12:
        raise ValueError(f"Nonce must be 12 bytes, got {len(nonce)}")
    if len(tag) != 16:
        raise ValueError(f"Tag must be 16 bytes, got {len(tag)}")
    
    aesgcm = AESGCM(key)
    ciphertext_with_tag = ciphertext + tag
    
    return aesgcm.decrypt(nonce, ciphertext_with_tag, aad)


def generate_nonce() -> bytes:
    """Generate a random 12-byte nonce."""
    import secrets
    return secrets.token_bytes(12)


# Convenience functions for WPKG
def encrypt_wpkg_payload(
    session_key: bytes,
    plaintext: bytes,
    header: bytes  # AAD
) -> Tuple[bytes, bytes, bytes]:
    """
    Encrypt WPKG payload.
    
    Args:
        session_key: derived from ECDH+HKDF
        plaintext: payload to encrypt
        header: WPKG header for AAD
    
    Returns:
        Tuple of (nonce, ciphertext, tag)
    """
    nonce = generate_nonce()
    ciphertext, tag = aes_gcm_encrypt(session_key, nonce, plaintext, header)
    return nonce, ciphertext, tag


def decrypt_wpkg_payload(
    session_key: bytes,
    nonce: bytes,
    ciphertext: bytes,
    tag: bytes,
    header: bytes
) -> bytes:
    """Decrypt WPKG payload."""
    return aes_gcm_decrypt(session_key, nonce, ciphertext, tag, header)
```

**测试**: 
```bash
python -c "from mn2mc.crypto.aes_gcm import aes_gcm_encrypt; print('AES-GCM OK')"
```

**检查点**: ☐ AES-128-GCM模块已创建

---

#### 1.4.2 创建 HKDF 模块 - 1小时

**创建文件**: `mn2mc/crypto/hkdf.py`

```python
"""HKDF-SHA256 for key derivation.

Based on udp_package_report.md:
- Extract: HKDF_Extract(salt=0, IKM=shared_secret) -> PRK
- Expand: HKDF_Expand(..., length=48) -> session_material
- Split: aes_key[0:16], nonce_base[16:28]
"""

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from typing import Tuple


def derive_session_material(shared_secret: bytes, length: int = 48) -> bytes:
    """
    Derive session material from ECDH shared secret.
    
    Args:
        shared_secret: 32 bytes from ECDH
        length: output length (default 48 for WPKG)
    
    Returns:
        Session material bytes
    """
    if len(shared_secret) != 32:
        raise ValueError(f"Shared secret must be 32 bytes, got {len(shared_secret)}")
    
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=None,  # salt=0 / None in original
        info=b''    # no info
    )
    
    return hkdf.derive(shared_secret)


def split_session_material(material: bytes) -> Tuple[bytes, bytes, bytes]:
    """
    Split session material into components.
    
    Args:
        material: 48 bytes from HKDF
    
    Returns:
        Tuple of (aes_key, nonce_base, reserved)
    """
    if len(material) != 48:
        raise ValueError(f"Material must be 48 bytes, got {len(material)}")
    
    aes_key = material[0:16]       # 16 bytes for AES-128
    nonce_base = material[16:28]   # 12 bytes for nonce base
    reserved = material[28:48]     # 20 bytes reserved/fill
    
    return aes_key, nonce_base, reserved


def derive_wpkg_keys(shared_secret: bytes) -> Tuple[bytes, bytes]:
    """
    Derive WPKG encryption keys from ECDH shared secret.
    
    Convenience function for WPKG protocol.
    
    Args:
        shared_secret: 32 bytes from ECDH handshake
    
    Returns:
        Tuple of (aes_key, nonce_base)
    """
    material = derive_session_material(shared_secret)
    aes_key, nonce_base, _ = split_session_material(material)
    return aes_key, nonce_base
```

**测试**:
```bash
python -c "from mn2mc.crypto.hkdf import derive_wpkg_keys; print('HKDF OK')"
```

**检查点**: ☐ HKDF模块已创建

---

#### 1.4.3 创建 ECDH 模块 - 1小时

**创建文件**: `mn2mc/crypto/ecdh.py`

```python
"""ECDH key exchange for WPKG protocol.

Based on udp_package_report.md:
- Client generates ephemeral EC key pair
- Server holds static ECDH public key (mmtls_g_ecdh_key_0/1)
- Compute shared_secret (32 bytes)
"""

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from typing import Tuple, Optional
import secrets


def generate_keypair() -> Tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
    """
    Generate ephemeral ECDH key pair.
    
    Returns:
        Tuple of (private_key, public_key)
    """
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key


def compute_shared_secret(
    private_key: ec.EllipticCurvePrivateKey,
    peer_public_key: ec.EllipticCurvePublicKey
) -> bytes:
    """
    Compute ECDH shared secret.
    
    Args:
        private_key: our private key
        peer_public_key: peer's public key
    
    Returns:
        32 bytes shared secret
    """
    shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
    return shared_key


def public_key_to_bytes(
    public_key: ec.EllipticCurvePublicKey,
    format: str = "uncompressed"
) -> bytes:
    """
    Serialize public key to bytes.
    
    Args:
        public_key: public key to serialize
        format: "uncompressed" (default), "compressed", or "raw"
    
    Returns:
        Serialized public key bytes
    """
    if format == "uncompressed":
        encoding = serialization.Encoding.X962
        format_spec = serialization.PublicFormat.UncompressedPoint
    elif format == "compressed":
        encoding = serialization.Encoding.X962
        format_spec = serialization.PublicFormat.CompressedPoint
    elif format == "raw":
        encoding = serialization.Encoding.X962
        format_spec = serialization.PublicFormat.UncompressedPoint
    else:
        raise ValueError(f"Unknown format: {format}")
    
    return public_key.public_bytes(encoding, format_spec)


def public_key_from_bytes(data: bytes) -> ec.EllipticCurvePublicKey:
    """
    Deserialize public key from bytes.
    
    Args:
        data: serialized public key
    
    Returns:
        Public key object
    """
    return ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(),
        data
    )


class ECDHSession:
    """ECDH session management."""
    
    def __init__(self):
        self._private_key: Optional[ec.EllipticCurvePrivateKey] = None
        self._public_key: Optional[ec.EllipticCurvePublicKey] = None
        self._shared_secret: Optional[bytes] = None
    
    def generate_ephemeral_keys(self) -> bytes:
        """
        Generate ephemeral key pair.
        
        Returns:
            Serialized public key bytes to send to peer
        """
        self._private_key, self._public_key = generate_keypair()
        return public_key_to_bytes(self._public_key)
    
    def compute_shared(self, peer_public_bytes: bytes) -> bytes:
        """
        Compute shared secret with peer.
        
        Args:
            peer_public_bytes: peer's serialized public key
        
        Returns:
            32 bytes shared secret
        """
        if self._private_key is None:
            raise RuntimeError("Must generate keys first")
        
        peer_public = public_key_from_bytes(peer_public_bytes)
        self._shared_secret = compute_shared_secret(
            self._private_key, peer_public
        )
        return self._shared_secret
    
    @property
    def shared_secret(self) -> bytes:
        """Get shared secret."""
        if self._shared_secret is None:
            raise RuntimeError("Shared secret not computed yet")
        return self._shared_secret
```

**检查点**: ☐ ECDH模块已创建

---

#### 1.4.4 创建 WPKG 协议模块 - 1小时

**创建文件**: `mn2mc/protocol/wpkg.py`

```python
"""WPKG (WeChat Package) protocol handler.

Based on udp_package_report.md:
- Magic: 'KG' = 0x4B47
- Header: 16 bytes
- EncryptAlgo: 0=HybridECDH, 1=AesGcm
- CompressAlgo: 0=none, 1/4=zlib, 2=lz4
"""

import struct
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import IntEnum

from mn2mc.crypto.aes_gcm import aes_gcm_encrypt, aes_gcm_decrypt


class EncryptAlgo(IntEnum):
    HYBRID_ECDH = 0
    AES_GCM = 1


class CompressAlgo(IntEnum):
    NONE = 0
    ZLIB = 1
    LZ4 = 2
    ZLIB_4 = 4  # zlib variant


@dataclass
class WPKGHeader:
    """WPKG packet header."""
    magic: int = 0x4B47  # 'KG'
    cmd_id: int = 0
    seq_no: int = 0
    body_len: int = 0
    encrypt_algo: EncryptAlgo = EncryptAlgo.AES_GCM
    compress_algo: CompressAlgo = CompressAlgo.NONE
    compress_ver: int = 0
    flags: int = 0
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'WPKGHeader':
        """Parse header from 16 bytes."""
        if len(data) < 16:
            raise ValueError(f"Header too short: {len(data)} bytes")
        
        return cls(
            magic=struct.unpack('>H', data[0:2])[0],
            cmd_id=struct.unpack('>H', data[2:4])[0],
            seq_no=struct.unpack('>I', data[4:8])[0],
            body_len=struct.unpack('>I', data[8:12])[0],
            encrypt_algo=EncryptAlgo(data[12]),
            compress_algo=CompressAlgo(data[13]),
            compress_ver=data[14],
            flags=data[15]
        )
    
    def to_bytes(self) -> bytes:
        """Serialize header to 16 bytes."""
        return struct.pack('>HHIIBBBBB',
            self.magic,
            self.cmd_id,
            self.seq_no,
            self.body_len,
            self.encrypt_algo,
            self.compress_algo,
            self.compress_ver,
            self.flags,
            0  # padding/reserved
        )
    
    def is_valid(self) -> bool:
        """Check if header magic is valid."""
        return self.magic == 0x4B47


@dataclass
class WPKGPacket:
    """WPKG packet structure."""
    header: WPKGHeader
    nonce: Optional[bytes] = None  # 12 bytes for AES-GCM
    ciphertext: bytes = b''
    tag: bytes = b''  # 16 bytes for AES-GCM
    
    @property
    def full_body(self) -> bytes:
        """Get full encrypted body (ciphertext + tag)."""
        return self.ciphertext + self.tag
    
    def decrypt(self, session_key: bytes, aad: bytes = None) -> bytes:
        """
        Decrypt packet payload.
        
        Args:
            session_key: 16 bytes AES key
            aad: optional additional authenticated data
        
        Returns:
            Decrypted plaintext
        """
        if self.nonce is None:
            raise ValueError("Nonce required for decryption")
        
        if aad is None:
            aad = self.header.to_bytes()
        
        return aes_gcm_decrypt(
            session_key,
            self.nonce,
            self.ciphertext,
            self.tag,
            aad
        )
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'WPKGPacket':
        """
        Parse WPKG packet from bytes.
        
        Args:
            data: raw packet bytes
        
        Returns:
            Parsed packet
        """
        if len(data) < 16:
            raise ValueError(f"Packet too short: {len(data)} bytes")
        
        header = WPKGHeader.from_bytes(data[:16])
        
        if not header.is_valid():
            raise ValueError(f"Invalid magic: {hex(header.magic)}")
        
        # Parse based on encryption algorithm
        if header.encrypt_algo == EncryptAlgo.AES_GCM:
            # Nonce at offset 16-28
            nonce = data[16:28]
            # Ciphertext from 28 to -16 (excluding tag)
            ciphertext = data[28:-16] if header.body_len > 0 else b''
            # Tag is last 16 bytes
            tag = data[-16:] if len(data) >= 44 else b''
        else:
            # HybridECDH - different layout
            # TODO: implement HybridECDH parsing
            nonce = data[16:28]
            ciphertext = data[28:-16]
            tag = data[-16:]
        
        return cls(
            header=header,
            nonce=nonce,
            ciphertext=ciphertext,
            tag=tag
        )


class WPKGCodec:
    """WPKG encoder/decoder."""
    
    @staticmethod
    def encode(
        cmd_id: int,
        seq_no: int,
        plaintext: bytes,
        session_key: bytes,
        compress: bool = False
    ) -> bytes:
        """
        Encode plaintext to WPKG packet.
        
        Args:
            cmd_id: command ID
            seq_no: sequence number
            plaintext: data to encrypt
            session_key: 16 bytes AES key
            compress: whether to compress
        
        Returns:
            Encoded packet bytes
        """
        from mn2mc.crypto.aes_gcm import generate_nonce, encrypt_wpkg_payload
        
        # Create header (without body_len for now)
        header = WPKGHeader(
            cmd_id=cmd_id,
            seq_no=seq_no,
            encrypt_algo=EncryptAlgo.AES_GCM,
            compress_algo=CompressAlgo.NONE  # TODO: implement compression
        )
        
        # Encrypt payload
        nonce, ciphertext, tag = encrypt_wpkg_payload(
            session_key,
            plaintext,
            header.to_bytes()
        )
        
        # Update header with body length
        header.body_len = len(ciphertext) + len(tag)
        
        # Combine all parts
        packet = header.to_bytes() + nonce + ciphertext + tag
        return packet
    
    @staticmethod
    def decode(data: bytes, session_key: bytes) -> Tuple[WPKGHeader, bytes]:
        """
        Decode WPKG packet to plaintext.
        
        Args:
            data: packet bytes
            session_key: 16 bytes AES key
        
        Returns:
            Tuple of (header, plaintext)
        """
        packet = WPKGPacket.from_bytes(data)
        plaintext = packet.decrypt(session_key)
        return packet.header, plaintext
```

**检查点**: ☐ WPKG协议模块已创建

---

### 阶段 1.5: 类型注解补充 (剩余时间)

使用 `mypy` 检查并补充类型注解：

```bash
# 安装mypy
pip install mypy

# 检查现有代码
mypy mn2mc/ --ignore-missing-imports

# 修复报告的类型错误
```

**检查点**: ☐ 类型注解已补充

---

## ✅ Phase 1 完成验收

### 代码验收清单

- [ ] 所有P0技术债务已修复
- [ ] `config.template.yaml` 已更新（含加密配置）
- [ ] `mn2mc/crypto/aes_gcm.py` 已创建并测试
- [ ] `mn2mc/crypto/hkdf.py` 已创建并测试
- [ ] `mn2mc/crypto/ecdh.py` 已创建并测试
- [ ] `mn2mc/protocol/wpkg.py` 已创建并测试
- [ ] `mn2mc/auth/manager.py` 已创建（替代全局变量）
- [ ] 类型注解已补充

### 测试验收

```bash
# 运行模块导入测试
python -c "from mn2mc.crypto.aes_gcm import aes_gcm_encrypt; print('✓ AES-GCM OK')"
python -c "from mn2mc.crypto.hkdf import derive_wpkg_keys; print('✓ HKDF OK')"
python -c "from mn2mc.crypto.ecdh import generate_keypair; print('✓ ECDH OK')"
python -c "from mn2mc.protocol.wpkg import WPKGHeader; print('✓ WPKG OK')"
python -c "from mn2mc.auth.manager import AuthManager; print('✓ AuthManager OK')"

# 运行加密测试
python -c "
from mn2mc.crypto.aes_gcm import aes_gcm_encrypt, aes_gcm_decrypt
key = b'0123456789abcdef'
nonce = b'0123456789ab'
pt = b'Hello WPKG!'
ct, tag = aes_gcm_encrypt(key, nonce, pt)
dt = aes_gcm_decrypt(key, nonce, ct, tag)
assert dt == pt
print('✓ AES-GCM encryption/decryption OK')
"
```

### 提交验收

```bash
# 提交所有更改
git add -A
git commit -m "2026-05-24-18: Phase 1完成 - 修复技术债务，实现WPKG加密基础"

# 创建版本tag
git tag 2026-05-24-18

# 提交到远程（如果需要）
# git push origin main --tags
```

---

## 📊 完成统计

| 项目 | 目标 | 实际 | 状态 |
|------|------|------|------|
| P0债务修复 | 3项 | 待填写 | ☐ |
| P1债务修复 | 2项 | 待填写 | ☐ |
| 新模块创建 | 5个 | 待填写 | ☐ |
| 类型覆盖率 | 80%+ | 待测试 | ☐ |
| 测试通过率 | 100% | 待测试 | ☐ |

---

**Phase 1 完成后，进入 Phase 2: UDP协议栈实现**

**参考文档**:
- `DISCOVERED_RESOURCES_INDEX.md` - 资源索引
- `PHASE1_DETAILED_PLAN.md` - 详细计划
- `udp_package_report.md` - WPKG协议规范
- `旧版登录说明.md` - 登录流程
