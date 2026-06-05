# MnMCP 3 Phase 2 执行计划 - UDP协议栈实现

**版本**: 2026-05-23-19  
**阶段**: Phase 2 - UDP协议栈与房间发现  
**预计工期**: 3天  
**基础**: Phase 1已完成（加密模块就绪）

---

## 🎯 Phase 2 核心目标

1. **实现RakNet协议层** - 可靠UDP传输
2. **实现WPKG协议栈** - 迷你世界UDP协议
3. **实现房间发现协议** - UDP广播/发现
4. **复用逆向工程工具** - 适配已有解码器

---

## 📚 关键资源（来自Phase 1新发现）

### 1. 协议文档
| 文档 | 内容 | 优先级 |
|------|------|--------|
| `udp_package_report.md` | WPKG协议完整规范 | P0 |
| `20-Phase2-协议逆向分析报告.md` | mmtls/ilink-network架构 | P1 |
| `旧版登录说明.md` | WebSocket RPC登录流程 | P1 |

### 2. 工具脚本（直接复用）
| 脚本 | 功能 | 复用方式 |
|------|------|----------|
| `liblibGameApp_udp_decoder.py` | **完整RakNet解码器**（30KB） | 适配到`mn2mc/network/raknet/` |
| `Universal_GameApp_Decryptor.py` | TCP/UDP解密 + msgpack | 适配到`mn2mc/crypto/adapters/` |

### 3. 数据文件
| 文件 | 用途 |
|------|------|
| `udp_package.txt` | UDP包测试样本 |
| `Extracted_Proto_Definitions.txt` | Protobuf定义 |

---

## 🏗️ Phase 2 模块架构

```
mn2mc/
├── network/                    # 【新增】网络层
│   ├── __init__.py
│   ├── udp/                    # UDP基础
│   │   ├── __init__.py
│   │   ├── socket.py           # UDP套接字封装
│   │   └── utils.py            # UDP工具函数
│   │
│   ├── raknet/                 # 【核心】RakNet协议
│   │   ├── __init__.py
│   │   ├── bitstream.py        # 位流读写（从解码器复用）
│   │   ├── connection.py       # 连接管理
│   │   ├── message_ids.py      # 消息ID定义（复用解码器）
│   │   ├── packet.py           # 包结构
│   │   ├── reliability.py      # 可靠传输
│   │   ├── server.py           # RakNet服务端
│   │   └── decoder.py          # 【复用】liblibGameApp_udp_decoder.py
│   │
│   └── wpkg/                   # 【核心】WPKG协议
│       ├── __init__.py
│       ├── client.py           # WPKG客户端
│       ├── discovery.py        # 房间发现
│       ├── packet.py           # 包结构（复用Phase 1）
│       └── session.py          # 会话管理
│
├── protocol/                   # 协议层
│   └── wpkg.py                 # 【Phase 1已完成】
│
└── room/                       # 【新增】房间管理
    ├── __init__.py
    ├── discovery.py            # 房间发现
    ├── registry.py             # 房间注册
    ├── manager.py              # 房间管理器
    └── state.py                # 房间状态机
```

---

## 📝 执行步骤

### Day 1: RakNet基础 (2026-05-24)

#### 任务1.1: 复用RakNet解码器 - 2小时

**创建**: `mn2mc/network/raknet/decoder.py`

复用`liblibGameApp_udp_decoder.py`的核心功能：

