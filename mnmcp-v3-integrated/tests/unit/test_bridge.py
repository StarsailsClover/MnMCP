"""
测试桥接核心
"""

import pytest
from mcp_core.bridge import MCPBridge, MCPBridgeConfig, BridgeState


class TestBridge:
    """测试桥接核心"""
    
    def test_create_bridge(self):
        """测试创建桥接器"""
        config = MCPBridgeConfig()
        bridge = MCPBridge(config)
        
        assert bridge is not None
        assert bridge.config is not None
    
    def test_initial_state(self):
        """测试初始状态"""
        config = MCPBridgeConfig()
        bridge = MCPBridge(config)
        
        assert bridge.state == BridgeState.STOPPED
        assert not bridge.is_running
    
    def test_event_registration(self):
        """测试事件注册"""
        config = MCPBridgeConfig()
        bridge = MCPBridge(config)
        
        @bridge.on('bridging')
        async def on_bridging():
            pass
        
        assert len(bridge._event_handlers['bridging']) == 1
    
    def test_yaw_conversion_mc_to_mnw(self):
        """测试 MC->MNW Yaw 转换"""
        config = MCPBridgeConfig()
        bridge = MCPBridge(config)
        
        # MC: 0=南 -> MNW: 180=南
        assert bridge._mc_yaw_to_mnw(0) == 180
        
        # MC: -90=东 -> MNW: 90=东
        assert bridge._mc_yaw_to_mnw(-90) == 90
    
    def test_yaw_conversion_mnw_to_mc(self):
        """测试 MNW->MC Yaw 转换"""
        config = MCPBridgeConfig()
        bridge = MCPBridge(config)
        
        # MNW: 180=南 -> MC: 0=南
        assert bridge._mnw_yaw_to_mc(180) == 0
        
        # MNW: 90=东 -> MC: -90=东
        assert bridge._mnw_yaw_to_mc(90) == -90
    
    def test_config_options(self):
        """测试配置选项"""
        config = MCPBridgeConfig(
            mc_host="localhost",
            mc_port=25565,
            mc_username="TestPlayer",
            mnw_uin=123456,
            mnw_passwd="password",
            sync_interval=0.05
        )
        
        assert config.mc_host == "localhost"
        assert config.mc_port == 25565
        assert config.mc_username == "TestPlayer"
        assert config.mnw_uin == 123456
        assert config.mnw_passwd == "password"
        assert config.sync_interval == 0.05


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
