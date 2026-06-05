"""
MnMCP v3 - 安全配置系统
统一配置管理，解决硬编码安全问题
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict


@dataclass
class ServerConfig:
    """服务器配置"""
    # MiniWorld 认证服务器
    mini_auth_host: str = "wskacchm.mini1.cn"
    mini_auth_port: int = 14130
    
    # MiniWorld 游戏服务器 (动态获取)
    mini_game_host: str = ""
    mini_game_port: int = 0
    
    # Minecraft 服务器 (本地桥接)
    mc_host: str = "127.0.0.1"
    mc_port: int = 25565
    
    # 协议版本
    mini_version: str = "1.55.0"
    mc_version: str = "1.19.2"
    mc_protocol: int = 760


@dataclass
class AuthConfig:
    """认证配置"""
    # 从环境变量读取，避免硬编码
    md5_salt: str = field(default_factory=lambda: os.getenv("MCP_MD5_SALT", ""))
    device_id: str = field(default_factory=lambda: os.getenv("MCP_DEVICE_ID", ""))
    
    # 用户凭证 (运行时传入，不保存)
    uin: str = ""
    passwd: str = ""


@dataclass
class CryptoConfig:
    """加密配置"""
    # XXTEA 密钥 (从环境变量读取)
    xxtea_key: bytes = field(default_factory=lambda: 
        os.getenv("MCP_XXTEA_KEY", "default_key_16bytes").encode()[:16]
    )
    
    # ECDH 配置
    ecdh_curve: str = "secp256r1"
    
    # AES-GCM 配置
    aes_key_size: int = 32  # 256-bit
    aes_nonce_size: int = 12  # 96-bit


@dataclass
class BridgeConfig:
    """桥接配置"""
    # 缓冲区大小
    buffer_size: int = 65536
    
    # 超时设置
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    keepalive_interval: float = 5.0
    
    # 重连设置
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # 日志级别
    log_level: str = "INFO"


@dataclass
class MCPUnifiedConfig:
    """
    MnMCP 统一配置
    
    使用方式:
        # 从环境变量加载
        config = MCPUnifiedConfig.from_env()
        
        # 从文件加载
        config = MCPUnifiedConfig.from_file("config.yaml")
        
        # 设置用户凭证
        config.auth.uin = "123456"
        config.auth.passwd = "password"
    """
    server: ServerConfig = field(default_factory=ServerConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    crypto: CryptoConfig = field(default_factory=CryptoConfig)
    bridge: BridgeConfig = field(default_factory=BridgeConfig)
    
    @classmethod
    def from_env(cls) -> "MCPUnifiedConfig":
        """从环境变量加载配置"""
        return cls()
    
    @classmethod
    def from_file(cls, path: str) -> "MCPUnifiedConfig":
        """从 YAML 文件加载配置"""
        if not YAML_AVAILABLE:
            return cls.from_env()
        
        path = Path(path)
        if not path.exists():
            # 创建默认配置文件
            config = cls()
            config.save_template(str(path))
            return config
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls._from_dict(data)
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "MCPUnifiedConfig":
        """从字典创建配置"""
        return cls(
            server=ServerConfig(**data.get('server', {})),
            auth=AuthConfig(**data.get('auth', {})),
            crypto=CryptoConfig(**data.get('crypto', {})),
            bridge=BridgeConfig(**data.get('bridge', {}))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'server': asdict(self.server),
            'auth': asdict(self.auth),
            'crypto': asdict(self.crypto),
            'bridge': asdict(self.bridge)
        }
    
    def save(self, path: str):
        """保存配置到文件"""
        if YAML_AVAILABLE:
            import yaml
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)
        else:
            # Fallback: save as JSON
            import json
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2)
    
    def save_template(self, path: str):
        """保存配置模板（注释说明）"""
        template = """# MnMCP 配置文件
# 安全提示: 敏感信息请使用环境变量，不要直接写入此文件

