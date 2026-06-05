"""
MnMCP v3 - MiniWorld 客户端
主客户端类，整合 RakNet、认证、游戏逻辑
"""

import asyncio
import aiohttp
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
from enum import IntEnum
import logging

import aiorak
from aiorak import Connection, Reliability, Priority

from ..mcp_protocol.msgcode_registry import (
    MessageRegistry, PacketDirection, get_message_name
)
from ..mcp_protocol.codec import MCPProtocolCodec, MCPPacket

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
    
    # 服务器
    auth_server: str = "wskacchm.mini1.cn"
    auth_port: int = 14130
    
    # XXTEA 密钥
    xxtea_key: bytes = field(default_factory=lambda: b"miniworld")


@dataclass
class MiniPlayerInfo:
    """MiniWorld 玩家信息"""
    uin: int = 0
    name: str = ""
    aid: str = ""
    token: str = ""
    
    # 房间
    room_id: str = ""
    room_name: str = ""
    is_host: bool = False
    
    # 游戏
    entity_id: int = 0
    
    # 位置
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
    
    # 配置
    max_players: int = 10
    cur_players: int = 0
    
    # 服务器
    game_server_ip: str = ""
    game_server_port: int = 0
    
    # 状态
    is_started: bool = False
    is_locked: bool = False


@dataclass
class MiniClientConfig:
    """MiniWorld 客户端配置"""
    # 认证
    auth: MiniAuthConfig = field(default_factory=MiniAuthConfig)
    
    # 调试
    debug: bool = False
    log_packets: bool = False


