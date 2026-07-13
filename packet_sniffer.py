#!/usr/bin/env python3
"""
MnMCP v3 - 数据包嗅探器
用于连接MiniWorld服务器并解析实时数据包

功能:
- 连接真实的MiniWorld服务器
- 嗅探并解码所有收到的数据包
- 显示消息名称、方向、大小
- 支持Protobuf动态解析
- 保存原始数据包到文件

使用方法:
    python packet_sniffer.py --host <服务器IP> --port <端口> --uin <账号> --passwd <密码>

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import argparse
import asyncio
import logging
import struct
import zlib
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('packet_sniffer.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    import aiorak
    from aiorak import Connection, Reliability, Priority
    AIORAK_AVAILABLE = True
except ImportError:
    AIORAK_AVAILABLE = False

try:
    import blackboxprotobuf
    BLACKBOX_AVAILABLE = True
except ImportError:
    BLACKBOX_AVAILABLE = False
    logger.warning("blackboxprotobuf not available, cannot parse protobuf")


@dataclass
class SnifferConfig:
    host: str = "127.0.0.1"
    port: int = 19132
    uin: str = ""
    passwd: str = ""
    device_id: str = ""
    version: str = "1.55.0"
    save_packets: bool = False
    output_file: str = "packets_dump.json"
    log_level: str = "DEBUG"
    max_packets: int = 1000


@dataclass
class PacketRecord:
    timestamp: str = ""
    msg_code: int = 0
    msg_name: str = ""
    direction: str = ""
    size: int = 0
    flags: int = 0
    session_id: int = 0
    is_compressed: bool = False
    is_encrypted: bool = False
    protobuf_data: Optional[Dict[str, Any]] = None
    raw_hex: str = ""


class MiniPacketCodec:
    """MiniWorld 数据包编解码器"""
    
    HEADER_SIZE = 7
    
    def __init__(self, xxtea_key: Optional[bytes] = None):
        self.xxtea_key = xxtea_key
    
    def decode(self, raw_data: bytes) -> Optional[Dict[str, Any]]:
        if len(raw_data) < self.HEADER_SIZE:
            return None
        
        try:
            msg_code, flags, session_id = struct.unpack('<HBI', raw_data[:self.HEADER_SIZE])
            data = raw_data[self.HEADER_SIZE:]
            
            is_compressed = bool(flags & 0x01)
            is_encrypted = bool(flags & 0x02)
            
            if is_encrypted and self.xxtea_key:
                data = self._xxtea_decrypt(data)
            elif is_encrypted:
                logger.warning("Encrypted packet but no key provided")
            
            if is_compressed:
                try:
                    data = zlib.decompress(data)
                except zlib.error:
                    logger.warning("Failed to decompress packet")
            
            return {
                'msg_code': msg_code,
                'flags': flags,
                'session_id': session_id,
                'data': data,
                'is_compressed': is_compressed,
                'is_encrypted': is_encrypted
            }
        except Exception as e:
            logger.error(f"Decode error: {e}")
            return None
    
    def _xxtea_decrypt(self, data: bytes) -> bytes:
        try:
            from src.mcp_crypto.xxtea_mcp import MCPXXTEA
            xxtea = MCPXXTEA(self.xxtea_key)
            return xxtea.decrypt_unzip(data)
        except Exception as e:
            logger.error(f"XXTEA decrypt error: {e}")
            return data


class MessageNameResolver:
    """消息名称解析器"""
    
    MSG_CODE_TO_NAME = {
        11: "PB_HeartBeatCH",
        12: "PB_HeartBeatHC",
        101: "PB_SyncChunkDataCH",
        102: "PB_SyncChunkDataHC",
        201: "PB_SpawnPlayerCH",
        202: "PB_SpawnPlayerHC",
        301: "PB_ChatContentCH",
        302: "PB_ChatContentHC",
        401: "PB_MovePlayerCH",
        402: "PB_MovePlayerHC",
        501: "PB_BlockChangeCH",
        502: "PB_BlockChangeHC",
        601: "PB_PlayerActionCH",
        602: "PB_PlayerActionHC",
        701: "PB_UseItemCH",
        702: "PB_UseItemHC",
        801: "PB_PingCH",
        802: "PB_PongHC",
        901: "PB_LoginRequestCH",
        902: "PB_LoginResponseHC",
        1001: "PB_EnterRoomCH",
        1002: "PB_EnterRoomHC",
    }
    
    @classmethod
    def get_name(cls, msg_code: int) -> str:
        return cls.MSG_CODE_TO_NAME.get(msg_code, f"Unknown_{msg_code}")


class PacketSniffer:
    """数据包嗅探器"""
    
    def __init__(self, config: SnifferConfig):
        self.config = config
        self.codec = MiniPacketCodec(xxtea_key=b"miniworld")
        self.connection: Optional[Any] = None
        self._running = False
        self._packet_count = 0
        self._packets: List[PacketRecord] = []
        self._stats: Dict[str, int] = {}
    
    async def connect(self):
        """连接到服务器"""
        logger.info(f"Connecting to {self.config.host}:{self.config.port}...")
        
        if AIORAK_AVAILABLE:
            try:
                self.connection = await aiorak.connect(self.config.host, self.config.port)
                logger.info("Connected successfully")
                return True
            except Exception as e:
                logger.error(f"Connection failed: {e}")
                return False
        else:
            logger.error("aiorak is required for packet sniffing")
            return False
    
    async def sniff(self):
        """开始嗅探"""
        self._running = True
        logger.info("Starting packet sniffing...")
        
        try:
            while self._running and self._packet_count < self.config.max_packets:
                try:
                    if AIORAK_AVAILABLE and self.connection:
                        data = await self.connection.recv()
                    else:
                        await asyncio.sleep(0.01)
                        continue
                    
                    if not data:
                        continue
                    
                    await self._process_packet(data)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Sniffing error: {e}")
                    await asyncio.sleep(0.1)
                    
        finally:
            self._running = False
            await self._save_packets()
            self._print_summary()
    
    async def _process_packet(self, raw_data: bytes):
        """处理收到的数据包"""
        self._packet_count += 1
        
        decoded = self.codec.decode(raw_data)
        
        if not decoded:
            logger.debug(f"Raw packet #{self._packet_count}: {len(raw_data)} bytes")
            return
        
        msg_code = decoded['msg_code']
        msg_name = MessageNameResolver.get_name(msg_code)
        
        record = PacketRecord(
            timestamp=datetime.now().isoformat(),
            msg_code=msg_code,
            msg_name=msg_name,
            direction="Server->Client",
            size=len(raw_data),
            flags=decoded['flags'],
            session_id=decoded['session_id'],
            is_compressed=decoded['is_compressed'],
            is_encrypted=decoded['is_encrypted'],
            raw_hex=raw_data.hex()[:100] + "..." if len(raw_data) > 50 else raw_data.hex()
        )
        
        if BLACKBOX_AVAILABLE:
            try:
                protobuf_data, typedef = blackboxprotobuf.decode_message(decoded['data'])
                record.protobuf_data = protobuf_data
            except Exception as e:
                logger.debug(f"Failed to parse protobuf for {msg_name}: {e}")
        
        self._packets.append(record)
        
        self._stats[msg_name] = self._stats.get(msg_name, 0) + 1
        
        logger.info(
            f"[{self._packet_count:4d}] {msg_name} "
            f"(code={msg_code}, size={len(raw_data)} bytes, "
            f"compressed={decoded['is_compressed']}, "
            f"encrypted={decoded['is_encrypted']})"
        )
        
        if record.protobuf_data:
            logger.debug(f"  Protobuf: {json.dumps(record.protobuf_data, ensure_ascii=False)[:200]}")
    
    async def _save_packets(self):
        """保存数据包到文件"""
        if self.config.save_packets and self._packets:
            try:
                with open(self.config.output_file, 'w', encoding='utf-8') as f:
                    json.dump([r.__dict__ for r in self._packets], f, 
                              ensure_ascii=False, indent=2)
                logger.info(f"Saved {len(self._packets)} packets to {self.config.output_file}")
            except Exception as e:
                logger.error(f"Failed to save packets: {e}")
    
    def _print_summary(self):
        """打印统计摘要"""
        print("\n" + "=" * 60)
        print("Packet Sniffer Summary")
        print("=" * 60)
        print(f"Total packets captured: {self._packet_count}")
        print(f"Unique message types: {len(self._stats)}")
        print("\nMessage distribution:")
        for msg_name, count in sorted(self._stats.items(), key=lambda x: -x[1]):
            print(f"  {msg_name}: {count}")
        print("=" * 60)
    
    async def disconnect(self):
        """断开连接"""
        self._running = False
        if AIORAK_AVAILABLE and self.connection:
            self.connection.disconnect()
        logger.info("Disconnected")


async def main():
    parser = argparse.ArgumentParser(description="MnMCP Packet Sniffer")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=19132, help="Server port")
    parser.add_argument("--uin", default="", help="UIN for authentication")
    parser.add_argument("--passwd", default="", help="Password for authentication")
    parser.add_argument("--device-id", default="", help="Device ID")
    parser.add_argument("--version", default="1.55.0", help="Client version")
    parser.add_argument("--save", action="store_true", help="Save packets to file")
    parser.add_argument("--output", default="packets_dump.json", help="Output file")
    parser.add_argument("--max-packets", type=int, default=1000, help="Max packets to capture")
    
    args = parser.parse_args()
    
    config = SnifferConfig(
        host=args.host,
        port=args.port,
        uin=args.uin,
        passwd=args.passwd,
        device_id=args.device_id,
        version=args.version,
        save_packets=args.save,
        output_file=args.output,
        max_packets=args.max_packets
    )
    
    sniffer = PacketSniffer(config)
    
    print("=" * 60)
    print("MnMCP v3 - Packet Sniffer")
    print("=" * 60)
    print(f"Target: {config.host}:{config.port}")
    print(f"Version: {config.version}")
    print(f"Max packets: {config.max_packets}")
    print(f"Save to file: {config.save_packets}")
    print("=" * 60)
    
    try:
        if await sniffer.connect():
            await sniffer.sniff()
        else:
            print("Failed to connect")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        await sniffer.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