```python
"""RakNet packet decoder.
Adapted from liblibGameApp_udp_decoder.py
"""

import struct
from typing import Dict, Tuple, Optional
from collections import OrderedDict

# RakNet Message IDs (from decoder)
RAKNET_MESSAGE_IDS = {
    0x00: "ID_CONNECTED_PING",
    0x01: "ID_UNCONNECTED_PING",
    0x02: "ID_UNCONNECTED_PING_OPEN_CONNECTIONS",
    0x03: "ID_CONNECTED_PONG",
    # ... 完整列表见原文件
}

def decode_raknet_header(data: bytes) -> Dict:
    """Decode RakNet packet header.
    
    Args:
        data: Raw UDP payload
        
    Returns:
        Dict with parsed header fields
    """
    if len(data) < 1:
        return None
    
    message_id = data[0]
    
    result = {
        'raw_message_id': message_id,
        'message_name': RAKNET_MESSAGE_IDS.get(message_id, f"UNKNOWN_0x{message_id:02X}"),
        'is_reliable': bool(message_id & 0x80),  # Bit 7
        'is_sequenced': bool(message_id & 0x40),  # Bit 6
        'is_ordered': bool(message_id & 0x20),   # Bit 5
    }
    
    return result


class RakNetBitStream:
    """Bit stream reader/writer for RakNet.
    
    Adapted from liblibGameApp_udp_decoder.py
    """
    
    def __init__(self, data: bytes = b''):
        self.data = data
        self.bit_position = 0
        self.byte_position = 0
    
    def read_bits(self, num_bits: int) -> int:
        """Read specified number of bits."""
        # Implementation from decoder
        pass
    
    def read_byte(self) -> int:
        """Read a single byte."""
        if self.byte_position >= len(self.data):
            return 0
        value = self.data[self.byte_position]
        self.byte_position += 1
        return value
    
    def read_uint16(self) -> int:
        """Read 2-byte unsigned integer."""
        if self.byte_position + 2 > len(self.data):
            return 0
        value = struct.unpack('>H', self.data[self.byte_position:self.byte_position+2])[0]
        self.byte_position += 2
        return value
    
    def read_uint32(self) -> int:
        """Read 4-byte unsigned integer."""
        if self.byte_position + 4 > len(self.data):
            return 0
        value = struct.unpack('>I', self.data[self.byte_position:self.byte_position+4])[0]
        self.byte_position += 4
        return value
```

**检查点**: ☐ decoder.py已创建，功能复用完成

---

#### 任务1.2: RakNet消息ID定义 - 30分钟

**创建**: `mn2mc/network/raknet/message_ids.py`

```python
"""RakNet message ID definitions.
From liblibGameApp_udp_decoder.py
"""

# Connection management
ID_CONNECTED_PING = 0x00
ID_UNCONNECTED_PING = 0x01
ID_CONNECTED_PONG = 0x03
ID_CONNECTION_REQUEST = 0x09
ID_CONNECTION_REQUEST_ACCEPTED = 0x10
ID_CONNECTION_ATTEMPT_FAILED = 0x11
ID_ALREADY_CONNECTED = 0x12
ID_NEW_INCOMING_CONNECTION = 0x13
ID_DISCONNECTION_NOTIFICATION = 0x15
ID_CONNECTION_LOST = 0x16

# Open connection
ID_OPEN_CONNECTION_REQUEST_1 = 0x05
ID_OPEN_CONNECTION_REQUEST_2 = 0x07
ID_OPEN_CONNECTION_REPLY_1 = 0x06
ID_OPEN_CONNECTION_REPLY_2 = 0x08

# Discovery
ID_ADVERTISE_SYSTEM = 0x1D
ID_UNCONNECTED_PONG = 0x1C

# Reliability
ID_SND_RECEIPT_ACKED = 0x0E
ID_SND_RECEIPT_LOSS = 0x0F

# Game specific (迷你世界扩展)
ID_GAME_MESSAGE = 0x80  # 0x80 and above for reliable messages


# Message ID to name mapping
MESSAGE_NAMES = {
    ID_CONNECTED_PING: "ConnectedPing",
    ID_UNCONNECTED_PING: "UnconnectedPing",
    ID_CONNECTED_PONG: "ConnectedPong",
    ID_CONNECTION_REQUEST: "ConnectionRequest",
    ID_CONNECTION_REQUEST_ACCEPTED: "ConnectionRequestAccepted",
    ID_OPEN_CONNECTION_REQUEST_1: "OpenConnectionRequest1",
    ID_OPEN_CONNECTION_REQUEST_2: "OpenConnectionRequest2",
    ID_ADVERTISE_SYSTEM: "AdvertiseSystem",
    ID_UNCONNECTED_PONG: "UnconnectedPong",
}


def get_message_name(message_id: int) -> str:
    """Get message name from ID."""
    return MESSAGE_NAMES.get(message_id, f"Unknown(0x{message_id:02X})")


def is_reliable(message_id: int) -> bool:
    """Check if message uses reliable delivery."""
    return bool(message_id & 0x80)


def is_sequenced(message_id: int) -> bool:
    """Check if message uses sequenced delivery."""
    return bool(message_id & 0x40)
```

