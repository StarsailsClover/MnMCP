"""
MnMCP Crypto Module
整合 MN2MC 的加密实现 + MnMCP 3 的高质量架构

支持:
- XXTEA: 迷你世界通信加密
- MD5: 签名验证
- Base64: URL安全编码
- Zlib: 数据压缩

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

from .xxtea_mcp import MCPXXTEA
from .auth_mcp import MCPAuthManager, MCPAuthenticationError

__all__ = ['MCPXXTEA', 'MCPAuthManager', 'MCPAuthenticationError']