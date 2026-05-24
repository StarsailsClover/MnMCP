#!/usr/bin/env python3
"""MnMCP v2 - MiniWorld to Minecraft Bridge
Version: 3.26.0.0-3100
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src import VERSION
from src.config import Config, MiniConfig, MCConfig
from src.miniworld import MiniWorldClient

async def main():
    print(f"MnMCP v{VERSION}")
    print("=" * 60)
    
    # Create default config
    config = Config(
        mini=MiniConfig(
            ip="127.0.0.1",
            port=8080,
            uin=2067729592,
            xxtea_key="mnmcp_key_2024"
        ),
        mc=MCConfig(
            ip="127.0.0.1",
            port=25565,
            username="MnMCP_Player"
        )
    )
    
    # Create client
    client = MiniWorldClient(config.mini)
    
    # Connect
    if await client.connect():
        print("✓ Connected to MiniWorld")
    else:
        print("✗ Connection failed")
        return
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
