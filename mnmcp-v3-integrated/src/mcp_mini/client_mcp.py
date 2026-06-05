#!/usr/bin/env python3
"""
MnMCP MiniWorld 客户端
基于 MN2MC mini/player.py，改进为高质量 Python 实现

功能:
- 连接到 MiniWorld 服务器
- 处理 MiniWorld 协议
- 玩家控制
- 数据包转发到 MC
"""

import asyncio
import logging
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum

from mcp_crypto.auth_mcp import MCPAuthManager, MCPAuthConfig

logger = logging.getLogger(__name__)


class MNWConnectionState(IntEnum):
    """连接状态"""
    DISCONNECTED = 0
    CONNECTING = 1
    AUTHENTICATING = 2
    CONNECTED = 3
    IN_GAME = 4
    DISCONNECTING = 5


@dataclass
class MNWPlayerState:
    """玩家状态"""
    uin: int = 0
    name: str = ""
    position: tuple = field(default_factory=lambda: (0.0, 0.0, 0.0))
    rotation: tuple = field(default_factory=lambda: (0.0, 0.0))
    health: float = 100.0
    level: int = 1
    room_id: str = ""


@dataclass
class MNWServerInfo:
    """服务器信息"""
    auth_host: str = "wskacchm.mini1.cn"
    auth_port: int = 14130
    game_host: str = ""
    game_port: int = 0
    version: str = "1.55.0"


class MCPMiniWorldClient:
    """
    MnMCP MiniWorld 客户端
    
    功能:
    1. 异步连接到 MNW 服务器
    2. 登录认证
    3. 进入房间/世界
    4. 玩家控制
    5. 数据包转发
    
    使用示例:
        client = MCPMiniWorldClient(server, auth)
        await client.connect()
        await client.login()
        await client.enter_world(room_id)
    """
    
    def __init__(
        self,
        server: MNWServerInfo,
        auth: MCPAuthManager
    ):
        """
        初始化
        
        Args:
            server: 服务器信息
            auth: 认证管理器
        """
        self.server = server
        self.auth = auth
        
        # 连接
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.state = MNWConnectionState.DISCONNECTED
        
        # 玩家状态
        self.player = MNWPlayerState()
        
        # 事件系统
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._running = False
        
        # 房间信息
        self.room_id: Optional[str] = None
        self.world_data: Optional[Dict] = None
        
        logger.info(f"MCPMiniWorldClient 初始化: {auth.config.uin}")
    
    async def connect(self) -> bool:
        """连接到游戏服务器"""
        if self.state != MNWConnectionState.DISCONNECTED:
            logger.warning(f"当前状态 {self.state.name}")
            return False
        
        try:
            # 获取游戏服务器地址 (从登录响应)
            if not self.auth.is_authenticated:
                logger.error("未登录，无法连接")
                return False
            
            # TODO: 从 auth 获取游戏服务器地址
            game_host = self.server.game_host or "game.mini1.cn"
            game_port = self.server.game_port or 20000
            
            logger.info(f"连接到游戏服务器 {game_host}:{game_port}...")
            self.state = MNWConnectionState.CONNECTING
            
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(game_host, game_port),
                timeout=10.0
            )
            
            self.state = MNWConnectionState.CONNECTED
            logger.info("✓ 游戏服务器连接成功")
            
            await self._trigger_event("connect")
            return True
            
        except Exception as e:
            logger.exception(f"连接失败: {e}")
            self.state = MNWConnectionState.DISCONNECTED
            return False
    
    async def login(self) -> bool:
        """执行登录"""
        if self.auth.is_authenticated:
            logger.info("已登录，跳过")
            self.player.uin = self.auth.uin
            self.player.name = self.auth.name
            return True
        
        return await self.auth.login()
    
    async def enter_room(self, room_id: str) -> bool:
        """
        进入房间
        
        Args:
            room_id: 房间ID
        """
        logger.info(f"进入房间: {room_id}")
        self.room_id = room_id
        
        # TODO: 发送进入房间请求
        
        self.state = MNWConnectionState.IN_GAME
        await self._trigger_event("enter_room", {"room_id": room_id})
        
        return True
    
    async def run(self):
        """主循环"""
        if not self.reader:
            logger.error("未连接")
            return
        
        self._running = True
        logger.info("开始主循环...")
        
        try:
            while self._running:
                try:
                    # 读取数据
                    data = await asyncio.wait_for(
                        self.reader.read(4096),
                        timeout=0.1
                    )
                    
                    if data:
                        await self._handle_data(data)
                        
                except asyncio.TimeoutError:
                    # 发送心跳
                    await self._send_heartbeat()
                    
                except Exception as e:
                    logger.error(f"处理错误: {e}")
                    break
                    
        except Exception as e:
            logger.exception(f"主循环错误: {e}")
        finally:
            await self.disconnect()
    
    async def _handle_data(self, data: bytes):
        """处理接收到的数据"""
        # TODO: 解析 MiniWorld 协议
        await self._trigger_event("data", {"raw": data})
    
    async def _send_heartbeat(self):
        """发送心跳"""
        # TODO: 实现心跳
        pass
    
    async def disconnect(self):
        """断开连接"""
        if self.state == MNWConnectionState.DISCONNECTED:
            return
        
        logger.info("断开连接")
        self._running = False
        self.state = MNWConnectionState.DISCONNECTING
        
        await self._trigger_event("disconnect")
        
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass
        
        self.state = MNWConnectionState.DISCONNECTED
    
    # 事件系统
    def on(self, event: str, handler: Optional[Callable] = None):
        """注册事件处理器"""
        def decorator(func):
            if event not in self._event_handlers:
                self._event_handlers[event] = []
            self._event_handlers[event].append(func)
            return func
        
        if handler:
            return decorator(handler)
        return decorator
    
    async def _trigger_event(self, event: str, *args, **kwargs):
        """触发事件"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(*args, **kwargs)
                else:
                    handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"事件错误 ({event}): {e}")
    
    # 玩家控制
    async def move(self, x: float, y: float, z: float, yaw: float = 0, pitch: float = 0):
        """移动玩家"""
        self.player.position = (x, y, z)
        self.player.rotation = (yaw, pitch)
        # TODO: 发送移动数据包
    
    async def place_block(self, x: int, y: int, z: int, block_id: int):
        """放置方块"""
        logger.debug(f"放置方块: {block_id} at ({x}, {y}, {z})")
        # TODO: 发送放置方块请求
    
    async def break_block(self, x: int, y: int, z: int):
        """破坏方块"""
        logger.debug(f"破坏方块: ({x}, {y}, {z})")
        # TODO: 发送破坏方块请求
    
    async def chat(self, message: str):
        """发送聊天消息"""
        logger.info(f"发送聊天: {message}")
        # TODO: 发送聊天数据包
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self.state in (MNWConnectionState.CONNECTED, MNWConnectionState.IN_GAME)
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "state": self.state.name,
            "uin": self.player.uin,
            "name": self.player.name,
            "room_id": self.room_id,
            "position": self.player.position
        }