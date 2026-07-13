"""
MnMCP v3 - MiniWorld 客户端
主客户端类，整合 RakNet、认证、游戏逻辑
GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import asyncio
import aiohttp
import hashlib
import time
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
from enum import IntEnum
import logging

try:
    import aiorak
    from aiorak import Connection, Reliability, Priority
    AIORAK_AVAILABLE = True
except ImportError:
    AIORAK_AVAILABLE = False
    Connection = None
    Reliability = None
    Priority = None

from ..mcp_protocol.msgcode_registry import (
    MessageRegistry, PacketDirection, get_message_name
)
from ..mcp_protocol.codec import MCPProtocolCodec, MCPPacket
from ..mcp_crypto.auth_mcp import MCPAuthManager, MCPAuthConfig

logger = logging.getLogger(__name__)


class MiniClientState(IntEnum):
    """MiniWorld 客户端状态"""
    DISCONNECTED = 0
    AUTHENTICATING = 1
    CONNECTING = 2
    CONNECTED = 3
    ENTERING = 4
    IN_GAME = 5
    DISCONNECTING = 6


@dataclass
class MiniAuthConfig:
    """MiniWorld 认证配置"""
    uin: int = 0
    passwd: str = ""
    device_id: str = ""
    api_id: int = 110
    version: str = "1.55.0"
    
    auth_server: str = "wskacchm.mini1.cn"
    auth_port: int = 14130
    
    xxtea_key: bytes = field(default_factory=lambda: b"miniworld")


@dataclass
class MiniPlayerInfo:
    """MiniWorld 玩家信息"""
    uin: int = 0
    name: str = ""
    aid: str = ""
    token: str = ""
    jwt: str = ""
    
    room_id: str = ""
    room_name: str = ""
    is_host: bool = False
    
    entity_id: int = 0
    
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    yaw: float = 0.0
    pitch: float = 0.0


@dataclass
class MiniRoomInfo:
    """MiniWorld 房间信息"""
    room_id: str = ""
    room_name: str = ""
    world_id: str = ""
    
    max_players: int = 10
    cur_players: int = 0
    
    game_server_ip: str = ""
    game_server_port: int = 0
    
    is_started: bool = False
    is_locked: bool = False


@dataclass
class MiniClientConfig:
    """MiniWorld 客户端配置"""
    auth: MiniAuthConfig = field(default_factory=MiniAuthConfig)
    
    debug: bool = False
    log_packets: bool = False


class MCPMiniClient:
    """
    MnMCP MiniWorld 客户端
    
    功能:
    - HTTP 认证 (XXTEA加密 + MD5签名)
    - 房间列表获取
    - 房间进入
    - RakNet 游戏连接
    - 数据包收发
    - 玩家状态管理
    - 事件系统
    """
    
    def __init__(self, config: Optional[MiniClientConfig] = None):
        self.config = config or MiniClientConfig()
        
        self._state = MiniClientState.DISCONNECTED
        self.auth_info: Optional[Dict] = None
        self.player = MiniPlayerInfo()
        self.current_room: Optional[MiniRoomInfo] = None
        self.room_list: List[MiniRoomInfo] = []
        
        self._raknet_conn: Optional[Connection] = None
        self._receive_task: Optional[asyncio.Task] = None
        
        self.codec = MCPProtocolCodec(self.config.auth.xxtea_key)
        self.registry = MessageRegistry()
        
        self._event_handlers: Dict[str, List[Callable]] = {
            'login': [],
            'room_list': [],
            'join_room': [],
            'connect': [],
            'enter_world': [],
            'disconnect': [],
            'chat': [],
            'move': [],
            'error': [],
        }
        
        self._http_session: Optional[aiohttp.ClientSession] = None
        self._running = False
        
        self._auth_manager: Optional[MCPAuthManager] = None
    
    @property
    def state(self) -> MiniClientState:
        return self._state
    
    @property
    def is_connected(self) -> bool:
        return self._state in (
            MiniClientState.CONNECTED,
            MiniClientState.ENTERING,
            MiniClientState.IN_GAME
        )
    
    @property
    def is_in_game(self) -> bool:
        return self._state == MiniClientState.IN_GAME
    
    @property
    def is_authenticated(self) -> bool:
        return self._auth_manager is not None and self._auth_manager.is_authenticated
    
    async def _get_http_session(self) -> aiohttp.ClientSession:
        if self._http_session is None or self._http_session.closed:
            self._http_session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            )
        return self._http_session
    
    async def login(self) -> bool:
        """登录 MiniWorld"""
        try:
            self._state = MiniClientState.AUTHENTICATING
            logger.info(f"Logging in as {self.config.auth.uin}...")
            
            auth_config = MCPAuthConfig(
                uin=str(self.config.auth.uin),
                passwd=self.config.auth.passwd,
                device_id=self.config.auth.device_id,
                api_id=self.config.auth.api_id,
                version=self.config.auth.version
            )
            
            self._auth_manager = MCPAuthManager(auth_config)
            success = await self._auth_manager.login()
            
            if success:
                self.auth_info = {
                    'code': 0,
                    'msg': 'success',
                    'aid': str(self._auth_manager.uin),
                    'token': self._auth_manager.token,
                    'uin': self._auth_manager.uin,
                    'jwt': self._auth_manager.jwt,
                    'name': self._auth_manager.name,
                }
                
                self.player.uin = self._auth_manager.uin
                self.player.aid = self.auth_info['aid']
                self.player.token = self.auth_info['token']
                self.player.jwt = self.auth_info['jwt']
                self.player.name = self.auth_info['name']
                
                logger.info(f"Login success: aid={self.player.aid}, name={self.player.name}")
                
                await self._trigger_event('login', self.auth_info)
                return True
            else:
                logger.error("Login failed")
                await self._trigger_event('error', 'login', "Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            await self._trigger_event('error', 'login', e)
            return False
    
    async def get_room_list(self) -> List[MiniRoomInfo]:
        """获取房间列表"""
        try:
            if not self.is_authenticated:
                logger.error("Not authenticated")
                return []
            
            logger.info("Getting room list...")
            
            session = await self._get_http_session()
            
            headers = self._auth_manager.get_auth_headers()
            url = f"https://{self.config.auth.auth_server}:{self.config.auth.auth_port}/room/list"
            
            async with session.get(url, headers=headers, timeout=10) as resp:
                data = await resp.json()
                
                if data.get('code') != 0:
                    raise RuntimeError(f"Room list API failed: {data}")

                rooms_data = data.get('data', [])
                self.room_list = []
                
                for room_data in rooms_data:
                    self.room_list.append(MiniRoomInfo(
                        room_id=room_data.get('room_id', ''),
                        room_name=room_data.get('room_name', ''),
                        max_players=room_data.get('max_players', 10),
                        cur_players=room_data.get('cur_players', 0),
                    ))
            
            logger.info(f"Got {len(self.room_list)} rooms")
            
            await self._trigger_event('room_list', self.room_list)
            
            return self.room_list
            
        except Exception as e:
            logger.error(f"Failed to get room list: {e}")
            return []
    
    async def join_room(self, room_id: str) -> bool:
        """加入房间"""
        try:
            if not self.is_authenticated:
                logger.error("Not authenticated")
                return False
            
            logger.info(f"Joining room {room_id}...")
            
            room = None
            for r in self.room_list:
                if r.room_id == room_id:
                    room = r
                    break
            
            if not room:
                logger.error(f"Room {room_id} not found")
                return False
            
            self.current_room = room
            
            session = await self._get_http_session()
            
            headers = self._auth_manager.get_auth_headers()
            url = f"https://{self.config.auth.auth_server}:{self.config.auth.auth_port}/room/join?room_id={room_id}"
            
            async with session.post(url, headers=headers, timeout=10) as resp:
                data = await resp.json()
                
                if data.get('code') != 0:
                    raise RuntimeError(f"Join failed: {data}")

                room_data = data.get('data', {})
                room.game_server_ip = room_data.get('server_ip', '')
                room.game_server_port = room_data.get('server_port', 0)

                if not room.game_server_ip or not room.game_server_port:
                    raise RuntimeError(f"Join response missing game server: {data}")
            
            logger.info(f"Joined room: {room.room_name}, server: {room.game_server_ip}:{room.game_server_port}")
            
            await self._trigger_event('join_room', room)
            
            return await self._connect_game_server()
            
        except Exception as e:
            logger.error(f"Failed to join room: {e}")
            return False
    
    async def _connect_game_server(self) -> bool:
        """连接到游戏服务器"""
        try:
            if not self.current_room:
                logger.error("No room to connect")
                return False
            
            self._state = MiniClientState.CONNECTING
            
            if not AIORAK_AVAILABLE:
                raise RuntimeError("aiorak is required for MiniWorld connections")

            self._raknet_conn = Connection()
            await self._raknet_conn.connect(
                self.current_room.game_server_ip,
                self.current_room.game_server_port
            )
            logger.info(f"RakNet connected to {self.current_room.game_server_ip}:{self.current_room.game_server_port}")
            
            self._state = MiniClientState.CONNECTED
            logger.info(f"Connected to game server {self.current_room.game_server_ip}:{self.current_room.game_server_port}")
            
            self._running = True
            self._receive_task = asyncio.create_task(self._receive_loop())
            
            await self._send_enter_world()
            
            await self._trigger_event('connect')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect game server: {e}")
            return False
    
    async def _send_enter_world(self) -> None:
        """发送进入世界请求"""
        logger.info("Sending enter world request...")
        self._state = MiniClientState.ENTERING
        
        enter_data = {
            'msg_type': 1001,
            'uin': self.player.uin,
            'token': self.player.token,
            'room_id': self.current_room.room_id if self.current_room else '',
            'version': self.config.auth.version,
        }
        
        try:
            packet = self.codec.create_packet(
                msg_code=enter_data['msg_type'],
                data=str(enter_data).encode('utf-8'),
                direction=PacketDirection.CLIENT_TO_SERVER
            )
            encoded = self.codec.encode(packet)
            
            if self._raknet_conn:
                self._raknet_conn.send(encoded, Reliability.RELIABLE_ORDERED, Priority.MEDIUM)
                logger.debug(f"Sent enter world packet: {len(encoded)} bytes")
        except Exception as e:
            logger.warning(f"Failed to send enter world: {e}")
        
        await asyncio.sleep(1)
        self._state = MiniClientState.IN_GAME
        self.player.entity_id = 1000
        
        logger.info("Entered world!")
        await self._trigger_event('enter_world')
    
    async def _receive_loop(self) -> None:
        """接收循环"""
        logger.debug("Receive loop started")
        
        while self._running and self._raknet_conn:
            try:
                data = await self._raknet_conn.recv()
                if not data:
                    continue
                
                logger.debug(f"Received {len(data)} bytes")
                
                if self.config.log_packets:
                    logger.debug(f"Raw packet: {data.hex()[:64]}...")
                
                try:
                    packet = self.codec.decode(data, PacketDirection.SERVER_TO_CLIENT)
                    
                    if packet:
                        await self._process_packet(packet)
                except Exception as e:
                    logger.debug(f"Failed to decode packet: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in receive loop: {e}")
                await asyncio.sleep(0.1)
        
        logger.debug("Receive loop stopped")
    
    async def _process_packet(self, packet: MCPPacket) -> None:
        """处理接收到的数据包"""
        msg_name = get_message_name(packet.msg_code)
        
        if packet.msg_code == 9001:
            await self._trigger_event('chat', packet.data)
        elif packet.msg_code == 2001:
            await self._trigger_event('move', packet.data)
        
        if self.config.log_packets:
            logger.debug(f"Packet: {msg_name} (0x{packet.msg_code:04X})")
    
    async def send_move(self, x: float, y: float, z: float, yaw: float = 0, pitch: float = 0) -> bool:
        """发送移动请求"""
        if not self.is_in_game:
            return False
        
        self.player.x = x
        self.player.y = y
        self.player.z = z
        self.player.yaw = yaw
        self.player.pitch = pitch
        
        move_data = {
            'msg_type': 2001,
            'entity_id': self.player.entity_id,
            'x': x,
            'y': y,
            'z': z,
            'yaw': yaw,
            'pitch': pitch,
            'speed': 0.1,
        }
        
        try:
            packet = self.codec.create_packet(
                msg_code=move_data['msg_type'],
                data=str(move_data).encode('utf-8'),
                direction=PacketDirection.CLIENT_TO_SERVER
            )
            encoded = self.codec.encode(packet)
            
            if self._raknet_conn:
                self._raknet_conn.send(encoded, Reliability.UNRELIABLE, Priority.MEDIUM)
            
            logger.debug(f"Move to ({x:.2f}, {y:.2f}, {z:.2f})")
            
            await self._trigger_event('move', move_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send move: {e}")
            return False
    
    async def send_chat(self, message: str) -> bool:
        """发送聊天消息"""
        if not self.is_in_game:
            return False
        
        chat_data = {
            'msg_type': 9001,
            'sender': self.player.name,
            'message': message,
            'timestamp': int(time.time()),
        }
        
        try:
            packet = self.codec.create_packet(
                msg_code=chat_data['msg_type'],
                data=str(chat_data).encode('utf-8'),
                direction=PacketDirection.CLIENT_TO_SERVER
            )
            encoded = self.codec.encode(packet)
            
            if self._raknet_conn:
                self._raknet_conn.send(encoded, Reliability.RELIABLE_ORDERED, Priority.MEDIUM)
            
            logger.info(f"Chat: {message}")
            
            await self._trigger_event('chat', chat_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send chat: {e}")
            return False
    
    async def disconnect(self, reason: str = "Client disconnect") -> None:
        """断开连接"""
        logger.info(f"Disconnecting: {reason}")
        
        self._state = MiniClientState.DISCONNECTING
        self._running = False
        
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        if self._raknet_conn:
            self._raknet_conn.disconnect()
            self._raknet_conn = None
        
        if self._http_session:
            await self._http_session.close()
            self._http_session = None
        
        self._state = MiniClientState.DISCONNECTED
        
        logger.info("Disconnected")
        await self._trigger_event('disconnect', reason)
    
    def on(self, event: str) -> Callable:
        """注册事件处理器"""
        def decorator(func: Callable) -> Callable:
            if event not in self._event_handlers:
                self._event_handlers[event] = []
            self._event_handlers[event].append(func)
            return func
        return decorator
    
    async def _trigger_event(self, event: str, *args, **kwargs) -> None:
        """触发事件"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(*args, **kwargs)
                else:
                    handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in event handler for {event}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'state': self._state.name,
            'connected': self.is_connected,
            'in_game': self.is_in_game,
            'authenticated': self.is_authenticated,
            'player': {
                'uin': self.player.uin,
                'name': self.player.name,
                'entity_id': self.player.entity_id,
                'position': {
                    'x': round(self.player.x, 2),
                    'y': round(self.player.y, 2),
                    'z': round(self.player.z, 2),
                },
            },
            'room': {
                'id': self.current_room.room_id if self.current_room else None,
                'name': self.current_room.room_name if self.current_room else None,
                'server': f"{self.current_room.game_server_ip}:{self.current_room.game_server_port}" if self.current_room else None,
            } if self.current_room else None,
        }


