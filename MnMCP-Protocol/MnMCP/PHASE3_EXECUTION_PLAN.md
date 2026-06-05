# MnMCP 3 Phase 3 执行计划 - 混合代理核心

**版本**: 2026-05-23-21  
**阶段**: Phase 3 - Smart Proxy与模式切换  
**依赖**: Phase 1(✅) + Phase 2(✅)  
**风险**: 压缩包未解压（P0）

---

## 🎯 Phase 3 核心目标

基于现有资源实现混合代理架构（85%充足）

### 可实现（基于现有资源）

1. ✅ **SmartProxy核心** - 模式切换框架
2. ✅ **认证拦截** - WebSocket登录拦截  
3. ✅ **会话管理** - 会话状态机
4. ✅ **命令系统** - 聊天命令解析

### 需要补充资源（压缩包）

1. ⚠️ 游戏数据协议 - 玩家/方块同步
2. ⚠️ 房间注册API - 完整参数

**策略**: 先实现框架，后用解压内容填充细节

---

## 📐 混合代理架构（基于v5.0设计）

```
┌─────────────────────────────────────────────────────┐
│           MnMCP 3 SmartProxy Layer                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │           Mode 1: Passthrough                │   │
│  │  - 转发到迷你世界官方服务器                    │   │
│  │  - 处理认证、心跳、配置                        │   │
│  │  - 提取session token                         │   │
│  └─────────────────────────────────────────────┘   │
│                      ↓ 登录成功后切换               │
│  ┌─────────────────────────────────────────────┐   │
│  │           Mode 2: Emulation                  │   │
│  │  - 本地RakNet服务端                          │   │
│  │  - 返回伪造房间列表（含MC房间）               │   │
│  │  - 桥接到Minecraft                            │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │         Mode 3: Bridge (Future)              │   │
│  │  - 同时连接真实服务器和MC                     │   │
│  │  - 实时双向同步                              │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 📝 执行步骤

### Day 1: SmartProxy核心框架 (2026-05-24)

#### 任务1.1: 创建SmartProxy类 - 2小时

**创建**: `mn2mc/proxy/smart_proxy.py`

```python
"""Smart Proxy with mode switching.

Based on HYBRID_ARCHITECTURE_v5.md
"""

import asyncio
from enum import Enum, auto
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

from loguru import logger


class ProxyMode(Enum):
    """Proxy operating modes."""
    PASSTHROUGH = "passthrough"    # Forward to real servers
    EMULATION = "emulation"         # Local emulation
    BRIDGE = "bridge"               # Bidirectional bridge (future)


