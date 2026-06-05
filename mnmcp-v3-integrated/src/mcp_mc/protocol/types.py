"""
MnMCP v3 - Minecraft 协议数据类型
实现 MC 1.19.2 协议的数据类型编解码
"""

import struct
import io
from typing import Union, Optional, List
from dataclasses import dataclass


class MCTypeError(Exception):
    """数据类型错误"""
    pass


# ==================== 基础类型 ====================

class VarInt:
    """变长整数 (32位有符号)"""
    
    MAX_BYTES = 5
    
    @staticmethod
    def encode(value: int) -> bytes:
        """编码 VarInt"""
        if value < -(2**31) or value >= 2**31:
            raise MCTypeError(f"VarInt out of range: {value}")
        
        result = []
        while True:
            byte = value & 0x7F
            value >>= 7
            if value != 0:
                byte |= 0x80
            result.append(byte)
            if value == 0:
                break
        return bytes(result)
    
    @staticmethod
    def decode(data: bytes) -> tuple:
        """
        解码 VarInt
        
        Returns:
            (value, bytes_read)
        """
        result = 0
        for i in range(len(data)):
            byte = data[i]
            result |= (byte & 0x7F) << (7 * i)
            if not (byte & 0x80):
                return result, i + 1
            if i >= VarInt.MAX_BYTES - 1:
                raise MCTypeError("VarInt too long")
        raise MCTypeError("Incomplete VarInt")
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> int:
        """从流中解码 VarInt"""
        result = 0
        for i in range(VarInt.MAX_BYTES):
            byte = stream.read(1)
            if not byte:
                raise MCTypeError("Unexpected EOF in VarInt")
            byte = byte[0]
            result |= (byte & 0x7F) << (7 * i)
            if not (byte & 0x80):
                return result
        raise MCTypeError("VarInt too long")


class VarLong:
    """变长整数 (64位有符号)"""
    
    MAX_BYTES = 10
    
    @staticmethod
    def encode(value: int) -> bytes:
        """编码 VarLong"""
        if value < -(2**63) or value >= 2**63:
            raise MCTypeError(f"VarLong out of range: {value}")
        
        result = []
        while True:
            byte = value & 0x7F
            value >>= 7
            if value != 0:
                byte |= 0x80
            result.append(byte)
            if value == 0:
                break
        return bytes(result)
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> int:
        """从流中解码 VarLong"""
        result = 0
        for i in range(VarLong.MAX_BYTES):
            byte = stream.read(1)
            if not byte:
                raise MCTypeError("Unexpected EOF in VarLong")
            byte = byte[0]
            result |= (byte & 0x7F) << (7 * i)
            if not (byte & 0x80):
                # 符号扩展
                if result & (1 << 63):
                    result -= (1 << 64)
                return result
        raise MCTypeError("VarLong too long")


# ==================== 字符串 ====================

class MCString:
    """Minecraft 字符串 (UTF-8, 最大32767字节)"""
    
    MAX_LENGTH = 32767
    
    @staticmethod
    def encode(value: str) -> bytes:
        """编码字符串"""
        encoded = value.encode('utf-8')
        length = len(encoded)
        if length > MCString.MAX_LENGTH:
            raise MCTypeError(f"String too long: {length}")
        return VarInt.encode(length) + encoded
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> str:
        """从流中解码字符串"""
        length = VarInt.decode_stream(stream)
        if length > MCString.MAX_LENGTH:
            raise MCTypeError(f"String length too large: {length}")
        data = stream.read(length)
        if len(data) != length:
            raise MCTypeError(f"Incomplete string: expected {length}, got {len(data)}")
        return data.decode('utf-8')


# ==================== 原始类型 ====================

class MCBoolean:
    """布尔值 (1字节)"""
    
    @staticmethod
    def encode(value: bool) -> bytes:
        return bytes([1 if value else 0])
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> bool:
        byte = stream.read(1)
        if not byte:
            raise MCTypeError("Unexpected EOF in Boolean")
        return byte[0] != 0


class MCByte:
    """有符号字节 (-128 ~ 127)"""
    
    @staticmethod
    def encode(value: int) -> bytes:
        if value < -128 or value > 127:
            raise MCTypeError(f"Byte out of range: {value}")
        return struct.pack('b', value)
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> int:
        data = stream.read(1)
        if len(data) != 1:
            raise MCTypeError("Unexpected EOF in Byte")
        return struct.unpack('b', data)[0]


class MCUnsignedByte:
    """无符号字节 (0 ~ 255)"""
    
    @staticmethod
    def encode(value: int) -> bytes:
        if value < 0 or value > 255:
            raise MCTypeError(f"UnsignedByte out of range: {value}")
        return bytes([value])
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> int:
        data = stream.read(1)
        if not data:
            raise MCTypeError("Unexpected EOF in UnsignedByte")
        return data[0]


class MCShort:
    """有符号短整 (-32768 ~ 32767)"""
    
    @staticmethod
    def encode(value: int) -> bytes:
        if value < -32768 or value > 32767:
            raise MCTypeError(f"Short out of range: {value}")
        return struct.pack('>h', value)
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> int:
        data = stream.read(2)
        if len(data) != 2:
            raise MCTypeError("Unexpected EOF in Short")
        return struct.unpack('>h', data)[0]


class MCUnsignedShort:
    """无符号短整 (0 ~ 65535)"""
    
    @staticmethod
    def encode(value: int) -> bytes:
        if value < 0 or value > 65535:
            raise MCTypeError(f"UnsignedShort out of range: {value}")
        return struct.pack('>H', value)
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> int:
        data = stream.read(2)
        if len(data) != 2:
            raise MCTypeError("Unexpected EOF in UnsignedShort")
        return struct.unpack('>H', data)[0]


