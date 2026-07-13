#!/usr/bin/env python3
"""
MnMCP XXTEA 加密模块
基于 MN2MC 实现，改进为高质量架构

流程:
1. 数据 → msgpack → zlib压缩 → XXTEA加密 → base64编码
2. 反向流程解密

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import struct
import zlib
import base64
import logging
from typing import Union, Optional

logger = logging.getLogger(__name__)

try:
    import xxtea as xxtea_lib
    HAS_XXTEA_LIB = True
except ImportError:
    HAS_XXTEA_LIB = False
    logger.warning("xxtea 库未安装，使用内置实现")


class MCPXXTEA:
    """
    MnMCP XXTEA 加密管理器
    
    功能:
    - XXTEA 加密/解密
    - Zlib 压缩/解压
    - Base64 URL安全编码
    - 数据打包/解包
    """
    
    DELTA = 0x9E3779B9
    ROUNDS = 32
    
    def __init__(self, key: bytes = b"default_key_16by"):
        """
        初始化
        
        Args:
            key: XXTEA 密钥 (16字节)
        """
        self.key = key[:16].ljust(16, b'\x00')
        self._key32 = self._bytes_to_uint32(self.key)
        self._has_lib = HAS_XXTEA_LIB
        
        logger.debug(f"MCPXXTEA 初始化: has_lib={self._has_lib}")
    
    def _bytes_to_uint32(self, data: bytes) -> list:
        """字节转 uint32 数组"""
        result = []
        for i in range(0, len(data), 4):
            chunk = data[i:i+4].ljust(4, b'\x00')
            result.append(struct.unpack('>I', chunk)[0])
        return result
    
    def _uint32_to_bytes(self, data: list) -> bytes:
        """uint32 数组转字节"""
        result = b''
        for val in data:
            result += struct.pack('>I', val & 0xFFFFFFFF)
        return result
    
    def set_key(self, key: bytes):
        """设置密钥"""
        self.key = key[:16].ljust(16, b'\x00')
        self._key32 = self._bytes_to_uint32(self.key)
    
    def pack(self, data: bytes) -> bytes:
        """
        打包数据
        格式: [长度:4字节][数据:N字节][填充:0-3字节]
        """
        packed = struct.pack(f'>I{len(data)}s', len(data), data)
        
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
            try:
                return xxtea_lib.encrypt(data, self.key)
            except:
                pass
        return self._encrypt_core(data)
    
    def decrypt(self, data: bytes) -> bytes:
        """
        XXTEA 解密
        
        Args:
            data: 加密数据
            
        Returns:
            明文数据
        """
        if self._has_lib:
            try:
                return xxtea_lib.decrypt(data, self.key)
            except:
                pass
        return self._decrypt_core(data)
    
    def _encrypt_core(self, data: bytes) -> bytes:
        """内置 XXTEA 加密实现"""
        if len(data) == 0:
            return data
        
        v = self._bytes_to_uint32(data)
        n = len(v)
        k = self._key32
        
        sum_val = 0
        z = v[n - 1]
        
        for _ in range(self.ROUNDS):
            sum_val = (sum_val + self.DELTA) & 0xFFFFFFFF
            e = sum_val >> 2 & 3
            
            for i in range(n - 1):
                y = v[i + 1]
                v[i] = (v[i] + ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum_val ^ y) + (k[i & 3 ^ e] ^ z))) & 0xFFFFFFFF
                z = v[i]
            
            y = v[0]
            v[n - 1] = (v[n - 1] + ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum_val ^ y) + (k[(n - 1) & 3 ^ e] ^ z))) & 0xFFFFFFFF
            z = v[n - 1]
        
        return self._uint32_to_bytes(v)
    
    def _decrypt_core(self, data: bytes) -> bytes:
        """内置 XXTEA 解密实现"""
        if len(data) == 0:
            return data
        
        v = self._bytes_to_uint32(data)
        n = len(v)
        k = self._key32
        
        sum_val = (self.DELTA * self.ROUNDS) & 0xFFFFFFFF
        y = v[0]
        
        for _ in range(self.ROUNDS):
            e = sum_val >> 2 & 3
            
            for i in range(n - 1, 0, -1):
                z = v[i - 1]
                v[i] = (v[i] - ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum_val ^ y) + (k[i & 3 ^ e] ^ z))) & 0xFFFFFFFF
                y = v[i]
            
            z = v[n - 1]
            v[0] = (v[0] - ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum_val ^ y) + (k[0 & 3 ^ e] ^ z))) & 0xFFFFFFFF
            y = v[0]
            sum_val = (sum_val - self.DELTA) & 0xFFFFFFFF
        
        return self._uint32_to_bytes(v)
    
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
        
        compressed = zlib.compress(data)
        packed = self.pack(compressed)
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
        decrypted = self.decrypt(data)
        unpacked = self.unpack(decrypted)
        decompressed = zlib.decompress(unpacked)
        
        return decompressed
    
    def encode_message(self, data: dict) -> str:
        """
        编码消息 (用于登录)
        
        流程:
        1. json 序列化
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
        
        serialized = json.dumps(data, ensure_ascii=False).encode('utf-8')
        encrypted = self.encrypt_zip(serialized)
        encoded = base64.urlsafe_b64encode(encrypted)
        result = encoded.replace(b'=', b':').decode('ascii')
        
        return result
    
    def decode_message(self, encoded: str) -> dict:
        """
        解码消息 (用于登录响应)
        
        Args:
            encoded: 编码后的字符串
            
        Returns:
            解码后的字典数据
        """
        import json
        
        encoded_bytes = encoded.replace(':', '=').encode('ascii')
        encrypted = base64.urlsafe_b64decode(encoded_bytes)
        decrypted = self.decrypt_unzip(encrypted)
        
        return json.loads(decrypted.decode('utf-8'))


_xxtea_instance: Optional[MCPXXTEA] = None


def get_xxtea(key: bytes = None) -> MCPXXTEA:
    """获取全局 XXTEA 实例"""
    global _xxtea_instance
    if _xxtea_instance is None or key is not None:
        _xxtea_instance = MCPXXTEA(key or b"default_key_16by")
    return _xxtea_instance


if __name__ == "__main__":
    print("=" * 60)
    print(" MCPXXTEA 测试 ".center(60))
    print("=" * 60)
    
    xxtea = MCPXXTEA(b"test_key_1234567")
    
    test_data = b"Hello, MiniWorld!"
    print(f"\n原始数据: {test_data}")
    
    packed = xxtea.pack(test_data)
    print(f"打包后: {packed.hex()}")
    
    unpacked = xxtea.unpack(packed)
    print(f"解包后: {unpacked}")
    
    encrypted = xxtea.encrypt_zip(test_data)
    print(f"加密后: {encrypted.hex()[:32]}...")
    
    decrypted = xxtea.decrypt_unzip(encrypted)
    print(f"解密后: {decrypted}")
    
    assert decrypted == test_data, "加密/解密失败"
    
    test_dict = {"uin": 123456, "action": "login"}
    encoded = xxtea.encode_message(test_dict)
    decoded = xxtea.decode_message(encoded)
    print(f"\n编码测试:")
    print(f"  原始: {test_dict}")
    print(f"  编码: {encoded[:50]}...")
    print(f"  解码: {decoded}")
    
    assert decoded == test_dict, "编码/解码失败"
    
    print("\n✓ 测试完成")