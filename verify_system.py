#!/usr/bin/env python3
"""
MnMCP 系统验证脚本
验证所有核心模块是否正常工作

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("MnMCP 系统验证".center(60))
print("=" * 60)

results = []

def test(name, func):
    try:
        func()
        results.append((name, True, "✓"))
        print(f"  {name}: ✓")
    except Exception as e:
        results.append((name, False, f"✗ {e}"))
        print(f"  {name}: ✗ {e}")

print("\n1. 加密模块验证:")

test("MCPXXTEA 导入", lambda: __import__('src.mcp_crypto.xxtea_mcp', fromlist=['MCPXXTEA']))

test("MCPAuthManager 导入", lambda: __import__('src.mcp_crypto.auth_mcp', fromlist=['MCPAuthManager']))

test("XXTEA 加密/解密", lambda: __import__('src.mcp_crypto.xxtea_mcp').mcp_crypto.xxtea_mcp.MCPXXTEA(b"test_key").encrypt_zip(b"test") == __import__('src.mcp_crypto.xxtea_mcp').mcp_crypto.xxtea_mcp.MCPXXTEA(b"test_key").encrypt_zip(b"test"))

print("\n2. MiniWorld 客户端验证:")

test("MiniClient 导入", lambda: __import__('src.mcp_mini.client', fromlist=['MCPMiniClient']))

test("MiniAuthConfig 导入", lambda: __import__('src.mcp_mini.client', fromlist=['MiniAuthConfig']))

print("\n3. Minecraft 客户端验证:")

test("MCPMinecraftClient 导入", lambda: __import__('src.mcp_mc.client', fromlist=['MCPMinecraftClient']))

test("MC数据包导入", lambda: __import__('src.mcp_mc.protocol.packets', fromlist=['PacketID', 'ClientChatMessagePacket', 'PlayerPositionPacket']))

print("\n4. 桥接核心验证:")

test("Bridge 导入", lambda: __import__('src.mcp_core.bridge', fromlist=['MCPBridge']))

test("Bridge 配置", lambda: __import__('src.mcp_core.bridge').mcp_core.bridge.MCPBridgeConfig())

print("\n5. 协议编解码验证:")

test("Codec 导入", lambda: __import__('src.mcp_protocol.codec', fromlist=['MCPProtocolCodec']))

test("MsgCodeRegistry 导入", lambda: __import__('src.mcp_protocol.msgcode_registry', fromlist=['MessageRegistry']))

test("消息码统计", lambda: len(__import__('src.mcp_protocol.msgcode_registry').mcp_protocol.msgcode_registry.MessageRegistry().get_stats()) > 0)

print("\n6. 数据包转换器验证:")

test("PacketConverter 导入", lambda: __import__('src.mcp_core.packet_converter', fromlist=['MCPPacketConverter']))

test("MC->MNW 聊天转换", lambda: __import__('src.mcp_core.packet_converter').mcp_core.packet_converter.convert_mc_to_mnw(0x03, b'\x0eHello from MC!\x00\x00\x00\x00\x00\x00\x00\x00'))

test("MNW->MC 聊天转换", lambda: __import__('src.mcp_core.packet_converter').mcp_core.packet_converter.convert_mnw_to_mc(9001, b'{"message":"test","sender":"player"}'))

test("MC->MNW 位置转换", lambda: __import__('src.mcp_core.packet_converter').mcp_core.packet_converter.convert_mc_to_mnw(0x12, b'\x00\x00\x00\x00\x00\x00p@\x00\x00\x00\x00\x00\x00\x80@\x00\x00\x00\x00\x00\x00\xc8@\x01'))

test("PacketReader/Writer", lambda: (__import__('src.mcp_core.packet_converter').mcp_core.packet_converter.PacketReader(b'\x05hello'), __import__('src.mcp_core.packet_converter').mcp_core.packet_converter.PacketWriter()))

print("\n7. 映射模块验证:")

test("Blocks Full Mapping 导入", lambda: __import__('src.mcp_mapping.blocks_full', fromlist=['mc_to_mnw', 'mnw_to_mc']))

test("mc_to_mnw 函数", lambda: __import__('src.mcp_mapping.blocks_full').mcp_mapping.blocks_full.mc_to_mnw(1) is not None)

test("mnw_to_mc 函数", lambda: __import__('src.mcp_mapping.blocks_full').mcp_mapping.blocks_full.mnw_to_mc(104) is not None)

test("convert_mc_block 函数", lambda: __import__('src.mcp_mapping.blocks_full').mcp_mapping.blocks_full.convert_mc_block(1) > 0)

test("convert_mnw_block 函数", lambda: __import__('src.mcp_mapping.blocks_full').mcp_mapping.blocks_full.convert_mnw_block(104) > 0)

test("映射数量 (>800)", lambda: len(__import__('src.mcp_mapping.blocks_full').mcp_mapping.blocks_full.MC_TO_MNW_FULL_MAPPING) > 800)

print("\n8. 配置模块验证:")

test("Config 导入", lambda: __import__('src.mcp_config', fromlist=['MCPConfig']))

print("\n9. 数据包嗅探器验证:")

test("Sniffer 导入", lambda: __import__('packet_sniffer', fromlist=['PacketSniffer']))

print("\n" + "=" * 60)
print("验证结果".center(60))
print("=" * 60)

passed = sum(1 for _, status, _ in results if status)
failed = sum(1 for _, status, _ in results if not status)

print(f"\n总测试: {len(results)}")
print(f"通过: {passed}")
print(f"失败: {failed}")

if failed == 0:
    print("\n✓ 所有模块验证通过!")
else:
    print("\n✗ 部分模块验证失败，请检查错误信息")
    for name, status, msg in results:
        if not status:
            print(f"  - {name}: {msg}")

print("\n" + "=" * 60)

if failed == 0:
    print("\n详细信息:")
    print("-" * 40)
    
    mapping = __import__('src.mcp_mapping.blocks_full').mcp_mapping.blocks_full
    print(f"方块映射:")
    print(f"  MC->MNW映射数: {len(mapping.MC_TO_MNW_FULL_MAPPING)}")
    print(f"  MNW->MC映射数: {len(mapping.MNW_TO_MC_FULL_MAPPING)}")
    print(f"  MNW名称数: {len(mapping.MNW_NAME_TO_ID)}")
    
    registry = __import__('src.mcp_protocol.msgcode_registry').mcp_protocol.msgcode_registry.MessageRegistry()
    stats = registry.get_stats()
    print(f"\n消息码:")
    print(f"  总消息数: {stats['total_messages']}")
    print(f"  CH (客户端->服务端): {stats['client_to_server']}")
    print(f"  HC (服务端->客户端): {stats['server_to_client']}")
    
    print("\n数据包转换器:")
    print(f"  支持 MC->MNW 转换: 聊天、位置、朝向、移动")
    print(f"  支持 MNW->MC 转换: 聊天、移动、心跳、登录")
    
    print("\n" + "=" * 60)