server:
  mini_auth_host: "wskacchm.mini1.cn"      # MiniWorld 认证服务器
  mini_auth_port: 14130                     # MiniWorld 认证端口
  mini_game_host: ""                         # MiniWorld 游戏服务器 (自动获取)
  mini_game_port: 0                           # MiniWorld 游戏端口 (自动获取)
  mc_host: "127.0.0.1"                       # Minecraft 桥接地址
  mc_port: 25565                             # Minecraft 桥接端口
  mini_version: "1.55.0"                     # MiniWorld 版本
  mc_version: "1.19.2"                       # Minecraft 版本
  mc_protocol: 760                           # Minecraft 协议版本

auth:
  md5_salt: ""                               # 从环境变量 MCP_MD5_SALT 读取
  device_id: ""                              # 从环境变量 MCP_DEVICE_ID 读取
  # 注意: uin 和 passwd 运行时传入，不要保存

crypto:
  xxtea_key: ""                              # 从环境变量 MCP_XXTEA_KEY 读取
  ecdh_curve: "secp256r1"                    # ECDH 曲线
  aes_key_size: 32                           # AES 密钥大小 (256-bit)
  aes_nonce_size: 12                          # AES nonce 大小 (96-bit)

bridge:
  buffer_size: 65536                         # 网络缓冲区大小
  connect_timeout: 10.0                        # 连接超时 (秒)
  read_timeout: 30.0                           # 读取超时 (秒)
  keepalive_interval: 5.0                      # 心跳间隔 (秒)
  max_retries: 3                               # 最大重试次数
  retry_delay: 1.0                             # 重试延迟 (秒)
  log_level: "INFO"                            # 日志级别
"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(template)


def setup_environment():
    """
    设置环境变量向导
    
    在开发前运行此函数，设置必要的环境变量
    """
    print("=" * 60)
    print("MnMCP v3 - 环境变量设置向导")
    print("=" * 60)
    print("\n请设置以下环境变量:\n")
    
    env_vars = {
        "MCP_MD5_SALT": "MD5 签名盐值 (用于 MiniWorld 认证)",
        "MCP_DEVICE_ID": "设备ID (用于 MiniWorld 认证)",
        "MCP_XXTEA_KEY": "XXTEA 加密密钥 (16字节)"
    }
    
    for var, desc in env_vars.items():
        current = os.getenv(var, "未设置")
        masked = current[:4] + "***" if current != "未设置" and len(current) > 4 else current
        print(f"  {var}")
        print(f"    说明: {desc}")
        print(f"    当前: {masked}")
        print()
    
    print("\nWindows PowerShell 设置示例:")
    print("  $env:MCP_MD5_SALT=\"your_salt_here\"")
    print("  $env:MCP_DEVICE_ID=\"your_device_id\"")
    print("  $env:MCP_XXTEA_KEY=\"your_16byte_key\"")
    
    print("\nLinux/macOS 设置示例:")
    print("  export MCP_MD5_SALT=\"your_salt_here\"")
    print("  export MCP_DEVICE_ID=\"your_device_id\"")
    print("  export MCP_XXTEA_KEY=\"your_16byte_key\"")
    
    print("\n" + "=" * 60)


# 便捷函数
def get_config(path: Optional[str] = None) -> MCPUnifiedConfig:
    """
    获取配置
    
    优先级: 文件 > 环境变量 > 默认值
    """
    if path and Path(path).exists():
        return MCPUnifiedConfig.from_file(path)
    return MCPUnifiedConfig.from_env()


if __name__ == "__main__":
    # 运行环境设置向导
    setup_environment()
    
    # 创建默认配置模板
    print("\n创建默认配置模板...")
    config = MCPUnifiedConfig()
    config.save_template("config.template.yaml")
    print("✓ 已创建 config.template.yaml")
    
    # 测试配置加载
    print("\n测试配置加载...")
    loaded = get_config("config.template.yaml")
    print(f"✓ 配置加载成功")
    print(f"  认证服务器: {loaded.server.mini_auth_host}:{loaded.server.mini_auth_port}")
    print(f"  MC桥接地址: {loaded.server.mc_host}:{loaded.server.mc_port}")
