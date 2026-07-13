"""
MnMCP v3 - 数据包转换器
实现 MC <-> MNW 数据包双向转换

功能:
- MC 数据包 -> MNW 数据包
- MNW 数据包 -> MC 数据包
- 位置数据转换
- 方块数据转换
- 聊天消息转换

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import struct
import zlib
import json
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import IntEnum
import logging

from ..mcp_protocol.msgcode_registry import MessageRegistry, PacketDirection, get_message_name
from ..mcp_mapping.blocks_full import mc_to_mnw, mnw_to_mc

logger = logging.getLogger(__name__)


class PacketType(IntEnum):
    """数据包类型"""
    UNKNOWN = 0
    POSITION = 1
    CHAT = 2
    BLOCK_PLACE = 3
    BLOCK_BREAK = 4
    ENTITY_SPAWN = 5
    ENTITY_MOVE = 6
    HEARTBEAT = 7
    LOGIN = 8
    OTHER = 99


@dataclass
class ConvertedPacket:
    """转换后的数据包"""
    msg_code: int
    data: bytes
    packet_type: PacketType = PacketType.UNKNOWN
    direction: PacketDirection = PacketDirection.UNKNOWN


class MCPPacketConverter:
    """
    数据包转换器
    
    负责 MC 和 MNW 数据包之间的双向转换
    """
    
    def __init__(self):
        self.registry = MessageRegistry()
        
        self._mc_packet_map = {
            0x03: self._convert_mc_chat,
            0x12: self._convert_mc_player_position,
            0x13: self._convert_mc_player_position_rotation,
            0x14: self._convert_mc_player_rotation,
            0x15: self._convert_mc_player_movement,
            0x36: self._convert_mc_teleport_confirm,
        }
        
        self._mnw_packet_map = {
            11: self._convert_mnw_heartbeat,
            12: self._convert_mnw_heartbeat_response,
            9001: self._convert_mnw_chat,
            2001: self._convert_mnw_player_move,
            902: self._convert_mnw_login_response,
        }
    
    def mc_to_mnw(self, mc_packet_id: int, mc_data: bytes) -> Optional[ConvertedPacket]:
        """
        MC 数据包 -> MNW 数据包
        
        Args:
            mc_packet_id: MC 数据包 ID
            mc_data: MC 数据包数据
            
        Returns:
            转换后的 MNW 数据包，失败返回 None
        """
        converter = self._mc_packet_map.get(mc_packet_id)
        
        if converter:
            try:
                return converter(mc_data)
            except Exception as e:
                logger.error(f"Failed to convert MC packet {mc_packet_id}: {e}")
                return None
        
        logger.debug(f"No converter for MC packet {mc_packet_id}")
        return None
    
    def mnw_to_mc(self, mnw_msg_code: int, mnw_data: bytes) -> Optional[ConvertedPacket]:
        """
        MNW 数据包 -> MC 数据包
        
        Args:
            mnw_msg_code: MNW 消息码
            mnw_data: MNW 数据包数据
            
        Returns:
            转换后的 MC 数据包，失败返回 None
        """
        converter = self._mnw_packet_map.get(mnw_msg_code)
        
        if converter:
            try:
                return converter(mnw_data)
            except Exception as e:
                logger.error(f"Failed to convert MNW packet {mnw_msg_code}: {e}")
                return None
        
        logger.debug(f"No converter for MNW packet {mnw_msg_code}")
        return None
    
    def _convert_mc_chat(self, mc_data: bytes) -> Optional[ConvertedPacket]:
        """转换 MC 聊天消息"""
        try:
            reader = PacketReader(mc_data)
            
            message = reader.read_string()
            timestamp = reader.read_long()
            
            chat_data = {
                'msg_type': 9001,
                'sender': 'MC_Player',
                'message': message,
                'timestamp': int(timestamp),
            }
            
            return ConvertedPacket(
                msg_code=9001,
                data=self._encode_mnw_chat(chat_data),
                packet_type=PacketType.CHAT,
                direction=PacketDirection.CLIENT_TO_SERVER
            )
            
        except Exception as e:
            logger.error(f"MC chat conversion error: {e}")
            return None
    
    def _convert_mnw_chat(self, mnw_data: bytes) -> Optional[ConvertedPacket]:
        """转换 MNW 聊天消息"""
        try:
            chat_data = self._decode_mnw_chat(mnw_data)
            
            if chat_data:
                message = chat_data.get('message', '')
                sender = chat_data.get('sender', 'MNW_Player')
                
                full_message = f"[MNW] {sender}: {message}"
                
                return ConvertedPacket(
                    msg_code=0x03,
                    data=self._encode_mc_chat(full_message),
                    packet_type=PacketType.CHAT,
                    direction=PacketDirection.SERVER_TO_CLIENT
                )
            
            return None
            
        except Exception as e:
            logger.error(f"MNW chat conversion error: {e}")
            return None
    
    def _convert_mc_player_position(self, mc_data: bytes) -> Optional[ConvertedPacket]:
        """转换 MC 玩家位置"""
        try:
            reader = PacketReader(mc_data)
            
            x = reader.read_double()
            y = reader.read_double()
            z = reader.read_double()
            on_ground = reader.read_bool()
            
            move_data = {
                'msg_type': 2001,
                'entity_id': 0,
                'x': x,
                'y': y,
                'z': z,
                'yaw': 0,
                'pitch': 0,
                'on_ground': on_ground,
            }
            
            return ConvertedPacket(
                msg_code=2001,
                data=self._encode_mnw_move(move_data),
                packet_type=PacketType.POSITION,
                direction=PacketDirection.CLIENT_TO_SERVER
            )
            
        except Exception as e:
            logger.error(f"MC position conversion error: {e}")
            return None
    
    def _convert_mc_player_position_rotation(self, mc_data: bytes) -> Optional[ConvertedPacket]:
        """转换 MC 玩家位置和朝向"""
        try:
            reader = PacketReader(mc_data)
            
            x = reader.read_double()
            y = reader.read_double()
            z = reader.read_double()
            yaw = reader.read_float()
            pitch = reader.read_float()
            on_ground = reader.read_bool()
            
            mnw_yaw = self._mc_yaw_to_mnw(yaw)
            
            move_data = {
                'msg_type': 2001,
                'entity_id': 0,
                'x': x,
                'y': y,
                'z': z,
                'yaw': mnw_yaw,
                'pitch': pitch,
                'on_ground': on_ground,
            }
            
            return ConvertedPacket(
                msg_code=2001,
                data=self._encode_mnw_move(move_data),
                packet_type=PacketType.POSITION,
                direction=PacketDirection.CLIENT_TO_SERVER
            )
            
        except Exception as e:
            logger.error(f"MC position rotation conversion error: {e}")
            return None
    
    def _convert_mc_player_rotation(self, mc_data: bytes) -> Optional[ConvertedPacket]:
        """转换 MC 玩家朝向"""
        try:
            reader = PacketReader(mc_data)
            
            yaw = reader.read_float()
            pitch = reader.read_float()
            on_ground = reader.read_bool()
            
            mnw_yaw = self._mc_yaw_to_mnw(yaw)
            
            move_data = {
                'msg_type': 2001,
                'entity_id': 0,
                'x': 0,
                'y': 0,
                'z': 0,
                'yaw': mnw_yaw,
                'pitch': pitch,
                'on_ground': on_ground,
            }
            
            return ConvertedPacket(
                msg_code=2001,
                data=self._encode_mnw_move(move_data),
                packet_type=PacketType.POSITION,
                direction=PacketDirection.CLIENT_TO_SERVER
            )
            
        except Exception as e:
            logger.error(f"MC rotation conversion error: {e}")
            return None
    
    def _convert_mc_player_movement(self, mc_data: bytes) -> Optional[ConvertedPacket]:
        """转换 MC 玩家移动"""
        try:
            reader = PacketReader(mc_data)
            
            on_ground = reader.read_bool()
            
            move_data = {
                'msg_type': 2001,
                'entity_id': 0,
                'on_ground': on_ground,
            }
            
            return ConvertedPacket(
                msg_code=2001,
                data=self._encode_mnw_move(move_data),
                packet_type=PacketType.OTHER,
                direction=PacketDirection.CLIENT_TO_SERVER
            )
            
        except Exception as e:
            logger.error(f"MC movement conversion error: {e}")
            return None
    
    def _convert_mnw_player_move(self, mnw_data: bytes) -> Optional[ConvertedPacket]:
        """转换 MNW 玩家移动"""
        try:
            move_data = self._decode_mnw_move(mnw_data)
            
            if move_data:
                x = move_data.get('x', 0.0)
                y = move_data.get('y', 0.0)
                z = move_data.get('z', 0.0)
                yaw = move_data.get('yaw', 0.0)
                pitch = move_data.get('pitch', 0.0)
                
                mc_yaw = self._mnw_yaw_to_mc(yaw)
                
                writer = PacketWriter()
                writer.write_double(x)
                writer.write_double(y)
                writer.write_double(z)
                writer.write_float(mc_yaw)
                writer.write_float(pitch)
                writer.write_bool(True)
                
                return ConvertedPacket(
                    msg_code=0x13,
                    data=writer.get_data(),
                    packet_type=PacketType.POSITION,
                    direction=PacketDirection.SERVER_TO_CLIENT
                )
            
            return None
            
        except Exception as e:
            logger.error(f"MNW move conversion error: {e}")
            return None
    
    def _convert_mc_teleport_confirm(self, mc_data: bytes) -> Optional[ConvertedPacket]:
        """转换 MC 传送确认"""
        try:
            reader = PacketReader(mc_data)
            teleport_id = reader.read_varint()
            
            confirm_data = {
                'msg_type': 9002,
                'teleport_id': teleport_id,
            }
            
            return ConvertedPacket(
                msg_code=9002,
                data=self._encode_mnw_confirm(confirm_data),
                packet_type=PacketType.OTHER,
                direction=PacketDirection.CLIENT_TO_SERVER
            )
            
        except Exception as e:
            logger.error(f"MC teleport confirm conversion error: {e}")
            return None
    
    def _convert_mnw_heartbeat(self, mnw_data: bytes) -> Optional[ConvertedPacket]:
        """转换 MNW 心跳"""
        try:
            heartbeat_data = self._decode_mnw_heartbeat(mnw_data)
            
            if heartbeat_data:
                writer = PacketWriter()
                writer.write_varint(heartbeat_data.get('timestamp', 0))
                
                return ConvertedPacket(
                    msg_code=0x1F,
                    data=writer.get_data(),
                    packet_type=PacketType.HEARTBEAT,
                    direction=PacketDirection.CLIENT_TO_SERVER
                )
            
            return None
            
        except Exception as e:
            logger.error(f"MNW heartbeat conversion error: {e}")
            return None
    
    def _convert_mnw_heartbeat_response(self, mnw_data: bytes) -> Optional[ConvertedPacket]:
        """转换 MNW 心跳响应"""
        try:
            writer = PacketWriter()
            writer.write_long(int(mnw_data[:8]) if len(mnw_data) >= 8 else 0)
            
            return ConvertedPacket(
                msg_code=0x1F,
                data=writer.get_data(),
                packet_type=PacketType.HEARTBEAT,
                direction=PacketDirection.SERVER_TO_CLIENT
            )
            
        except Exception as e:
            logger.error(f"MNW heartbeat response conversion error: {e}")
            return None
    
    def _convert_mnw_login_response(self, mnw_data: bytes) -> Optional[ConvertedPacket]:
        """转换 MNW 登录响应"""
        try:
            login_data = self._decode_mnw_login(mnw_data)
            
            if login_data and login_data.get('success', False):
                writer = PacketWriter()
                writer.write_string(login_data.get('uuid', ''))
                writer.write_string(login_data.get('username', 'MnMCP_Player'))
                
                return ConvertedPacket(
                    msg_code=0x02,
                    data=writer.get_data(),
                    packet_type=PacketType.LOGIN,
                    direction=PacketDirection.SERVER_TO_CLIENT
                )
            
            return None
            
        except Exception as e:
            logger.error(f"MNW login response conversion error: {e}")
            return None
    
    def _mc_yaw_to_mnw(self, mc_yaw: float) -> float:
        """MC Yaw -> MNW Yaw"""
        return (mc_yaw + 180) % 360
    
    def _mnw_yaw_to_mc(self, mnw_yaw: float) -> float:
        """MNW Yaw -> MC Yaw"""
        mc_yaw = (mnw_yaw - 180) % 360
        if mc_yaw > 180:
            mc_yaw -= 360
        return mc_yaw
    
    def _encode_mnw_chat(self, data: Dict[str, Any]) -> bytes:
        """编码 MNW 聊天消息"""
        try:
            import blackboxprotobuf
            return blackboxprotobuf.encode_message(data)
        except:
            return json.dumps(data).encode('utf-8')
    
    def _decode_mnw_chat(self, data: bytes) -> Optional[Dict[str, Any]]:
        """解码 MNW 聊天消息"""
        try:
            import blackboxprotobuf
            decoded, _ = blackboxprotobuf.decode_message(data)
            return decoded
        except:
            try:
                return json.loads(data.decode('utf-8', errors='replace'))
            except:
                return None
    
    def _encode_mnw_move(self, data: Dict[str, Any]) -> bytes:
        """编码 MNW 移动消息"""
        try:
            import blackboxprotobuf
            return blackboxprotobuf.encode_message(data)
        except:
            return json.dumps(data).encode('utf-8')
    
    def _decode_mnw_move(self, data: bytes) -> Optional[Dict[str, Any]]:
        """解码 MNW 移动消息"""
        try:
            import blackboxprotobuf
            decoded, _ = blackboxprotobuf.decode_message(data)
            return decoded
        except:
            try:
                return json.loads(data.decode('utf-8', errors='replace'))
            except:
                return None
    
    def _encode_mnw_confirm(self, data: Dict[str, Any]) -> bytes:
        """编码 MNW 确认消息"""
        try:
            import blackboxprotobuf
            return blackboxprotobuf.encode_message(data)
        except:
            return json.dumps(data).encode('utf-8')
    
    def _decode_mnw_heartbeat(self, data: bytes) -> Optional[Dict[str, Any]]:
        """解码 MNW 心跳消息"""
        try:
            import blackboxprotobuf
            decoded, _ = blackboxprotobuf.decode_message(data)
            return decoded
        except:
            return {'timestamp': int.from_bytes(data, 'little')}
    
    def _decode_mnw_login(self, data: bytes) -> Optional[Dict[str, Any]]:
        """解码 MNW 登录消息"""
        try:
            import blackboxprotobuf
            decoded, _ = blackboxprotobuf.decode_message(data)
            return decoded
        except:
            try:
                return json.loads(data.decode('utf-8', errors='replace'))
            except:
                return {'success': False}
    
    def _encode_mc_chat(self, message: str) -> bytes:
        """编码 MC 聊天消息"""
        writer = PacketWriter()
        writer.write_string(message)
        writer.write_long(0)
        return writer.get_data()


class PacketReader:
    """数据包读取器"""
    
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
    
    def read_byte(self) -> int:
        result = self.data[self.pos]
        self.pos += 1
        return result
    
    def read_bool(self) -> bool:
        return self.read_byte() != 0
    
    def read_short(self) -> int:
        result = struct.unpack_from('<h', self.data, self.pos)[0]
        self.pos += 2
        return result
    
    def read_ushort(self) -> int:
        result = struct.unpack_from('<H', self.data, self.pos)[0]
        self.pos += 2
        return result
    
    def read_int(self) -> int:
        result = struct.unpack_from('<i', self.data, self.pos)[0]
        self.pos += 4
        return result
    
    def read_uint(self) -> int:
        result = struct.unpack_from('<I', self.data, self.pos)[0]
        self.pos += 4
        return result
    
    def read_long(self) -> int:
        result = struct.unpack_from('<q', self.data, self.pos)[0]
        self.pos += 8
        return result
    
    def read_ulong(self) -> int:
        result = struct.unpack_from('<Q', self.data, self.pos)[0]
        self.pos += 8
        return result
    
    def read_float(self) -> float:
        result = struct.unpack_from('<f', self.data, self.pos)[0]
        self.pos += 4
        return result
    
    def read_double(self) -> float:
        result = struct.unpack_from('<d', self.data, self.pos)[0]
        self.pos += 8
        return result
    
    def read_varint(self) -> int:
        result = 0
        shift = 0
        while True:
            byte = self.read_byte()
            result |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7
        return result
    
    def read_string(self) -> str:
        length = self.read_varint()
        result = self.data[self.pos:self.pos + length].decode('utf-8')
        self.pos += length
        return result
    
    def read_bytes(self, length: int) -> bytes:
        result = self.data[self.pos:self.pos + length]
        self.pos += length
        return result
    
    def read_remaining(self) -> bytes:
        result = self.data[self.pos:]
        self.pos = len(self.data)
        return result


class PacketWriter:
    """数据包写入器"""
    
    def __init__(self):
        self.buffer = bytearray()
    
    def write_byte(self, value: int) -> None:
        self.buffer.append(value & 0xFF)
    
    def write_bool(self, value: bool) -> None:
        self.write_byte(1 if value else 0)
    
    def write_short(self, value: int) -> None:
        self.buffer.extend(struct.pack('<h', value))
    
    def write_ushort(self, value: int) -> None:
        self.buffer.extend(struct.pack('<H', value))
    
    def write_int(self, value: int) -> None:
        self.buffer.extend(struct.pack('<i', value))
    
    def write_uint(self, value: int) -> None:
        self.buffer.extend(struct.pack('<I', value))
    
    def write_long(self, value: int) -> None:
        self.buffer.extend(struct.pack('<q', value))
    
    def write_ulong(self, value: int) -> None:
        self.buffer.extend(struct.pack('<Q', value))
    
    def write_float(self, value: float) -> None:
        self.buffer.extend(struct.pack('<f', value))
    
    def write_double(self, value: float) -> None:
        self.buffer.extend(struct.pack('<d', value))
    
    def write_varint(self, value: int) -> None:
        if value < 0:
            value += (1 << 64)
        while value >= 0x80:
            self.write_byte((value & 0x7F) | 0x80)
            value >>= 7
        self.write_byte(value)
    
    def write_string(self, value: str) -> None:
        encoded = value.encode('utf-8')
        self.write_varint(len(encoded))
        self.buffer.extend(encoded)
    
    def write_bytes(self, value: bytes) -> None:
        self.buffer.extend(value)
    
    def get_data(self) -> bytes:
        return bytes(self.buffer)


# 便捷函数
def convert_mc_to_mnw(packet_id: int, data: bytes) -> Optional[ConvertedPacket]:
    """
    快速转换 MC 到 MNW
    
    Args:
        packet_id: MC 数据包 ID
        data: MC 数据包数据
        
    Returns:
        转换后的数据包
    """
    converter = MCPPacketConverter()
    return converter.mc_to_mnw(packet_id, data)


def convert_mnw_to_mc(msg_code: int, data: bytes) -> Optional[ConvertedPacket]:
    """
    快速转换 MNW 到 MC
    
    Args:
        msg_code: MNW 消息码
        data: MNW 数据包数据
        
    Returns:
        转换后的数据包
    """
    converter = MCPPacketConverter()
    return converter.mnw_to_mc(msg_code, data)


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("MnMCP v3 - 数据包转换器测试")
    print("=" * 60)
    
    converter = MCPPacketConverter()
    
    print("\n1. MC Chat -> MNW Chat")
    mc_chat_data = PacketWriter()
    mc_chat_data.write_string("Hello from MC!")
    mc_chat_data.write_long(0)
    result = converter.mc_to_mnw(0x03, mc_chat_data.get_data())
    if result:
        print(f"  ✓ 转换成功: msg_code={result.msg_code}, type={result.packet_type.name}")
    else:
        print("  ✗ 转换失败")
    
    print("\n2. MC Position -> MNW Move")
    mc_pos_data = PacketWriter()
    mc_pos_data.write_double(100.5)
    mc_pos_data.write_double(64.0)
    mc_pos_data.write_double(200.5)
    mc_pos_data.write_bool(True)
    result = converter.mc_to_mnw(0x12, mc_pos_data.get_data())
    if result:
        print(f"  ✓ 转换成功: msg_code={result.msg_code}, type={result.packet_type.name}")
    else:
        print("  ✗ 转换失败")
    
    print("\n3. MC Position+Rotation -> MNW Move")
    mc_pos_rot_data = PacketWriter()
    mc_pos_rot_data.write_double(100.5)
    mc_pos_rot_data.write_double(64.0)
    mc_pos_rot_data.write_double(200.5)
    mc_pos_rot_data.write_float(90.0)
    mc_pos_rot_data.write_float(0.0)
    mc_pos_rot_data.write_bool(True)
    result = converter.mc_to_mnw(0x13, mc_pos_rot_data.get_data())
    if result:
        print(f"  ✓ 转换成功: msg_code={result.msg_code}, type={result.packet_type.name}")
    else:
        print("  ✗ 转换失败")
    
    print("\n4. MNW Chat -> MC Chat")
    mnw_chat_data = json.dumps({
        'msg_type': 9001,
        'sender': 'TestPlayer',
        'message': 'Hello from MNW!'
    }).encode('utf-8')
    result = converter.mnw_to_mc(9001, mnw_chat_data)
    if result:
        print(f"  ✓ 转换成功: msg_code={result.msg_code}, type={result.packet_type.name}")
    else:
        print("  ✗ 转换失败")
    
    print("\n5. MNW Move -> MC Position")
    mnw_move_data = json.dumps({
        'msg_type': 2001,
        'entity_id': 1000,
        'x': 100.5,
        'y': 64.0,
        'z': 200.5,
        'yaw': 90.0,
        'pitch': 0.0
    }).encode('utf-8')
    result = converter.mnw_to_mc(2001, mnw_move_data)
    if result:
        print(f"  ✓ 转换成功: msg_code={result.msg_code}, type={result.packet_type.name}")
    else:
        print("  ✗ 转换失败")
    
    print("\n" + "=" * 60)
    print("✓ 转换器测试完成")
    print("=" * 60)
