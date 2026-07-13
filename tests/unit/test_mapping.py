"""
测试方块映射模块
"""

import pytest
from mcp_mapping.blocks_integrated import BlockMapperIntegrated


class TestBlockMapper:
    """测试方块映射器"""
    
    def test_create_mapper(self):
        """测试创建映射器"""
        mapper = BlockMapperIntegrated()
        assert mapper is not None
        assert mapper.blocks is not None
    
    def test_mc_to_mnw_basic(self):
        """测试基础 MC->MNW 映射"""
        mapper = BlockMapperIntegrated()
        
        # Stone (MC:1) -> MNW
        result = mapper.mc_to_mnw(1)
        assert result is not None
        assert result > 0
    
    def test_mnw_to_mc_basic(self):
        """测试基础 MNW->MC 映射"""
        mapper = BlockMapperIntegrated()
        
        # 获取 MNW ID
        mnw_id = mapper.mc_to_mnw(1)
        
        # 反向映射
        mc_id = mapper.mnw_to_mc(mnw_id)
        assert mc_id == 1
    
    def test_get_mapping(self):
        """测试获取映射详情"""
        mapper = BlockMapperIntegrated()
        
        mapping = mapper.get_mapping(1)
        assert mapping is not None
        assert mapping.mc_id == 1
        assert mapping.mc_name is not None
    
    def test_invalid_mc_block(self):
        """测试无效 MC 方块"""
        mapper = BlockMapperIntegrated()
        
        result = mapper.mc_to_mnw(999999)
        assert result is None
    
    def test_invalid_mnw_block(self):
        """测试无效 MNW 方块"""
        mapper = BlockMapperIntegrated()
        
        result = mapper.mnw_to_mc(999999)
        assert result is None
    
    def test_get_stats(self):
        """测试获取统计信息"""
        mapper = BlockMapperIntegrated()
        
        stats = mapper.get_stats()
        assert 'total_mappings' in stats
        assert stats['total_mappings'] > 0
    
    def test_multiple_mappings(self):
        """测试多个映射"""
        mapper = BlockMapperIntegrated()
        
        # 测试常见方块
        test_cases = [
            (1, "stone"),
            (2, "grass_block"),
            (3, "dirt"),
        ]
        
        for mc_id, expected_name in test_cases:
            mapping = mapper.get_mapping(mc_id)
            if mapping:
                assert mapping.mc_name == expected_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