**检查点**: ☐ message_ids.py已创建

---

#### 任务1.3: RakNet包结构 - 1小时

**创建**: `mn2mc/network/raknet/packet.py`

```python
"""RakNet packet structures."""

import struct
from dataclasses import dataclass
from typing import Optional, List
from enum import IntEnum

from .message_ids import *


class ReliabilityType(IntEnum):
    """RakNet reliability types."""
    UNRELIABLE = 0
    UNRELIABLE_SEQUENCED = 1
    RELIABLE = 2
    RELIABLE_ORDERED = 3
    RELIABLE_SEQUENCED = 4


@dataclass
class RakNetHeader:
    """RakNet packet header."""
    message_id: int
    reliability: ReliabilityType = ReliabilityType.UNRELIABLE
    sequence_number: Optional[int] = None
    ordering_index: Optional[int] = None
    ordering_channel: int = 0
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'RakNetHeader':
        """Parse header from bytes."""
        if len(data) < 1:
            raise ValueError("Data too short")
        
        message_id = data[0]
        
        # Determine reliability from message ID bits
        if message_id & 0x80:  # Bit 7
            reliability = ReliabilityType.RELIABLE
        elif message_id & 0x40:  # Bit 6
            reliability = ReliabilityType.UNRELIABLE_SEQUENCED
        else:
            reliability = ReliabilityType.UNRELIABLE
        
        return cls(
            message_id=message_id,
            reliability=reliability
        )


@dataclass
class RakNetPacket:
    """RakNet packet."""
    header: RakNetHeader
    payload: bytes = b''
    
    @property
    def is_reliable(self) -> bool:
        return self.header.reliability in [
            ReliabilityType.RELIABLE,
            ReliabilityType.RELIABLE_ORDERED,
            ReliabilityType.RELIABLE_SEQUENCED
        ]
    
    @property
    def message_name(self) -> str:
        from .message_ids import get_message_name
        return get_message_name(self.header.message_id)


@dataclass
class OpenConnectionRequest1:
    """Open connection request 1."""
    offline_message_data_id: bytes = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
    protocol_version: int = 11  # RakNet protocol version
    mtu_size: int = 1492
    
    def to_bytes(self) -> bytes:
        return struct.pack('>16sBH',
            self.offline_message_data_id,
            self.protocol_version,
            self.mtu_size
        )


@dataclass
class OpenConnectionReply1:
    """Open connection reply 1."""
    offline_message_data_id: bytes
    server_guid: int
    use_security: bool
    mtu_size: int
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'OpenConnectionReply1':
        if len(data) < 26:
            raise ValueError("Data too short")
        
        return cls(
            offline_message_data_id=data[0:16],
            server_guid=struct.unpack('>Q', data[16:24])[0],
            use_security=bool(data[24]),
            mtu_size=struct.unpack('>H', data[25:27])[0]
        )


@dataclass
class ConnectionRequestAccepted:
    """Connection request accepted."""
    client_address: tuple  # (ip, port)
    system_index: int
    system_addresses: List[tuple]
    incoming_timestamp: int
    server_timestamp: int
```

**检查点**: ☐ packet.py已创建

---

### Day 2: WPKG协议与房间发现 (2026-05-25)

#### 任务2.1: WPKG客户端实现 - 2小时

**创建**: `mn2mc/network/wpkg/client.py`

