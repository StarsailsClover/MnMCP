import yaml
from dataclasses import dataclass
from typing import Optional

@dataclass
class MiniConfig:
    ip: str = "127.0.0.1"
    port: int = 8080
    uin: int = 2067729592
    xxtea_key: str = ""

@dataclass
class MCConfig:
    ip: str = "127.0.0.1"
    port: int = 25565
    username: str = "MnMCP_Player"

@dataclass
class Config:
    mini: MiniConfig
    mc: MCConfig
    
    @classmethod
    def load(cls, path: str) -> "Config":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(
            mini=MiniConfig(**data.get("mini", {})),
            mc=MCConfig(**data.get("mc", {}))
        )
    
    def save(self, path: str):
        with open(path, "w") as f:
            yaml.dump({
                "mini": self.mini.__dict__,
                "mc": self.mc.__dict__
            }, f)