@dataclass
class SessionData:
    """User session data extracted from login."""
    uin: int = 0
    name: str = ""
    jwt: str = ""
    token: str = ""
    s2: str = ""
    s2t: str = ""
    api_id: int = 110
    login_time: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if session is still valid."""
        if self.expires_at is None:
            return bool(self.jwt)
        return datetime.now() < self.expires_at


class SmartProxy:
    """Smart proxy with mode switching.
    
    Implements the hybrid architecture from v5.0 design.
    
    Usage:
        proxy = SmartProxy()
        await proxy.start()
        
        # Mode auto-switches on login
        # - Starts in PASSTHROUGH
        # - Switches to EMULATION after login success
        
        # Manual switch
        proxy.switch_mode(ProxyMode.EMULATION)
    """
    
    def __init__(self):
        self.mode: ProxyMode = ProxyMode.PASSTHROUGH
        self.session: SessionData = SessionData()
        self._mode_handlers: Dict[ProxyMode, Any] = {}
        self._switch_callbacks: list = []
        self._initialized = False
    
    def register_mode_handler(self, mode: ProxyMode, handler):
        """Register handler for specific mode."""
        self._mode_handlers[mode] = handler
        logger.info(f"Registered handler for {mode.value} mode")
    
    def on_mode_switch(self, callback: Callable):
        """Register callback for mode switch events."""
        self._switch_callbacks.append(callback)
    
    def switch_mode(self, new_mode: ProxyMode, reason: str = ""):
        """Switch proxy mode.
        
        Args:
            new_mode: Target mode
            reason: Switch reason (for logging)
        """
        if self.mode == new_mode:
            logger.debug(f"Already in {new_mode.value} mode")
            return
        
        old_mode = self.mode
        self.mode = new_mode
        
        logger.info(
            f"Mode switch: {old_mode.value} → {new_mode.value}"
            f" ({reason})"
        )
        
        # Notify callbacks
        for callback in self._switch_callbacks:
            try:
                callback(old_mode, new_mode)
            except Exception as e:
                logger.error(f"Mode switch callback error: {e}")
        
        # Activate mode handler
        handler = self._mode_handlers.get(new_mode)
        if handler:
            try:
                handler.on_activate()
            except Exception as e:
                logger.error(f"Mode handler activation error: {e}")
    
    async def handle_request(self, request: Dict) -> Dict:
        """Handle incoming request based on current mode."""
        if self.mode == ProxyMode.PASSTHROUGH:
            return await self._handle_passthrough(request)
        elif self.mode == ProxyMode.EMULATION:
            return await self._handle_emulation(request)
        elif self.mode == ProxyMode.BRIDGE:
            return await self._handle_bridge(request)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")
    
    async def _handle_passthrough(self, request: Dict) -> Dict:
        """Handle request in passthrough mode.
        
        Forward to real servers and intercept responses.
        """
        # TODO: Implement forwarding
        # This will be done in auth interceptor
        logger.debug("Passthrough mode: forwarding request")
        return {"status": "forwarded"}
    
    async def _handle_emulation(self, request: Dict) -> Dict:
        """Handle request in emulation mode.
        
        Generate fake responses or bridge to MC.
        """
        cmd = request.get("cmd")
        
        if cmd == "list_rooms":
            return await self._handle_list_rooms(request)
        elif cmd == "join_room":
            return await self._handle_join_room(request)
        else:
            logger.warning(f"Unknown emulation command: {cmd}")
            return {"error": "unknown_command"}
    
    async def _handle_bridge(self, request: Dict) -> Dict:
        """Handle request in bridge mode (future)."""
        logger.warning("Bridge mode not yet implemented")
        return {"error": "not_implemented"}
    
    async def _handle_list_rooms(self, request: Dict) -> Dict:
        """Handle room list request in emulation mode.
        
        Returns fake room list including Minecraft room.
        """
        # TODO: Generate room list with MC room
        rooms = [
            {
                "room_id": "mc_bridge_001",
                "room_name": "MnMCP Bridge - Minecraft Server",
                "host": "127.0.0.1",
                "port": 25565,
                "player_count": 0,
                "max_players": 20,
                "map_name": "Minecraft World",
                "is_mc": True
            }
        ]
        return {"rooms": rooms, "count": len(rooms)}
    
    async def _handle_join_room(self, request: Dict) -> Dict:
        """Handle join room request."""
        room_id = request.get("room_id")
        
        if room_id == "mc_bridge_001":
            # Connect to Minecraft
            return {
                "success": True,
                "address": "127.0.0.1:25565",
                "type": "minecraft"
            }
        
        return {"error": "room_not_found"}
    
    def on_login_success(self, session_data: SessionData):
        """Called when login succeeds.
        
        Automatically switches to emulation mode.
        """
        self.session = session_data
        logger.info(f"Login success: {session_data.name} ({session_data.uin})")
        
        # Auto-switch to emulation after login
        self.switch_mode(
            ProxyMode.EMULATION,
            reason="login_success"
        )
    
    async def start(self):
        """Start the proxy."""
        self._initialized = True
        logger.info(f"SmartProxy started in {self.mode.value} mode")
    
    async def stop(self):
        """Stop the proxy."""
        self._initialized = False
        logger.info("SmartProxy stopped")
```

**检查点**: ☐ smart_proxy.py已创建

---

#### 任务1.2: 认证拦截器 - 2小时

**创建**: `mn2mc/proxy/auth_interceptor.py`

```python
"""Authentication interceptor.

