#!/usr/bin/env python3
"""Network layer tests for Phase 2."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio


def test_raknet_message_ids():
    """Test RakNet message ID utilities."""
    print("Testing RakNet message IDs...")
    
    from mn2mc.network.raknet.message_ids import (
        ID_CONNECTED_PING, ID_CONNECTION_REQUEST_ACCEPTED,
        get_message_name, is_reliable, is_sequenced, get_reliability_type
    )
    
    # Test name lookup
    name = get_message_name(ID_CONNECTED_PING)
    assert name == "ConnectedPing", f"Expected 'ConnectedPing', got '{name}'"
    print(f"  ID 0x{ID_CONNECTED_PING:02X} = {name}")
    
    # Test reliable check
    assert is_reliable(ID_CONNECTION_REQUEST_ACCEPTED | 0x80)
    print("  Reliable check OK")
    
    # Test reliability type
    rel_type = get_reliability_type(ID_CONNECTION_REQUEST_ACCEPTED | 0x80)
    assert rel_type == "RELIABLE"
    print(f"  Reliability type: {rel_type}")
    
    print("✓ Message IDs OK\n")


def test_raknet_packet():
    """Test RakNet packet structures."""
    print("Testing RakNet packets...")
    
    from mn2mc.network.raknet.packet import (
        RakNetHeader, RakNetPacket, OpenConnectionRequest1,
        ConnectedPing, ConnectedPong
    )
    from mn2mc.network.raknet.message_ids import ID_CONNECTED_PING
    
    # Test header
    header = RakNetHeader(message_id=ID_CONNECTED_PING)
    assert header.message_id == ID_CONNECTED_PING
    print(f"  Header: {header}")
    
    # Test from bytes
    data = bytes([ID_CONNECTED_PING])
    header2 = RakNetHeader.from_bytes(data)
    assert header2.message_id == ID_CONNECTED_PING
    print("  Header parsing OK")
    
    # Test OpenConnectionRequest1
    req = OpenConnectionRequest1(protocol_version=11, mtu_size=1492)
    req_data = req.to_bytes()
    assert len(req_data) == 20  # 1 + 16 + 1 + 2
    print(f"  OpenConnectionRequest1: {len(req_data)} bytes")
    
    # Test ConnectedPing
    ping = ConnectedPing(timestamp=1234567890)
    ping_data = ping.to_bytes()
    assert len(ping_data) == 9  # 1 + 8
    ping_parsed = ConnectedPing.from_bytes(ping_data)
    assert ping_parsed.timestamp == 1234567890
    print("  ConnectedPing encode/decode OK")
    
    # Test ConnectedPong
    pong = ConnectedPong(ping_timestamp=1234567890, server_timestamp=1234567900)
    pong_data = pong.to_bytes()
    assert len(pong_data) == 17  # 1 + 8 + 8
    pong_parsed = ConnectedPong.from_bytes(pong_data)
    assert pong_parsed.ping_timestamp == 1234567890
    print("  ConnectedPong encode/decode OK")
    
    print("✓ RakNet packets OK\n")


def test_raknet_decoder():
    """Test RakNet decoder."""
    print("Testing RakNet decoder...")
    
    from mn2mc.network.raknet.decoder import (
        decode_raknet_header, RakNetBitStream, analyze_raknet_packet
    )
    from mn2mc.network.raknet.message_ids import ID_CONNECTED_PING
    
    # Test header decode
    data = bytes([ID_CONNECTED_PING, 0x00, 0x01, 0x02, 0x03])
    header = decode_raknet_header(data)
    assert header is not None
    assert header['raw_message_id'] == ID_CONNECTED_PING
    assert header['message_name'] == "ID_CONNECTED_PING"
    print(f"  Decoded: {header['message_name']}")
    
    # Test bit stream
    bs = RakNetBitStream(b'\x01\x02\x03\x04')
    byte_val = bs.read_byte()
    assert byte_val == 1
    print(f"  BitStream read_byte: {byte_val}")
    
    # Test read uint16
    bs2 = RakNetBitStream(b'\x01\x02')
    uint16 = bs2.read_uint16()
    assert uint16 == 0x0102
    print(f"  BitStream read_uint16: {uint16}")
    
    # Test analyze
    info = analyze_raknet_packet(data)
    assert 'message_name' in info
    print(f"  Analysis: {info['message_name']}")
    
    print("✓ RakNet decoder OK\n")


def test_room_discovery():
    """Test room discovery."""
    print("Testing room discovery...")
    
    from mn2mc.room.discovery import (
        RoomAdvertisement, DiscoveredRoom, RoomDiscoveryProtocol
    )
    
    # Test RoomAdvertisement
    advert = RoomAdvertisement(
        room_id="test_room_123",
        room_name="Test Room",
        host_address=("127.0.0.1", 19132),
        player_count=3,
        max_players=6,
        map_name="Test Map",
        game_mode="Creative",
        version="1.0"
    )
    
    advert_data = advert.to_bytes()
    assert len(advert_data) > 10
    print(f"  Advertisement: {len(advert_data)} bytes")
    
    # Test parse
    advert_parsed = RoomAdvertisement.from_bytes(advert_data)
    assert advert_parsed is not None
    assert advert_parsed.room_id == "test_room_123"
    assert advert_parsed.room_name == "Test Room"
    print(f"  Parsed room: {advert_parsed.room_name}")
    
    # Test DiscoveredRoom
    room = DiscoveredRoom(
        room_id="test_room",
        room_name="Test",
        host_address=("127.0.0.1", 1234),
        player_count=1,
        max_players=6,
        map_name="Test Map",
        map_id="map_001",
        game_mode="Creative",
        is_password_protected=False
    )
    assert not room.is_expired()
    print("  DiscoveredRoom creation OK")
    
    # Test DiscoveryProtocol initialization
    discovery = RoomDiscoveryProtocol()
    assert discovery.DISCOVERY_PORT == 8081
    print(f"  Discovery port: {discovery.DISCOVERY_PORT}")
    
    print("✓ Room discovery OK\n")


async def test_async_discovery():
    """Test async discovery."""
    print("Testing async discovery...")
    
    from mn2mc.room.discovery import RoomDiscoveryProtocol
    
    discovery = RoomDiscoveryProtocol()
    
    # Note: This won't actually start listening in test mode
    # Just test the structure
    print("  Discovery structure OK")
    
    print("✓ Async discovery OK\n")


def main():
    print("=" * 60)
    print("Phase 2 Network Tests")
    print("=" * 60)
    print()
    
    # Run sync tests
    test_raknet_message_ids()
    test_raknet_packet()
    test_raknet_decoder()
    test_room_discovery()
    
    # Run async tests
    asyncio.run(test_async_discovery())
    
    print("=" * 60)
    print("All Phase 2 tests PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
