#!/usr/bin/env python3
"""
MnMCP 数据包处理器
处理 Minecraft 协议数据包

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import struct
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MCPPocket:
    """Minecraft 数据包"""
    packet_id: int
    data: bytes
    timestamp: datetime
    direction: str  # "in" or "out"


class MCPPocketHandler:
    """
    Minecraft 数据包处理器
    
    功能:
    - 解析数据包
    - 编码数据包
    - 事件分发
    - 数据转换
    """
    
    def __init__(self, client):
        self.client = client
        self._handlers: Dict[int, Callable] = {}
        self.registry = {}  # 协议注册表
    
    def register_handler(self, packet_id: int, handler: Callable):
        """注册数据包处理器"""
        self._handlers[packet_id] = handler
    
    async def parse_packet(self, raw_data: bytes) -> Optional[MCPPocket]:
        """
        解析原始数据为数据包
        
        格式: [长度: VarInt] [ID: VarInt] [数据: bytes]
        """
        try:
            # 读取长度
            length, offset = self._read_varint(raw_data, 0)
            
            # 读取ID
            packet_id, offset = self._read_varint(raw_data, offset)
            
            # 读取数据
            data = raw_data[offset:offset + length - (offset - 0)]
            
            return MCPPocket(
                packet_id=packet_id,
                data=data,
                timestamp=datetime.now(),
                direction="in"
            )
            
        except Exception as e:
            logger.error(f"解析错误: {e}")
            return None
    
    def encode_packet(self, packet_id: int, data: bytes) -> bytes:
        """编码数据包"""
        # ID + 数据
        packet_data = self._write_varint(packet_id) + data
        
        # 长度 + 包
        result = self._write_varint(len(packet_data)) + packet_data
        
        return result
    
    def _read_varint(self, data: bytes, offset: int) -> tuple:
        """读取 VarInt"""
        result = 0
        shift = 0
        
        while True:
            if offset >= len(data):
                raise ValueError("数据不足")
            
            byte = data[offset]
            offset += 1
            
            result |= (byte & 0x7F) << shift
            shift += 7
            
            if not (byte & 0x80):
                break
            
            if shift >= 32:
                raise ValueError("VarInt 太大")
        
        return result, offset
    
    def _write_varint(self, value: int) -> bytes:
        """写入 VarInt"""
        result = bytearray()
        
        while True:
            byte = value & 0x7F
            value >>= 7
            
            if value:
                byte |= 0x80
            
            result.append(byte)
            
            if not value:
                break
        
        return bytes(result)
    
    def _read_string(self, data: bytes, offset: int) -> tuple:
        """读取字符串"""
        length, offset = self._read_varint(data, offset)
        string_data = data[offset:offset + length]
        return string_data.decode('utf-8'), offset + length
    
    def _write_string(self, value: str) -> bytes:
        """写入字符串"""
        encoded = value.encode('utf-8')
        return self._write_varint(len(encoded)) + encoded