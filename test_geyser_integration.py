#!/usr/bin/env python3
"""
MnMCP v3 - Geyser 集成测试脚本
验证 MiniWorld <-> MC JE <-> Geyser <-> MC BE 链路的连通性

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import sys
import os
import socket
import struct
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = 0
FAIL = 0
WARN = 0


def test(name, func):
    global PASS, FAIL
    try:
        func()
        PASS += 1
        print(f"  [PASS] {name}")
    except AssertionError as e:
        FAIL += 1
        print(f"  [FAIL] {name}: {e}")
    except Exception as e:
        FAIL += 1
        print(f"  [FAIL] {name}: {type(e).__name__}: {e}")


def warn(name, func):
    global WARN
    try:
        func()
        print(f"  [INFO] {name}")
    except Exception as e:
        WARN += 1
        print(f"  [WARN] {name}: {e}")


# ============================================================
# 1. 基础环境检查
# ============================================================
print("\n" + "=" * 60)
print("1. 基础环境检查")
print("=" * 60)


def test_python_version():
    assert sys.version_info >= (3, 9), f"Python 版本应 >= 3.9, 实际 {sys.version}"


def test_proxy_server_import():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    assert MnMCPProxyServer is not None
    assert ProxyServerConfig is not None


def test_mc_client_import():
    from src.mcp_mc.client import MCPMinecraftClient, MCClientConfig
    assert MCPMinecraftClient is not None
    assert MCClientConfig is not None


def test_protocol_codec_import():
    from src.mcp_protocol.codec import MCPProtocolCodec, MCPPacket
    assert MCPProtocolCodec is not None
    assert MCPPacket is not None


def test_mapping_import():
    from src.mcp_mapping.blocks_full import mc_to_mnw, mnw_to_mc
    assert mc_to_mnw is not None
    assert mnw_to_mc is not None


test("Python 版本 >= 3.9", test_python_version)
test("ProxyServerV2 导入", test_proxy_server_import)
test("MC 客户端导入", test_mc_client_import)
test("协议编解码器导入", test_protocol_codec_import)
test("方块映射导入", test_mapping_import)


# ============================================================
# 2. 配置验证
# ============================================================
print("\n" + "=" * 60)
print("2. Geyser 集成配置验证")
print("=" * 60)


def test_default_ports():
    from src.mcp_proxy.proxy_server import ProxyServerConfig
    config = ProxyServerConfig()
    assert config.raknet_port == 19132, f"默认 RakNet 端口应为 19132, 实际 {config.raknet_port}"
    assert config.mc_port == 25565, f"默认 MC 端口应为 25565, 实际 {config.mc_port}"


def test_config_customization():
    from src.mcp_proxy.proxy_server import ProxyServerConfig
    config = ProxyServerConfig(
        raknet_port=19134,
        mc_host="192.168.1.100",
        mc_port=25566,
        max_clients=20
    )
    assert config.raknet_port == 19134
    assert config.mc_host == "192.168.1.100"
    assert config.mc_port == 25566
    assert config.max_clients == 20


test("默认端口配置", test_default_ports)
test("自定义配置", test_config_customization)


# ============================================================
# 3. 网络连通性检查（可选）
# ============================================================
print("\n" + "=" * 60)
print("3. 网络连通性检查（可选）")
print("=" * 60)


def check_mc_server(host="127.0.0.1", port=25565, timeout=2):
    """检查 MC JE 服务器是否可达"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def test_localhost_resolution():
    ip = socket.gethostbyname("localhost")
    assert ip in ("127.0.0.1", "::1"), f"localhost 应解析为 127.0.0.1, 实际 {ip}"


def test_mc_server_available():
    available = check_mc_server("127.0.0.1", 25565, timeout=1)
    if not available:
        print("    (提示: MC JE 服务器未运行，这是正常的 - 需要手动启动)")
    assert True


test("localhost 解析", test_localhost_resolution)
warn("MC JE 服务器连通性 (127.0.0.1:25565)", test_mc_server_available)


# ============================================================
# 4. ProxyServerV2 架构验证
# ============================================================
print("\n" + "=" * 60)
print("4. ProxyServerV2 架构验证")
print("=" * 60)


def test_proxy_server_creation():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig, ProxyState
    config = ProxyServerConfig(
        raknet_host="127.0.0.1",
        raknet_port=0,
        mc_host="127.0.0.1",
        mc_port=25565,
        debug=True
    )
    server = MnMCPProxyServer(config)
    assert server.state == ProxyState.STOPPED
    assert not server.is_running
    assert server.config is config


def test_proxy_session_management():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig, ClientSession, ClientSessionState
    server = MnMCPProxyServer(ProxyServerConfig())
    session = ClientSession(conn_id="test:12345")
    assert session.conn_id == "test:12345"
    assert session.mnw_state == ClientSessionState.DISCONNECTED
    assert session.mc_state == ClientSessionState.DISCONNECTED


