import struct
from dataclasses import dataclass
from typing import Union

@dataclass
class LoginPacket:
    uin: int
    token: str

@dataclass
class RoomListPacket:
    pass

@dataclass
class JoinRoomPacket:
    room_id: str

Packet = Union[LoginPacket, RoomListPacket, JoinRoomPacket]

class Packet:
    @staticmethod
    def serialize(packet: Packet) -> bytes:
        if isinstance(packet, LoginPacket):
            return struct.pack("!BQ", 0x01, packet.uin) + packet.token.encode()
        elif isinstance(packet, RoomListPacket):
            return struct.pack("!B", 0x02)
        elif isinstance(packet, JoinRoomPacket):
            return struct.pack("!B", 0x03) + packet.room_id.encode()
        return b""
    
    @staticmethod
    def deserialize(data: bytes) -> Optional[Packet]:
        if len(data) < 1:
            return None
        packet_type = data[0]
        if packet_type == 0x01:
            uin = struct.unpack("!Q", data[1:9])[0]
            token = data[9:].decode()
            return LoginPacket(uin=uin, token=token)
        elif packet_type == 0x02:
            return RoomListPacket()
        elif packet_type == 0x03:
            room_id = data[1:].decode()
            return JoinRoomPacket(room_id=room_id)
        return None
