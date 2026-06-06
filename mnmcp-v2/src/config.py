"""
MnMCP Configuration Module
Supports JSON configuration with environment variable overrides
"""

import os
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class ServerConfig:
    """Server connection configuration"""
    host: str = ""
    ip: str = "127.0.0.1"
    port: int = 8080


@dataclass
class MiniAuthConfig:
    """MiniWorld authentication configuration"""
    server: ServerConfig = field(default_factory=lambda: ServerConfig(
        host="certification.mini1.cn",
        ip="116.205.254.145",
        port=19921
    ))
    uin: int = 0
    username: str = ""
    password: str = ""  # Loaded from env var MINI_PASSWORD
    xxtea_key: str = ""  # Loaded from env var MINI_XXTEA_KEY
    auth_sign_key: str = ""  # Loaded from env var MINI_AUTH_KEY
    version: str = "1.55.0"
    platform: str = "pc"
    channel: str = "110"
    device_id: str = ""


@dataclass
class MiniRoomConfig:
    """MiniWorld room server configuration"""
    server: ServerConfig = field(default_factory=lambda: ServerConfig(
        host="openroom.mini1.cn",
        ip="116.205.254.229",
        port=19601
    ))


@dataclass
class MiniConfig:
    """Complete MiniWorld configuration"""
    auth: MiniAuthConfig = field(default_factory=MiniAuthConfig)
    room: MiniRoomConfig = field(default_factory=MiniRoomConfig)


@dataclass
class MCServerConfig:
    """Minecraft server configuration"""
    host: str = "127.0.0.1"
    port: int = 25565


@dataclass
class MCConfig:
    """Complete Minecraft configuration"""
    server: MCServerConfig = field(default_factory=MCServerConfig)
    username: str = "MnMCP_Player"
    uuid: str = ""
    protocol_version: int = 760  # 1.19.2
    bridge_port: int = 25566


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file: str = "logs/mnmcp.log"
    max_size: str = "10MB"
    backup_count: int = 5
    console: bool = True


@dataclass
class SecurityConfig:
    """Security settings"""
    encryption: bool = True
    verify_ssl: bool = False
    timeout: int = 30


@dataclass
class DevelopmentConfig:
    """Development settings"""
    debug: bool = False
    intercept_mode: bool = True
    fake_servers: Dict[str, str] = field(default_factory=lambda: {
        "auth": "127.0.0.1",
        "room": "127.0.0.1"
    })


@dataclass
class Config:
    """Main configuration class"""
    mini: MiniConfig = field(default_factory=MiniConfig)
    mc: MCConfig = field(default_factory=MCConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    development: DevelopmentConfig = field(default_factory=DevelopmentConfig)
    
    @classmethod
    def load(cls, path: str = "config.json") -> "Config":
        """Load configuration from JSON file with env var overrides"""
        config_path = Path(path)
        
        # Load from file if exists
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f) or {}
        else:
            data = {}
        
        # Create config from data with env var overrides
        config = cls._from_dict(data)
        config._apply_env_overrides()
        
        return config
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config from dictionary"""
        mini_data = data.get("mini", {})
        mc_data = data.get("mc", {})
        
        return cls(
            mini=MiniConfig(
                auth=MiniAuthConfig(
                    server=ServerConfig(**mini_data.get("auth_server", {})),
                    uin=mini_data.get("uin", 0),
                    username=mini_data.get("username", ""),
                    password=mini_data.get("password", ""),
                    xxtea_key=mini_data.get("xxtea_key", ""),
                    auth_sign_key=mini_data.get("auth_sign_key", ""),
                    version=mini_data.get("version", "1.55.0"),
                    platform=mini_data.get("platform", "pc"),
                    channel=mini_data.get("channel", "110"),
                    device_id=mini_data.get("device_id", ""),
                ),
                room=MiniRoomConfig(
                    server=ServerConfig(**mini_data.get("room_server", {}))
                )
            ),
            mc=MCConfig(
                server=MCServerConfig(**mc_data.get("server", {})),
                username=mc_data.get("username", "MnMCP_Player"),
                uuid=mc_data.get("uuid", ""),
                protocol_version=mc_data.get("protocol_version", 760),
                bridge_port=mc_data.get("bridge_port", 25566),
            ),
            logging=LoggingConfig(**data.get("logging", {})),
            security=SecurityConfig(**data.get("security", {})),
            development=DevelopmentConfig(**data.get("development", {}))
        )
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        # Security sensitive values from env vars
        if mini_password := os.getenv("MINI_PASSWORD"):
            self.mini.auth.password = mini_password
        if mini_key := os.getenv("MINI_XXTEA_KEY"):
            self.mini.auth.xxtea_key = mini_key
        if auth_key := os.getenv("MINI_AUTH_KEY"):
            self.mini.auth.auth_sign_key = auth_key
        
        # Override server addresses in development mode
        if self.development.intercept_mode:
            self.mini.auth.server.ip = self.development.fake_servers.get("auth", "127.0.0.1")
            self.mini.room.server.ip = self.development.fake_servers.get("room", "127.0.0.1")
    
    def save(self, path: str = "config.json"):
        """Save configuration to JSON file"""
        data = {
            "mini": {
                "auth_server": {
                    "host": self.mini.auth.server.host,
                    "ip": self.mini.auth.server.ip,
                    "port": self.mini.auth.server.port
                },
                "room_server": {
                    "host": self.mini.room.server.host,
                    "ip": self.mini.room.server.ip,
                    "port": self.mini.room.server.port
                },
                "uin": self.mini.auth.uin,
                "username": self.mini.auth.username,
                "xxtea_key": "",  # Don't save to file
                "auth_sign_key": "",  # Don't save to file
                "version": self.mini.auth.version,
                "platform": self.mini.auth.platform,
                "channel": self.mini.auth.channel,
                "device_id": self.mini.auth.device_id,
            },
            "mc": {
                "server": {
                    "host": self.mc.server.host,
                    "port": self.mc.server.port
                },
                "username": self.mc.username,
                "uuid": self.mc.uuid,
                "protocol_version": self.mc.protocol_version,
                "bridge_port": self.mc.bridge_port
            },
            "logging": self.logging.__dict__,
            "security": self.security.__dict__,
            "development": self.development.__dict__
        }
        
        with open(path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        if self.mini.auth.uin == 0:
            errors.append("mini.auth.uin is required")
        if not self.mini.auth.xxtea_key:
            errors.append("mini.auth.xxtea_key is required (set MINI_XXTEA_KEY env var)")
        
        if errors:
            print("Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