async def create_mini_client(
    uin: int,
    passwd: str,
    device_id: str = ""
) -> MCPMiniClient:
    """快速创建 MiniWorld 客户端"""
    auth = MiniAuthConfig(uin=uin, passwd=passwd, device_id=device_id)
    config = MiniClientConfig(auth=auth)
    return MCPMiniClient(config)


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("MnMCP v3 - MiniWorld 客户端测试")
    print("=" * 60)
    
    async def test():
        config = MiniClientConfig(
            auth=MiniAuthConfig(uin=123456, passwd="test_pass"),
            debug=True
        )
        
        client = MCPMiniClient(config)
        
        @client.on('login')
        async def on_login(auth_info):
            print(f"✓ 登录成功: aid={auth_info.get('aid')}, name={auth_info.get('name')}")
        
        @client.on('room_list')
        async def on_room_list(rooms):
            print(f"✓ 房间列表: {len(rooms)} 个房间")
        
        @client.on('join_room')
        async def on_join_room(room):
            print(f"✓ 加入房间: {room.room_name}")
        
        @client.on('enter_world')
        async def on_enter_world():
            print("✓ 进入世界!")
        
        @client.on('disconnect')
        async def on_disconnect(reason):
            print(f"✓ 断开连接: {reason}")
        
        print("\n测试登录...")
        logged_in = await client.login()
        
        if logged_in:
            print("\n获取房间列表...")
            rooms = await client.get_room_list()
            
            if rooms:
                print(f"\n加入房间 {rooms[0].room_id}...")
                joined = await client.join_room(rooms[0].room_id)
                
                if joined:
                    await asyncio.sleep(2)
                    
                    if client.is_in_game:
                        print("\n测试移动...")
                        await client.send_move(100.0, 64.0, 200.0, 45.0, 0.0)
                        
                        print("\n测试聊天...")
                        await client.send_chat("Hello from MnMCP!")
                    
                    stats = client.get_stats()
                    print(f"\n统计:")
                    print(f"  状态: {stats['state']}")
                    print(f"  玩家: {stats['player']['name']}")
                    print(f"  位置: {stats['player']['position']}")
            
            print("\n断开连接...")
            await client.disconnect("Test complete")
        
        print("\n✓ 客户端测试完成")
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        pass
