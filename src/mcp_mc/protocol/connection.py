"""
MnMCP v3 - Minecraft 协议连接管理器
实现 TCP 连接、状态机、数据包收发

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import asyncio
import io
import struct
import zlib
from typing import Optional, Callable, Dict, Any, Union
from dataclasses import dataclass, field
from enum import IntEnum, auto
from datetime import datetime
import logging

from .types import VarInt, MCTypeError
from .packets import MCPacket, PacketID, get_packet_class

logger = logging.getLogger(__name__)


class ConnectionState(IntEnum):
    """连接状态"""
    DISCONNECTED = 0
    CONNECTING = 1
    HANDSHAKING = 2
    LOGIN = 3
    PLAY = 4
    DISCONNECTING = 5


class CompressionState(IntEnum):
    """压缩状态"""
    DISABLED = 0
    ENABLED = 1


@dataclass
class ConnectionConfig:
    """连接配置"""
    host: str = "localhost"
    port: int = 25565
    protocol_version: int = 760  # 1.19.2
    
    # 超时
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    keepalive_interval: float = 5.0
    
    # 压缩
    compression_threshold: int = 256
    
    # 调试
    debug: bool = False
    log_packets: bool = False


@dataclass
class ConnectionStats:
    """连接统计"""
    connected_at: Optional[datetime] = None
    packets_sent: int = 0
    packets_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    keepalive_count: int = 0
    errors: int = 0


class MCPProtocolConnection:
    """
    Minecraft 协议连接管理器
    
    功能:
    - TCP 连接管理
    - 连接状态机
    - 数据包编码/发送
    - 数据包接收/解码
    - 压缩处理
    - 事件分发
    
    使用示例:
        conn = MCPProtocolConnection(config)
        await conn.connect()
        await conn.send_packet(packet)
        packet = await conn.receive_packet()
    """
    
    def __init__(self, config: Optional[ConnectionConfig] = None):
        """
        初始化连接
        
        Args:
            config: 连接配置
        """
        self.config = config or ConnectionConfig()
        self.stats = ConnectionStats()
        
        # 网络
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        
        # 状态
        self._state = ConnectionState.DISCONNECTED
        self._compression = CompressionState.DISABLED
        self._compression_threshold = -1  # -1 = disabled
        
        # 事件
        self._handlers: Dict[int, list] = {}
        self._global_handlers: list = []
        
        # 锁
        self._write_lock = asyncio.Lock()
        self._read_lock = asyncio.Lock()
        
        # 运行状态
        self._running = False
        self._receive_task: Optional[asyncio.Task] = None
        
        # 加密 (Phase 4.4 实现)
        self._encryptor: Optional[Any] = None
        self._decryptor: Optional[Any] = None
    
    @property
    def state(self) -> ConnectionState:
        """当前连接状态"""
        return self._state
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._state in (ConnectionState.LOGIN, ConnectionState.PLAY)
    
    @property
    def is_playing(self) -> bool:
        """是否在游戏中"""
        return self._state == ConnectionState.PLAY
    
    async def connect(self) -> bool:
        """
        连接到服务器
        
        Returns:
            是否连接成功
        """
        try:
            if self._state != ConnectionState.DISCONNECTED:
                logger.warning("Already connected or connecting")
                return False
            
            self._state = ConnectionState.CONNECTING
            logger.info(f"Connecting to {self.config.host}:{self.config.port}...")
            
            # 建立 TCP 连接
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.config.host, self.config.port),
                timeout=self.config.connect_timeout
            )
            
            self._state = ConnectionState.HANDSHAKING
            self.stats.connected_at = datetime.now()
            self._running = True
            
            # 启动接收循环
            self._receive_task = asyncio.create_task(self._receive_loop())
            
            logger.info(f"Connected to {self.config.host}:{self.config.port}")
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"Connection timeout to {self.config.host}:{self.config.port}")
            self._state = ConnectionState.DISCONNECTED
            return False
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self._state = ConnectionState.DISCONNECTED
            return False
    
    async def disconnect(self, reason: str = "Client disconnect") -> None:
        """
        断开连接
        
        Args:
            reason: 断开原因
        """
        if self._state == ConnectionState.DISCONNECTED:
            return
        
        logger.info(f"Disconnecting: {reason}")
        self._state = ConnectionState.DISCONNECTING
        self._running = False
        
        # 取消接收任务
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        # 关闭连接
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass
        
        self.reader = None
        self.writer = None
        self._state = ConnectionState.DISCONNECTED
        
        logger.info("Disconnected")
    
    async def send_packet(self, packet: MCPacket) -> bool:
        """
        发送数据包
        
        Args:
            packet: 数据包
            
        Returns:
            是否发送成功
        """
        async with self._write_lock:
            try:
                if not self.writer or self._state == ConnectionState.DISCONNECTED:
                    logger.warning("Not connected, cannot send packet")
                    return False
                
                # 编码数据包
                data = packet.encode()
                
                # 加密 (如果启用)
                if self._encryptor:
                    data = self._encryptor.encrypt(data)
                
                if self._compression == CompressionState.ENABLED:
                    if len(data) >= self._compression_threshold:
                        uncompressed_length = len(data)
                        data = VarInt.encode(uncompressed_length) + zlib.compress(data)
                    else:
                        data = VarInt.encode(0) + data
                
                # 添加长度前缀
                length = VarInt.encode(len(data))
                full_data = length + data
                
                # 发送
                self.writer.write(full_data)
                await self.writer.drain()
                
                # 统计
                self.stats.packets_sent += 1
                self.stats.bytes_sent += len(full_data)
                
                if self.config.log_packets:
                    logger.debug(f"Sent packet {packet.packet_id:02X} ({len(full_data)} bytes)")
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to send packet: {e}")
                self.stats.errors += 1
                return False
    
    async def receive_packet(self) -> Optional[MCPacket]:
        """
        接收单个数据包 (阻塞)
        
        Returns:
            数据包，出错返回 None
        """
        try:
            if not self.reader:
                return None
            
            # 读取长度
            length = await self._read_varint()
            if length is None:
                return None
            
            if length <= 0:
                logger.warning(f"Invalid packet length: {length}")
                return None
            
            # 读取数据
            data = await self._read_exactly(length)
            if data is None:
                return None
            
            # 解密 (如果启用)
            if self._decryptor:
                data = self._decryptor.decrypt(data)
            
            # 解压 (如果启用)
            if self._compression == CompressionState.ENABLED:
                data = self._decompress_packet(data)
            
            # 解码数据包
            packet = self._decode_packet(data)
            
            if packet:
                self.stats.packets_received += 1
                self.stats.bytes_received += length + len(VarInt.encode(length))
                
                if self.config.log_packets:
                    logger.debug(f"Received packet {packet.packet_id:02X} ({length} bytes)")
            
            return packet
            
        except asyncio.TimeoutError:
            logger.warning("Receive timeout")
            return None
        except Exception as e:
            logger.error(f"Failed to receive packet: {e}")
            self.stats.errors += 1
            return None
    
    async def _receive_loop(self) -> None:
        """后台接收循环"""
        logger.debug("Receive loop started")
        
        while self._running:
            try:
                packet = await self.receive_packet()
                if packet:
                    if packet.packet_id in (PacketID.SET_COMPRESSION,):
                        threshold = packet.data.get('threshold', -1)
                        self.set_compression(threshold)
                    elif packet.packet_id == PacketID.LOGIN_SUCCESS:
                        self._state = ConnectionState.PLAY
                    elif packet.packet_id == PacketID.KEEP_ALIVE_PACKET:
                        await self._handle_keepalive(packet)
                    await self._dispatch_packet(packet)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in receive loop: {e}")
                self.stats.errors += 1
                await asyncio.sleep(0.1)
        
        logger.debug("Receive loop stopped")
    
    async def _dispatch_packet(self, packet: MCPacket) -> None:
        """
        分发数据包到处理器
        
        Args:
            packet: 数据包
        """
        # 全局处理器
        for handler in self._global_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(packet)
                else:
                    handler(packet)
            except Exception as e:
                logger.error(f"Error in global handler: {e}")
        
        # 特定 ID 处理器
        handlers = self._handlers.get(packet.packet_id, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(packet)
                else:
                    handler(packet)
            except Exception as e:
                logger.error(f"Error in packet handler: {e}")
    
    async def _handle_keepalive(self, packet: MCPacket) -> None:
        """处理心跳包"""
        from .packets import KeepAlivePacket
        keepalive_id = packet.data.get('keep_alive_id', 0)
        response = KeepAlivePacket(keep_alive_id=keepalive_id)
        await self.send_packet(response)
        
        self.stats.keepalive_count += 1
        logger.debug(f"Keepalive #{self.stats.keepalive_count}")
    
    async def _read_varint(self) -> Optional[int]:
        """读取 VarInt"""
        try:
            result = 0
            for i in range(5):
                byte = await self.reader.read(1)
                if not byte:
                    return None
                
                value = byte[0]
                result |= (value & 0x7F) << (7 * i)
                
                if not (value & 0x80):
                    return result
            
            logger.error("VarInt too long")
            return None
            
        except Exception as e:
            logger.error(f"Error reading VarInt: {e}")
            return None
    
    async def _read_exactly(self, length: int) -> Optional[bytes]:
        """读取精确字节数"""
        try:
            data = await self.reader.readexactly(length)
            return data
        except asyncio.IncompleteReadError:
            logger.error(f"Incomplete read, expected {length} bytes")
            return None
        except Exception as e:
            logger.error(f"Error reading data: {e}")
            return None
    
    def _decode_packet(self, data: bytes) -> Optional[MCPacket]:
        """
        解码数据包
        
        Args:
            data: 原始数据
            
        Returns:
            解码后的数据包
        """
        try:
            if len(data) < 1:
                return None
            
            # 读取包 ID
            stream = io.BytesIO(data)
            packet_id = VarInt.decode_stream(stream)
            
            # 获取包类
            packet_class = get_packet_class(packet_id)
            
            if packet_class:
                return packet_class.decode(data)
            else:
                # 未知包，创建通用包
                return MCPacket(packet_id=packet_id, data={'raw': stream.read()})
                
        except Exception as e:
            logger.error(f"Failed to decode packet: {e}")
            return None
    
    def _decompress_packet(self, data: bytes) -> bytes:
        """解压数据包"""
        try:
            stream = io.BytesIO(data)
            uncompressed_length = VarInt.decode_stream(stream)
            
            if uncompressed_length == 0:
                return stream.read()
            compressed = stream.read()
            return zlib.decompress(compressed)
            
        except Exception as e:
            logger.error(f"Failed to decompress: {e}")
            return data
    
    def on_packet(self, packet_id: Optional[int] = None):
        """
        注册包处理器装饰器
        
        Args:
            packet_id: 包 ID，None 表示全局处理器
            
        Usage:
            @conn.on_packet(0x26)
            async def handle_join(packet):
                print("Joined game!")
        """
        def decorator(func: Callable):
            if packet_id is None:
                self._global_handlers.append(func)
            else:
                if packet_id not in self._handlers:
                    self._handlers[packet_id] = []
                self._handlers[packet_id].append(func)
            return func
        return decorator
    
    def set_compression(self, threshold: int) -> None:
        """
        设置压缩
        
        Args:
            threshold: 压缩阈值，-1 禁用
        """
        self._compression_threshold = threshold
        if threshold >= 0:
            self._compression = CompressionState.ENABLED
            logger.info(f"Compression enabled with threshold {threshold}")
        else:
            self._compression = CompressionState.DISABLED
            logger.info("Compression disabled")
    
    def enable_encryption(self, shared_secret: bytes) -> None:
        """
        启用加密 (Phase 4.4 完整实现)
        
        Args:
            shared_secret: 共享密钥
        """
        # TODO: 实现 AES-CFB8 加密
        logger.info("Encryption enabled (stub)")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'state': self._state.name,
            'connected': self.is_connected,
            'playing': self.is_playing,
            'packets_sent': self.stats.packets_sent,
            'packets_received': self.stats.packets_received,
            'bytes_sent': self.stats.bytes_sent,
            'bytes_received': self.stats.bytes_received,
            'keepalive_count': self.stats.keepalive_count,
            'errors': self.stats.errors,
            'compression': self._compression.name,
            'encryption': 'enabled' if self._encryptor else 'disabled',
        }


# 测试
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("MnMCP v3 - MC 连接管理器测试")
    print("=" * 60)
    
    async def test():
        # 创建配置
        config = ConnectionConfig(
            host="127.0.0.1",
            port=25565,
            debug=True
        )
        
        conn = MCPProtocolConnection(config)
        
        # 测试状态
        print(f"\n初始状态: {conn.state.name}")
        print(f"连接状态: {conn.is_connected}")
        
        # 注册测试处理器
        @conn.on_packet(0x26)  # Join Game
        async def on_join(packet):
            print(f"  收到 Join Game: {packet}")
        
        @conn.on_packet(None)  # 全局
        async def on_any(packet):
            print(f"  收到包 {packet.packet_id:02X}")
        
        # 尝试连接 (可能会失败，因为本地没有MC服务器)
        print("\n尝试连接 (5秒超时)...")
        try:
            connected = await conn.connect()
            print(f"连接结果: {connected}")
            
            if connected:
                print("连接成功，等待 3 秒...")
                await asyncio.sleep(3)
                
                # 统计
                stats = conn.get_stats()
                print(f"\n统计:")
                for k, v in stats.items():
                    print(f"  {k}: {v}")
                
                await conn.disconnect("Test complete")
            else:
                print("连接失败 (预期行为，没有本地MC服务器)")
                
        except Exception as e:
            print(f"连接异常: {e}")
        
        print("\n✓ 连接管理器测试完成")
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        pass
