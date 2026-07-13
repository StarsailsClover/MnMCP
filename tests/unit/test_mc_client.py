"""
测试 MC 客户端
"""

import pytest
import asyncio
from mcp_mc.client import MCPMinecraftClient, MCClientConfig


class TestMCClient:
    """测试 Minecraft 客户端"""
    
    def test_create_client(self):
        """测试创建客户端"""
        config = MCClientConfig(
            host="localhost",
            port=25565,
            username="TestPlayer"
        )
        client = MCPMinecraftClient(config)
        
        assert client is not None
        assert client.config.host == "localhost"
        assert client.config.port == 25565
        assert client.config.username == "TestPlayer"
    
    def test_event_registration(self):
        """测试事件注册"""
        config = MCClientConfig()
        client = MCPMinecraftClient(config)
        
        @client.on('join')
        async def on_join():
            pass
        
        assert len(client._event_handlers['join']) == 1
    
    def test_player_state(self):
        """测试玩家状态"""
        config = MCClientConfig(username="TestPlayer")
        client = MCPMinecraftClient(config)
        
        assert client.player.username == "TestPlayer"
        assert client.player.health == 20.0
    
    def test_position_update(self):
        """测试位置更新"""
        config = MCClientConfig()
        client = MCPMinecraftClient(config)
        
        client.position.x = 100.0
        client.position.y = 64.0
        client.position.z = 200.0
        
        assert client.position.x == 100.0
        assert client.position.y == 64.0
        assert client.position.z == 200.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