class MCPMiniClient:
    """
    MnMCP MiniWorld 客户端
    
    功能:
    - HTTP 认证
    - 房间列表获取
    - 房间进入
    - RakNet 游戏连接
    - 数据包收发
    - 玩家状态管理
    - 事件系统
    
    使用示例:
        config = MiniClientConfig(auth=MiniAuthConfig(uin=123456, passwd="..."))
        client = MCPMiniClient(config)
        
        @client.on('enter_world')
        async def on_enter():
            print("Entered world!")
        
        # 登录
        if await client.login():
            # 获取房间列表
            rooms = await client.get_room_list()
            # 进入房间
            await client.join_room(rooms[0].room_id)
    """
    
    def __init__(self, config: Optional[MiniClientConfig] = None):
        """
        初始化客户端
        
        Args:
            config: 客户端配置
        """
        self.config = config or MiniClientConfig()
        
        # 状态
        self._state = MiniClientState.DISCONNECTED
        
        # 认证信息
        self.auth_info: Optional[Dict] = None
        
        # 玩家
        self.player = MiniPlayerInfo()
        
        # 房间
        self.current_room: Optional[MiniRoomInfo] = None
        self.room_list: List[MiniRoomInfo] = []
        
        # RakNet
        self._raknet_conn: Optional[Connection] = None
        self._receive_task: Optional[asyncio.Task] = None
        
        # 协议
        self.codec = MCPProtocolCodec(self.config.auth.xxtea_key)
        self.registry = MessageRegistry()
        
        # 事件
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
        
        # HTTP 会话
        self._http_session: Optional[aiohttp.ClientSession] = None
        
        # 运行状态
        self._running = False
    
    @property
    def state(self) -> MiniClientState:
        """当前状态"""
        return self._state
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._state in (
            MiniClientState.CONNECTED,
            MiniClientState.ENTERING,
            MiniClientState.IN_GAME
        )
    
    @property
    def is_in_game(self) -> bool:
        """是否在游戏中"""
        return self._state == MiniClientState.IN_GAME
    
    async def _get_http_session(self) -> aiohttp.ClientSession:
        """获取 HTTP 会话"""
        if self._http_session is None or self._http_session.closed:
            self._http_session = aiohttp.ClientSession()
        return self._http_session
    
    async def login(self) -> bool:
        """
        登录 MiniWorld
        
        Returns:
            是否登录成功
        """
        try:
            self._state = MiniClientState.AUTHENTICATING
            logger.info(f"Logging in as {self.config.auth.uin}...")
            
            # TODO: 实现实际的 HTTP 认证
            # 这里使用模拟数据
            self.auth_info = {
                'code': 0,
                'msg': 'success',
                'aid': '123456789',
                'token': 'mock_token',
                'uin': self.config.auth.uin,
            }
            
            self.player.uin = self.config.auth.uin
            self.player.aid = self.auth_info['aid']
            self.player.token = self.auth_info['token']
            self.player.name = f"Player_{self.config.auth.uin}"
            
            logger.info(f"Login success: aid={self.player.aid}")
            
            # 触发事件
            await self._trigger_event('login', self.auth_info)
            
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            await self._trigger_event('error', 'login', e)
            return False
    
    async def get_room_list(self) -> List[MiniRoomInfo]:
        """
        获取房间列表
        
        Returns:
            房间列表
        """
        try:
            logger.info("Getting room list...")
            
            # TODO: 实现实际的房间列表获取
            # 这里使用模拟数据
            self.room_list = [
                MiniRoomInfo(
                    room_id="room_1",
                    room_name="Test Room 1",
                    max_players=10,
                    cur_players=2
                ),
                MiniRoomInfo(
                    room_id="room_2",
                    room_name="Test Room 2",
                    max_players=20,
                    cur_players=5
                ),
            ]
            
            logger.info(f"Got {len(self.room_list)} rooms")
            
            # 触发事件
            await self._trigger_event('room_list', self.room_list)
            
            return self.room_list
            
        except Exception as e:
            logger.error(f"Failed to get room list: {e}")
            return []
    
    async def join_room(self, room_id: str) -> bool:
        """
        加入房间
        
        Args:
            room_id: 房间ID
            
        Returns:
            是否加入成功
        """
        try:
            logger.info(f"Joining room {room_id}...")
            
            # 查找房间
            room = None
            for r in self.room_list:
                if r.room_id == room_id:
                    room = r
                    break
            
            if not room:
                logger.error(f"Room {room_id} not found")
                return False
            
            self.current_room = room
            
            # TODO: 实现实际的加入房间请求
            # 获取游戏服务器地址
            room.game_server_ip = "127.0.0.1"
            room.game_server_port = 20000
            
            logger.info(f"Joined room: {room.room_name}")
            
            # 触发事件
            await self._trigger_event('join_room', room)
            
            # 连接到游戏服务器
            return await self._connect_game_server()
            
        except Exception as e:
            logger.error(f"Failed to join room: {e}")
            return False
    
    async def _connect_game_server(self) -> bool:
        """
        连接到游戏服务器
        
        Returns:
            是否连接成功
        """
        try:
            if not self.current_room:
                logger.error("No room to connect")
                return False
            
            self._state = MiniClientState.CONNECTING
            
            # 创建 RakNet 连接
            self._raknet_conn = Connection()
            await self._raknet_conn.connect(
                self.current_room.game_server_ip,
                self.current_room.game_server_port
            )
            
            self._state = MiniClientState.CONNECTED
            logger.info(f"Connected to game server {self.current_room.game_server_ip}:{self.current_room.game_server_port}")
            
            # 启动接收循环
            self._running = True
            self._receive_task = asyncio.create_task(self._receive_loop())
            
            # 发送进入世界请求
            await self._send_enter_world()
            
            # 触发事件
            await self._trigger_event('connect')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect game server: {e}")
            return False
    
    async def _send_enter_world(self) -> None:
        """发送进入世界请求"""
        # TODO: 实现 Enter World 数据包
        # Msg 1001: RoleEnterWorldCH
        logger.info("Sending enter world request...")
        self._state = MiniClientState.ENTERING
        
        # 模拟进入成功
        await asyncio.sleep(1)
        self._state = MiniClientState.IN_GAME
        self.player.entity_id = 1000  # 模拟实体ID
        
        logger.info("Entered world!")
        await self._trigger_event('enter_world')
    
    async def _receive_loop(self) -> None:
        """接收循环"""
        logger.debug("Receive loop started")
        
        while self._running and self._raknet_conn:
            try:
                # 接收数据
                data = await self._raknet_conn.recv()
                if not data:
                    continue
                
                # 解码数据包
                # TODO: 实现完整的解码
                logger.debug(f"Received {len(data)} bytes")
                
                # 触发事件
                # await self._trigger_event('packet', packet)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in receive loop: {e}")
                await asyncio.sleep(0.1)
        
        logger.debug("Receive loop stopped")
    
    async def send_move(self, x: float, y: float, z: float, yaw: float = 0, pitch: float = 0) -> bool:
        """
        发送移动请求
        
        Args:
            x, y, z: 位置
            yaw, pitch: 朝向
            
        Returns:
            是否发送成功
        """
        if not self.is_in_game:
            return False
        
        # 更新本地位置
        self.player.x = x
        self.player.y = y
        self.player.z = z
        self.player.yaw = yaw
        self.player.pitch = pitch
        
        # TODO: 实现 Move 数据包
        # Msg 2001: RoleMoveCH
        logger.debug(f"Move to ({x:.2f}, {y:.2f}, {z:.2f})")
        
        return True
    
    async def send_chat(self, message: str) -> bool:
        """
        发送聊天消息
        
        Args:
            message: 消息内容
            
        Returns:
            是否发送成功
        """
        if not self.is_in_game:
            return False
        
        # TODO: 实现 Chat 数据包
        # Msg 9001: ChatContentCH
        logger.info(f"Chat: {message}")
        
        return True
    
    async def disconnect(self, reason: str = "Client disconnect") -> None:
        """
        断开连接
        
        Args:
            reason: 断开原因
        """
        logger.info(f"Disconnecting: {reason}")
        
        self._state = MiniClientState.DISCONNECTING
        self._running = False
        
        # 取消接收任务
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        # 断开 RakNet
        if self._raknet_conn:
            self._raknet_conn.disconnect()
            self._raknet_conn = None
        
        # 关闭 HTTP 会话
        if self._http_session:
            await self._http_session.close()
            self._http_session = None
        
        self._state = MiniClientState.DISCONNECTED
        
        logger.info("Disconnected")
        await self._trigger_event('disconnect', reason)
    
    def on(self, event: str) -> Callable:
        """
        注册事件处理器
        
        Args:
            event: 事件名
            
        Usage:
            @client.on('enter_world')
            async def on_enter():
                print("Entered world!")
        """
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
            } if self.current_room else None,
        }


