"""
MnMCP v3 - RakNet 网关模块
整合 MN2MC 和 MnMCP-MN2MC 的长处
GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import asyncio
import struct
from typing import Optional, Dict, Any, Callable, Set
from dataclasses import dataclass
from enum import Enum
import logging

try:
    import aiorak
    from aiorak import Connection, ConnectionState, Reliability, Priority
    AIORAK_AVAILABLE = True
except ImportError:
    AIORAK_AVAILABLE = False
    Connection = None
    ConnectionState = None
    Reliability = None
    Priority = None

from ..mcp_protocol.codec import MCPProtocolCodec, MCPPacket, PacketDirection
from ..mcp_protocol.msgcode_registry import MessageRegistry, get_message_name

logger = logging.getLogger(__name__)


class GatewayMode(Enum):
    """网关模式"""
    STANDALONE = "standalone"      # 独立模式（创建房间）
    BRIDGE = "bridge"              # 桥接模式（转发到MC）
    PROXY = "proxy"                # 代理模式（透传到真实MNW）


@dataclass
class GatewayConfig:
    """网关配置"""
    host: str = "0.0.0.0"
    port: int = 19132
    mode: GatewayMode = GatewayMode.BRIDGE
    
    # MC 服务器配置（桥接模式）
    mc_host: str = "127.0.0.1"
    mc_port: int = 25565
    
    # 真实 MNW 服务器（代理模式）
    mnw_host: str = ""
    mnw_port: int = 0
    
    # 加密
    xxtea_key: Optional[bytes] = None
    
    # 性能
    max_connections: int = 100
    connection_timeout: float = 30.0


class MCPRakNetGateway:
    """
    MnMCP RakNet 网关
    
    功能:
    1. 接收 MiniWorld 客户端连接
    2. 处理 MiniWorld 协议
    3. 模式选择:
       - STANDALONE: 创建本地房间
       - BRIDGE: 桥接到 Minecraft
       - PROXY: 透传到真实 MiniWorld
    
    移植整合:
    - MN2MC 的协议处理能力
    - MnMCP-MN2MC 的网关架构
    - MnMCP v3 的代码质量
    """
    
    def __init__(self, config: Optional[GatewayConfig] = None):
        """
        初始化网关
        
        Args:
            config: 网关配置
        """
        self.config = config or GatewayConfig()
        self.codec = MCPProtocolCodec(self.config.xxtea_key)
        self.registry = MessageRegistry()
        
        # 服务器
        self.server: Optional[Any] = None
        self._running = False
        
        # 连接管理
        self.connections: Dict[str, Any] = {}
        self._handlers: Dict[int, Callable] = {}
        
        # 统计
        self.stats = {
            'connections_total': 0,
            'connections_active': 0,
            'packets_received': 0,
            'packets_sent': 0,
            'bytes_received': 0,
            'bytes_sent': 0,
        }
    
    async def start(self) -> None:
        """启动网关"""
        try:
            if not AIORAK_AVAILABLE:
                raise RuntimeError("aiorak is required for RakNet gateway")

            self.server = await aiorak.start_server(
                host=self.config.host,
                port=self.config.port,
                on_connect=self._on_connect,
                on_disconnect=self._on_disconnect,
                on_data=self._on_data
            )
            
            self._running = True
            
            logger.info(
                f"RakNet Gateway started on {self.config.host}:{self.config.port}"
            )
            logger.info(f"Mode: {self.config.mode.value}")
            
        except Exception as e:
            logger.error(f"Failed to start gateway: {e}")
            raise
    
    async def stop(self) -> None:
        """停止网关"""
        try:
            self._running = False
            
            # 断开所有连接
            for conn_id, conn in list(self.connections.items()):
                await self._disconnect_client(conn_id)
            
            if self.server:
                self.server.close()
                await self.server.wait_closed()
            
            logger.info("RakNet Gateway stopped")
            
        except Exception as e:
            logger.error(f"Error stopping gateway: {e}")
    
    async def _on_connect(self, conn: Any) -> None:
        """客户端连接回调"""
        conn_id = f"{conn.address[0]}:{conn.address[1]}"
        
        if len(self.connections) >= self.config.max_connections:
            logger.warning(f"Max connections reached, rejecting {conn_id}")
            conn.disconnect()
            return
        
        self.connections[conn_id] = conn
        self.stats['connections_total'] += 1
        self.stats['connections_active'] = len(self.connections)
        
        logger.info(f"Client connected: {conn_id} (active: {self.stats['connections_active']})")
    
    async def _on_disconnect(self, conn: Any) -> None:
        """客户端断开回调"""
        conn_id = f"{conn.address[0]}:{conn.address[1]}"
        
        if conn_id in self.connections:
            del self.connections[conn_id]
            self.stats['connections_active'] = len(self.connections)
        
        logger.info(f"Client disconnected: {conn_id} (active: {self.stats['connections_active']})")
    
    async def _on_data(self, conn: Any, data: bytes) -> None:
        """数据接收回调"""
        try:
            conn_id = f"{conn.address[0]}:{conn.address[1]}"
            
            self.stats['packets_received'] += 1
            self.stats['bytes_received'] += len(data)
            
            # 解码数据包
            packet = self.codec.decode(data, PacketDirection.CLIENT_TO_SERVER)
            
            logger.debug(
                f"[{conn_id}] Received {packet.msg_code} ({packet.get_message_name()})"
            )
            
            # 根据模式处理
            if self.config.mode == GatewayMode.BRIDGE:
                await self._handle_bridge_mode(conn, packet)
            elif self.config.mode == GatewayMode.PROXY:
                await self._handle_proxy_mode(conn, packet)
            elif self.config.mode == GatewayMode.STANDALONE:
                await self._handle_standalone_mode(conn, packet)
            
        except Exception as e:
            logger.error(f"Error handling data: {e}")
    
    async def _handle_bridge_mode(self, conn: Any, packet: MCPPacket) -> None:
        """桥接模式处理"""
        # TODO: 实现桥接到 MC 的逻辑
        logger.debug(f"Bridge mode: {packet.msg_code}")
        
        # 处理特定消息
        handler = self._handlers.get(packet.msg_code)
        if handler:
            await handler(conn, packet)
    
    async def _handle_proxy_mode(self, conn: Any, packet: MCPPacket) -> None:
        """代理模式处理"""
        # TODO: 透传到真实 MNW 服务器
        logger.debug(f"Proxy mode: {packet.msg_code}")
    
    async def _handle_standalone_mode(self, conn: Any, packet: MCPPacket) -> None:
        """独立模式处理"""
        # TODO: 处理本地房间逻辑
        logger.debug(f"Standalone mode: {packet.msg_code}")
    
    async def send_to_client(
        self,
        conn_id: str,
        packet: MCPPacket,
        reliability: Optional[Any] = None,
        priority: Optional[Any] = None
    ) -> bool:
        """
        发送数据包到客户端
        
        Args:
            conn_id: 连接ID
            packet: 数据包
            reliability: 可靠性
            priority: 优先级
            
        Returns:
            是否发送成功
        """
        try:
            if not AIORAK_AVAILABLE:
                logger.error("aiorak is required for RakNet gateway")
                return False

            conn = self.connections.get(conn_id)
            if not conn or conn.state != ConnectionState.CONNECTED:
                logger.warning(f"Connection {conn_id} not available")
                return False

            reliability = reliability or Reliability.RELIABLE_ORDERED
            priority = priority or Priority.MEDIUM
            
            # 编码
            encoded = self.codec.encode(packet)
            
            # 发送
            conn.send(encoded, reliability, priority=priority)
            
            self.stats['packets_sent'] += 1
            self.stats['bytes_sent'] += len(encoded)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending to {conn_id}: {e}")
            return False
    
    async def broadcast(
        self,
        packet: MCPPacket,
        exclude: Optional[Set[str]] = None
    ) -> int:
        """
        广播数据包
        
        Args:
            packet: 数据包
            exclude: 排除的连接ID
            
        Returns:
            成功发送的数量
        """
        exclude = exclude or set()
        count = 0
        
        for conn_id in self.connections:
            if conn_id not in exclude:
                if await self.send_to_client(conn_id, packet):
                    count += 1
        
        return count
    
    async def _disconnect_client(self, conn_id: str) -> None:
        """断开客户端"""
        conn = self.connections.get(conn_id)
        if conn:
            conn.disconnect()
            if conn_id in self.connections:
                del self.connections[conn_id]
    
    def register_handler(self, msg_code: int, handler: Callable) -> None:
        """
        注册消息处理器
        
        Args:
            msg_code: 消息码
            handler: 处理函数 (conn, packet) -> None
        """
        self._handlers[msg_code] = handler
        logger.debug(f"Registered handler for {msg_code} ({get_message_name(msg_code)})")
    
    def unregister_handler(self, msg_code: int) -> None:
        """注销消息处理器"""
        if msg_code in self._handlers:
            del self._handlers[msg_code]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            'host': self.config.host,
            'port': self.config.port,
            'mode': self.config.mode.value,
        }


# 便捷函数
async def start_gateway(
    host: str = "0.0.0.0",
    port: int = 19132,
    mode: GatewayMode = GatewayMode.BRIDGE
) -> MCPRakNetGateway:
    """
    快速启动网关
    
    Args:
        host: 监听地址
        port: 监听端口
        mode: 网关模式
        
    Returns:
        网关实例
    """
    config = GatewayConfig(host=host, port=port, mode=mode)
    gateway = MCPRakNetGateway(config)
    await gateway.start()
    return gateway


# 测试
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("MnMCP v3 - RakNet 网关测试")
    print("=" * 60)
    
    async def test():
        gateway = MCPRakNetGateway()
        
        try:
            await gateway.start()
            print(f"\n✓ 网关已启动")
            print(f"  监听: 0.0.0.0:19132")
            
            # 注册测试处理器
            async def test_handler(conn, packet):
                print(f"  收到消息: {packet.msg_code}")
            
            gateway.register_handler(11, test_handler)  # HeartBeat
            
            print("\n按 Ctrl+C 停止...")
            while True:
                await asyncio.sleep(1)
                stats = gateway.get_stats()
                if stats['packets_received'] > 0:
                    print(f"  Stats: {stats['packets_received']} packets")
                    
        except KeyboardInterrupt:
            print("\n停止中...")
        finally:
            await gateway.stop()
            print("✓ 网关已停止")
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        pass
