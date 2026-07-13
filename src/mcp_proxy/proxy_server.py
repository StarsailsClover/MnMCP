"""
MnMCP v3 - 双向代理服务器 (ProxyServerV2)
实现 MiniWorld <-> Minecraft JE 双向实时桥接

架构:
  MiniWorld Client (RakNet)
      ↕
  ProxyServerV2 (本模块)
      ↕
  MCPMinecraftClient (TCP)
      ↕
  MC JE Server (with Geyser -> MC BE)

功能:
- 接受 MiniWorld 客户端 RakNet 连接
- 为每个客户端创建 MC JE 连接
- 双向数据包转换与转发
- 登录/认证流程管理
- 位置同步（双向）
- 聊天消息桥接
- 方块交互同步
- 心跳保持

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import asyncio
import json
import struct
import time
import zlib
import importlib
from typing import Optional, Dict, Any, Callable, List, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import logging
import sys
import os

from .gateway import MCPRakNetGateway, GatewayConfig, GatewayMode

from ..mcp_protocol.codec import MCPProtocolCodec, MCPPacket, PacketDirection
from ..mcp_protocol.msgcode_registry import MessageRegistry, get_message_name
from ..mcp_core.packet_converter import MCPPacketConverter, ConvertedPacket, PacketType
from ..mcp_mapping.blocks_full import mc_to_mnw, mnw_to_mc, convert_mc_block, convert_mnw_block, get_mc_block_name

logger = logging.getLogger(__name__)


class ProxyState(IntEnum):
    """代理状态"""
    STOPPED = 0
    STARTING = 1
    RUNNING = 2
    STOPPING = 3
    ERROR = 4


class ClientSessionState(IntEnum):
    """客户端会话状态"""
    DISCONNECTED = 0
    CONNECTED = 1
    AUTHENTICATED = 2
    IN_GAME = 3


@dataclass
class ClientSession:
    """
    客户端会话
    
    管理单个 MiniWorld 客户端到 MC 服务器的桥接状态
    """
    conn_id: str
    mnw_address: Tuple[str, int] = ("", 0)
    
    # MiniWorld 状态
    mnw_state: ClientSessionState = ClientSessionState.DISCONNECTED
    mnw_entity_id: int = 0
    mnw_uin: str = ""
    mnw_name: str = ""
    mnw_token: str = ""
    mnw_room_id: str = ""
    
    # MC 状态
    mc_state: ClientSessionState = ClientSessionState.DISCONNECTED
    mc_entity_id: int = 0
    mc_username: str = ""
    
    # 位置
    x: float = 0.0
    y: float = 64.0
    z: float = 0.0
    yaw: float = 0.0
    pitch: float = 0.0
    
    # 统计
    packets_mnw_to_mc: int = 0
    packets_mc_to_mnw: int = 0
    bytes_mnw_to_mc: int = 0
    bytes_mc_to_mnw: int = 0
    connected_at: float = 0.0
    
    # MC 客户端引用
    mc_client: Optional[Any] = None


@dataclass
class ProxyServerConfig:
    """代理服务器配置"""
    # RakNet 监听
    raknet_host: str = "0.0.0.0"
    raknet_port: int = 19132
    
    # MC 服务器
    mc_host: str = "127.0.0.1"
    mc_port: int = 25565
    mc_protocol: int = 766
    
    # 加密
    xxtea_key: Optional[bytes] = None
    
    # 性能
    max_clients: int = 10
    sync_interval: float = 0.05  # 20Hz
    idle_timeout: float = 300.0
    
    # 调试
    debug: bool = False
    log_packets: bool = False
    log_sync: bool = False


@dataclass
class ProxyStats:
    """代理统计"""
    started_at: float = 0.0
    connections_total: int = 0
    connections_active: int = 0
    packets_mnw_to_mc: int = 0
    packets_mc_to_mnw: int = 0
    bytes_mnw_to_mc: int = 0
    bytes_mc_to_mnw: int = 0
    chat_messages: int = 0
    position_syncs: int = 0
    block_updates: int = 0
    errors: int = 0


class MnMCPProxyServer:
    """
    MnMCP 双向代理服务器 (ProxyServerV2)
    
    核心功能:
    1. 启动 RakNet 网关，监听 MiniWorld 客户端连接
    2. 为每个 MiniWorld 客户端创建 MC JE 连接
    3. 双向数据包转换和转发
    4. 管理所有客户端会话
    
    使用示例:
        config = ProxyServerConfig(
            raknet_port=19132,
            mc_host="127.0.0.1",
            mc_port=25565
        )
        server = MnMCPProxyServer(config)
        await server.start()
        
        # 按 Ctrl+C 停止
        await server.stop()
    """
    
    def __init__(self, config: Optional[ProxyServerConfig] = None):
        self.config = config or ProxyServerConfig()
        self.stats = ProxyStats()
        
        # 状态
        self._state: ProxyState = ProxyState.STOPPED
        self._running = False
        
        # 网关
        self.gateway: Optional[MCPRakNetGateway] = None
        
        # 会话管理
        self.sessions: Dict[str, ClientSession] = {}
        
        # 编解码器
        self.codec = MCPProtocolCodec(self.config.xxtea_key)
        self.converter = MCPPacketConverter()
        self.registry = MessageRegistry()
        self._mini_proto: Optional[Any] = None
        self._mini_proto_loaded = False
        
        # 事件处理器
        self._event_handlers: Dict[str, List[Callable]] = {
            'started': [],
            'stopped': [],
            'client_connect': [],
            'client_disconnect': [],
            'client_login': [],
            'client_enter_game': [],
            'chat': [],
            'error': [],
        }
    
    # ============================================================
    # 生命周期
    # ============================================================
    
    async def start(self) -> bool:
        """启动代理服务器"""
        try:
            self._state = ProxyState.STARTING
            logger.info("=" * 60)
            logger.info("MnMCP ProxyServerV2 启动中...")
            logger.info("=" * 60)
            
            # 创建网关
            gw_config = GatewayConfig(
                host=self.config.raknet_host,
                port=self.config.raknet_port,
                mode=GatewayMode.BRIDGE,
                mc_host=self.config.mc_host,
                mc_port=self.config.mc_port,
                xxtea_key=self.config.xxtea_key,
                max_connections=self.config.max_clients
            )
            self.gateway = MCPRakNetGateway(gw_config)
            
            # 注册网关处理器
            self._register_gateway_handlers()
            
            # 启动网关
            await self.gateway.start()
            
            self._state = ProxyState.RUNNING
            self._running = True
            self.stats.started_at = time.time()
            
            logger.info(f"RakNet 网关: {self.config.raknet_host}:{self.config.raknet_port}")
            logger.info(f"MC 服务器: {self.config.mc_host}:{self.config.mc_port}")
            logger.info(f"最大客户端: {self.config.max_clients}")
            logger.info("=" * 60)
            logger.info("ProxyServerV2 启动完成!")
            logger.info("=" * 60)
            
            await self._trigger_event('started')
            
            return True
            
        except Exception as e:
            logger.error(f"启动失败: {e}")
            self._state = ProxyState.ERROR
            await self._trigger_event('error', e)
            return False
    
    async def stop(self) -> None:
        """停止代理服务器"""
        if self._state == ProxyState.STOPPED:
            return
        
        logger.info("停止 ProxyServerV2...")
        self._state = ProxyState.STOPPING
        self._running = False
        
        # 断开所有客户端
        for conn_id, session in list(self.sessions.items()):
            await self._disconnect_client(conn_id, "Server stopped")
        
        # 停止网关
        if self.gateway:
            await self.gateway.stop()
        
        self._state = ProxyState.STOPPED
        logger.info("ProxyServerV2 已停止")
        await self._trigger_event('stopped')
    
    def _register_gateway_handlers(self) -> None:
        """注册网关消息处理器"""
        if not self.gateway:
            return
        
        # 登录相关
        self.gateway.register_handler(901, self._handle_mnw_login)
        self.gateway.register_handler(1001, self._handle_mnw_enter_room)
        
        # 心跳
        self.gateway.register_handler(11, self._handle_mnw_heartbeat)
        
        # 聊天
        self.gateway.register_handler(301, self._handle_mnw_chat)
        self.gateway.register_handler(4010, self._handle_mnw_chat)
        
        # 移动
        self.gateway.register_handler(401, self._handle_mnw_move)
        self.gateway.register_handler(2001, self._handle_mnw_move)
        self.gateway.register_handler(2004, self._handle_mnw_move)
        self.gateway.register_handler(4047, self._handle_mnw_move)
        self.gateway.register_handler(4050, self._handle_mnw_move)
        
        # 方块
        self.gateway.register_handler(103, self._handle_mnw_block_update)
        self.gateway.register_handler(104, self._handle_mnw_block_update)
        self.gateway.register_handler(3001, self._handle_mnw_block_interact_end)
        self.gateway.register_handler(3002, self._handle_mnw_block_interact)
        self.gateway.register_handler(3003, self._handle_mnw_block_punch)
        self.gateway.register_handler(3004, self._handle_mnw_item_use)
        
        # 玩家动作
        self.gateway.register_handler(601, self._handle_mnw_player_action)
        
        # 使用物品
        self.gateway.register_handler(701, self._handle_mnw_use_item)
        
        # Ping
        self.gateway.register_handler(801, self._handle_mnw_ping)
    
    # ============================================================
    # 网关消息处理器
    # ============================================================
    
    async def _handle_mnw_login(self, conn: Any, packet: MCPPacket) -> None:
        """处理 MiniWorld 登录请求"""
        conn_id = self._get_conn_id(conn)
        logger.info(f"[{conn_id}] 登录请求")
        
        try:
            # 解析登录数据
            login_data = self._parse_packet_data(packet)
            
            # 创建会话
            session = ClientSession(
                conn_id=conn_id,
                mnw_address=conn.address if hasattr(conn, 'address') else ("", 0),
                mnw_state=ClientSessionState.CONNECTED,
                mnw_uin=login_data.get('uin', ''),
                mnw_name=login_data.get('name', f'Player_{conn_id[:8]}'),
                mnw_token=login_data.get('token', ''),
                connected_at=time.time()
            )
            self.sessions[conn_id] = session
            self.stats.connections_total += 1
            self.stats.connections_active = len(self.sessions)
            
            # 发送登录响应
            response = self.codec.create_packet(
                msg_code=902,
                data=json.dumps({
                    'code': 0,
                    'msg': 'success',
                    'uin': login_data.get('uin', ''),
                    'name': session.mnw_name,
                    'entity_id': 0,
                }).encode('utf-8'),
                direction=PacketDirection.SERVER_TO_CLIENT
            )
            await self.gateway.send_to_client(conn_id, response)
            
            session.mnw_state = ClientSessionState.AUTHENTICATED
            logger.info(f"[{conn_id}] 登录成功: {session.mnw_name}")
            
            await self._trigger_event('client_login', conn_id, session)
            
        except Exception as e:
            logger.error(f"[{conn_id}] 登录失败: {e}")
            self.stats.errors += 1
    
    async def _handle_mnw_enter_room(self, conn: Any, packet: MCPPacket) -> None:
        """处理进入房间请求 - 创建 MC 连接"""
        conn_id = self._get_conn_id(conn)
        session = self.sessions.get(conn_id)
        
        if not session:
            logger.warning(f"[{conn_id}] 未登录就尝试进入房间")
            return
        
        logger.info(f"[{conn_id}] 进入房间请求 -> 连接 MC 服务器")
        
        try:
            enter_data = self._parse_packet_data(packet)
            role_enter = self._parse_mnw_protobuf(packet)
            if role_enter:
                session.mnw_uin = str(getattr(role_enter, 'Uin', session.mnw_uin) or session.mnw_uin)
                role_info = getattr(role_enter, 'RoleInfo', None)
                nick_name = getattr(role_info, 'NickName', '') if role_info else ''
                if nick_name:
                    session.mnw_name = nick_name
            session.mnw_room_id = enter_data.get('room_id', '')
            
            # 创建 MC 客户端连接
            from ..mcp_mc.client import MCPMinecraftClient, MCClientConfig
            
            mc_username = f"MnMCP_{session.mnw_name[:8]}"
            mc_config = MCClientConfig(
                host=self.config.mc_host,
                port=self.config.mc_port,
                username=mc_username,
                protocol_version=self.config.mc_protocol,
                debug=self.config.debug
            )
            
            mc_client = MCPMinecraftClient(mc_config)
            session.mc_client = mc_client
            session.mc_username = mc_username
            
            # 注册 MC 事件
            self._register_mc_events(session, mc_client)
            
            # 连接 MC
            if not await mc_client.connect():
                logger.error(f"[{conn_id}] MC 连接失败")
                await self._send_mnw_error(conn_id, "MC connection failed")
                return
            
            # 登录 MC
            if not await mc_client.login():
                logger.error(f"[{conn_id}] MC 登录失败")
                await self._send_mnw_error(conn_id, "MC login failed")
                return
            
            session.mc_state = ClientSessionState.CONNECTED
            logger.info(f"[{conn_id}] MC 连接成功: {mc_username}")
            
            # 发送进入房间响应（暂用简单确认，完整 PB_RoleEnterWorldHC 在 MC join 后发送）
            response = self.codec.create_packet(
                msg_code=1002,
                data=self._build_mnw_enter_world_payload(
                    uin=int(session.mnw_uin) if session.mnw_uin.isdigit() else 0,
                    name=session.mnw_name,
                    x=0.0, y=64.0, z=0.0,
                    world_name="MnMCP Proxy"
                ),
                direction=PacketDirection.SERVER_TO_CLIENT
            )
            await self.gateway.send_to_client(conn_id, response)
            
            # 等待 MC join game 事件设置 mc_state
            # (异步处理，mc_state 在 _register_mc_events 中更新)
            
            await self._trigger_event('client_enter_game', conn_id, session)
            
        except Exception as e:
            logger.error(f"[{conn_id}] 进入房间失败: {e}")
            await self._send_mnw_error(conn_id, str(e))
            self.stats.errors += 1
    
    def _register_mc_events(self, session: ClientSession, mc_client: Any) -> None:
        """注册 MC 客户端事件回调"""
        conn_id = session.conn_id
        
        @mc_client.on('join')
        async def on_mc_join():
            session.mc_state = ClientSessionState.IN_GAME
            session.mc_entity_id = mc_client.player.entity_id
            logger.info(f"[{conn_id}] MC 进入游戏: entity_id={session.mc_entity_id}")
            
            # 通知 MiniWorld 客户端进入世界
            if self.gateway:
                enter_world = self.codec.create_packet(
                    msg_code=1002,
                    data=self._build_mnw_enter_world_payload(
                        uin=int(session.mnw_uin) if session.mnw_uin.isdigit() else session.mc_entity_id,
                        name=session.mnw_name,
                        x=mc_client.position.x,
                        y=mc_client.position.y,
                        z=mc_client.position.z,
                        world_name="MnMCP Proxy",
                        entity_id=session.mc_entity_id
                    ),
                    direction=PacketDirection.SERVER_TO_CLIENT
                )
                await self.gateway.send_to_client(conn_id, enter_world)
            
            session.mnw_state = ClientSessionState.IN_GAME
        
        @mc_client.on('chat')
        async def on_mc_chat(message, position):
            """MC 聊天 -> MNW 聊天"""
            self.stats.chat_messages += 1
            await self._forward_chat_mc_to_mnw(conn_id, message)
        
        @mc_client.on('position')
        async def on_mc_position(pos):
            """MC 位置 -> MNW 位置"""
            self.stats.position_syncs += 1
            await self._forward_position_mc_to_mnw(conn_id, pos)
        
        @mc_client.on('disconnect')
        async def on_mc_disconnect(reason):
            logger.info(f"[{conn_id}] MC 断开: {reason}")
            await self._disconnect_client(conn_id, f"MC: {reason}")
    
    async def _handle_mnw_heartbeat(self, conn: Any, packet: MCPPacket) -> None:
        """处理心跳"""
        conn_id = self._get_conn_id(conn)
        
        # 直接回复心跳
        response = self.codec.create_packet(
            msg_code=12,
            data=packet.data,
            direction=PacketDirection.SERVER_TO_CLIENT
        )
        await self.gateway.send_to_client(conn_id, response)
    
    async def _handle_mnw_chat(self, conn: Any, packet: MCPPacket) -> None:
        """处理 MiniWorld 聊天 -> MC"""
        conn_id = self._get_conn_id(conn)
        session = self.sessions.get(conn_id)
        
        if not session or not session.mc_client:
            return
        
        try:
            chat_data = self._parse_packet_data(packet)
            chat_msg = self._parse_mnw_protobuf(packet)
            message = getattr(chat_msg, 'Content', '') if chat_msg else ''
            if not message:
                message = chat_data.get('Content', '') or chat_data.get('message', '') or chat_data.get('text', '')
            sender = session.mnw_name
            
            if message:
                await session.mc_client.send_chat(f"[MNW] {sender}: {message}")
                self.stats.chat_messages += 1
                self.stats.packets_mnw_to_mc += 1
                
                if self.config.log_packets:
                    logger.debug(f"[{conn_id}] MNW Chat -> MC: {sender}: {message[:50]}")
                    
        except Exception as e:
            logger.error(f"[{conn_id}] 聊天转发失败: {e}")
    
    async def _handle_mnw_move(self, conn: Any, packet: MCPPacket) -> None:
        """处理 MiniWorld 移动 -> MC"""
        conn_id = self._get_conn_id(conn)
        session = self.sessions.get(conn_id)
        
        if not session or not session.mc_client or not session.mc_client.is_in_game:
            return
        
        try:
            move_data = self._parse_packet_data(packet)
            move_msg = self._parse_mnw_protobuf(packet)
            
            if move_msg and hasattr(move_msg, 'pos'):
                x = -float(move_msg.pos.X) / 100.0
                y = float(move_msg.pos.Y) / 100.0
                z = float(move_msg.pos.Z) / 100.0
                yaw = session.yaw
                pitch = session.pitch
                if hasattr(move_msg, 'HasField') and move_msg.HasField('move_opera'):
                    yaw = float(getattr(move_msg.move_opera, 'yaw', session.yaw))
                    pitch = float(getattr(move_msg.move_opera, 'pitch', session.pitch))
            else:
                x = float(move_data.get('x', session.x))
                y = float(move_data.get('y', session.y))
                z = float(move_data.get('z', session.z))
                yaw = float(move_data.get('yaw', session.yaw))
                pitch = float(move_data.get('pitch', session.pitch))
            
            # 更新会话位置
            session.x, session.y, session.z = x, y, z
            session.yaw, session.pitch = yaw, pitch
            
            # MNW Yaw -> MC Yaw
            mc_yaw = self._mnw_yaw_to_mc(yaw)
            
            # 发送到 MC
            await session.mc_client.update_position(
                x=x, y=y, z=z,
                yaw=mc_yaw, pitch=pitch,
                on_ground=True
            )
            
            self.stats.packets_mnw_to_mc += 1
            self.stats.position_syncs += 1
            
            if self.config.log_sync:
                logger.debug(f"[{conn_id}] MNW Move -> MC: ({x:.1f}, {y:.1f}, {z:.1f})")
                
        except Exception as e:
            logger.error(f"[{conn_id}] 移动转发失败: {e}")
    
    async def _handle_mnw_block_interact(self, conn: Any, packet: MCPPacket) -> None:
        """处理方块交互（放置/右键）"""
        conn_id = self._get_conn_id(conn)
        session = self.sessions.get(conn_id)
        
        if not session or not session.mc_client or not session.mc_client.is_in_game:
            return
        
        try:
            interact_msg = self._parse_mnw_protobuf(packet)
            
            if interact_msg and hasattr(interact_msg, 'blockpos'):
                blockpos = interact_msg.blockpos
                x = -int(blockpos.X / 100) - 1
                y = int(blockpos.Y / 100)
                z = int(blockpos.Z / 100)
                face = getattr(interact_msg, 'face', 0)
                mc_face = self._mnw_face_to_mc(int(face))
                
                if self.config.debug:
                    logger.debug(f"[{conn_id}] BlockInteract: ({x}, {y}, {z}), face={face} -> mc_face={mc_face}")
                
                mc_block_name = self._mnw_block_to_mc_command_name(0, 1)
                await session.mc_client.send_chat(f"/setblock {x} {y} {z} {mc_block_name}")
            else:
                block_data = self._parse_packet_data(packet)
                x = int(block_data.get('x', 0))
                y = int(block_data.get('y', 0))
                z = int(block_data.get('z', 0))
                action = int(block_data.get('action', 1))
                
                mc_block_name = self._mnw_block_to_mc_command_name(0, action)
                await session.mc_client.send_chat(f"/setblock {x} {y} {z} {mc_block_name}")
            
            self.stats.block_updates += 1
            self.stats.packets_mnw_to_mc += 1
            
        except Exception as e:
            logger.error(f"[{conn_id}] 方块交互失败: {e}")
    
    async def _handle_mnw_block_punch(self, conn: Any, packet: MCPPacket) -> None:
        """处理方块挖掘（破坏/左键）"""
        conn_id = self._get_conn_id(conn)
        session = self.sessions.get(conn_id)
        
        if not session or not session.mc_client or not session.mc_client.is_in_game:
            return
        
        try:
            punch_msg = self._parse_mnw_protobuf(packet)
            
            if punch_msg and hasattr(punch_msg, 'blockpos'):
                blockpos = punch_msg.blockpos
                x = -int(blockpos.X / 100) - 1
                y = int(blockpos.Y / 100)
                z = int(blockpos.Z / 100)
                status = int(getattr(punch_msg, 'status', 0))
                
                if status == 0 or status == 2:
                    mc_block_name = "minecraft:air"
                    await session.mc_client.send_chat(f"/setblock {x} {y} {z} {mc_block_name}")
            else:
                block_data = self._parse_packet_data(packet)
                x = int(block_data.get('x', 0))
                y = int(block_data.get('y', 0))
                z = int(block_data.get('z', 0))
                
                mc_block_name = "minecraft:air"
                await session.mc_client.send_chat(f"/setblock {x} {y} {z} {mc_block_name}")
            
            self.stats.block_updates += 1
            self.stats.packets_mnw_to_mc += 1
            
        except Exception as e:
            logger.error(f"[{conn_id}] 方块挖掘失败: {e}")
    
    async def _handle_mnw_item_use(self, conn: Any, packet: MCPPacket) -> None:
        """处理物品使用"""
        conn_id = self._get_conn_id(conn)
        session = self.sessions.get(conn_id)
        
        if not session or not session.mc_client or not session.mc_client.is_in_game:
            return
        
        try:
            item_msg = self._parse_mnw_protobuf(packet)
            
            if item_msg and self.config.debug:
                item_id = getattr(item_msg, 'itemid', 0)
                status = getattr(item_msg, 'status', 0)
                logger.debug(f"[{conn_id}] ItemUse: item_id={item_id}, status={status}")
            
            self.stats.packets_mnw_to_mc += 1
            
        except Exception as e:
            logger.error(f"[{conn_id}] 物品使用失败: {e}")
    
    async def _handle_mnw_block_interact_end(self, conn: Any, packet: MCPPacket) -> None:
        """处理方块交互结束"""
        conn_id = self._get_conn_id(conn)
        if self.config.debug:
            logger.debug(f"[{conn_id}] BlockInteractEnd")
    
    async def _handle_mnw_block_update(self, conn: Any, packet: MCPPacket) -> None:
        """处理服务端方块更新（HC）"""
        conn_id = self._get_conn_id(conn)
        if self.config.debug:
            logger.debug(f"[{conn_id}] BlockUpdate (HC): msg_code={packet.msg_code}")

    def _mnw_face_to_mc(self, mnw_face: int) -> int:
        """MNW 面 -> MC 面"""
        face_map = {0: 5, 1: 4, 2: 2, 3: 3, 4: 0, 5: 1}
        return face_map.get(mnw_face, 1)
    
    def _mc_face_to_mnw(self, mc_face: int) -> int:
        """MC 面 -> MNW 面"""
        face_map = {0: 4, 1: 5, 2: 2, 3: 3, 4: 1, 5: 0}
        return face_map.get(mc_face, 0)

    def _mnw_block_to_mc_command_name(self, mnw_block_id: int, action: int = 1) -> str:
        """转换 MNW 方块为 MC setblock 名称"""
        if action == 0 or mnw_block_id == 0:
            return "minecraft:air"

        mapping = mnw_to_mc(mnw_block_id)
        if not mapping:
            return "minecraft:air"

        mc_id, mc_name, _ = mapping
        if mc_name and mc_name != "unknown":
            return mc_name if mc_name.startswith("minecraft:") else f"minecraft:{mc_name}"

        fallback = get_mc_block_name(mc_id)
        if fallback and not fallback.startswith("unknown_"):
            return fallback if fallback.startswith("minecraft:") else f"minecraft:{fallback}"
        return "minecraft:stone"
    
    async def _handle_mnw_player_action(self, conn: Any, packet: MCPPacket) -> None:
        """处理玩家动作"""
        conn_id = self._get_conn_id(conn)
        # TODO: 实现具体的玩家动作转换
        if self.config.debug:
            logger.debug(f"[{conn_id}] Player action: {packet.msg_code}")
    
    async def _handle_mnw_use_item(self, conn: Any, packet: MCPPacket) -> None:
        """处理使用物品"""
        conn_id = self._get_conn_id(conn)
        # TODO: 实现物品使用转换
        if self.config.debug:
            logger.debug(f"[{conn_id}] Use item: {packet.msg_code}")
    
    async def _handle_mnw_ping(self, conn: Any, packet: MCPPacket) -> None:
        """处理 Ping"""
        conn_id = self._get_conn_id(conn)
        response = self.codec.create_packet(
            msg_code=802,
            data=packet.data,
            direction=PacketDirection.SERVER_TO_CLIENT
        )
        await self.gateway.send_to_client(conn_id, response)
    
    # ============================================================
    # 转发函数
    # ============================================================
    
    async def _forward_chat_mc_to_mnw(self, conn_id: str, message: str) -> None:
        """转发 MC 聊天到 MNW"""
        try:
            # 提取文本
            text = message
            if isinstance(message, str):
                try:
                    parsed = json.loads(message)
                    if isinstance(parsed, dict):
                        text = parsed.get('text', message)
                        # 处理 extra 数组
                        if 'extra' in parsed:
                            for extra in parsed['extra']:
                                if isinstance(extra, dict):
                                    text += extra.get('text', '')
                except (json.JSONDecodeError, TypeError):
                    pass
            
            chat_packet = self.codec.create_packet(
                msg_code=4011,
                data=self._build_mnw_chat_payload('MC', text),
                direction=PacketDirection.SERVER_TO_CLIENT
            )
            await self.gateway.send_to_client(conn_id, chat_packet)
            self.stats.packets_mc_to_mnw += 1
            
        except Exception as e:
            logger.error(f"[{conn_id}] MC->MNW 聊天转发失败: {e}")
    
    async def _forward_position_mc_to_mnw(self, conn_id: str, pos) -> None:
        """转发 MC 位置到 MNW"""
        session = self.sessions.get(conn_id)
        if not session:
            return
        
        try:
            mnw_yaw = self._mc_yaw_to_mnw(pos.yaw)
            
            move_packet = self.codec.create_packet(
                msg_code=4048,
                data=self._build_mnw_move_payload(session.mnw_entity_id, pos.x, pos.y, pos.z),
                direction=PacketDirection.SERVER_TO_CLIENT
            )
            await self.gateway.send_to_client(conn_id, move_packet)
            self.stats.packets_mc_to_mnw += 1
            
        except Exception as e:
            logger.error(f"[{conn_id}] MC->MNW 位置转发失败: {e}")
    
    # ============================================================
    # 工具函数
    # ============================================================
    
    def _get_conn_id(self, conn: Any) -> str:
        """获取连接 ID"""
        if hasattr(conn, 'address'):
            return f"{conn.address[0]}:{conn.address[1]}"
        return str(id(conn))
    
    def _parse_packet_data(self, packet: MCPPacket) -> Dict[str, Any]:
        """解析数据包数据"""
        if not packet.data:
            return {}
        
        try:
            proto_msg = self._parse_mnw_protobuf(packet)
            if proto_msg:
                return self._protobuf_to_dict(proto_msg)

            # 尝试 protobuf
            try:
                import blackboxprotobuf
                decoded, _ = blackboxprotobuf.decode_message(packet.data)
                return decoded if isinstance(decoded, dict) else {}
            except ImportError:
                pass
            
            # 尝试 JSON
            return json.loads(packet.data.decode('utf-8', errors='replace'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {'raw': packet.data.hex()}

    def _load_mini_proto(self) -> Optional[Any]:
        if self._mini_proto_loaded:
            return self._mini_proto
        self._mini_proto_loaded = True
        try:
            import mnmcp.mini.proto as proto
            self._mini_proto = proto
            return proto
        except ImportError:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            proto_root = os.path.join(root, 'MnMCP-Protocol', 'MnMCP')
            if os.path.isdir(proto_root) and proto_root not in sys.path:
                sys.path.insert(0, proto_root)
            try:
                self._mini_proto = importlib.import_module('mnmcp.mini.proto')
                return self._mini_proto
            except Exception as e:
                logger.debug(f"MiniWorld protobuf unavailable: {e}")
                return None

    def _parse_mnw_protobuf(self, packet: MCPPacket) -> Optional[Any]:
        proto = self._load_mini_proto()
        if not proto:
            return None
        msg_name = self.registry.get_name(packet.msg_code)
        if not msg_name:
            return None
        module = getattr(proto, 'ch', None) if msg_name.endswith('CH') else getattr(proto, 'hc', None)
        message_class = getattr(module, msg_name, None) if module else None
        if not message_class:
            return None
        try:
            msg = message_class()
            msg.ParseFromString(packet.data)
            return msg
        except Exception as e:
            if self.config.debug:
                logger.debug(f"Protobuf parse failed for {packet.msg_code} {msg_name}: {e}")
            return None

    def _protobuf_to_dict(self, msg: Any) -> Dict[str, Any]:
        try:
            from google.protobuf.json_format import MessageToDict
            return MessageToDict(msg, preserving_proto_field_name=True)
        except Exception:
            return {}

    def _build_mnw_chat_payload(self, speaker: str, text: str) -> bytes:
        proto = self._load_mini_proto()
        if proto and hasattr(proto, 'hc'):
            message_class = getattr(proto.hc, 'PB_ChatHC', None)
            if message_class:
                return message_class(ChatType=0, Uin=0, Speaker=speaker, Content=text, Language=1, Extend='{"buddle":1}').SerializeToString()
        return json.dumps({'sender': speaker, 'message': text, 'timestamp': int(time.time())}).encode('utf-8')

    def _build_mnw_move_payload(self, entity_id: int, x: float, y: float, z: float) -> bytes:
        proto = self._load_mini_proto()
        if proto and hasattr(proto, 'hc') and hasattr(proto, 'common'):
            message_class = getattr(proto.hc, 'PB_MoveSyncHC', None)
            vector_class = getattr(proto.common, 'PB_Vector3', None)
            vectorf_class = getattr(proto.common, 'PB_Vector3f', None)
            if message_class and vector_class and vectorf_class:
                return message_class(
                    id=int(entity_id),
                    accept=True,
                    pos=vector_class(X=-int(x * 100), Y=int(y * 100), Z=int(z * 100)),
                    motion=vectorf_class(X=0.0, Y=0.0, Z=0.0)
                ).SerializeToString()
        return json.dumps({'entity_id': entity_id, 'x': x, 'y': y, 'z': z}).encode('utf-8')

    def _build_mnw_enter_world_payload(
        self,
        uin: int,
        name: str,
        x: float,
        y: float,
        z: float,
        world_name: str = "MnMCP",
        entity_id: int = 0
    ) -> bytes:
        proto = self._load_mini_proto()
        if not proto or not hasattr(proto, 'hc') or not hasattr(proto, 'common'):
            return json.dumps({
                'code': 0,
                'msg': 'success',
                'uin': uin,
                'entity_id': entity_id,
                'spawn_x': x,
                'spawn_y': y,
                'spawn_z': z,
            }).encode('utf-8')

        try:
            common = proto.common
            hc = proto.hc

            enter_world_class = getattr(hc, 'PB_RoleEnterWorldHC', None)
            player_info_class = getattr(common, 'PB_PlayerInfo', None)
            role_data_class = getattr(common, 'PB_RoleData', None)
            pos_class = getattr(common, 'PB_Pos', None)
            body_dir_class = getattr(common, 'PB_BodyDir', None)
            vector3_class = getattr(common, 'PB_Vector3', None)
            vector3f_class = getattr(common, 'PB_Vector3f', None)
            role_package_class = getattr(common, 'PB_RolePackage', None)
            shortcut_pak_class = getattr(common, 'PB_ShortcutPak', None)
            item_grid_class = getattr(common, 'PB_ItemGrid', None)
            item_grid_data_class = getattr(common, 'PB_ItemGridData', None)
            item_class = getattr(common, 'PB_Item', None)
            buff_list_class = getattr(common, 'PB_ActorBuffList', None)
            ow_global_class = getattr(common, 'PB_OWGlobal', None)
            ow_global_misc_class = getattr(common, 'PB_OWGlobalMisc', None)
            world_desc_class = getattr(common, 'PB_WorldDesc', None)
            world_create_data_class = getattr(common, 'PB_WorldCreateData', None)
            skill_cd_data_class = getattr(common, 'PB_SkillCDData', None)

            if not all([
                enter_world_class, player_info_class, role_data_class,
                pos_class, body_dir_class, vector3_class, vector3f_class,
                role_package_class, shortcut_pak_class, item_grid_class,
                item_grid_data_class, item_class, buff_list_class,
                ow_global_class, ow_global_misc_class, world_desc_class,
                world_create_data_class, skill_cd_data_class
            ]):
                return json.dumps({
                    'code': 0, 'msg': 'success', 'uin': uin,
                    'entity_id': entity_id, 'spawn_x': x, 'spawn_y': y, 'spawn_z': z,
                }).encode('utf-8')

            pos_int_x = -int(x * 100)
            pos_int_y = int(y * 100)
            pos_int_z = int(z * 100)
            uin_val = uin if uin != 0 else (entity_id if entity_id != 0 else 10000)

            role_data = role_data_class(
                Uin=uin_val,
                OWID=10213705870553,
                HP=100.0,
                Oxygen=10,
                FoodLevel=100,
                FoodSatLevel=100,
                UsedStamina=0,
                Exp=0,
                Level=1,
                LastLoginTime=int(time.time()),
                LoginNum=1,
                FallDist=0.0,
                Flags=0,
                LiveTicks=0,
                RideActorID=0,
                Pos=pos_class(X=pos_int_x, Y=pos_int_y, Z=pos_int_z, Map=0),
                Dir=body_dir_class(
                    RotationYaw=0.0,
                    RotationPitch=0.0,
                    Motion=vector3_class(X=0, Y=0, Z=0)
                ),
                Package=role_package_class(
                    ShortcutPak=shortcut_pak_class(
                        HandIdx=0,
                        Grids=[
                            item_grid_class(
                                ItemGridData=item_grid_data_class(
                                    Item=item_class(DefID=100)
                                )
                            )
                        ]
                    )
                ),
                Buff=buff_list_class(),
                CarringActorID=0,
                STRENGTH=100.0,
                ENABLE_STRENGTH=False,
                max_strength=100.0,
                Armor=0.0,
                Perseverance=0.0,
                MaxHP=100.0,
                StrengthFoodShowState=1,
                StarDebuffStage=0,
                StarDebuffTime=0,
                CanThrow=False,
            )

            player_info = player_info_class(
                ObjID=uin_val,
                anim=0,
                anim1=-1,
                RoleData=role_data,
                BodyColor=0,
                customscale=1.0,
                actSeqId=-1,
                animweapon=-1,
                scale=vector3f_class(X=1.0, Y=1.0, Z=1.0),
            )

            global_info = ow_global_class(
                OWID=10213705870553,
                ID=0,
                Uin=uin_val,
                SvrStart=4049,
                GridChgNum=0,
                Misc=ow_global_misc_class(
                    GlobalFlag=4512,
                    ChunkVer=0,
                    ChunkVerBroadCast=0,
                    InitPos=pos_class(X=pos_int_x, Y=pos_int_y, Z=pos_int_z, Map=0),
                    RevicePos=pos_class(X=pos_int_x, Y=pos_int_y, Z=pos_int_z, Map=0),
                ),
            )

            world_desc = world_desc_class(
                WorldId=10213705870553,
                WorldType=1,
                OwnerUin=273640665,
                CreateData=world_create_data_class(
                    TerrType=0,
                    RandSeed1=0,
                    RandSeed2=0,
                    RoleModel=0,
                    SeedStr="",
                    TilesX=0,
                    TilesZ=0,
                ),
                FromOWID=10213705870553,
                RealOwnerUin=273640665,
                WorldOpen=2,
                WorldName=world_name,
                TempType=0,
                pwid=0,
                SpecialType=0,
                editorSceneSwitch=1,
                ctype=1,
                extraInfo='{"editSceneSw": 1,"modpacksDesc": "{}","openCode": 5}',
            )

            enter_world = enter_world_class(
                Uin=uin_val,
                PlayerInfo=player_info,
                GlobalInfo=global_info,
                WorldDesc=world_desc,
                SkillCDData=skill_cd_data_class(NumSkillCD=0),
                HasRole=False,
                TeleportMsg="",
                ActorSyncFrequency=4,
            )

            return enter_world.SerializeToString()

        except Exception as e:
            if self.config.debug:
                logger.debug(f"Build enter_world protobuf failed: {e}")
            return json.dumps({
                'code': 0, 'msg': 'success', 'uin': uin,
                'entity_id': entity_id, 'spawn_x': x, 'spawn_y': y, 'spawn_z': z,
            }).encode('utf-8')
    
    async def _send_mnw_error(self, conn_id: str, message: str) -> None:
        """发送错误消息到 MiniWorld 客户端"""
        if not self.gateway:
            return
        
        try:
            error_packet = self.codec.create_packet(
                msg_code=902,
                data=json.dumps({
                    'code': -1,
                    'msg': message,
                }).encode('utf-8'),
                direction=PacketDirection.SERVER_TO_CLIENT
            )
            await self.gateway.send_to_client(conn_id, error_packet)
        except Exception as e:
            logger.error(f"发送错误消息失败: {e}")
    
    async def _disconnect_client(self, conn_id: str, reason: str = "") -> None:
        """断开客户端"""
        session = self.sessions.pop(conn_id, None)
        
        if session:
            # 断开 MC
            if session.mc_client:
                await session.mc_client.disconnect(reason)
                session.mc_client = None
            
            self.stats.connections_active = len(self.sessions)
            logger.info(f"[{conn_id}] 客户端断开: {reason}")
            await self._trigger_event('client_disconnect', conn_id, reason)
    
    def _mc_yaw_to_mnw(self, mc_yaw: float) -> float:
        """MC Yaw -> MNW Yaw"""
        return (mc_yaw + 180) % 360
    
    def _mnw_yaw_to_mc(self, mnw_yaw: float) -> float:
        """MNW Yaw -> MC Yaw"""
        mc_yaw = (mnw_yaw - 180) % 360
        if mc_yaw >= 180:
            mc_yaw -= 360
        return mc_yaw
    
    # ============================================================
    # 事件系统
    # ============================================================
    
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
                logger.error(f"事件处理器 {event} 错误: {e}")
    
    # ============================================================
    # 状态查询
    # ============================================================
    
    @property
    def state(self) -> ProxyState:
        return self._state
    
    @property
    def is_running(self) -> bool:
        return self._running and self._state == ProxyState.RUNNING
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        runtime = time.time() - self.stats.started_at if self.stats.started_at else 0
        
        return {
            'state': self._state.name,
            'runtime': f"{runtime:.1f}s",
            'connections_total': self.stats.connections_total,
            'connections_active': self.stats.connections_active,
            'sessions': len(self.sessions),
            'packets_mnw_to_mc': self.stats.packets_mnw_to_mc,
            'packets_mc_to_mnw': self.stats.packets_mc_to_mnw,
            'chat_messages': self.stats.chat_messages,
            'position_syncs': self.stats.position_syncs,
            'block_updates': self.stats.block_updates,
            'errors': self.stats.errors,
            'raknet': f"{self.config.raknet_host}:{self.config.raknet_port}",
            'mc': f"{self.config.mc_host}:{self.config.mc_port}",
        }
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """获取活跃会话列表"""
        result = []
        for conn_id, session in self.sessions.items():
            result.append({
                'conn_id': conn_id,
                'mnw_name': session.mnw_name,
                'mnw_state': session.mnw_state.name,
                'mc_username': session.mc_username,
                'mc_state': session.mc_state.name,
                'position': f"({session.x:.1f}, {session.y:.1f}, {session.z:.1f})",
                'packets_mnw_to_mc': session.packets_mnw_to_mc,
                'packets_mc_to_mnw': session.packets_mc_to_mnw,
                'connected_for': f"{time.time() - session.connected_at:.0f}s",
            })
        return result


# ============================================================
# 便捷函数
# ============================================================

async def create_proxy_server(
    raknet_host: str = "0.0.0.0",
    raknet_port: int = 19132,
    mc_host: str = "127.0.0.1",
    mc_port: int = 25565,
    debug: bool = False
) -> MnMCPProxyServer:
    """快速创建代理服务器"""
    config = ProxyServerConfig(
        raknet_host=raknet_host,
        raknet_port=raknet_port,
        mc_host=mc_host,
        mc_port=mc_port,
        debug=debug
    )
    return MnMCPProxyServer(config)


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MnMCP v3 - ProxyServerV2 测试")
    print("=" * 60)
    
    async def test():
        config = ProxyServerConfig(
            raknet_host="127.0.0.1",
            raknet_port=19132,
            mc_host="127.0.0.1",
            mc_port=25565,
            debug=True
        )
        
        server = MnMCPProxyServer(config)
        
        @server.on('started')
        async def on_started():
            print("  [EVENT] 服务器已启动")
        
        @server.on('client_connect')
        async def on_client_connect(conn_id, session):
            print(f"  [EVENT] 客户端连接: {conn_id}")
        
        @server.on('client_login')
        async def on_client_login(conn_id, session):
            print(f"  [EVENT] 客户端登录: {session.mnw_name}")
        
        @server.on('stopped')
        async def on_stopped():
            print("  [EVENT] 服务器已停止")
        
        print("\n启动代理服务器...")
        started = await server.start()
        
        if started:
            print("✓ 代理服务器启动成功!")
            print(f"\n统计信息:")
            stats = server.get_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
            print("\n运行中 (按 Ctrl+C 停止)...")
            try:
                await asyncio.sleep(5)
            except KeyboardInterrupt:
                pass
            
            await server.stop()
        else:
            print("✗ 代理服务器启动失败 (预期，需要 aiorak 和 MC 服务器)")
        
        print("\n✓ ProxyServerV2 测试完成")
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        pass