class MCInt:
    """有符号整数 (32位)"""
    
    @staticmethod
    def encode(value: int) -> bytes:
        return struct.pack('>i', value)
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> int:
        data = stream.read(4)
        if len(data) != 4:
            raise MCTypeError("Unexpected EOF in Int")
        return struct.unpack('>i', data)[0]


class MCLong:
    """有符号长整 (64位)"""
    
    @staticmethod
    def encode(value: int) -> bytes:
        return struct.pack('>q', value)
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> int:
        data = stream.read(8)
        if len(data) != 8:
            raise MCTypeError("Unexpected EOF in Long")
        return struct.unpack('>q', data)[0]


class MCFloat:
    """单精度浮点 (32位)"""
    
    @staticmethod
    def encode(value: float) -> bytes:
        return struct.pack('>f', value)
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> float:
        data = stream.read(4)
        if len(data) != 4:
            raise MCTypeError("Unexpected EOF in Float")
        return struct.unpack('>f', data)[0]


class MCDouble:
    """双精度浮点 (64位)"""
    
    @staticmethod
    def encode(value: float) -> bytes:
        return struct.pack('>d', value)
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> float:
        data = stream.read(8)
        if len(data) != 8:
            raise MCTypeError("Unexpected EOF in Double")
        return struct.unpack('>d', data)[0]


# ==================== 复杂类型 ====================

class MCPosition:
    """坐标位置 (X, Y, Z 编码为长整)"""
    
    @staticmethod
    def encode(x: int, y: int, z: int) -> bytes:
        """
        编码坐标
        
        MC协议格式:
        ((x & 0x3FFFFFF) << 38) | ((z & 0x3FFFFFF) << 12) | (y & 0xFFF)
        """
        value = ((x & 0x3FFFFFF) << 38) | ((z & 0x3FFFFFF) << 12) | (y & 0xFFF)
        return struct.pack('>q', value)
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> tuple:
        """
        解码坐标
        
        Returns:
            (x, y, z)
        """
        data = stream.read(8)
        if len(data) != 8:
            raise MCTypeError("Unexpected EOF in Position")
        value = struct.unpack('>q', data)[0]
        
        x = value >> 38
        y = value & 0xFFF
        z = (value >> 12) & 0x3FFFFFF
        
        # 符号扩展
        if x >= 2**25:
            x -= 2**26
        if y >= 2**11:
            y -= 2**12
        if z >= 2**25:
            z -= 2**26
        
        return x, y, z


class MCUUID:
    """UUID (16字节)"""
    
    @staticmethod
    def encode(value: str) -> bytes:
        """编码 UUID 字符串"""
        # 移除连字符
        hex_str = value.replace('-', '')
        if len(hex_str) != 32:
            raise MCTypeError(f"Invalid UUID: {value}")
        return bytes.fromhex(hex_str)
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> str:
        """解码 UUID 为字符串"""
        data = stream.read(16)
        if len(data) != 16:
            raise MCTypeError("Unexpected EOF in UUID")
        hex_str = data.hex()
        # 添加连字符
        return f"{hex_str[:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:]}"


class MCByteArray:
    """字节数组 (VarInt 长度前缀)"""
    
    @staticmethod
    def encode(data: bytes) -> bytes:
        return VarInt.encode(len(data)) + data
    
    @staticmethod
    def decode_stream(stream: io.BytesIO) -> bytes:
        length = VarInt.decode_stream(stream)
        return stream.read(length)


# ==================== 类型别名 ====================

MCTypes = {
    'varint': VarInt,
    'varlong': VarLong,
    'string': MCString,
    'bool': MCBoolean,
    'byte': MCByte,
    'ubyte': MCUnsignedByte,
    'short': MCShort,
    'ushort': MCUnsignedShort,
    'int': MCInt,
    'long': MCLong,
    'float': MCFloat,
    'double': MCDouble,
    'position': MCPosition,
    'uuid': MCUUID,
    'bytearray': MCByteArray,
}


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("MnMCP v3 - MC 协议类型测试")
    print("=" * 60)
    
    # 测试 VarInt
    print("\nVarInt 测试:")
    test_values = [0, 1, 127, 128, 255, 256, 16383, 16384, 65535, 65536, 2147483647]
    for value in test_values:
        encoded = VarInt.encode(value)
        decoded, _ = VarInt.decode(encoded)
        assert decoded == value, f"VarInt failed: {value} -> {decoded}"
    print(f"  ✓ {len(test_values)} 个值测试通过")
    
    # 测试字符串
    print("\nString 测试:")
    test_strings = ["Hello", "Minecraft 中文测试", ""]
    for s in test_strings:
        encoded = MCString.encode(s)
        stream = io.BytesIO(encoded)
        decoded = MCString.decode_stream(stream)
        assert decoded == s, f"String failed: {s}"
    print(f"  ✓ {len(test_strings)} 个字符串测试通过")
    
    # 测试坐标
    print("\nPosition 测试:")
    x, y, z = 100, 64, -200
    encoded = MCPosition.encode(x, y, z)
    stream = io.BytesIO(encoded)
    dx, dy, dz = MCPosition.decode_stream(stream)
    assert (dx, dy, dz) == (x, y, z), f"Position failed: {(x,y,z)} != {(dx,dy,dz)}"
    print(f"  ✓ 坐标 ({x}, {y}, {z}) 编码解码正确")
    
    print("\n✓ 所有类型测试通过!")