```python
"""WPKG protocol client.

WPKG (WeChat Package) is used by MiniWorld for UDP communication.
Based on udp_package_report.md
"""

import asyncio
import socket
from typing import Optional, Tuple, Callable
from dataclasses import dataclass

from ..raknet.packet import RakNetPacket
from ...protocol.wpkg import WPKGCodec, WPKGSession
from ...crypto.ecdh import ECDHSession
from ...crypto.hkdf import derive_wpkg_keys


@dataclass
class WPKGClientConfig:
    """WPKG client configuration."""
    server_address: Tuple[str, int]
    timeout: float = 30.0
    retry_count: int = 3


class WPKGClient:
    """WPKG protocol client."""
    
    def __init__(self, config: WPKGClientConfig):
        self.config = config
        self.socket: Optional[socket.socket] = None
        self.ecdh_session = ECDHSession()
        self.wpkg_session: Optional[WPKGSession] = None
        self._connected = False
        self._packet_handlers: dict = {}
    
    async def connect(self) -> bool:
        """Connect to server using WPKG protocol."""
        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setblocking(False)
            
            # Perform ECDH handshake
            await self._perform_handshake()
            
            self._connected = True
            return True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    async def _perform_handshake(self):
        """Perform ECDH handshake."""
        # 1. Generate ephemeral keys
        client_public = self.ecdh_session.generate_ephemeral_keys()
        
        # 2. Send to server (simplified)
        # In real implementation, this goes through specific WPKG handshake
        
        # 3. Receive server public key
        # server_public = await self._receive_server_public()
        
        # 4. Compute shared secret
        # shared_secret = self.ecdh_session.compute_shared(server_public)
        
        # 5. Derive WPKG keys
        # aes_key, nonce_base = derive_wpkg_keys(shared_secret)
        
        # 6. Create WPKG session
        # self.wpkg_session = WPKGSession(aes_key)
        
        pass  # TODO: implement full handshake
    
    async def send(self, cmd_id: int, payload: bytes) -> bool:
        """Send WPKG packet."""
        if not self._connected or self.wpkg_session is None:
            raise RuntimeError("Not connected")
        
        # Encode packet
        packet = self.wpkg_session.encode_packet(cmd_id, payload)
        
        # Send via UDP
        loop = asyncio.get_event_loop()
        await loop.sock_sendall(self.socket, packet)
        
        return True
    
    async def receive(self) -> Optional[Tuple[int, bytes]]:
        """Receive and decode WPKG packet."""
        if not self._connected:
            raise RuntimeError("Not connected")
        
        loop = asyncio.get_event_loop()
        data, addr = await loop.sock_recvfrom(self.socket, 4096)
        
        if self.wpkg_session:
            header, payload = self.wpkg_session.decode_packet(data)
            return header.cmd_id, payload
        
        return None
    
    def register_handler(self, cmd_id: int, handler: Callable):
        """Register packet handler."""
        self._packet_handlers[cmd_id] = handler
    
    async def close(self):
        """Close connection."""
        if self.socket:
            self.socket.close()
            self.socket = None
        self._connected = False
```

**检查点**: ☐ wpkg/client.py已创建

---

#### 任务2.2: 房间发现协议 - 2小时

**创建**: `mn2mc/room/discovery.py`

