"""
测试加密模块
"""

import pytest
from mcp_crypto.xxtea_mcp import MCPXXTEA


class TestXXTEA:
    """测试 XXTEA 加密"""
    
    def test_create_xxtea(self):
        """测试创建 XXTEA"""
        xxtea = MCPXXTEA(b"test_key_16bytes")
        assert xxtea is not None
    
    def test_encrypt_decrypt(self):
        """测试加解密"""
        xxtea = MCPXXTEA(b"test_key_16bytes")
        
        plaintext = b"Hello, World!"
        encrypted = xxtea.encrypt_zip(plaintext)
        decrypted = xxtea.decrypt_unzip(encrypted)
        
        assert decrypted == plaintext
    
    def test_empty_data(self):
        """测试空数据"""
        xxtea = MCPXXTEA(b"test_key_16bytes")
        
        plaintext = b""
        encrypted = xxtea.encrypt_zip(plaintext)
        decrypted = xxtea.decrypt_unzip(encrypted)
        
        assert decrypted == plaintext
    
    def test_large_data(self):
        """测试大数据"""
        xxtea = MCPXXTEA(b"test_key_16bytes")
        
        plaintext = b"A" * 10000
        encrypted = xxtea.encrypt_zip(plaintext)
        decrypted = xxtea.decrypt_unzip(encrypted)
        
        assert decrypted == plaintext
    
    def test_binary_data(self):
        """测试二进制数据"""
        xxtea = MCPXXTEA(b"test_key_16bytes")
        
        plaintext = bytes(range(256))
        encrypted = xxtea.encrypt_zip(plaintext)
        decrypted = xxtea.decrypt_unzip(encrypted)
        
        assert decrypted == plaintext


class TestAuth:
    """测试认证模块"""
    
    def test_create_auth_config(self):
        """测试创建认证配置"""
        from mcp_crypto.auth_mcp import MCPAuthConfig
        
        config = MCPAuthConfig(
            uin="123456",
            passwd="test_pass",
            api_id=110
        )
        
        assert config.uin == "123456"
        assert config.passwd == "test_pass"
        assert config.api_id == 110


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
