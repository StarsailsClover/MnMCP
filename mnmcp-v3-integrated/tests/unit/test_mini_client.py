"""
测试 MiniWorld 客户端
"""

import pytest
from mcp_mini.client import (
    MCPMiniClient, MiniClientConfig, MiniAuthConfig,
    MiniClientState
)


class TestMiniClient:
    """测试 MiniWorld 客户端"""
    
    def test_create_client(self):
        """测试创建客户端"""
        config = MiniClientConfig(
            auth=MiniAuthConfig(uin=123456, passwd="test_pass")
        )
        client = MCPMiniClient(config)
        
        assert client is not None
        assert client.config.auth.uin == 123456
    
    def test_initial_state(self):
        """测试初始状态"""
        config = MiniClientConfig()
        client = MCPMiniClient(config)
        
        assert client.state == MiniClientState.DISCONNECTED
        assert not client.is_connected
        assert not client.is_in_game
    
    def test_event_registration(self):
        """测试事件注册"""
        config = MiniClientConfig()
        client = MCPMiniClient(config)
        
        @client.on('enter_world')
        async def on_enter():
            pass
        
        assert len(client._event_handlers['enter_world']) == 1
    
    def test_player_info(self):
        """测试玩家信息"""
        config = MiniClientConfig(
            auth=MiniAuthConfig(uin=123456, name="TestPlayer")
        )
        client = MCPMiniClient(config)
        
        client.player.uin = 123456
        client.player.name = "TestPlayer"
        
        assert client.player.uin == 123456
        assert client.player.name == "TestPlayer"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
