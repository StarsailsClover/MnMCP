#!/usr/bin/env python3
"""
MnMCP v3 - 离线测试脚本
无需账号，测试所有本地模块功能

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import sys
import os
import struct
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = 0
FAIL = 0


def test(name, func):
    global PASS, FAIL
    try:
        func()
        PASS += 1
        print(f"  [PASS] {name}")
    except Exception as e:
        FAIL += 1
        print(f"  [FAIL] {name}: {e}")


# ============================================================
# 1. 加密模块测试
# ============================================================
print("\n" + "=" * 60)
print("1. 加密模块测试 (XXTEA)")
print("=" * 60)


def test_xxtea_encrypt_decrypt():
    from src.mcp_crypto.xxtea_mcp import MCPXXTEA
    xxtea = MCPXXTEA(b"test_key_12345")
    data = b"Hello MnMCP v3 Victoria!"
    encrypted = xxtea.encrypt_zip(data)
    decrypted = xxtea.decrypt_unzip(encrypted)
    assert data == decrypted, f"解密不一致: {decrypted}"


def test_xxtea_empty_data():
    from src.mcp_crypto.xxtea_mcp import MCPXXTEA
    xxtea = MCPXXTEA(b"test_key_12345")
    data = b""
    encrypted = xxtea.encrypt_zip(data)
    decrypted = xxtea.decrypt_unzip(encrypted)
    assert data == decrypted, f"空数据解密不一致"


def test_xxtea_large_data():
    from src.mcp_crypto.xxtea_mcp import MCPXXTEA
    xxtea = MCPXXTEA(b"test_key_12345")
    data = b"A" * 10000
    encrypted = xxtea.encrypt_zip(data)
    decrypted = xxtea.decrypt_unzip(encrypted)
    assert data == decrypted, f"大数据解密不一致"


def test_xxtea_binary_data():
    from src.mcp_crypto.xxtea_mcp import MCPXXTEA
    xxtea = MCPXXTEA(b"test_key_12345")
    data = bytes(range(256)) * 10
    encrypted = xxtea.encrypt_zip(data)
    decrypted = xxtea.decrypt_unzip(encrypted)
    assert data == decrypted, f"二进制数据解密不一致"


def test_xxtea_different_keys():
    from src.mcp_crypto.xxtea_mcp import MCPXXTEA
    xxtea1 = MCPXXTEA(b"key_one_1234567")
    xxtea2 = MCPXXTEA(b"key_two_1234567")
    data = b"Secret message"
    enc1 = xxtea1.encrypt_zip(data)
    enc2 = xxtea2.encrypt_zip(data)
    assert enc1 != enc2, "不同密钥应产生不同密文"
    assert xxtea1.decrypt_unzip(enc1) == data
    assert xxtea2.decrypt_unzip(enc2) == data


test("XXTEA 加密/解密", test_xxtea_encrypt_decrypt)
test("XXTEA 空数据", test_xxtea_empty_data)
test("XXTEA 大数据 (10KB)", test_xxtea_large_data)
test("XXTEA 二进制数据", test_xxtea_binary_data)
test("XXTEA 不同密钥", test_xxtea_different_keys)


# ============================================================
# 2. 方块映射测试
# ============================================================
print("\n" + "=" * 60)
print("2. 方块映射测试")
print("=" * 60)


def test_block_mc_to_mnw():
    from src.mcp_mapping.blocks_full import mc_to_mnw
    result = mc_to_mnw(1)
    assert result is not None, "MC方块1 (石头) 应有映射"
    mnw_id, mc_name, mnw_name = result
    assert mnw_id > 0, f"MNW ID 应 > 0, 得到 {mnw_id}"


def test_block_mnw_to_mc():
    from src.mcp_mapping.blocks_full import mnw_to_mc
    result = mnw_to_mc(104)
    assert result is not None, "MNW方块104 应有映射"
    mc_id, mc_name, mnw_name = result
    assert mc_id > 0, f"MC ID 应 > 0, 得到 {mc_id}"


def test_block_roundtrip():
    from src.mcp_mapping.blocks_full import mc_to_mnw, mnw_to_mc
    mc_id = 1
    result = mc_to_mnw(mc_id)
    assert result is not None
    mnw_id = result[0]
    reverse = mnw_to_mc(mnw_id)
    assert reverse is not None, f"MNW {mnw_id} 应能反向映射"
    assert reverse[0] == mc_id, f"反向映射应得到 MC {mc_id}, 得到 {reverse[0]}"


def test_block_convert_functions():
    from src.mcp_mapping.blocks_full import convert_mc_block, convert_mnw_block
    mnw_id = convert_mc_block(1)
    assert mnw_id > 0, f"convert_mc_block(1) 应 > 0, 得到 {mnw_id}"
    mc_id = convert_mnw_block(104)
    assert mc_id > 0, f"convert_mnw_block(104) 应 > 0, 得到 {mc_id}"


def test_block_unknown_returns_none():
    from src.mcp_mapping.blocks_full import mc_to_mnw, mnw_to_mc
    result = mc_to_mnw(999999)
    assert result is None, "未知MC方块应返回 None"


def test_block_mapping_count():
    from src.mcp_mapping.blocks_full import MC_TO_MNW_FULL_MAPPING, MNW_TO_MC_FULL_MAPPING
    assert len(MC_TO_MNW_FULL_MAPPING) >= 800, f"MC->MNW映射应 >= 800, 实际 {len(MC_TO_MNW_FULL_MAPPING)}"
    assert len(MNW_TO_MC_FULL_MAPPING) >= 200, f"MNW->MC映射应 >= 200, 实际 {len(MNW_TO_MC_FULL_MAPPING)}"


def test_block_name_lookup():
    from src.mcp_mapping.blocks_full import get_mc_block_name, get_mnw_block_name
    mc_name = get_mc_block_name(1)
    assert mc_name and mc_name != "unknown_1", f"MC方块1应有名称, 得到 {mc_name}"
    mnw_name = get_mnw_block_name(104)
    assert mnw_name and mnw_name != "未知_104", f"MNW方块104应有名称, 得到 {mnw_name}"


test("MC->MNW 方块映射", test_block_mc_to_mnw)
test("MNW->MC 方块映射", test_block_mnw_to_mc)
test("方块双向映射一致性", test_block_roundtrip)
test("convert 函数", test_block_convert_functions)
test("未知方块返回 None", test_block_unknown_returns_none)
test("映射数量检查", test_block_mapping_count)
test("方块名称查询", test_block_name_lookup)


# ============================================================
# 3. 数据包转换器测试
# ============================================================
print("\n" + "=" * 60)
print("3. 数据包转换器测试")
print("=" * 60)


def test_packet_reader_writer():
    from src.mcp_core.packet_converter import PacketReader, PacketWriter
    writer = PacketWriter()
    writer.write_byte(42)
    writer.write_bool(True)
    writer.write_short(1234)
    writer.write_int(56789)
    writer.write_float(3.14)
    writer.write_double(2.71828)
    writer.write_string("Hello MnMCP")
    writer.write_varint(300)
    data = writer.get_data()
    reader = PacketReader(data)
    assert reader.read_byte() == 42
    assert reader.read_bool() == True
    assert reader.read_short() == 1234
    assert reader.read_int() == 56789
    assert abs(reader.read_float() - 3.14) < 0.001
    assert abs(reader.read_double() - 2.71828) < 0.00001
    assert reader.read_string() == "Hello MnMCP"
    assert reader.read_varint() == 300


def test_mc_chat_to_mnw():
    from src.mcp_core.packet_converter import MCPPacketConverter, PacketWriter
    converter = MCPPacketConverter()
    writer = PacketWriter()
    writer.write_string("Hello from MC!")
    writer.write_long(0)
    result = converter.mc_to_mnw(0x03, writer.get_data())
    assert result is not None, "MC聊天应能转换"
    assert result.msg_code == 9001
    assert result.packet_type.value == 2  # CHAT


def test_mc_position_to_mnw():
    from src.mcp_core.packet_converter import MCPPacketConverter, PacketWriter
    converter = MCPPacketConverter()
    writer = PacketWriter()
    writer.write_double(100.5)
    writer.write_double(64.0)
    writer.write_double(200.5)
    writer.write_bool(True)
    result = converter.mc_to_mnw(0x12, writer.get_data())
    assert result is not None, "MC位置应能转换"
    assert result.msg_code == 2001
    assert result.packet_type.value == 1  # POSITION


def test_mc_pos_rot_to_mnw():
    from src.mcp_core.packet_converter import MCPPacketConverter, PacketWriter
    converter = MCPPacketConverter()
    writer = PacketWriter()
    writer.write_double(100.5)
    writer.write_double(64.0)
    writer.write_double(200.5)
    writer.write_float(90.0)
    writer.write_float(0.0)
    writer.write_bool(True)
    result = converter.mc_to_mnw(0x13, writer.get_data())
    assert result is not None, "MC位置+朝向应能转换"
    assert result.msg_code == 2001


def test_mnw_chat_to_mc():
    from src.mcp_core.packet_converter import MCPPacketConverter
    converter = MCPPacketConverter()
    mnw_data = json.dumps({
        "msg_type": 9001,
        "sender": "TestPlayer",
        "message": "Hello from MNW!"
    }).encode("utf-8")
    result = converter.mnw_to_mc(9001, mnw_data)
    assert result is not None, "MNW聊天应能转换"
    assert result.msg_code == 0x03
    assert result.packet_type.value == 2  # CHAT


def test_mnw_move_to_mc():
    from src.mcp_core.packet_converter import MCPPacketConverter
    converter = MCPPacketConverter()
    mnw_data = json.dumps({
        "msg_type": 2001,
        "entity_id": 1000,
        "x": 100.5,
        "y": 64.0,
        "z": 200.5,
        "yaw": 90.0,
        "pitch": 0.0
    }).encode("utf-8")
    result = converter.mnw_to_mc(2001, mnw_data)
    assert result is not None, "MNW移动应能转换"
    assert result.msg_code == 0x13
    assert result.packet_type.value == 1  # POSITION


def test_unknown_packet_returns_none():
    from src.mcp_core.packet_converter import MCPPacketConverter
    converter = MCPPacketConverter()
    result = converter.mc_to_mnw(0xFF, b"\x00\x00")
    assert result is None, "未知MC数据包应返回 None"


test("PacketReader/Writer 读写", test_packet_reader_writer)
test("MC聊天 -> MNW", test_mc_chat_to_mnw)
test("MC位置 -> MNW", test_mc_position_to_mnw)
test("MC位置+朝向 -> MNW", test_mc_pos_rot_to_mnw)
test("MNW聊天 -> MC", test_mnw_chat_to_mc)
test("MNW移动 -> MC", test_mnw_move_to_mc)
test("未知数据包返回 None", test_unknown_packet_returns_none)


# ============================================================
# 4. 消息码注册表测试
# ============================================================
print("\n" + "=" * 60)
print("4. 消息码注册表测试")
print("=" * 60)


def test_msgcode_total():
    from src.mcp_protocol.msgcode_registry import MessageRegistry
    registry = MessageRegistry()
    stats = registry.get_stats()
    assert stats["total_messages"] >= 600, f"总消息数应 >= 600, 实际 {stats['total_messages']}"


def test_msgcode_direction():
    from src.mcp_protocol.msgcode_registry import MessageRegistry
    registry = MessageRegistry()
    stats = registry.get_stats()
    assert stats["client_to_server"] > 0, "CH消息数应 > 0"
    assert stats["server_to_client"] > 0, "HC消息数应 > 0"


def test_msgcode_lookup():
    from src.mcp_protocol.msgcode_registry import get_message_name
    name = get_message_name(11)
    assert name and "HeartBeat" in name, f"消息码11应为HeartBeat, 得到 {name}"


def test_msgcode_known_codes():
    from src.mcp_protocol.msgcode_registry import get_message_name
    codes = {11: "HeartBeat", 12: "HeartBeat", 101: "Chunk", 102: "Chunk"}
    for code, keyword in codes.items():
        name = get_message_name(code)
        assert name and keyword.lower() in name.lower(), \
            f"消息码{code}应包含'{keyword}', 得到 {name}"


def test_msgcode_unknown():
    from src.mcp_protocol.msgcode_registry import get_message_name
    name = get_message_name(99999)
    assert name is None or "Unknown" in str(name), f"未知消息码应返回Unknown或None, 得到 {name}"


test("消息码总数 (>= 600)", test_msgcode_total)
test("消息方向统计", test_msgcode_direction)
test("消息码查询", test_msgcode_lookup)
test("已知消息码验证", test_msgcode_known_codes)
test("未知消息码处理", test_msgcode_unknown)


# ============================================================
# 5. 配置系统测试
# ============================================================
print("\n" + "=" * 60)
print("5. 配置系统测试")
print("=" * 60)


def test_config_default():
    from src.mcp_config import MCPUnifiedConfig
    config = MCPUnifiedConfig()
    assert config.server.mini_auth_host == "wskacchm.mini1.cn"
    assert config.server.mc_host == "127.0.0.1"
    assert config.server.mc_port == 25565
    assert config.bridge.buffer_size == 65536


def test_config_from_file():
    from src.mcp_config import get_config
    config = get_config("config.yaml")
    assert config.server.mini_auth_host == "wskacchm.mini1.cn"
    assert config.server.mc_port == 25565


def test_config_to_dict():
    from src.mcp_config import MCPUnifiedConfig
    config = MCPUnifiedConfig()
    d = config.to_dict()
    assert "server" in d
    assert "auth" in d
    assert "crypto" in d
    assert "bridge" in d
    assert d["server"]["mc_host"] == "127.0.0.1"


def test_config_save_load():
    from src.mcp_config import MCPUnifiedConfig
    config = MCPUnifiedConfig()
    config.save("test_config_output.yaml")
    loaded = MCPUnifiedConfig.from_file("test_config_output.yaml")
    assert loaded.server.mc_host == config.server.mc_host
    os.remove("test_config_output.yaml")


test("默认配置", test_config_default)
test("从文件加载配置", test_config_from_file)
test("配置转字典", test_config_to_dict)
test("配置保存/加载", test_config_save_load)


# ============================================================
# 6. 桥接核心测试
# ============================================================
print("\n" + "=" * 60)
print("6. 桥接核心测试")
print("=" * 60)


def test_bridge_config():
    from src.mcp_core.bridge import MCPBridgeConfig
    config = MCPBridgeConfig()
    assert config.mc_host == "127.0.0.1"
    assert config.mc_port == 25565
    assert config.log_sync == False


def test_bridge_state():
    from src.mcp_core.bridge import MCPBridge, BridgeState
    bridge = MCPBridge()
    assert bridge._state == BridgeState.STOPPED


def test_bridge_yaw_conversion():
    from src.mcp_core.bridge import MCPBridge
    bridge = MCPBridge()
    # MC: -180=北, 0=南, 90=西, -90=东
    # MNW: 0=北, 90=东, 180=南, 270=西
    mc_yaw = 0.0  # 南
    mnw_yaw = bridge._mc_yaw_to_mnw(mc_yaw)
    assert abs(mnw_yaw - 180.0) < 0.01, f"MC 0度应映射到MNW 180度, 得到 {mnw_yaw}"

    mc_yaw = -180.0  # 北
    mnw_yaw = bridge._mc_yaw_to_mnw(mc_yaw)
    assert abs(mnw_yaw) < 0.01 or abs(mnw_yaw - 360.0) < 0.01, \
        f"MC -180度应映射到MNW 0度, 得到 {mnw_yaw}"


def test_bridge_yaw_roundtrip():
    from src.mcp_core.bridge import MCPBridge
    bridge = MCPBridge()
    for mc_yaw in [-180, -90, 0, 45, 90, 135, 180]:
        mnw_yaw = bridge._mc_yaw_to_mnw(float(mc_yaw))
        back = bridge._mnw_yaw_to_mc(mnw_yaw)
        diff = abs(back - mc_yaw)
        if diff > 180:
            diff = 360 - diff
        assert diff < 0.01, f"Yaw往返转换不一致: {mc_yaw} -> {mnw_yaw} -> {back}"


test("桥接配置", test_bridge_config)
test("桥接初始状态", test_bridge_state)
test("Yaw角度转换 MC->MNW", test_bridge_yaw_conversion)
test("Yaw角度往返转换一致性", test_bridge_yaw_roundtrip)


# ============================================================
# 7. MiniWorld 真实依赖保护测试
# ============================================================
print("\n" + "=" * 60)
print("7. MiniWorld 真实依赖保护测试")
print("=" * 60)


def test_mini_config_has_no_test_stub_switch():
    from src.mcp_mini.client import MiniClientConfig
    config = MiniClientConfig()
    assert set(config.__dataclass_fields__) == {"auth", "debug", "log_packets"}


def test_mini_requires_aiorak():
    import asyncio
    from src.mcp_mini.client import MCPMiniClient, MiniRoomInfo, AIORAK_AVAILABLE
    if AIORAK_AVAILABLE:
        return

    async def run():
        client = MCPMiniClient()
        client.current_room = MiniRoomInfo(
            room_id="offline",
            room_name="Offline Test",
            game_server_ip="127.0.0.1",
            game_server_port=8080,
        )
        result = await client._connect_game_server()
        assert result is False
        assert not client.is_connected

    asyncio.run(run())


test("MiniWorld 配置无测试替身开关", test_mini_config_has_no_test_stub_switch)
test("MiniWorld 无 aiorak 时连接失败", test_mini_requires_aiorak)


# ============================================================
# 8. 协议编解码器测试
# ============================================================
print("\n" + "=" * 60)
print("7. 协议编解码器测试")
print("=" * 60)


def test_codec_init():
    from src.mcp_protocol.codec import MCPProtocolCodec
    codec = MCPProtocolCodec()
    assert codec is not None


def test_codec_encode_decode():
    from src.mcp_protocol.codec import MCPProtocolCodec, MCPPacket
    from src.mcp_protocol.msgcode_registry import PacketDirection
    codec = MCPProtocolCodec()
    test_data = b"test payload data"
    packet = MCPPacket(msg_code=11, data=test_data, direction=PacketDirection.SERVER_TO_CLIENT)
    encoded = codec.encode(packet)
    assert len(encoded) > len(test_data), "编码后应比原始数据长"
    decoded = codec.decode(encoded, PacketDirection.SERVER_TO_CLIENT)
    assert decoded is not None, "解码不应返回 None"
    assert decoded.msg_code == 11, f"消息码应为11, 得到 {decoded.msg_code}"
    assert encoded[0] == 0x89, "服务端包应使用 MiniWorld 0x89 包头"
    assert encoded[1:5] == b"\x0b\x00\x11\x00", "服务端包头应为 msgcode+length 小端格式"


def test_codec_compressed():
    from src.mcp_protocol.codec import MCPProtocolCodec, MCPPacket
    from src.mcp_protocol.msgcode_registry import PacketDirection
    codec = MCPProtocolCodec()
    test_data = b"A" * 1000
    packet = MCPPacket(msg_code=11, data=test_data, direction=PacketDirection.SERVER_TO_CLIENT)
    encoded = codec.encode(packet)
    decoded = codec.decode(encoded, PacketDirection.SERVER_TO_CLIENT)
    assert decoded is not None
    assert decoded.data == test_data, "压缩编码/解码后数据应一致"


def test_codec_client_header():
    from src.mcp_protocol.codec import MCPProtocolCodec, MCPPacket
    from src.mcp_protocol.msgcode_registry import PacketDirection
    codec = MCPProtocolCodec()
    packet = MCPPacket(msg_code=11, data=b"ping", direction=PacketDirection.CLIENT_TO_SERVER, session_id=123456)
    encoded = codec.encode(packet)
    assert encoded[0] == 0x89
    assert encoded[1:5] == (123456).to_bytes(4, "big")
    assert encoded[5:13] == b"\x00" * 8
    assert encoded[13:17] == b"\x0b\x00\x04\x00"
    decoded = codec.decode(encoded, PacketDirection.CLIENT_TO_SERVER)
    assert decoded.session_id == 123456
    assert decoded.msg_code == 11
    assert decoded.data == b"ping"


test("编解码器初始化", test_codec_init)
test("编解码器 encode/decode", test_codec_encode_decode)
test("编解码器压缩模式", test_codec_compressed)
test("编解码器客户端 0x89 包头", test_codec_client_header)


# ============================================================
# 9. ProxyServerV2 测试
# ============================================================
print("\n" + "=" * 60)
print("9. ProxyServerV2 测试")
print("=" * 60)


def test_proxy_server_import():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig, ProxyState
    assert MnMCPProxyServer is not None
    assert ProxyServerConfig is not None
    assert ProxyState is not None


def test_proxy_server_config():
    from src.mcp_proxy.proxy_server import ProxyServerConfig
    config = ProxyServerConfig(
        raknet_host="127.0.0.1",
        raknet_port=19132,
        mc_host="127.0.0.1",
        mc_port=25565,
        max_clients=5,
        debug=True
    )
    assert config.raknet_port == 19132
    assert config.mc_port == 25565
    assert config.max_clients == 5
    assert config.debug is True


def test_proxy_server_create():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    config = ProxyServerConfig()
    server = MnMCPProxyServer(config)
    assert server is not None
    assert not server.is_running
    assert server.config is config


def test_proxy_server_session():
    from src.mcp_proxy.proxy_server import ClientSession, ClientSessionState
    session = ClientSession(conn_id="127.0.0.1:12345")
    assert session.conn_id == "127.0.0.1:12345"
    assert session.mnw_state == ClientSessionState.DISCONNECTED
    assert session.mc_state == ClientSessionState.DISCONNECTED
    assert session.x == 0.0 and session.y == 64.0 and session.z == 0.0


def test_proxy_server_yaw_conversion():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    
    # MC yaw -180 (北) -> MNW yaw 0 (北)
    assert abs(server._mc_yaw_to_mnw(-180) - 0) < 0.01
    # MC yaw -90 (东) -> MNW yaw 90 (东)
    assert abs(server._mc_yaw_to_mnw(-90) - 90) < 0.01
    # MC yaw 0 (南) -> MNW yaw 180 (南)
    assert abs(server._mc_yaw_to_mnw(0) - 180) < 0.01
    
    # MNW yaw 0 (北) -> MC yaw -180 (北)
    assert abs(server._mnw_yaw_to_mc(0) - (-180)) < 0.01
    # MNW yaw 90 (东) -> MC yaw -90 (东)
    assert abs(server._mnw_yaw_to_mc(90) - (-90)) < 0.01
    # MNW yaw 180 (南) -> MC yaw 0 (南)
    assert abs(server._mnw_yaw_to_mc(180) - 0) < 0.01


def test_proxy_server_stats():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    stats = server.get_stats()
    assert 'state' in stats
    assert 'connections_active' in stats
    assert 'packets_mnw_to_mc' in stats
    assert 'packets_mc_to_mnw' in stats
    assert stats['connections_active'] == 0
    assert stats['packets_mnw_to_mc'] == 0


def test_mc_client_login_events():
    from src.mcp_mc.client import MCPMinecraftClient, MCClientConfig
    client = MCPMinecraftClient(MCClientConfig())
    assert 'position' in client._event_handlers
    assert client._login_event is None
    assert client._join_event is None


def test_mc_keepalive_decode():
    from src.mcp_mc.protocol.packets import KeepAlivePacket, PacketID
    from src.mcp_mc.protocol.types import VarInt, MCLong
    keepalive_id = 123456789
    packet = KeepAlivePacket.decode(VarInt.encode(PacketID.KEEP_ALIVE_PACKET) + MCLong.encode(keepalive_id))
    assert packet.keep_alive_id == keepalive_id
    assert packet.data['keep_alive_id'] == keepalive_id


def test_proxy_block_command_mapping():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    assert server._mnw_block_to_mc_command_name(104, 0) == "minecraft:air"
    assert server._mnw_block_to_mc_command_name(104, 1).startswith("minecraft:")
    assert server._mnw_block_to_mc_command_name(999999, 1) == "minecraft:air"


def test_proxy_chat_payload_build():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    payload = server._build_mnw_chat_payload("TestSpeaker", "Hello World")
    assert len(payload) > 0
    proto = server._load_mini_proto()
    if proto and hasattr(proto, 'hc'):
        msg_class = getattr(proto.hc, 'PB_ChatHC', None)
        if msg_class:
            msg = msg_class()
            msg.ParseFromString(payload)
            assert msg.Speaker == "TestSpeaker"
            assert msg.Content == "Hello World"


def test_proxy_move_payload_build():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    payload = server._build_mnw_move_payload(123, 10.5, 64.0, -20.5)
    assert len(payload) > 0
    proto = server._load_mini_proto()
    if proto and hasattr(proto, 'hc'):
        msg_class = getattr(proto.hc, 'PB_MoveSyncHC', None)
        if msg_class:
            msg = msg_class()
            msg.ParseFromString(payload)
            assert msg.id == 123
            assert msg.accept == True
            assert msg.pos is not None


def test_proxy_enter_world_payload_build():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    payload = server._build_mnw_enter_world_payload(
        uin=10001,
        name="TestPlayer",
        x=10.0,
        y=64.0,
        z=20.0,
        world_name="TestWorld"
    )
    assert len(payload) > 0
    proto = server._load_mini_proto()
    if proto and hasattr(proto, 'hc'):
        msg_class = getattr(proto.hc, 'PB_RoleEnterWorldHC', None)
        if msg_class:
            msg = msg_class()
            msg.ParseFromString(payload)
            assert msg.Uin == 10001
            assert msg.PlayerInfo is not None
            assert msg.WorldDesc is not None


def test_proxy_protobuf_parse():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    from src.mcp_protocol.codec import MCPPacket
    from src.mcp_protocol.msgcode_registry import PacketDirection
    server = MnMCPProxyServer(ProxyServerConfig())
    proto = server._load_mini_proto()
    if proto and hasattr(proto, 'hc'):
        chat_class = getattr(proto.hc, 'PB_ChatHC', None)
        if chat_class:
            chat_msg = chat_class(ChatType=0, Uin=0, Speaker="Tester", Content="Test message", Language=1, Extend='{}')
            data = chat_msg.SerializeToString()
            packet = MCPPacket(msg_code=4011, data=data, direction=PacketDirection.SERVER_TO_CLIENT)
            parsed = server._parse_mnw_protobuf(packet)
            assert parsed is not None
            assert parsed.Speaker == "Tester"
            assert parsed.Content == "Test message"


def test_proxy_face_mapping():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    assert server._mnw_face_to_mc(0) == 5
    assert server._mnw_face_to_mc(1) == 4
    assert server._mnw_face_to_mc(2) == 2
    assert server._mnw_face_to_mc(3) == 3
    assert server._mnw_face_to_mc(4) == 0
    assert server._mnw_face_to_mc(5) == 1
    assert server._mc_face_to_mnw(0) == 4
    assert server._mc_face_to_mnw(1) == 5
    assert server._mc_face_to_mnw(2) == 2
    assert server._mc_face_to_mnw(3) == 3
    assert server._mc_face_to_mnw(4) == 1
    assert server._mc_face_to_mnw(5) == 0


def test_proxy_block_interact_parse():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    from src.mcp_protocol.codec import MCPPacket
    from src.mcp_protocol.msgcode_registry import PacketDirection
    server = MnMCPProxyServer(ProxyServerConfig())
    proto = server._load_mini_proto()
    if proto and hasattr(proto, 'ch') and hasattr(proto, 'common'):
        interact_class = getattr(proto.ch, 'PB_BlockInteractCH', None)
        vector3_class = getattr(proto.common, 'PB_Vector3', None)
        if interact_class and vector3_class:
            interact_msg = interact_class(
                face=1,
                colptx=0, colpty=0, colptz=0,
                blockpos=vector3_class(X=-100, Y=6400, Z=200)
            )
            data = interact_msg.SerializeToString()
            packet = MCPPacket(msg_code=3002, data=data, direction=PacketDirection.CLIENT_TO_SERVER)
            parsed = server._parse_mnw_protobuf(packet)
            assert parsed is not None
            assert parsed.face == 1
            assert parsed.blockpos is not None
            assert parsed.blockpos.X == -100
            assert parsed.blockpos.Y == 6400
            assert parsed.blockpos.Z == 200


def test_proxy_block_punch_parse():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    from src.mcp_protocol.codec import MCPPacket
    from src.mcp_protocol.msgcode_registry import PacketDirection
    server = MnMCPProxyServer(ProxyServerConfig())
    proto = server._load_mini_proto()
    if proto and hasattr(proto, 'ch') and hasattr(proto, 'common'):
        punch_class = getattr(proto.ch, 'PB_BlockPunchCH', None)
        vector3_class = getattr(proto.common, 'PB_Vector3', None)
        if punch_class and vector3_class:
            punch_msg = punch_class(
                status=0,
                face=1,
                digmethod=0,
                blockpos=vector3_class(X=-100, Y=6400, Z=200),
                vehicleObjID=0,
                clienttick=0
            )
            data = punch_msg.SerializeToString()
            packet = MCPPacket(msg_code=3003, data=data, direction=PacketDirection.CLIENT_TO_SERVER)
            parsed = server._parse_mnw_protobuf(packet)
            assert parsed is not None
            assert parsed.status == 0
            assert parsed.face == 1
            assert parsed.blockpos is not None


def test_proxy_item_use_parse():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    from src.mcp_protocol.codec import MCPPacket
    from src.mcp_protocol.msgcode_registry import PacketDirection
    server = MnMCPProxyServer(ProxyServerConfig())
    proto = server._load_mini_proto()
    if proto and hasattr(proto, 'ch') and hasattr(proto, 'common'):
        item_class = getattr(proto.ch, 'PB_ItemUseCH', None)
        vector3_class = getattr(proto.common, 'PB_Vector3', None)
        if item_class and vector3_class:
            item_msg = item_class(
                itemid=100,
                status=0,
                shift=0,
                CurSpread=0.0,
                CurYaw=0.0,
                CurPitch=0.0,
                CurPos=vector3_class(X=0, Y=0, Z=0),
                usetick=0,
                itemindex=0,
                fireInterval=0,
                PickResultPos=vector3_class(X=0, Y=0, Z=0),
                PickResultFace=0
            )
            data = item_msg.SerializeToString()
            packet = MCPPacket(msg_code=3004, data=data, direction=PacketDirection.CLIENT_TO_SERVER)
            parsed = server._parse_mnw_protobuf(packet)
            assert parsed is not None
            assert parsed.itemid == 100
            assert parsed.status == 0


test("ProxyServerV2 导入", test_proxy_server_import)
test("ProxyServerV2 配置", test_proxy_server_config)
test("ProxyServerV2 创建", test_proxy_server_create)
test("ProxyServerV2 会话管理", test_proxy_server_session)
test("ProxyServerV2 Yaw 转换", test_proxy_server_yaw_conversion)
test("ProxyServerV2 统计信息", test_proxy_server_stats)
test("MC 客户端登录事件", test_mc_client_login_events)
test("MC 心跳解码", test_mc_keepalive_decode)
test("ProxyServerV2 方块命令映射", test_proxy_block_command_mapping)
test("ProxyServerV2 聊天 protobuf 构造", test_proxy_chat_payload_build)
test("ProxyServerV2 移动 protobuf 构造", test_proxy_move_payload_build)
test("ProxyServerV2 进世界 protobuf 构造", test_proxy_enter_world_payload_build)
test("ProxyServerV2 protobuf 解析", test_proxy_protobuf_parse)
test("ProxyServerV2 面映射", test_proxy_face_mapping)
test("ProxyServerV2 方块交互 protobuf 解析", test_proxy_block_interact_parse)
test("ProxyServerV2 方块挖掘 protobuf 解析", test_proxy_block_punch_parse)
test("ProxyServerV2 物品使用 protobuf 解析", test_proxy_item_use_parse)


# ============================================================
# 汇总
# ============================================================
print("\n" + "=" * 60)
print("离线测试结果汇总".center(60))
print("=" * 60)
total = PASS + FAIL
print(f"\n总测试: {total}")
print(f"通过: {PASS}")
print(f"失败: {FAIL}")
print(f"通过率: {PASS / total * 100:.1f}%")

if FAIL == 0:
    print("\n✓ 所有离线测试通过!")
else:
    print(f"\n✗ {FAIL} 个测试失败")

print("\n" + "=" * 60)

sys.exit(0 if FAIL == 0 else 1)