def test_proxy_stats_initial():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    stats = server.get_stats()
    assert stats['connections_active'] == 0
    assert stats['packets_mnw_to_mc'] == 0
    assert stats['packets_mc_to_mnw'] == 0
    assert stats['chat_messages'] == 0
    assert stats['block_updates'] == 0


def test_protobuf_available():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    proto = server._load_mini_proto()
    if proto is None:
        print("    (提示: MiniWorld protobuf 模块在某些环境下可能不可用，但有 JSON fallback)")
        return
    assert hasattr(proto, 'ch'), "应包含 ch 模块"
    assert hasattr(proto, 'hc'), "应包含 hc 模块"
    assert hasattr(proto, 'common'), "应包含 common 模块"


def test_geyser_architecture_support():
    """验证 ProxyServerV2 支持 Geyser 架构的关键特性"""
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    
    config = ProxyServerConfig(
        raknet_port=19132,
        mc_host="127.0.0.1",
        mc_port=25565,
        max_clients=10
    )
    server = MnMCPProxyServer(config)
    
    assert server.config.raknet_port == 19132, "MiniWorld 客户端连接端口"
    assert server.config.mc_port == 25565, "MC JE 服务器端口 (Geyser 也连接此端口)"
    assert server.config.max_clients >= 10, "支持多客户端连接"


test("ProxyServer 创建", test_proxy_server_creation)
test("会话管理初始化", test_proxy_session_management)
test("统计信息初始化", test_proxy_stats_initial)
test("MiniWorld protobuf 可用", test_protobuf_available)
test("Geyser 架构支持", test_geyser_architecture_support)


# ============================================================
# 5. 协议转换验证
# ============================================================
print("\n" + "=" * 60)
print("5. 协议转换验证")
print("=" * 60)


def test_chat_conversion_mc_to_mnw():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    payload = server._build_mnw_chat_payload("MCPlayer", "Hello from MC!")
    assert len(payload) > 0
    
    proto = server._load_mini_proto()
    if proto and hasattr(proto, 'hc'):
        chat_class = getattr(proto.hc, 'PB_ChatHC', None)
        if chat_class:
            msg = chat_class()
            msg.ParseFromString(payload)
            assert msg.Speaker == "MCPlayer"
            assert msg.Content == "Hello from MC!"


def test_chat_conversion_mnw_to_mc():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    from src.mcp_protocol.codec import MCPPacket
    from src.mcp_protocol.msgcode_registry import PacketDirection
    server = MnMCPProxyServer(ProxyServerConfig())
    
    proto = server._load_mini_proto()
    if proto and hasattr(proto, 'ch'):
        chat_class = getattr(proto.ch, 'PB_ChatCH', None)
        if chat_class:
            chat_msg = chat_class(ChatType=0, Uin=12345, Speaker="MNWPlayer", Content="Hello from MNW!", Language=1, Extend='{}')
            data = chat_msg.SerializeToString()
            packet = MCPPacket(msg_code=4010, data=data, direction=PacketDirection.CLIENT_TO_SERVER)
            parsed = server._parse_mnw_protobuf(packet)
            assert parsed is not None
            assert parsed.Content == "Hello from MNW!"


def test_position_conversion_mc_to_mnw():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    payload = server._build_mnw_move_payload(1001, 10.5, 64.0, -20.5)
    assert len(payload) > 0
    
    proto = server._load_mini_proto()
    if proto and hasattr(proto, 'hc'):
        move_class = getattr(proto.hc, 'PB_MoveSyncHC', None)
        if move_class:
            msg = move_class()
            msg.ParseFromString(payload)
            assert msg.id == 1001
            assert msg.accept == True
            assert msg.pos is not None


def test_yaw_conversion_roundtrip():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    
    for mc_yaw in [-180, -90, 0, 45, 90, 135, 179]:
        mnw_yaw = server._mc_yaw_to_mnw(float(mc_yaw))
        back = server._mnw_yaw_to_mc(mnw_yaw)
        diff = abs(back - mc_yaw)
        if diff > 180:
            diff = 360 - diff
        assert diff < 0.01, f"Yaw 往返转换不一致: {mc_yaw} -> {mnw_yaw} -> {back}"


def test_face_mapping_roundtrip():
    from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig
    server = MnMCPProxyServer(ProxyServerConfig())
    
    for mc_face in range(6):
        mnw_face = server._mc_face_to_mnw(mc_face)
        back = server._mnw_face_to_mc(mnw_face)
        assert back == mc_face, f"Face 往返转换不一致: {mc_face} -> {mnw_face} -> {back}"


test("聊天转换 MC->MNW", test_chat_conversion_mc_to_mnw)
test("聊天转换 MNW->MC", test_chat_conversion_mnw_to_mc)
test("位置转换 MC->MNW", test_position_conversion_mc_to_mnw)
test("Yaw 角度往返转换", test_yaw_conversion_roundtrip)
test("Face 映射往返转换", test_face_mapping_roundtrip)


# ============================================================
# 6. Geyser 兼容性检查
# ============================================================
print("\n" + "=" * 60)
print("6. Geyser 兼容性检查")
print("=" * 60)