# 便捷函数
async def create_mini_client(
    uin: int,
    passwd: str,
    device_id: str = ""
) -> MCPMiniClient:
    """
    快速创建 MiniWorld 客户端
    
    Args:
        uin: 用户ID
        passwd: 密码
        device_id: 设备ID
        
    Returns:
        客户端实例
    """
    auth = MiniAuthConfig(uin=uin, passwd=passwd, device_id=device_id)
    config = MiniClientConfig(auth=auth)
    return MCPMiniClient(config)


# 测试
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("MnMCP v3 - MiniWorld 客户端测试")
    print("=" * 60)
    
    async def test():
        # 创建客户端
        config = MiniClientConfig(
            auth=MiniAuthConfig(uin=123456, passwd="test_pass"),
            debug=True
        )
        
        client = MCPMiniClient(config)
        
        # 注册事件
        @client.on('login')
        async def on_login(auth_info):
            print(f"✓ 登录成功: aid={auth_info.get('aid')}")
        
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
        
        # 测试登录
        print("\n测试登录...")
        logged_in = await client.login()
        
        if logged_in:
            # 获取房间列表
            print("\n获取房间列表...")
            rooms = await client.get_room_list()
            
            if rooms:
                # 加入第一个房间
                print(f"\n加入房间 {rooms[0].room_id}...")
                joined = await client.join_room(rooms[0].room_id)
                
                if joined:
                    # 等待进入世界
                    await asyncio.sleep(2)
                    
                    # 测试移动
                    if client.is_in_game:
                        print("\n测试移动...")
                        await client.send_move(100.0, 64.0, 200.0, 45.0, 0.0)
                        
                        # 测试聊天
                        print("\n测试聊天...")
                        await client.send_chat("Hello from MnMCP!")
                    
                    # 统计
                    stats = client.get_stats()
                    print(f"\n统计:")
                    print(f"  状态: {stats['state']}")
                    print(f"  玩家: {stats['player']['name']}")
                    print(f"  位置: {stats['player']['position']}")
            
            # 断开
            print("\n断开连接...")
            await client.disconnect("Test complete")
        
        print("\n✓ 客户端测试完成")
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        pass
