"""
MnMCP v3 - Minecraft 客户端
主客户端类，整合连接、加密、玩家状态

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import asyncio
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from enum import IntEnum
from datetime import datetime
import logging

from .protocol.connection import MCPProtocolConnection, ConnectionConfig, ConnectionState
from .protocol.packets import (
    MCPacket, HandshakePacket, LoginStartPacket,
    PacketID, JoinGamePacket, PlayerPositionAndLookPacket,
    TeleportConfirmPacket, KeepAlivePacket,
    ClientChatMessagePacket, PlayerPositionPacket,
    PlayerPositionAndRotationPacket, PlayerRotationPacket
)
from .protocol.crypto import MCProtocolCrypto

logger = logging.getLogger(__name__)


class Gamemode(IntEnum):
    """游戏模式"""
    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2
    SPECTATOR = 3


@dataclass
class PlayerPosition:
    """玩家位置"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    yaw: float = 0.0
    pitch: float = 0.0
    on_ground: bool = True


@dataclass
class PlayerInfo:
    """玩家信息"""
    username: str = ""
    uuid: str = ""
    entity_id: int = 0
    gamemode: Gamemode = Gamemode.SURVIVAL
    health: float = 20.0
    food: int = 20
    level: int = 0


@dataclass
class MCClientConfig:
    """MC 客户端配置"""
    host: str = "localhost"
    port: int = 25565
    username: str = "MnMCPPlayer"
    
    # 协议 - MC 1.20.6
    protocol_version: int = 766
    
    # 连接
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    
    # 调试
    debug: bool = False