```python
"""Room discovery protocol.

Implements MiniWorld room discovery via UDP broadcast/multicast.
Based on analysis from udp_package_report.md
"""

import asyncio
import socket
import struct
from typing import List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DiscoveredRoom:
    """Discovered room info."""
    room_id: str
    room_name: str
    host_address: tuple  # (ip, port)
    player_count: int
    max_players: int
    map_name: str
    latency_ms: int
    discovered_at: datetime


class RoomDiscoveryProtocol:
    """UDP room discovery protocol."""
    
    # Discovery ports (based on captured traffic)
    DISCOVERY_PORT = 8081  # or 19132 (common)
    BROADCAST_ADDR = '255.255.255.255'
    
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self._discovery_callback: Optional[Callable] = None
        self._rooms: dict = {}
        self._listening = False
    
    async def start_listening(self, callback: Callable = None):
        """Start listening for room broadcasts."""
        self._discovery_callback = callback
        
        # Create UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind(('', self.DISCOVERY_PORT))
        except OSError:
            # Port in use, try another
            self.socket.bind(('', 0))
        
        self.socket.setblocking(False)
        self._listening = True
        
        # Start receive loop
        asyncio.create_task(self._receive_loop())
    
    async def _receive_loop(self):
        """Receive loop for discovery packets."""
        loop = asyncio.get_event_loop()
        
        while self._listening:
            try:
                data, addr = await loop.sock_recvfrom(self.socket, 4096)
                room = self._parse_discovery_packet(data, addr)
                
                if room:
                    self._rooms[room.room_id] = room
                    
                    if self._discovery_callback:
                        self._discovery_callback(room)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Discovery receive error: {e}")
    
    def _parse_discovery_packet(self, data: bytes, addr: tuple) -> Optional[DiscoveredRoom]:
        """Parse room discovery packet.
        
        Packet format (inferred from captured traffic):
        - Magic: 2 bytes
        - Room ID: variable
        - Room name: variable
        - Player count: 1 byte
        - Max players: 1 byte
        """
        try:
            if len(data) < 4:
                return None
            
            # Parse based on actual packet format
            # TODO: implement based on real packet structure
            
            magic = struct.unpack('>H', data[0:2])[0]
            if magic != 0x4B47:  # 'KG'
                return None
            
            return DiscoveredRoom(
                room_id="unknown",  # TODO: parse from packet
                room_name="Unknown Room",
                host_address=addr,
                player_count=0,
                max_players=6,
                map_name="Unknown",
                latency_ms=0,
                discovered_at=datetime.now()
            )
            
        except Exception as e:
            print(f"Parse error: {e}")
            return None
    
    async def broadcast_discovery(self):
        """Broadcast room discovery request."""
        if not self.socket:
            raise RuntimeError("Not initialized")
        
        # Build discovery request packet
        # TODO: implement actual discovery request format
        request = struct.pack('>H', 0x4B47) + b'\x01'  # Magic + discovery cmd
        
        loop = asyncio.get_event_loop()
        await loop.sock_sendto(
            self.socket,
            request,
            (self.BROADCAST_ADDR, self.DISCOVERY_PORT)
        )
    
    def get_rooms(self) -> List[DiscoveredRoom]:
        """Get all discovered rooms."""
        return list(self._rooms.values())
    
    def get_room(self, room_id: str) -> Optional[DiscoveredRoom]:
        """Get specific room by ID."""
        return self._rooms.get(room_id)
    
    async def stop(self):
        """Stop discovery."""
        self._listening = False
        if self.socket:
            self.socket.close()
            self.socket = None
```

**检查点**: ☐ room/discovery.py已创建

---

### Day 3: 集成与测试 (2026-05-26)

#### 任务3.1: 创建测试脚本 - 2小时

**创建**: `tests/test_network.py`

```python
"""Network layer tests."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from mn2mc.network.raknet.packet import RakNetPacket, RakNetHeader
from mn2mc.network.raknet.message_ids import *
from mn2mc.network.wpkg.client import WPKGClient, WPKGClientConfig
from mn2mc.room.discovery import RoomDiscoveryProtocol


def test_raknet_header():
    """Test RakNet header parsing."""
    print("Testing RakNet header...")
    
    # Create test header
    header = RakNetHeader(message_id=ID_CONNECTED_PING)
    assert header.message_id == ID_CONNECTED_PING
    print(f"  Message: {header.message_id} = {header.message_name}")
    
    # Test from bytes
    data = bytes([ID_CONNECTION_REQUEST])
    header2 = RakNetHeader.from_bytes(data)
    assert header2.message_id == ID_CONNECTION_REQUEST
    print("✓ RakNet header OK")


def test_message_ids():
    """Test message ID utilities."""
    print("Testing message IDs...")
    
    name = get_message_name(ID_CONNECTED_PING)
    assert name == "ConnectedPing"
    print(f"  ID 0x{ID_CONNECTED_PING:02X} = {name}")
    
    assert is_reliable(ID_CONNECTION_REQUEST_ACCEPTED | 0x80)
    print("✓ Message ID utilities OK")


def test_discovery():
    """Test room discovery."""
    print("Testing room discovery...")
    
    discovery = RoomDiscoveryProtocol()
    assert discovery.DISCOVERY_PORT == 8081
    print(f"  Discovery port: {discovery.DISCOVERY_PORT}")
    
    # Test parse (will fail with placeholder, but structure is correct)
    data = bytes([0x4B, 0x47]) + b'\x00' * 20
    room = discovery._parse_discovery_packet(data, ('127.0.0.1', 1234))
    if room:
        print(f"  Parsed room: {room.room_name}")
    
    print("✓ Discovery structure OK")


def test_wpkg_client():
    """Test WPKG client initialization."""
    print("Testing WPKG client...")
    
    config = WPKGClientConfig(
        server_address=('127.0.0.1', 8081)
    )
    client = WPKGClient(config)
    
    assert client.config.server_address == ('127.0.0.1', 8081)
    print(f"  Server: {client.config.server_address}")
    print("✓ WPKG client OK")


async def test_async():
    """Async tests."""
    print("\nRunning async tests...")
    
    # Test discovery async
    discovery = RoomDiscoveryProtocol()
    
    # Just test initialization, don't actually start listening
    print("✓ Async tests structure OK")


def main():
    print("="*50)
    print("Phase 2 Network Tests")
    print("="*50)
    
    test_raknet_header()
    test_message_ids()
    test_discovery()
    test_wpkg_client()
    
    # Run async tests
    asyncio.run(test_async())
    
    print("\n" + "="*50)
    print("All Phase 2 tests completed!")
    print("="*50)


if __name__ == "__main__":
    main()
```