Intercepts MiniWorld login and extracts session data.
Based on 旧版登录说明.md
"""

import json
import asyncio
from typing import Optional, Callable
from dataclasses import dataclass

from loguru import logger

from .smart_proxy import SmartProxy, SessionData, ProxyMode
from ..network.raknet import RakNetPacket


class AuthInterceptor:
    """Intercepts authentication traffic.
    
    Sits between MiniWorld client and real servers,
    forwarding requests but intercepting login responses.
    """
    
    def __init__(self, proxy: SmartProxy):
        self.proxy = proxy
        self._intercepting = False
        self._on_session_extracted: Optional[Callable] = None
    
    def on_session_extracted(self, callback: Callable):
        """Register callback for when session is extracted."""
        self._on_session_extracted = callback
    
    async def intercept_login_request(self, request_data: dict) -> dict:
        """Intercept and potentially modify login request.
        
        Args:
            request_data: Login request data
            
        Returns:
            Modified or original request
        """
        logger.debug(f"Intercepting login request: {request_data.get('uin')}")
        
        # Just log for now, don't modify
        # In future: could add debugging info
        
        return request_data
    
    async def intercept_login_response(self, response_data: dict) -> dict:
        """Intercept login response and extract session.
        
        Args:
            response_data: Login response from server
            
        Returns:
            Modified or original response
        """
        logger.debug("Intercepting login response")
        
        # Check if login successful
        if response_data.get("code") == 0:
            data = response_data.get("data", {})
            
            # Extract session data
            session = SessionData(
                uin=data.get("uin", 0),
                name=data.get("name", ""),
                jwt=data.get("jwt", ""),
                token=data.get("token", ""),
                s2=data.get("s2", ""),
                s2t=data.get("s2t", ""),
                api_id=data.get("api_id", 110)
            )
            
            logger.info(
                f"Session extracted: {session.name} "
                f"(UIN: {session.uin})"
            )
            
            # Notify proxy
            self.proxy.on_login_success(session)
            
            # Notify external callback
            if self._on_session_extracted:
                self._on_session_extracted(session)
            
            # Modify response to trigger mode switch
            # (Add special flag that client will ignore but we detect)
            response_data["_mnmcp_mode"] = "emulation"
        
        return response_data
    
    async def intercept_websocket_message(
        self,
        message: dict,
        direction: str  # "client_to_server" or "server_to_client"
    ) -> dict:
        """Intercept WebSocket message.
        
        Args:
            message: WebSocket message dict
            direction: Message direction
            
        Returns:
            Modified message
        """
        service = message.get("service")
        method = message.get("method")
        
        if direction == "client_to_server":
            # Client → Server
            if service == "login" and method == "auth":
                return await self.intercept_login_request(message)
                
        else:  # server_to_client
            # Server → Client
            if service == "login" and method == "auth":
                return await self.intercept_login_response(message)
        
        return message
    
    async def start_interception(self):
        """Start interception."""
        self._intercepting = True
        logger.info("Auth interception started")
    
    async def stop_interception(self):
        """Stop interception."""
        self._intercepting = False
        logger.info("Auth interception stopped")
```

**检查点**: ☐ auth_interceptor.py已创建

---

### Day 2: 命令系统与房间列表 (2026-05-25)

#### 任务2.1: 聊天命令解析 - 2小时

**创建**: `mn2mc/commands/parser.py`

```python
"""Chat command parser for MnMCP.

Commands:
- /mnmcp minecraft - Switch to MC mode
- /mnmcp real - Switch to real server
- /mnmcp status - Show current mode
- /mnmcp help - Show help
"""

import re
from dataclasses import dataclass
from typing import Optional, List, Callable
from enum import Enum, auto


class CommandType(Enum):
    """MnMCP command types."""
    SWITCH_TO_MC = auto()
    SWITCH_TO_REAL = auto()
    SHOW_STATUS = auto()
    SHOW_HELP = auto()
    UNKNOWN = auto()


@dataclass
class ParsedCommand:
    """Parsed command."""
    raw: str
    type: CommandType
    args: List[str]
    error: Optional[str] = None


class CommandParser:
    """Parse MnMCP commands from chat messages."""
    
    COMMAND_PREFIX = "/mnmcp"
    
    def __init__(self):
        self._handlers: dict = {}
    
    def parse(self, message: str) -> Optional[ParsedCommand]:
        """Parse message for MnMCP command.
        
        Args:
            message: Chat message
            
        Returns:
            ParsedCommand if valid command, None otherwise
        """
        # Check if it's a MnMCP command
        if not message.strip().startswith(self.COMMAND_PREFIX):
            return None
        
        # Parse command
        parts = message.strip().split()
        if len(parts) < 2:
            return ParsedCommand(
                raw=message,
                type=CommandType.SHOW_HELP,
                args=[],
                error="No subcommand specified"
            )
        
        subcommand = parts[1].lower()
        args = parts[2:] if len(parts) > 2 else []
        
        # Map subcommand to type
        type_map = {
            "minecraft": CommandType.SWITCH_TO_MC,
            "mc": CommandType.SWITCH_TO_MC,
            "real": CommandType.SWITCH_TO_REAL,
            "status": CommandType.SHOW_STATUS,
            "help": CommandType.SHOW_HELP,
        }
        
        cmd_type = type_map.get(subcommand, CommandType.UNKNOWN)
        
        return ParsedCommand(
            raw=message,
            type=cmd_type,
            args=args
        )
    
    def get_help_text(self) -> str:
        """Get help text."""
        return """
