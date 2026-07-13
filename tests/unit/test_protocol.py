"""
测试协议模块
"""

import io
import pytest
from mcp_protocol.msgcode_registry import MessageRegistry, PacketDirection
from mcp_protocol.codec import MCPProtocolCodec, MCPPacket, PacketFlag


class TestMessageRegistry:
    """测试消息注册表"""
    
    def test_create_registry(self):
        """测试创建注册表"""
        registry = MessageRegistry()
        assert registry is not None
    
    def test_get_name(self):
        """测试获取消息名称"""
        registry = MessageRegistry()
        
        name = registry.get_name(9001)
        assert name is not None
        assert "Chat" in name or "CH" in name
    
    def test_get_direction(self):
        """测试获取消息方向"""
        registry = MessageRegistry()
        
        direction = registry.get_direction(9001)
        assert direction == PacketDirection.CLIENT_TO_SERVER
    
    def test_get_stats(self):
        """测试获取统计"""
        registry = MessageRegistry()
        
        stats = registry.get_stats()
        assert 'total_messages' in stats
        assert stats['total_messages'] > 0


class TestVarInt:
    """测试 VarInt"""
    
    def test_encode_zero(self):
        """测试编码 0"""
        from mcp_protocol.types import VarInt
        assert VarInt.encode(0) == b'\x00'
    
    def test_encode_128(self):
        """测试编码 128"""
        from mcp_protocol.types import VarInt
        assert VarInt.encode(128) == b'\x80\x01'
    
    def test_decode_zero(self):
        """测试解码 0"""
        from mcp_protocol.types import VarInt
        value, length = VarInt.decode(b'\x00')
        assert value == 0
        assert length == 1
    
    def test_decode_128(self):
        """测试解码 128"""
        from mcp_protocol.types import VarInt
        value, length = VarInt.decode(b'\x80\x01')
        assert value == 128
        assert length == 2
    
    def test_encode_decode(self):
        """测试编解码一致性"""
        from mcp_protocol.types import VarInt
        
        test_values = [0, 1, 127, 128, 255, 256, 16383, 65535]
        for value in test_values:
            encoded = VarInt.encode(value)
            decoded, _ = VarInt.decode(encoded)
            assert decoded == value


class TestMCPacket:
    """测试数据包"""
    
    def test_create_packet(self):
        """测试创建数据包"""
        packet = MCPPacket(
            msg_code=9001,
            data=b"test"
        )
        
        assert packet.msg_code == 9001
        assert packet.data == b"test"
    
    def test_packet_flags(self):
        """测试数据包标志"""
        packet = MCPPacket(
            msg_code=9001,
            data=b"test",
            flags=PacketFlag.COMPRESSED
        )
        
        assert packet.is_compressed
        assert not packet.is_encrypted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
