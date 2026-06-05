"""
MnMCP v3 - 数据包处理器
"""

from typing import Optional, Callable, Dict, Any
import logging

from .msgcode_registry import PacketDirection
from .codec import MCPPacket

logger = logging.getLogger(__name__)


class MCPPocketHandler:
    """
    数据包处理器
    
    用于处理进出数据包的回调
    """
    
    def __init__(self):
        self._handlers: Dict[int, Callable] = {}
    
    def on(self, msg_code: int, handler: Callable[[MCPPacket], None]):
        """注册处理器"""
        self._handlers[msg_code] = handler
    
    def handle(self, packet: MCPPacket):
        """处理数据包"""
        handler = self._handlers.get(packet.msg_code)
        if handler:
            handler(packet)
        else:
            logger.debug(f"No handler for message {packet.msg_code}")


# 导出
__all__ = ['MCPPocketHandler']
