"""
MnMCP v3 - Minecraft and MiniWorld CrossPlatform CrossPlay

核心模块:
- mcp_core: 桥接核心
- mcp_crypto: 加密模块 (XXTEA, MD5, Base64)
- mcp_mini: MiniWorld 客户端
- mcp_mc: Minecraft 客户端
- mcp_protocol: 协议编解码
- mcp_mapping: 方块/物品映射
- mcp_proxy: 代理服务器

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

__version__ = "Victoria v3.1-20260605 Phase8 Stable"
__author__ = "StarsailsClover"
__description__ = "Minecraft and MiniWorld CrossPlatform CrossPlay"

from .mcp_core.bridge import MCPBridge
from .mcp_crypto.xxtea_mcp import MCPXXTEA
from .mcp_crypto.auth_mcp import MCPAuthManager
from .mcp_mini.client import MCPMiniClient
from .mcp_mc.client import MCPMinecraftClient
from .mcp_config import MCPUnifiedConfig

__all__ = [
    'MCPBridge',
    'MCPXXTEA',
    'MCPAuthManager',
    'MCPMiniClient',
    'MCPMinecraftClient',
    'MCPUnifiedConfig',
]