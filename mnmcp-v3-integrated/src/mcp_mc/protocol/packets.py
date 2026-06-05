"""
MnMCP v3 - Minecraft 数据包定义
MC 1.19.2 协议数据包
"""

import io
import struct
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import IntEnum

from .types import (
    VarInt, MCString, MCBoolean, MCByte, MCUnsignedByte,
    MCShort, MCInt, MCLong, MCFloat, MCDouble, MCPosition, MCUUID
)


class PacketID(IntEnum):
    """数据包 ID (MC 1.19.2)"""
    # 握手
    HANDSHAKE = 0x00
    
    # 状态
    STATUS_REQUEST = 0x00
    STATUS_RESPONSE = 0x00
    
    # 登录 (C->S)
    LOGIN_START = 0x00
    ENCRYPTION_RESPONSE = 0x01
    LOGIN_PLUGIN_RESPONSE = 0x02
    
    # 登录 (S->C)
    LOGIN_DISCONNECT = 0x00
    ENCRYPTION_REQUEST = 0x01
    LOGIN_SUCCESS = 0x02
    SET_COMPRESSION = 0x03
    LOGIN_PLUGIN_REQUEST = 0x04
    
    # 游戏 (C->S)
    TELEPORT_CONFIRM = 0x00
    QUERY_BLOCK_NBT = 0x01
    SET_DIFFICULTY = 0x02
    CHAT_MESSAGE = 0x03
    CLIENT_STATUS = 0x04
    CLIENT_SETTINGS = 0x05
    TAB_COMPLETE = 0x06
    CLICK_WINDOW_BUTTON = 0x07
    CLICK_WINDOW = 0x08
    CLOSE_WINDOW = 0x09
    PLUGIN_MESSAGE = 0x0A
    EDIT_BOOK = 0x0B
    QUERY_ENTITY_NBT = 0x0C
    INTERACT_ENTITY = 0x0D
    GENERATE_STRUCTURE = 0x0E
    KEEP_ALIVE = 0x0F
    LOCK_DIFFICULTY = 0x10
    PLAYER_POSITION = 0x11
    PLAYER_POSITION_AND_ROTATION = 0x12
    PLAYER_ROTATION = 0x13
    PLAYER_MOVEMENT = 0x14
    VEHICLE_MOVE = 0x15
    STEER_BOAT = 0x16
    PICK_ITEM = 0x17
    CRAFT_RECIPE_REQUEST = 0x18
    PLAYER_ABILITIES = 0x19
    DIGGING = 0x1A
    ENTITY_ACTION = 0x1B
    STEER_VEHICLE = 0x1C
    PONG = 0x1D
    SET_RECIPE_BOOK_STATE = 0x1E
    SET_DISPLAYED_RECIPE = 0x1F
    NAME_ITEM = 0x20
    RESOURCE_PACK_STATUS = 0x21
    ADVANCEMENT_TAB = 0x22
    SELECT_TRADE = 0x23
    SET_BEACON_EFFECT = 0x24
    HELD_ITEM_CHANGE = 0x25
    UPDATE_COMMAND_BLOCK = 0x26
    UPDATE_COMMAND_BLOCK_MINECART = 0x27
    UPDATE_JIGSAW_BLOCK = 0x28
    UPDATE_STRUCTURE_BLOCK = 0x29
    UPDATE_SIGN = 0x2A
    ANIMATION = 0x2B
    SPECTATE = 0x2C
    PLAYER_BLOCK_PLACEMENT = 0x2D
    USE_ITEM = 0x2E
    
    # 游戏 (S->C) - 部分重要包
    SPAWN_ENTITY = 0x00
    SPAWN_EXPERIENCE_ORB = 0x01
    SPAWN_LIVING_ENTITY = 0x02
    SPAWN_PAINTING = 0x03
    SPAWN_PLAYER = 0x04
    SCULK_VIBRATION_SIGNAL = 0x05
    ENTITY_ANIMATION = 0x06
    STATISTICS = 0x07
    ACKNOWLEDGE_PLAYER_DIGGING = 0x08
    BLOCK_BREAK_ANIMATION = 0x09
    BLOCK_ENTITY_DATA = 0x0A
    BLOCK_ACTION = 0x0B
    BLOCK_CHANGE = 0x0C
    BOSS_BAR = 0x0D
    SERVER_DIFFICULTY = 0x0E
    CHAT_MESSAGE_PACKET = 0x0F  # 原名CHAT_MESSAGE，避免冲突
    CLEAR_TITLES = 0x10
    TAB_COMPLETE_REPLY = 0x11
    DECLARE_COMMANDS = 0x12
    CLOSE_WINDOW_PACKET = 0x13
    WINDOW_ITEMS = 0x14
    WINDOW_PROPERTY = 0x15
    SET_SLOT = 0x16
    SET_COOLDOWN = 0x17
    PLUGIN_MESSAGE_PACKET = 0x18
    NAMED_SOUND_EFFECT = 0x19
    DISCONNECT = 0x1A
    ENTITY_STATUS = 0x1B
    EXPLOSION = 0x1C
    UNLOAD_CHUNK = 0x1D
    CHANGE_GAME_STATE = 0x1E
    OPEN_HORSE_WINDOW = 0x1F
    INITIALIZE_WORLD_BORDER = 0x20
    KEEP_ALIVE_PACKET = 0x21
    CHUNK_DATA = 0x22
    EFFECT = 0x23
    PARTICLE = 0x24
    UPDATE_LIGHT = 0x25
    JOIN_GAME = 0x26
    MAP_DATA = 0x27
    TRADE_LIST = 0x28
    ENTITY_POSITION = 0x29
    ENTITY_POSITION_AND_ROTATION = 0x2A
    ENTITY_ROTATION = 0x2B
    VEHICLE_POSITION = 0x2C
    OPEN_WINDOW_PACKET = 0x2D
    OPEN_SIGN_EDITOR = 0x2E
    PING = 0x30
    CRAFT_RECIPE_RESPONSE = 0x31
    PLAYER_ABILITIES_PACKET = 0x32
    END_COMBAT_EVENT = 0x33
    ENTER_COMBAT_EVENT = 0x34
    DEATH_COMBAT_EVENT = 0x35
    PLAYER_INFO = 0x36
    FACE_PLAYER = 0x37
    PLAYER_POSITION_AND_LOOK = 0x38
    UNLOCK_RECIPES = 0x39
    DESTROY_ENTITIES = 0x3A
    REMOVE_ENTITY_EFFECT = 0x3B
    RESOURCE_PACK_SEND = 0x3C
    RESPAWN = 0x3D
    ENTITY_HEAD_LOOK = 0x3E
    MULTI_BLOCK_CHANGE = 0x3F
    SELECT_ADVANCEMENT_TAB = 0x40
    ACTION_BAR = 0x41
    WORLD_BORDER_CENTER = 0x42
    WORLD_BORDER_LERP_SIZE = 0x43
    WORLD_BORDER_SIZE = 0x44
    WORLD_BORDER_WARNING_DELAY = 0x45
    WORLD_BORDER_WARNING_REACH = 0x46
    CAMERA = 0x47
    HELD_ITEM_CHANGE_PACKET = 0x48
    UPDATE_VIEW_POSITION = 0x49
    UPDATE_VIEW_DISTANCE = 0x4A
    SPAWN_POSITION = 0x4B
    DISPLAY_SCOREBOARD = 0x4C
    ENTITY_METADATA = 0x4D
    ATTACH_ENTITY = 0x4E
    ENTITY_VELOCITY = 0x4F
    ENTITY_EQUIPMENT = 0x50
    SET_EXPERIENCE = 0x51
    UPDATE_HEALTH = 0x52
    SCOREBOARD_OBJECTIVE = 0x53
    SET_PASSENGERS = 0x54
    TEAMS = 0x55
    UPDATE_SCORE = 0x56
    SET_TITLE_SUBTITLE = 0x57
    TIME_UPDATE = 0x58
    SET_TITLE_TEXT = 0x59
    SET_TITLE_TIME = 0x5A
    ENTITY_SOUND_EFFECT = 0x5B
    SOUND_EFFECT = 0x5C
    STOP_SOUND = 0x5D
    SYSTEM_CHAT_MESSAGE = 0x5E
    PLAYER_CHAT_MESSAGE = 0x5F
    DAMAGE_EVENT = 0x6B