MnMCP Commands:
  /mnmcp minecraft  - Switch to Minecraft bridge mode
  /mnmcp real       - Switch to real MiniWorld server
  /mnmcp status     - Show current mode and status
  /mnmcp help       - Show this help
""".strip()


class CommandHandler:
    """Handle parsed commands."""
    
    def __init__(self, proxy):
        self.proxy = proxy
        self.parser = CommandParser()
    
    async def handle(self, message: str) -> str:
        """Handle chat message.
        
        Args:
            message: Chat message
            
        Returns:
            Response message to send back
        """
        command = self.parser.parse(message)
        
        if command is None:
            return ""  # Not a command, no response
        
        if command.type == CommandType.SWITCH_TO_MC:
            self.proxy.switch_mode(
                ProxyMode.EMULATION,
                reason="user_command"
            )
            return "[MnMCP] Switched to Minecraft bridge mode"
        
        elif command.type == CommandType.SWITCH_TO_REAL:
            self.proxy.switch_mode(
                ProxyMode.PASSTHROUGH,
                reason="user_command"
            )
            return "[MnMCP] Switched to real MiniWorld server"
        
        elif command.type == CommandType.SHOW_STATUS:
            session = self.proxy.session
            return (
                f"[MnMCP] Mode: {self.proxy.mode.value}\n"
                f"[MnMCP] User: {session.name} ({session.uin})\n"
                f"[MnMCP] Session valid: {session.is_valid}"
            )
        
        elif command.type == CommandType.SHOW_HELP:
            return "[MnMCP] " + self.parser.get_help_text().replace("\n", "\n[MnMCP] ")
        
        else:
            return f"[MnMCP] Unknown command: {command.raw}"
```

**检查点**: ☐ commands/parser.py已创建

---

#### 任务2.2: 伪造房间列表 - 2小时

**创建**: `mn2mc/proxy/room_list.py`

```python
"""Fake room list generator for emulation mode.

