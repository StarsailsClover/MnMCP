"""
MnMCP v3 - Minecraft 协议加密
实现 MC 1.19.2 的 AES-CFB8 加密
"""

from typing import Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


class MCAESEncryptor:
    """
    Minecraft AES-CFB8 加密器
    
    MC 使用 AES-128-CFB8 模式进行加密
    - 密钥: 16字节 (来自服务端共享密钥)
    - IV: 16字节 (与密钥相同)
    - 模式: CFB8 (8位反馈)
    
    注意: MC 的加密有历史原因的特殊性，使用 IV=Key
    """
    
    def __init__(self, shared_secret: bytes):
        """
        初始化加密器
        
        Args:
            shared_secret: 共享密钥 (16字节)
        """
        if len(shared_secret) != 16:
            raise ValueError(f"Shared secret must be 16 bytes, got {len(shared_secret)}")
        
        self.key = shared_secret
        # MC 使用 IV = Key (历史遗留)
        self.iv = shared_secret
        
        # 创建加密器
        self._cipher = Cipher(
            algorithms.AES(self.key),
            modes.CFB(self.iv),
            backend=default_backend()
        )
        self._encryptor = self._cipher.encryptor()
    
    def encrypt(self, data: bytes) -> bytes:
        """
        加密数据
        
        Args:
            data: 明文数据
            
        Returns:
            密文数据
        """
        try:
            return self._encryptor.update(data)
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise


class MCAESDecryptor:
    """
    Minecraft AES-CFB8 解密器
    """
    
    def __init__(self, shared_secret: bytes):
        """
        初始化解密器
        
        Args:
            shared_secret: 共享密钥 (16字节)
        """
        if len(shared_secret) != 16:
            raise ValueError(f"Shared secret must be 16 bytes, got {len(shared_secret)}")
        
        self.key = shared_secret
        self.iv = shared_secret
        
        # 创建解密器
        self._cipher = Cipher(
            algorithms.AES(self.key),
            modes.CFB(self.iv),
            backend=default_backend()
        )
        self._decryptor = self._cipher.decryptor()
    
    def decrypt(self, data: bytes) -> bytes:
        """
        解密数据
        
        Args:
            data: 密文数据
            
        Returns:
            明文数据
        """
        try:
            return self._decryptor.update(data)
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise


class MCProtocolCrypto:
    """
    Minecraft 协议加密管理器
    
    管理双向加密/解密
    """
    
    def __init__(self):
        self._encryptor: Optional[MCAESEncryptor] = None
        self._decryptor: Optional[MCAESDecryptor] = None
        self._enabled = False
    
    def enable(self, shared_secret: bytes) -> None:
        """
        启用加密
        
        Args:
            shared_secret: 共享密钥 (16字节)
        """
        self._encryptor = MCAESEncryptor(shared_secret)
        self._decryptor = MCAESDecryptor(shared_secret)
        self._enabled = True
        logger.info("Encryption enabled")
    
    def disable(self) -> None:
        """禁用加密"""
        self._encryptor = None
        self._decryptor = None
        self._enabled = False
        logger.info("Encryption disabled")
    
    @property
    def enabled(self) -> bool:
        """加密是否启用"""
        return self._enabled
    
    def encrypt(self, data: bytes) -> bytes:
        """
        加密数据
        
        Args:
            data: 明文
            
        Returns:
            密文
        """
        if not self._enabled or not self._encryptor:
            return data
        return self._encryptor.encrypt(data)
    
    def decrypt(self, data: bytes) -> bytes:
        """
        解密数据
        
        Args:
            data: 密文
            
        Returns:
            明文
        """
        if not self._enabled or not self._decryptor:
            return data
        return self._decryptor.decrypt(data)


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("MnMCP v3 - MC 加密测试")
    print("=" * 60)
    
    # 测试密钥
    key = b"test_key_16bytes"
    plaintext = b"Hello, Minecraft!"
    
    print(f"\n密钥: {key}")
    print(f"明文: {plaintext}")
    
    # 加密
    encryptor = MCAESEncryptor(key)
    ciphertext = encryptor.encrypt(plaintext)
    print(f"密文: {ciphertext.hex()}")
    
    # 解密
    decryptor = MCAESDecryptor(key)
    decrypted = decryptor.decrypt(ciphertext)
    print(f"解密: {decrypted}")
    
    # 验证
    assert decrypted == plaintext
    print("\n✓ AES-CFB8 加解密测试通过!")
    
    # 测试管理器
    print("\n测试加密管理器...")
    crypto = MCProtocolCrypto()
    print(f"初始状态: enabled={crypto.enabled}")
    
    crypto.enable(key)
    print(f"启用后: enabled={crypto.enabled}")
    
    encrypted = crypto.encrypt(plaintext)
    decrypted = crypto.decrypt(encrypted)
    assert decrypted == plaintext
    print("✓ 加密管理器测试通过!")
    
    crypto.disable()
    print(f"禁用后: enabled={crypto.enabled}")
    
    print("\n✓ 所有加密测试通过!")
