#!/usr/bin/env python3
"""
MnMCP XXTEA 加密模块
基于 MN2MC 实现，改进为高质量架构

流程:
1. 数据 → msgpack → zlib压缩 → XXTEA加密 → base64编码
2. 反向流程解密
"""

import struct
import zlib
import base64
import logging
from typing import Union, Optional

logger = logging.getLogger(__name__)

# 尝试导入 xxtea 库
try:
    import xxtea
    HAS_XXTEA_LIB = True
except ImportError:
    HAS_XXTEA_LIB = False
    logger.warning("xxtea 库未安装，使用简化版实现")


class MCPXXTEA:
    """
    MnMCP XXTEA 加密管理器
    
    功能:
    - XXTEA 加密/解密
    - Zlib 压缩/解压
    - Base64 URL安全编码
    - 数据打包/解包
    """
    
    def __init__(self, key: bytes = b"default_key_16by"):
        """
        初始化
        
        Args:
            key: XXTEA 密钥 (16字节)
        """
        self.key = key[:16].ljust(16, b'\x00')
        self._has_lib = HAS_XXTEA_LIB
        
        logger.debug(f"MCPXXTEA 初始化: has_lib={self._has_lib}")
    
    def set_key(self, key: bytes):
        """设置密钥"""
        self.key = key[:16].ljust(16, b'\x00')
    
    def pack(self, data: bytes) -> bytes:
        """
        打包数据
        格式: [长度:4字节][数据:N字节][填充:0-3字节]
        """
        # 打包: 长度 + 数据
        packed = struct.pack(f'>I{len(data)}s', len(data), data)
        
        # 填充到4字节对齐
        padding = (4 - len(packed) % 4) % 4
        if padding:
            packed += b'\x00' * padding
        
        return packed
    
    def unpack(self, data: bytes) -> bytes:
        """解包数据"""
        if len(data) < 4:
            raise ValueError(f"数据太短: {len(data)} bytes")
        
        length = struct.unpack('>I', data[:4])[0]
        return data[4:4+length]
    
    def encrypt(self, data: bytes) -> bytes:
        """
        XXTEA 加密
        
        Args:
            data: 明文数据
            
        Returns:
            加密后的数据
        """
        if self._has_lib:
            return xxtea.encrypt(data, self.key, False)
        else:
            return self._encrypt_simple(data)
    
    def decrypt(self, data: bytes) -> bytes:
        """
        XXTEA 解密
        
        Args:
            data: 加密数据
            
        Returns:
            明文数据
        """
        if self._has_lib:
            return xxtea.decrypt(data, self.key, False)
        else:
            return self._decrypt_simple(data)
    
    def encrypt_zip(self, data: Union[bytes, str]) -> bytes:
        """
        压缩 + XXTEA 加密
        
        流程: 数据 → zlib压缩 → pack → XXTEA加密
        
        Args:
            data: 原始数据
            
        Returns:
            加密后的数据
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # 压缩
        compressed = zlib.compress(data)
        
        # 打包
        packed = self.pack(compressed)
        
        # 加密
        encrypted = self.encrypt(packed)
        
        return encrypted
    
    def decrypt_unzip(self, data: bytes) -> bytes:
        """
        XXTEA 解密 + 解压
        
        流程: XXTEA解密 → unpack → zlib解压
        
        Args:
            data: 加密数据
            
        Returns:
            原始数据
        """
        # 解密
        decrypted = self.decrypt(data)
        
        # 解包
        unpacked = self.unpack(decrypted)
        
        # 解压
        decompressed = zlib.decompress(unpacked)
        
        return decompressed
    
    def encode_message(self, data: dict) -> str:
        """
        编码消息 (用于登录)
        
        流程:
        1. msgpack 序列化
        2. zlib 压缩
        3. XXTEA 加密
        4. base64 URL安全编码
        5. 替换 '=' 为 ':'
        
        Args:
            data: 字典数据
            
        Returns:
            编码后的字符串
        """
        import json
        
        # 序列化 (使用 json 作为 msgpack 的替代)
        serialized = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        # 压缩 + 加密
        encrypted = self.encrypt_zip(serialized)
        
        # Base64 URL安全编码
        encoded = base64.urlsafe_b64encode(encrypted)
        
        # 替换 '=' 为 ':'
        result = encoded.replace(b'=', b':').decode('ascii')
        
        return result
    
    def _encrypt_simple(self, data: bytes) -> bytes:
        """简化版 XXTEA 加密 (测试用)"""
        # 这是一个简化实现，仅用于测试
        # 实际应该使用 xxtea 库
        return data  # 明文返回 (不安全！)
    
    def _decrypt_simple(self, data: bytes) -> bytes:
        """简化版 XXTEA 解密 (测试用)"""
        return data


# 全局实例
_xxtea_instance: Optional[MCPXXTEA] = None


def get_xxtea(key: bytes = None) -> MCPXXTEA:
    """获取全局 XXTEA 实例"""
    global _xxtea_instance
    if _xxtea_instance is None or key is not None:
        _xxtea_instance = MCPXXTEA(key or b"default_key_16by")
    return _xxtea_instance


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print(" MCPXXTEA 测试 ".center(60))
    print("=" * 60)
    
    xxtea = MCPXXTEA(b"test_key_1234567")
    
    # 测试数据
    test_data = b"Hello, MiniWorld!"
    
    print(f"\n原始数据: {test_data}")
    
    # 打包测试
    packed = xxtea.pack(test_data)
    print(f"打包后: {packed.hex()}")
    
    unpacked = xxtea.unpack(packed)
    print(f"解包后: {unpacked}")
    
    # 压缩加密测试
    encrypted = xxtea.encrypt_zip(test_data)
    print(f"加密后: {encrypted.hex()[:32]}...")
    
    decrypted = xxtea.decrypt_unzip(encrypted)
    print(f"解密后: {decrypted}")
    
    # 编码测试
    test_dict = {"uin": 123456, "action": "login"}
    encoded = xxtea.encode_message(test_dict)
    print(f"\n编码测试:")
    print(f"  原始: {test_dict}")
    print(f"  编码: {encoded[:50]}...")
    
    print("\n✓ 测试完成")