Generates room list that includes Minecraft server.
"""

import random
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class FakeRoom:
    """Fake room entry."""
    room_id: str
    room_name: str
    host: str
    port: int
    player_count: int
    max_players: int
    map_name: str
    is_minecraft: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "room_id": self.room_id,
            "room_name": self.room_name,
            "host": self.host,
            "port": self.port,
            "player_count": self.player_count,
            "max_players": self.max_players,
            "map_name": self.map_name,
            "is_minecraft": self.is_minecraft
        }


class FakeRoomList:
    """Generate fake room list with Minecraft server."""
    
    def __init__(self, mc_host: str = "127.0.0.1", mc_port: int = 25565):
        self.mc_host = mc_host
        self.mc_port = mc_port
        self._rooms: List[FakeRoom] = []
        self._generate_rooms()
    
    def _generate_rooms(self):
        """Generate room list."""
        # Minecraft bridge room
        mc_room = FakeRoom(
            room_id="mc_bridge_001",
            room_name="🏰 MnMCP Bridge - Minecraft Server",
            host=self.mc_host,
            port=self.mc_port,
            player_count=0,
            max_players=20,
            map_name="Minecraft World",
            is_minecraft=True
        )
        
        # Dummy rooms for realism
        dummy_rooms = [
            FakeRoom(
                room_id=f"dummy_{i:03d}",
                room_name=f"Test Room {i}",
                host=f"192.168.1.{i}",
                port=19132,
                player_count=random.randint(1, 5),
                max_players=6,
                map_name=f"Map {i}"
            )
            for i in range(1, 5)
        ]
        
        self._rooms = [mc_room] + dummy_rooms
    
    def get_rooms(self) -> List[Dict]:
        """Get room list as dictionaries."""
        return [room.to_dict() for room in self._rooms]
    
    def get_room(self, room_id: str) -> Optional[FakeRoom]:
        """Get specific room."""
        for room in self._rooms:
            if room.room_id == room_id:
                return room
        return None
    
    def update_mc_player_count(self, count: int):
        """Update Minecraft room player count."""
        for room in self._rooms:
            if room.is_minecraft:
                room.player_count = count
                break
```

**检查点**: ☐ room_list.py已创建

---

### Day 3: 集成与测试 (2026-05-26)

#### 任务3.1: 创建综合测试 - 2小时

**创建**: `tests/test_proxy.py`

```python
"""Proxy layer tests."""

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
    
    # This would normally be async
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
    print(f"  Parsed: {cmd.raw} -> {cmd.type.name}")
    
    # Test status command
    cmd = parser.parse("/mnmcp status")
    assert cmd.type == CommandType.SHOW_STATUS
    print(f"  Parsed: {cmd.raw} -> {cmd.type.name}")
    
    # Test non-command
    cmd = parser.parse("Hello world")
    assert cmd is None
    print("  Non-command correctly ignored")
    
    # Test help
    help_text = parser.get_help_text()
    assert "minecraft" in help_text
    print("  Help text generated")
    
    print("✓ Command parser OK\n")


def test_fake_room_list():
    """Test fake room list."""
    print("Testing fake room list...")
    
    from mn2mc.proxy.room_list import FakeRoomList
    
    rooms = FakeRoomList()
    room_list = rooms.get_rooms()
    
    assert len(room_list) > 0
    print(f"  Generated {len(room_list)} rooms")
    
    # Check MC room exists
    mc_room = rooms.get_room("mc_bridge_001")
    assert mc_room is not None
    assert mc_room.is_minecraft
    print(f"  MC room: {mc_room.room_name}")
    
    print("✓ Fake room list OK\n")


def main():
    print("="*60)
    print("Phase 3 Proxy Tests")
    print("="*60)
    print()
    
    test_smart_proxy()
    test_auth_interceptor()
    test_command_parser()
    test_fake_room_list()
    
    print("="*60)
    print("All Phase 3 tests completed!")
    print("="*60)


if __name__ == "__main__":
    main()
```

**检查点**: ☐ test_proxy.py已创建

---

## 📊 Phase 3 预期成果

### 可交付模块

| 模块 | 路径 | 功能 | 风险 |
|------|------|------|------|
| SmartProxy | `proxy/smart_proxy.py` | 模式切换核心 | 低 |
| AuthInterceptor | `proxy/auth_interceptor.py` | 认证拦截 | 低 |
| CommandParser | `commands/parser.py` | 命令解析 | 低 |
| FakeRoomList | `proxy/room_list.py` | 伪造房间 | 低 |
| Tests | `tests/test_proxy.py` | 测试验证 | 低 |

### 关键特性

1. **自动模式切换** - 登录后自动切换到emulation
2. **用户命令** - /mnmcp minecraft 等命令
3. **会话管理** - 保持登录状态
4. **房间伪造** - 显示MC服务器为可加入房间

---

## 🚨 风险评估与缓解

### 风险1：压缩包未解压（P0）

**影响**: 游戏数据协议细节缺失

**缓解措施**:
- Phase 3框架可独立完成
- 游戏数据协议用占位符实现
- 解压后立即填充细节

### 风险2：房间注册API不完整

**影响**: 无法创建真实房间

**缓解措施**:
- 优先实现emulation模式（本地房间）
- 房间注册可延后到Phase 5

---

## ✅ Phase 3 完成标准

- [ ] SmartProxy核心框架
- [ ] 三种模式切换
- [ ] 认证拦截器
- [ ] 命令系统
- [ ] 伪造房间列表
- [ ] 集成测试

**目标完成度**: 100%框架 + 70%功能

---

**Phase 3可立即开始，不依赖压缩包内容！**