@dataclass
class MCPacket:
    """Minecraft 数据包基类"""
    packet_id: int
    data: Dict[str, Any] = field(default_factory=dict)
    
    def encode(self) -> bytes:
        """编码为字节"""
        raise NotImplementedError()
    
    @classmethod
    def decode(cls, data: bytes) -> 'MCPacket':
        """从字节解码"""
        raise NotImplementedError()


@dataclass
class HandshakePacket(MCPacket):
    """握手数据包"""
    protocol_version: int = 760  # 1.19.2
    server_address: str = "localhost"
    server_port: int = 25565
    next_state: int = 2  # 2=Login
    
    def __post_init__(self):
        self.packet_id = PacketID.HANDSHAKE
    
    def encode(self) -> bytes:
        """编码握手包"""
        result = VarInt.encode(self.packet_id)
        result += VarInt.encode(self.protocol_version)
        result += MCString.encode(self.server_address)
        result += struct.pack('>H', self.server_port)
        result += VarInt.encode(self.next_state)
        return result
    
    @classmethod
    def decode(cls, data: bytes) -> 'HandshakePacket':
        """解码握手包"""
        stream = io.BytesIO(data)
        packet_id = VarInt.decode_stream(stream)
        assert packet_id == PacketID.HANDSHAKE
        
        protocol_version = VarInt.decode_stream(stream)
        server_address = MCString.decode_stream(stream)
        server_port = struct.unpack('>H', stream.read(2))[0]
        next_state = VarInt.decode_stream(stream)
        
        return cls(
            packet_id=packet_id,
            protocol_version=protocol_version,
            server_address=server_address,
            server_port=server_port,
            next_state=next_state
        )