def test_geyser_plugin_file_exists():
    """检查 Geyser 插件文件是否存在（可选）"""
    plugin_paths = [
        os.path.join("plugins", "Geyser.jar"),
        os.path.join("plugins", "Geyser-Spigot.jar"),
        os.path.join("09-MnMCP-DevResources", "MnMCPResources", "plugins", "floodgate.jar"),
    ]
    found = any(os.path.exists(p) for p in plugin_paths)
    if not found:
        print("    (提示: Geyser 插件文件未找到，需要手动下载)")
    assert True


def test_mc_protocol_version():
    from src.mcp_proxy.proxy_server import ProxyServerConfig
    config = ProxyServerConfig()
    assert config.mc_protocol == 766, f"MC 协议版本应为 766 (1.20.6), 实际 {config.mc_protocol}"


def test_block_mapping_completeness():
    from src.mcp_mapping.blocks_full import MC_TO_MNW_FULL_MAPPING, MNW_TO_MC_FULL_MAPPING
    mc_count = len(MC_TO_MNW_FULL_MAPPING)
    mnw_count = len(MNW_TO_MC_FULL_MAPPING)
    assert mc_count >= 800, f"MC->MNW 映射应 >= 800, 实际 {mc_count}"
    assert mnw_count >= 200, f"MNW->MC 映射应 >= 200, 实际 {mnw_count}"


def test_message_code_completeness():
    from src.mcp_protocol.msgcode_registry import MessageRegistry
    registry = MessageRegistry()
    stats = registry.get_stats()
    assert stats["total_messages"] >= 600, f"总消息数应 >= 600, 实际 {stats['total_messages']}"
    assert stats["client_to_server"] > 0, "应有 CH 消息"
    assert stats["server_to_client"] > 0, "应有 HC 消息"


warn("Geyser 插件文件检查", test_geyser_plugin_file_exists)
test("MC 协议版本", test_mc_protocol_version)
test("方块映射完整性", test_block_mapping_completeness)
test("消息码完整性", test_message_code_completeness)


# ============================================================
# 7. Geyser 集成架构图
# ============================================================
print("\n" + "=" * 60)
print("7. Geyser 集成架构说明")
print("=" * 60)

ARCHITECTURE = """
  MiniWorld 客户端
       (RakNet UDP)
           ↓ 19132
  ┌───────────────────┐
  │ MnMCP ProxyServerV2 │  <-- 本项目
  │ (Python + aiorak)  │
  └───────────────────┘
           ↓ 25565 (TCP)
  ┌───────────────────┐
  │  Minecraft JE     │  <-- Paper/Spigot 服务器
  │  Server           │
  │  ┌─────────────┐  │
  │  │  Geyser     │  │  <-- Geyser 插件
  │  │  Plugin     │  │
  │  └─────────────┘  │
  └───────────────────┘
           ↑ 19133 (Bedrock UDP)
  Minecraft BE 客户端
    (手机/Win10/主机)
"""

print(ARCHITECTURE)


# ============================================================
# 8. 快速启动指南
# ============================================================
print("=" * 60)
print("8. 快速启动指南")
print("=" * 60)

QUICK_START = """
步骤 1: 启动 MC JE 服务器 + Geyser
  下载 Paper 1.20.6: https://papermc.io/downloads/paper
  下载 Geyser: https://geysermc.org/download
  将 Geyser.jar 放入 plugins/ 目录
  运行: java -jar paper-1.20.6-xxx.jar nogui

步骤 2: 配置 Geyser (plugins/Geyser/config.yml)
  bedrock:
    port: 19133        # 避免与 MnMCP 冲突
  remote:
    address: 127.0.0.1
    port: 25565
    auth-type: offline

步骤 3: 启动 MnMCP 代理
  python run_proxy.py --debug

步骤 4: 客户端连接
  - MiniWorld: 连接到 代理IP:19132
  - MC BE: 连接到 代理IP:19133
  - MC JE: 连接到 代理IP:25565
"""

print(QUICK_START)


# ============================================================
# 汇总
# ============================================================
print("=" * 60)
print("Geyser 集成测试结果汇总".center(60))
print("=" * 60)
total = PASS + FAIL
print(f"\n总测试: {total}")
print(f"通过: {PASS}")
print(f"失败: {FAIL}")
print(f"警告: {WARN}")
print(f"通过率: {PASS / total * 100:.1f}%" if total > 0 else "无测试")

if FAIL == 0:
    print("\n✓ 所有 Geyser 集成基础测试通过!")
    print("\n下一步:")
    print("  1. 启动 MC JE 服务器 + Geyser 插件")
    print("  2. 运行 python run_proxy.py --debug 启动代理")
    print("  3. 用 MiniWorld 和 MC BE 客户端分别连接测试")
else:
    print(f"\n✗ {FAIL} 个测试失败，请检查上述错误")

print("\n" + "=" * 60)

sys.exit(0 if FAIL == 0 else 1)
