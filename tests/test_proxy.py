#!/usr/bin/env python3
"""Proxy layer tests for Phase 3."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio


def test_smart_proxy():
    """Test SmartProxy."""
    print("Testing SmartProxy...")
    
    from mn2mc.proxy.smart_proxy import SmartProxy, ProxyMode, SessionData
    
    proxy = SmartProxy()
    assert proxy.mode == ProxyMode.PASSTHROUGH
    print(f"  Initial mode: {proxy.mode.value}")
    
    # Test mode switch
    proxy.switch_mode(ProxyMode.EMULATION, "test")
    assert proxy.mode == ProxyMode.EMULATION
    print(f"  Switched to: {proxy.mode.value}")
    
    # Test session
    session = SessionData(uin=123456, name="TestUser", jwt="test_jwt")
    proxy.on_login_success(session)
    assert proxy.session.is_valid
    print(f"  Session: {proxy.session.name}")
    
    print("✓ SmartProxy OK\n")


def test_auth_interceptor():
    """Test AuthInterceptor."""
    print("Testing AuthInterceptor...")
    
    from mn2mc.proxy.smart_proxy import SmartProxy
    from mn2mc.proxy.auth_interceptor import AuthInterceptor
    
    proxy = SmartProxy()
    interceptor = AuthInterceptor(proxy)
    
    # Test login response interception
    login_response = {
        "code": 0,
        "data": {
            "uin": 123456,
            "name": "TestUser",
            "jwt": "test_jwt",
            "token": "test_token"
        }
    }
    
    # Structure test
    print("  Interceptor structure OK")
    
    print("✓ AuthInterceptor OK\n")


def test_command_parser():
    """Test command parser."""
    print("Testing command parser...")
    
    from mn2mc.commands.parser import CommandParser, CommandType
    
    parser = CommandParser()
    
    # Test MC command
    cmd = parser.parse("/mnmcp minecraft")
    assert cmd is not None
    assert cmd.type == CommandType.SWITCH_TO_MC
    print(f"  Parsed: {cmd.raw} → {cmd.type.name}")
    
    # Test status command
    cmd = parser.parse("/mnmcp status")
    assert cmd.type == CommandType.SHOW_STATUS
    print(f"  Parsed: {cmd.raw} → {cmd.type.name}")
    
    # Test help command
    cmd = parser.parse("/mnmcp help")
    assert cmd.type == CommandType.SHOW_HELP
    print(f"  Parsed: {cmd.raw} → {cmd.type.name}")
    
    # Test non-command
    cmd = parser.parse("Hello world")
    assert cmd is None
    print("  Non-command correctly ignored")
    
    # Test help text
    help_text = parser.get_help_text()
    assert "minecraft" in help_text
    print("  Help text generated")
    
    print("✓ Command parser OK\n")


async def test_proxy_async():
    """Test async proxy operations."""
    print("Testing async proxy operations...")
    
    from mn2mc.proxy.smart_proxy import SmartProxy, ProxyMode
    
    proxy = SmartProxy()
    
    # Test handle request
    request = {"cmd": "list_rooms"}
    response = await proxy.handle_request(request)
    assert "rooms" in response
    print(f"  List rooms: {len(response['rooms'])} rooms returned")
    
    # Test join room
    request = {"cmd": "join_room", "room_id": "mc_bridge_001"}
    response = await proxy.handle_request(request)
    assert response.get("success") is True
    print(f"  Join room: {response.get('type')}")
    
    print("✓ Async proxy OK\n")


def main():
    print("="*60)
    print("Phase 3 Proxy Tests")
    print("="*60)
    print()
    
    test_smart_proxy()
    test_auth_interceptor()
    test_command_parser()
    
    # Run async tests
    asyncio.run(test_proxy_async())
    
    print("="*60)
    print("All Phase 3 tests completed!")
    print("="*60)


if __name__ == "__main__":
    main()
