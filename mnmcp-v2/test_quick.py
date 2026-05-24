#!/usr/bin/env python3
"""MnMCP v2 - Quick Test (No Input)
Version: 3.26.0.0-3100
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src import VERSION
from src.config import MiniConfig
from src.miniworld import MiniWorldLoginClient, MiniWorldRoomClient

async def test_login():
    """Quick login test"""
    print(f"\nMnMCP v{VERSION}")
    print("=" * 60)
    print("\nTesting Login...")
    
    config = MiniConfig(
        ip="116.205.254.145",
        port=19921,
        uin=2067729592,
        xxtea_key="mnmcp_key_2024"
    )
    
    login_client = MiniWorldLoginClient(config)
    
    # Attempt login (will fail without interceptors, that's OK)
    success = await login_client.login("test_user", "test_pass")
    
    if success:
        print("\n✓ Login test PASSED")
        print(f"  Token: {login_client.session_token[:20]}...")
    else:
        print("\n⚠ Login test - expected without interceptors")
    
    login_client.close()
    return success, login_client

async def main():
    """Run quick test"""
    print("Starting MnMCP v2 Quick Test...")
    print("MiniWorld client should be running!")
    print()
    
    # Quick login test
    login_success, login_client = await test_login()
    
    print("\n" + "=" * 60)
    if login_success:
        print("✓ Test PASSED - Interceptors working!")
    else:
        print("⚠ Test incomplete - Start interceptors first")
        print("  Run: update_hosts_v3.bat (as Admin)")
        print("  Then: miniworld_interceptor_v3.py")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
