"""
MnMCP v3 - 协议编解码器
移植自 MN2MC，融合 MnMCP v3 高质量架构

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import struct
import zlib
from typing import Dict, Optional, Tuple, Any, Union, List
from dataclasses import dataclass
from enum import IntEnum
import logging

from .msgcode_registry import MessageRegistry, PacketDirection

logger = logging.getLogger(__name__)


class PacketFlag(IntEnum):
    """数据包标志"""
    NONE = 0
    COMPRESSED = 1  # Zlib 压缩
    ENCRYPTED = 2   # XXTEA 加密


@dataclass
class MCPPacket:
    """
    MnMCP 数据包
    
    Attributes:
        msg_code: 消息码
        data: 原始数据
        direction: 消息方向
        flags: 标志位
        session_id: 会话ID
    """
    msg_code: int
    data: bytes
    direction: PacketDirection = PacketDirection.UNKNOWN
    flags: int = 0
    session_id: int = 0
    
    @property
    def is_compressed(self) -> bool:
        """是否压缩"""
        return bool(self.flags & PacketFlag.COMPRESSED)
    
    @property
    def is_encrypted(self) -> bool:
        """是否加密"""
        return bool(self.flags & PacketFlag.ENCRYPTED)
    
    def get_message_name(self) -> Optional[str]:
        """获取消息名称"""
        registry = MessageRegistry()
        return registry.get_name(self.msg_code)


class MCPProtocolCodec:
    """
    MiniWorld 协议编解码器
    
    移植自 MN2MC，改进:
    - 完整的类型注解
    - 完善的错误处理
    - 支持多种编码格式
    
    数据包格式 (RakNet):
    Client->Server: 0x89 + UIN(4, BE) + Reserved(8) + MsgCode(2, LE) + Length(2, LE) + Data
    Server->Client: 0x89 + MsgCode(2, LE) + Length(2, LE) + Data
    
    对于 CH 消息 (Client->Host):
    - 通常需要 XXTEA 加密 + Zlib 压缩
    
    对于 HC 消息 (Host->Client):
    - 通常只需要 Zlib 解压
    """
    
    MAGIC = 0x89
    SERVER_HEADER_SIZE = 5
    CLIENT_HEADER_SIZE = 17
    
    def __init__(self, xxtea_key: Optional[bytes] = None):
        """
        初始化编解码器
        
        Args:
            xxtea_key: XXTEA 加密密钥
        """
        self.xxtea_key = xxtea_key
        self.registry = MessageRegistry()
        self._compression_threshold = 256  # 超过此大小压缩
    
    def encode(self, packet: MCPPacket) -> bytes:
        """
        编码数据包
        
        Args:
            packet: 数据包
            
        Returns:
            编码后的字节
        """
        try:
            data = packet.data
            if len(data) > 0xFFFF:
                raise ProtocolEncodeError(f"Payload too large: {len(data)} bytes")

            if packet.direction == PacketDirection.CLIENT_TO_SERVER:
                uin = packet.session_id & 0xFFFFFFFF
                return bytes([self.MAGIC]) + struct.pack('>I', uin) + (b'\x00' * 8) + struct.pack('<HH', packet.msg_code, len(data)) + data

            return bytes([self.MAGIC]) + struct.pack('<HH', packet.msg_code, len(data)) + data
            
        except Exception as e:
            logger.error(f"Failed to encode packet {packet.msg_code}: {e}")
            raise ProtocolEncodeError(f"Encode error: {e}")
    
    def decode(self, raw_data: bytes, direction: PacketDirection) -> MCPPacket:
        """
        解码数据包
        
        Args:
            raw_data: 原始数据
            direction: 消息方向
            
        Returns:
            解码后的数据包
        """
        try:
            min_size = self.CLIENT_HEADER_SIZE if direction == PacketDirection.CLIENT_TO_SERVER else self.SERVER_HEADER_SIZE
            if len(raw_data) < min_size:
                raise ProtocolDecodeError(f"Data too short: {len(raw_data)} bytes")

            if raw_data[0] != self.MAGIC:
                return self._decode_legacy(raw_data, direction)

            if direction == PacketDirection.CLIENT_TO_SERVER:
                session_id = struct.unpack('>I', raw_data[1:5])[0]
                msg_code, length = struct.unpack('<HH', raw_data[13:17])
                payload_start = self.CLIENT_HEADER_SIZE
            else:
                session_id = 0
                msg_code, length = struct.unpack('<HH', raw_data[1:5])
                payload_start = self.SERVER_HEADER_SIZE

            payload_end = payload_start + length
            if len(raw_data) < payload_end:
                raise ProtocolDecodeError(f"Incomplete payload: expected {length}, got {len(raw_data) - payload_start}")

            data = raw_data[payload_start:payload_end]

            return MCPPacket(
                msg_code=msg_code,
                data=data,
                direction=direction,
                flags=0,
                session_id=session_id
            )
            
        except zlib.error as e:
            logger.error(f"Zlib decompression error: {e}")
            raise ProtocolDecodeError(f"Decompression error: {e}")
        except struct.error as e:
            logger.error(f"Struct unpack error: {e}")
            raise ProtocolDecodeError(f"Packet format error: {e}")
        except Exception as e:
            logger.error(f"Failed to decode packet: {e}")
            raise ProtocolDecodeError(f"Decode error: {e}")

    def _decode_legacy(self, raw_data: bytes, direction: PacketDirection) -> MCPPacket:
        if len(raw_data) < 7:
            raise ProtocolDecodeError(f"Legacy data too short: {len(raw_data)} bytes")
        header = raw_data[:7]
        msg_code, flags, session_id = struct.unpack('<HBI', header)
        data = raw_data[7:]
        if flags & PacketFlag.ENCRYPTED:
            if self.xxtea_key:
                data = self._xxtea_decrypt(data)
            else:
                logger.warning("Received encrypted packet but no key provided")
        if flags & PacketFlag.COMPRESSED:
            data = zlib.decompress(data)
        return MCPPacket(
            msg_code=msg_code,
            data=data,
            direction=direction,
            flags=flags,
            session_id=session_id
        )
    
    def _xxtea_encrypt(self, data: bytes) -> bytes:
        """XXTEA 加密"""
        if not self.xxtea_key:
            return data
        
        try:
            from ..mcp_crypto.xxtea_mcp import MCPXXTEA
            xxtea = MCPXXTEA(self.xxtea_key)
            return xxtea.encrypt_zip(data)
        except Exception as e:
            logger.error(f"XXTEA encryption error: {e}")
            return data
    
    def _xxtea_decrypt(self, data: bytes) -> bytes:
        """XXTEA 解密"""
        if not self.xxtea_key:
            return data
        
        try:
            from ..mcp_crypto.xxtea_mcp import MCPXXTEA
            xxtea = MCPXXTEA(self.xxtea_key)
            return xxtea.decrypt_unzip(data)
        except Exception as e:
            logger.error(f"XXTEA decryption error: {e}")
            return data
    
    def create_packet(
        self,
        msg_code: int,
        data: bytes,
        direction: PacketDirection,
        session_id: int = 0
    ) -> MCPPacket:
        """
        创建数据包
        
        Args:
            msg_code: 消息码
            data: 数据
            direction: 方向
            session_id: 会话ID
            
        Returns:
            数据包
        """
        return MCPPacket(
            msg_code=msg_code,
            data=data,
            direction=direction,
            session_id=session_id
        )
    
    def parse_protobuf(self, packet: MCPPacket) -> Optional[Dict[str, Any]]:
        """
        解析 Protobuf 数据
        
        使用 blackboxprotobuf 动态解析
        
        Args:
            packet: 数据包
            
        Returns:
            解析后的字典，失败返回 None
        """
        try:
            import blackboxprotobuf
            
            message_type = self.registry.get_message_class(packet.msg_code)
            
            if message_type:
                # 已知消息类型
                msg = message_type()
                msg.ParseFromString(packet.data)
                return self._protobuf_to_dict(msg)
            else:
                # 未知消息，使用 blackboxprotobuf
                decoded, typedef = blackboxprotobuf.decode_message(packet.data)
                return decoded
                
        except Exception as e:
            logger.warning(f"Failed to parse protobuf for {packet.msg_code}: {e}")
            return None
    
    def _protobuf_to_dict(self, msg) -> Dict[str, Any]:
        """Protobuf 消息转字典"""
        from google.protobuf.json_format import MessageToDict
        return MessageToDict(msg, preserving_proto_field_name=True)


class ProtocolEncodeError(Exception):
    """编码错误"""
    pass


class ProtocolDecodeError(Exception):
    """解码错误"""
    pass


# 便捷函数
def encode_packet(
    msg_code: int,
    data: bytes,
    direction: PacketDirection,
    xxtea_key: Optional[bytes] = None
) -> bytes:
    """
    快速编码数据包
    
    Args:
        msg_code: 消息码
        data: 数据
        direction: 方向
        xxtea_key: 加密密钥
        
    Returns:
        编码后的字节
    """
    codec = MCPProtocolCodec(xxtea_key)
    packet = codec.create_packet(msg_code, data, direction)
    return codec.encode(packet)


def decode_packet(
    raw_data: bytes,
    direction: PacketDirection,
    xxtea_key: Optional[bytes] = None
) -> MCPPacket:
    """
    快速解码数据包
    
    Args:
        raw_data: 原始数据
        direction: 方向
        xxtea_key: 加密密钥
        
    Returns:
        解码后的数据包
    """
    codec = MCPProtocolCodec(xxtea_key)
    return codec.decode(raw_data, direction)


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("MnMCP v3 - 协议编解码器测试")
    print("=" * 60)
    
    # 测试编解码
    codec = MCPProtocolCodec(xxtea_key=b"test_key_16bytes")
    
    test_data = b"Hello, MnMCP v3! This is a test message."
    
    # 编码
    packet = codec.create_packet(
        msg_code=9001,  # PB_ChatContentCH
        data=test_data,
        direction=PacketDirection.CLIENT_TO_SERVER
    )
    encoded = codec.encode(packet)
    print(f"\n原始数据: {test_data}")
    print(f"编码后: {len(encoded)} bytes")
    
    # 解码
    decoded = codec.decode(encoded, PacketDirection.CLIENT_TO_SERVER)
    print(f"解码后: {decoded.data}")
    print(f"消息码: {decoded.msg_code} ({decoded.get_message_name()})")
    print(f"是否压缩: {decoded.is_compressed}")
    print(f"是否加密: {decoded.is_encrypted}")
    
    # 验证
    assert decoded.data == test_data
    print("\n✓ 编解码测试通过")
    
    # 统计
    stats = codec.registry.get_stats()
    print(f"\n消息注册表统计:")
    print(f"  总消息数: {stats['total_messages']}")
    print(f"  Client->Server: {stats['client_to_server']}")
    print(f"  Server->Client: {stats['server_to_client']}")