@dataclass  
class LoginStartPacket(MCPacket):
    """登录开始数据包"""
    username: str = ""
    
    def __post_init__(self):
        self.packet_id = PacketID.LOGIN_START
    
    def encode(self) -> bytes:
        result = VarInt.encode(self.packet_id)
        result += MCString.encode(self.username)
        return result


@dataclass
class JoinGamePacket(MCPacket):
    """加入游戏数据包 (S->C)"""
    entity_id: int = 0
    is_hardcore: bool = False
    gamemode: int = 0  # 0=survival, 1=creative, 2=adventure, 3=spectator
    previous_gamemode: int = 0
    world_names: list = field(default_factory=list)
    dimension_codec: dict = field(default_factory=dict)
    dimension: str = "minecraft:overworld"
    world_name: str = "minecraft:overworld"
    hashed_seed: int = 0
    max_players: int = 20
    view_distance: int = 10
    simulation_distance: int = 10
    reduced_debug_info: bool = False
    enable_respawn_screen: bool = True
    is_debug: bool = False
    is_flat: bool = False
    
    def __post_init__(self):
        self.packet_id = PacketID.JOIN_GAME


@dataclass
class PlayerPositionAndLookPacket(MCPacket):
    """玩家位置和朝向数据包 (S->C)"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    yaw: float = 0.0
    pitch: float = 0.0
    flags: int = 0  # 位掩码
    teleport_id: int = 0
    
    def __post_init__(self):
        self.packet_id = PacketID.PLAYER_POSITION_AND_LOOK


@dataclass
class TeleportConfirmPacket(MCPacket):
    """传送确认数据包 (C->S)"""
    teleport_id: int = 0
    
    def __post_init__(self):
        self.packet_id = PacketID.TELEPORT_CONFIRM
    
    def encode(self) -> bytes:
        result = VarInt.encode(self.packet_id)
        result += VarInt.encode(self.teleport_id)
        return result


@dataclass
class KeepAlivePacket(MCPacket):
    """心跳数据包 (双向)"""
    keep_alive_id: int = 0
    
    def __post_init__(self):
        self.packet_id = PacketID.KEEP_ALIVE
    
    def encode(self) -> bytes:
        result = VarInt.encode(self.packet_id)
        result += struct.pack('>q', self.keep_alive_id)
        return result


@dataclass
class ChatMessagePacket(MCPacket):
    """聊天消息数据包 (S->C)"""
    json_data: str = ""
    position: int = 0  # 0=chat, 1=system, 2=game_info
    sender: str = ""  # UUID
    
    def __post_init__(self):
        self.packet_id = PacketID.CHAT_MESSAGE_PACKET


# 数据包注册表
PACKET_REGISTRY: Dict[int, type] = {
    PacketID.HANDSHAKE: HandshakePacket,
    PacketID.LOGIN_START: LoginStartPacket,
    PacketID.JOIN_GAME: JoinGamePacket,
    PacketID.PLAYER_POSITION_AND_LOOK: PlayerPositionAndLookPacket,
    PacketID.TELEPORT_CONFIRM: TeleportConfirmPacket,
    PacketID.KEEP_ALIVE: KeepAlivePacket,
    PacketID.CHAT_MESSAGE_PACKET: ChatMessagePacket,
}


def get_packet_class(packet_id: int) -> Optional[type]:
    """获取数据包类"""
    return PACKET_REGISTRY.get(packet_id)


def register_packet(packet_id: int, packet_class: type):
    """注册数据包类"""
    PACKET_REGISTRY[packet_id] = packet_class


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("MnMCP v3 - MC 数据包测试")
    print("=" * 60)
    
    # 测试握手包
    print("\nHandshake 包测试:")
    handshake = HandshakePacket(
        protocol_version=760,
        server_address="localhost",
        server_port=25565,
        next_state=2
    )
    encoded = handshake.encode()
    print(f"  编码后: {len(encoded)} bytes")
    print(f"  数据: {encoded.hex()}")
    
    # 测试登录开始
    print("\nLogin Start 包测试:")
    login = LoginStartPacket(username="TestPlayer")
    encoded = login.encode()
    print(f"  编码后: {len(encoded)} bytes")
    print(f"  用户名: {login.username}")
    
    # 测试传送确认
    print("\nTeleport Confirm 包测试:")
    tp = TeleportConfirmPacket(teleport_id=123)
    encoded = tp.encode()
    print(f"  编码后: {len(encoded)} bytes")
    print(f"  Teleport ID: {tp.teleport_id}")
    
    # 统计
    print(f"\n已定义数据包: {len(PACKET_REGISTRY)}")
    print("✓ 数据包测试完成")