class MCPMinecraftClient:
    """
    MnMCP Minecraft 客户端
    
    功能:
    - 连接到 MC 服务器
    - 登录流程
    - 玩家状态管理
    - 位置同步
    - 事件系统
    - 聊天收发
    
    使用示例:
        config = MCClientConfig(host="localhost", username="TestPlayer")
        client = MCPMinecraftClient(config)
        
        @client.on_join
        async def on_join():
            print("Joined game!")
        
        await client.connect()
        await client.login()
    """
    
    def __init__(self, config: Optional[MCClientConfig] = None):
        """
        初始化客户端
        
        Args:
            config: 客户端配置
        """
        self.config = config or MCClientConfig()
        
        # 连接
        conn_config = ConnectionConfig(
            host=self.config.host,
            port=self.config.port,
            protocol_version=self.config.protocol_version,
            debug=self.config.debug
        )
        self.connection = MCPProtocolConnection(conn_config)
        
        # 加密
        self.crypto = MCProtocolCrypto()
        
        # 玩家
        self.player = PlayerInfo(username=self.config.username)
        self.position = PlayerPosition()
        
        # 事件处理器
        self._event_handlers: Dict[str, list] = {
            'connect': [],
            'disconnect': [],
            'login': [],
            'join': [],
            'position': [],
            'spawn': [],
            'death': [],
            'chat': [],
            'error': [],
        }
        self._login_event: Optional[asyncio.Event] = None
        self._join_event: Optional[asyncio.Event] = None
        
        # 注册连接事件
        self._register_connection_handlers()
        
        # 状态
        self._connected = False
        self._logged_in = False
        self._in_game = False
    
    def _register_connection_handlers(self) -> None:
        """注册连接层事件处理器"""
        
        @self.connection.on_packet(PacketID.LOGIN_SUCCESS)
        async def on_login_success(packet: MCPacket):
            """登录成功"""
            self.player.uuid = packet.data.get('uuid', '')
            self.player.username = packet.data.get('username', self.config.username)
            self._logged_in = True
            if self._login_event:
                self._login_event.set()
            logger.info(f"Login success: {self.player.username} ({self.player.uuid})")
            await self._trigger_event('login')
        
        @self.connection.on_packet(PacketID.JOIN_GAME)
        async def on_join_game(packet: JoinGamePacket):
            """加入游戏"""
            self.player.entity_id = packet.entity_id
            self.player.gamemode = Gamemode(packet.gamemode)
            self._in_game = True
            if self._join_event:
                self._join_event.set()
            logger.info(f"Joined game: entity_id={self.player.entity_id}, gamemode={self.player.gamemode.name}")
            await self._trigger_event('join')
        
        @self.connection.on_packet(PacketID.PLAYER_POSITION_AND_LOOK)
        async def on_position_look(packet: PlayerPositionAndLookPacket):
            """收到位置和朝向更新"""
            self.position.x = packet.x
            self.position.y = packet.y
            self.position.z = packet.z
            self.position.yaw = packet.yaw
            self.position.pitch = packet.pitch
            
            # 确认传送
            await self.confirm_teleport(packet.teleport_id)
            await self._trigger_event('position', self.position)
            
            logger.debug(f"Position updated: ({packet.x:.2f}, {packet.y:.2f}, {packet.z:.2f})")
        
        @self.connection.on_packet(PacketID.CHAT_MESSAGE_PACKET)
        async def on_chat(packet: MCPacket):
            """收到聊天消息"""
            message = packet.data.get('json_data', '{}')
            position = packet.data.get('position', 0)
            await self._trigger_event('chat', message, position)
    
    async def connect(self) -> bool:
        """
        连接到服务器
        
        Returns:
            是否连接成功
        """
        try:
            logger.info(f"Connecting to {self.config.host}:{self.config.port}...")
            
            if not await self.connection.connect():
                return False
            
            self._connected = True
            logger.info(f"Connected to {self.config.host}:{self.config.port}")
            
            # 触发事件
            await self._trigger_event('connect')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    async def disconnect(self, reason: str = "Client disconnect") -> None:
        """
        断开连接
        
        Args:
            reason: 断开原因
        """
        if not self._connected:
            return
        
        logger.info(f"Disconnecting: {reason}")
        
        await self.connection.disconnect(reason)
        
        self._connected = False
        self._logged_in = False
        self._in_game = False
        
        # 触发事件
        await self._trigger_event('disconnect', reason)
    
    async def login(self) -> bool:
        """
        登录流程
        
        1. 发送 Handshake
        2. 发送 Login Start
        3. 等待 Login Success / Encryption Request
        
        Returns:
            是否登录成功
        """
        if not self._connected:
            logger.error("Not connected")
            return False
        
        if self._logged_in:
            logger.warning("Already logged in")
            return True
        
        try:
            logger.info("Starting login...")
            
            self._login_event = asyncio.Event()
            self._join_event = asyncio.Event()

            handshake = HandshakePacket(
                protocol_version=self.config.protocol_version,
                server_address=self.config.host,
                server_port=self.config.port,
                next_state=2  # Login
            )
            
            if not await self.connection.send_packet(handshake):
                logger.error("Failed to send handshake")
                return False
            self.connection._state = ConnectionState.LOGIN
            
            logger.debug("Handshake sent")
            login_start = LoginStartPacket(username=self.config.username)
            
            if not await self.connection.send_packet(login_start):
                logger.error("Failed to send login start")
                return False
            
            logger.debug("Login start sent")

            await asyncio.wait_for(self._login_event.wait(), timeout=self.config.read_timeout)

            try:
                await asyncio.wait_for(self._join_event.wait(), timeout=self.config.read_timeout)
            except asyncio.TimeoutError:
                logger.warning("Login success but Join Game was not received before timeout")

            return self._logged_in
            
        except asyncio.TimeoutError:
            logger.error("Login timed out")
            return False
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    async def confirm_teleport(self, teleport_id: int) -> bool:
        """
        确认传送
        
        Args:
            teleport_id: 传送ID
            
        Returns:
            是否发送成功
        """
        if not self._in_game:
            return False
        
        packet = TeleportConfirmPacket(teleport_id=teleport_id)
        return await self.connection.send_packet(packet)
    
    async def update_position(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
        yaw: Optional[float] = None,
        pitch: Optional[float] = None,
        on_ground: Optional[bool] = None
    ) -> bool:
        """
        更新位置并发送
        
        Args:
            x, y, z: 坐标
            yaw, pitch: 朝向
            on_ground: 是否在地面上
            
        Returns:
            是否发送成功
        """
        if not self._in_game:
            return False
        
        if x is not None:
            self.position.x = x
        if y is not None:
            self.position.y = y
        if z is not None:
            self.position.z = z
        if yaw is not None:
            self.position.yaw = yaw
        if pitch is not None:
            self.position.pitch = pitch
        if on_ground is not None:
            self.position.on_ground = on_ground
        
        has_position = x is not None or y is not None or z is not None
        has_rotation = yaw is not None or pitch is not None
        
        if has_position and has_rotation:
            packet = PlayerPositionAndRotationPacket(
                x=self.position.x,
                y=self.position.y,
                z=self.position.z,
                yaw=self.position.yaw,
                pitch=self.position.pitch,
                on_ground=self.position.on_ground
            )
        elif has_position:
            packet = PlayerPositionPacket(
                x=self.position.x,
                y=self.position.y,
                z=self.position.z,
                on_ground=self.position.on_ground
            )
        elif has_rotation:
            packet = PlayerRotationPacket(
                yaw=self.position.yaw,
                pitch=self.position.pitch,
                on_ground=self.position.on_ground
            )
        else:
            return True
        
        logger.debug(f"Position update: ({self.position.x:.2f}, {self.position.y:.2f}, {self.position.z:.2f})")
        
        return await self.connection.send_packet(packet)
    
    async def send_chat(self, message: str) -> bool:
        """
        发送聊天消息
        
        Args:
            message: 消息内容
            
        Returns:
            是否发送成功
        """
        if not self._in_game:
            return False
        
        if len(message) > 256:
            message = message[:256]
        
        packet = ClientChatMessagePacket(message=message)
        
        logger.info(f"Chat: {message}")
        
        return await self.connection.send_packet(packet)
    
    def on(self, event: str) -> Callable:
        """
        注册事件处理器
        
        Args:
            event: 事件名 (connect, disconnect, login, join, chat, ...)
            
        Usage:
            @client.on('join')
            async def on_join():
                print("Joined game!")
        """
        def decorator(func: Callable) -> Callable:
            if event not in self._event_handlers:
                self._event_handlers[event] = []
            self._event_handlers[event].append(func)
            return func
        return decorator
    
    async def _trigger_event(self, event: str, *args, **kwargs) -> None:
        """
        触发事件
        
        Args:
            event: 事件名
            *args, **kwargs: 事件参数
        """
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(*args, **kwargs)
                else:
                    handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in event handler for {event}: {e}")
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected
    
    @property
    def is_logged_in(self) -> bool:
        """是否已登录"""
        return self._logged_in
    
    @property
    def is_in_game(self) -> bool:
        """是否在游戏中"""
        return self._in_game
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'connected': self._connected,
            'logged_in': self._logged_in,
            'in_game': self._in_game,
            'player': {
                'username': self.player.username,
                'uuid': self.player.uuid,
                'entity_id': self.player.entity_id,
                'gamemode': self.player.gamemode.name,
            },
            'position': {
                'x': round(self.position.x, 2),
                'y': round(self.position.y, 2),
                'z': round(self.position.z, 2),
                'yaw': round(self.position.yaw, 2),
                'pitch': round(self.position.pitch, 2),
            },
            'connection': self.connection.get_stats(),
        }


