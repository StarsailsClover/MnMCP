#!/usr/bin/env python3
"""MnMCP v2 - Full Login and Room Test
Version: 3.26.0.0-3100
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src import VERSION
from src.config import Config, MiniConfig, MCConfig
from src.miniworld import MiniWorldLoginClient, MiniWorldRoomClient

async def test_login():
    """Test full login flow"""
    print(f"\nMnMCP v{VERSION}")
    print("=" * 60)
    print("\n[1/3] Testing Login...")
    
    config = MiniConfig(
        ip="116.205.254.145",
        port=19921,
        uin=2067729592,
        xxtea_key="mnmcp_key_2024"
    )
    
    login_client = MiniWorldLoginClient(config)
    
    # Attempt login
    success = await login_client.login("test_user", "test_pass")
    
    if success:
        print("\n✓ Login test PASSED")
        print(f"  Token: {login_client.session_token[:20]}...")
        print(f"  User: {login_client.user_info.get('nickname')}")
    else:
        print("\n✗ Login test FAILED")
        print("  (Expected if MiniWorld servers are not intercepted)")
    
    login_client.close()
    return success, login_client

async def test_room_list(login_client):
    """Test room list"""
    print("\n[2/3] Testing Room List...")
    
    config = MiniConfig(
        ip="116.205.254.229",
        port=19601,
        uin=2067729592,
        xxtea_key="mnmcp_key_2024"
    )
    
    room_client = MiniWorldRoomClient(config, login_client)
    
    # Get room list
    rooms = await room_client.get_room_list()
    
    if rooms:
        print(f"\n✓ Room list test PASSED")
        print(f"  Found {len(rooms)} rooms:")
        for room in rooms[:3]:
            print(f"    - {room.room_name} (ID: {room.room_id})")
    else:
        print("\n✗ Room list test FAILED")
    
    return rooms

async def test_minecraft_room(login_client):
    """Test joining Minecraft room"""
    print("\n[3/3] Testing Minecraft Room...")
    
    config = MiniConfig(
        ip="116.205.254.229",
        port=19601,
        uin=2067729592,
        xxtea_key="mnmcp_key_2024"
    )
    
    room_client = MiniWorldRoomClient(config, login_client)
    
    # Join Minecraft room
    success = await room_client.join_room("999999999")
    
    if success:
        print("\n✓ Minecraft room test PASSED")
        print("  Ready to connect to Minecraft server!")
    else:
        print("\n✗ Minecraft room test FAILED")
    
    return success

async def main():
    """Run all tests"""
    print("Starting MnMCP v2 Tests...")
    print("Make sure MiniWorld client is ready to test!")
    input("\nPress Enter to start...")
    
    # Test 1: Login
    login_success, login_client = await test_login()
    
    if not login_success:
        print("\n[!] Login failed - expected if interceptors not running")
        print("    Start interceptors first, then test again")
        return
    
    # Test 2: Room List
    rooms = await test_room_list(login_client)
    
    # Test 3: Minecraft Room
    mc_success = await test_minecraft_room(login_client)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Login:          {'✓ PASS' if login_success else '✗ FAIL'}")
    print(f"  Room List:      {'✓ PASS' if rooms else '✗ FAIL'}")
    print(f"  Minecraft Room: {'✓ PASS' if mc_success else '✗ FAIL'}")
    print("=" * 60)
    
    if login_success and rooms and mc_success:
        print("\n🎉 All tests PASSED!")
        print("   Ready for full integration!")
    else:
        print("\n⚠ Some tests failed")
        print("   Check interceptors and try again")

if __name__ == "__main__":
    asyncio.run(main())