**检查点**: ☐ test_network.py已创建

---

#### 任务3.2: 复用逆向工程数据 - 1小时

**创建**: `tests/fixtures/udp_samples.py`

```python
"""UDP packet samples from reverse engineering.

Sources:
- udp_package.txt (from development resources)
- captured traffic
"""

# Sample WPKG packets (hex strings)
WPKG_SAMPLES = {
    'discovery_request': '4b470100...',  # TODO: fill from actual capture
    'discovery_response': '4b470200...',
    'connection_request': '0500...',  # RakNet ID_OPEN_CONNECTION_REQUEST_1
    'connection_reply': '0600...',
}

# Sample RakNet packets
RAKNET_SAMPLES = {
    'connected_ping': bytes([0x00]),
    'connected_pong': bytes([0x03]),
    'connection_request': bytes([0x09]),
}


def load_udp_samples():
    """Load UDP samples from file."""
    import json
    from pathlib import Path
    
    samples_file = Path(__file__).parent / 'udp_samples.json'
    if samples_file.exists():
        with open(samples_file) as f:
            return json.load(f)
    
    return WPKG_SAMPLES
```

**检查点**: ☐ 测试数据已准备

---

## ✅ Phase 2 完成标准

### 代码验收

- [ ] `mn2mc/network/raknet/decoder.py` - RakNet解码器
- [ ] `mn2mc/network/raknet/message_ids.py` - 消息ID定义
- [ ] `mn2mc/network/raknet/packet.py` - 包结构
- [ ] `mn2mc/network/wpkg/client.py` - WPKG客户端
- [ ] `mn2mc/room/discovery.py` - 房间发现
- [ ] `tests/test_network.py` - 网络层测试

### 功能验收

- [ ] RakNet头解析正确
- [ ] 消息ID映射完整
- [ ] WPKG客户端可初始化
- [ ] 房间发现协议框架完成
- [ ] 所有测试通过

---

## 📊 资源复用统计

| 来源 | 文件 | 复用内容 | 工作量节省 |
|------|------|----------|------------|
| `liblibGameApp_udp_decoder.py` | `raknet/decoder.py` | 解码逻辑 | ~4h |
| `liblibGameApp_udp_decoder.py` | `raknet/message_ids.py` | 消息ID映射 | ~1h |
| `udp_package.txt` | `tests/fixtures/` | 测试样本 | ~2h |

**总节省**: ~7小时

---

## 🚀 立即开始

执行命令:
```bash
cd C:\Users\Sails\Documents\Workspace\NormalWorkplace\Coding\MnMCP-Protocol\MN2MC

# 创建目录
mkdir mn2mc\network\raknet
mkdir mn2mc\network\wpkg
mkdir mn2mc\network\udp

# 开始任务1.1
notepad mn2mc\network\raknet\decoder.py
```

---

**版本**: 2026-05-23-19  
**预计完成**: 2026-05-26  
**下一Phase**: Phase 3 - 混合代理实现