# 便捷函数
async def create_mc_client(
    host: str,
    port: int,
    username: str
) -> MCPMinecraftClient:
    """
    快速创建客户端
    
    Args:
        host: 服务器地址
        port: 端口
        username: 用户名
        
    Returns:
        客户端实例
    """
    config = MCClientConfig(host=host, port=port, username=username)
    return MCPMinecraftClient(config)


# 测试
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("MnMCP v3 - MC 客户端测试")
    print("=" * 60)
    
    async def test():
        # 创建客户端
        config = MCClientConfig(
            host="127.0.0.1",
            port=25565,
            username="TestPlayer",
            debug=True
        )
        
        client = MCPMinecraftClient(config)
        
        # 注册事件
        @client.on('connect')
        async def on_connect():
            print("✓ 事件: 已连接")
        
        @client.on('login')
        async def on_login():
            print("✓ 事件: 已登录")
        
        @client.on('join')
        async def on_join():
            print("✓ 事件: 已加入游戏")
        
        @client.on('disconnect')
        async def on_disconnect(reason):
            print(f"✓ 事件: 已断开 ({reason})")
        
        # 测试连接 (可能失败，因为没有本地MC服务器)
        print("\n尝试连接...")
        connected = await client.connect()
        
        if connected:
            print(f"✓ 连接成功")
            
            # 获取统计
            stats = client.get_stats()
            print(f"\n统计:")
            print(f"  连接: {stats['connected']}")
            print(f"  登录: {stats['logged_in']}")
            print(f"  游戏中: {stats['in_game']}")
            print(f"  玩家: {stats['player']['username']}")
            
            # 尝试登录
            print("\n尝试登录...")
            # await client.login()  # 实际登录流程
            
            # 等待
            await asyncio.sleep(2)
            
            # 断开
            await client.disconnect("Test complete")
        else:
            print(f"✗ 连接失败 (预期，没有本地MC服务器)")
        
        print("\n✓ 客户端测试完成")
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        pass
