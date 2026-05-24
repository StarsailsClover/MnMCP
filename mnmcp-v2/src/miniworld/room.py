import asyncio
import socket
import struct
import json
import time
from typing import List, Dict, Optional
from ..config import MiniConfig
from .protocol import Packet
from .room_info import RoomInfo
from .login import MiniWorldLoginClient

class MiniWorldRoomClient:
    """MiniWorld room management client"""
    
    def __init__(self, config: MiniConfig, login_client: MiniWorldLoginClient):
        self.config = config
        self.login = login_client
        self.socket: Optional[socket.socket] = None
        self.rooms: List[RoomInfo] = []
        
        # Minecraft room to inject
        self.minecraft_room = RoomInfo(
            room_id="999999999",
            room_name="🎮 Minecraft Server",
            host_name="MnMCP Bridge",
            host_uin="2067729592",
            current_players=0,
            max_players=20,
            map_name="Minecraft World",
            game_mode="生存模式",
            version="1.55.0",
            ping=10
        )
    
    async def get_room_list(self) -> List[RoomInfo]:
        """Get room list from server"""
        print("[Room] Fetching room list...")
        
        # Connect to room server
        if not await self._connect_room_server():
            print("[Room] ✗ Connection failed")
            return []
        
        # Send room list request
        if not await self._send_room_list_request():
            print("[Room] ✗ Request failed")
            return []
        
        # Receive response
        rooms = await self._recv_room_list()
        if not rooms:
            print("[Room] ✗ No rooms received")
            return []
        
        # Inject Minecraft room
        rooms.insert(0, self.minecraft_room)
        self.rooms = rooms
        
        print(f"[Room] ✓ Got {len(rooms)} rooms (including Minecraft)")
        return rooms
    
    async def create_room(self, room_name: str, max_players: int = 6) -> Optional[str]:
        """Create a new room"""
        print(f"[Room] Creating room: {room_name}")
        
        # TODO: Implement room creation
        room_id = f"{int(time.time())}"
        print(f"[Room] ✓ Room created: {room_id}")
        return room_id
    
    async def join_room(self, room_id: str) -> bool:
        """Join a room"""
        print(f"[Room] Joining room: {room_id}")
        
        if room_id == self.minecraft_room.room_id:
            print("[Room] ✓ Joining Minecraft room!")
            # TODO: Connect to Minecraft server
            return True
        
        # TODO: Join regular MiniWorld room
        return True
    
    async def _connect_room_server(self) -> bool:
        """Connect to room server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setblocking(False)
            self.socket.settimeout(10)
            
            loop = asyncio.get_event_loop()
            await loop.sock_connect(self.socket, ("116.205.254.229", 19601))
            
            return True
        except Exception as e:
            print(f"[Room] Connection error: {e}")
            return False
    
    async def _send_room_list_request(self) -> bool:
        """Send room list request"""
        try:
            request = {
                "cmd": "get_room_list",
                "uin": self.config.uin,
                "token": self.login.session_token,
                "timestamp": int(time.time())
            }
            
            json_data = json.dumps(request).encode()
            
            # Send length prefix + data
            loop = asyncio.get_event_loop()
            await loop.sock_sendall(self.socket, struct.pack("!I", len(json_data)) + json_data)
            
            return True
        except Exception as e:
            print(f"[Room] Send error: {e}")
            return False
    
    async def _recv_room_list(self) -> List[RoomInfo]:
        """Receive room list"""
        try:
            loop = asyncio.get_event_loop()
            
            # Receive length
            length_data = await loop.sock_recv(self.socket, 4)
            length = struct.unpack("!I", length_data)[0]
            
            # Receive data
            data = b""
            while len(data) < length:
                chunk = await loop.sock_recv(self.socket, 4096)
                if not chunk:
                    break
                data += chunk
            
            # Parse response
            response = json.loads(data.decode())
            
            if response.get("ret") == 0:
                rooms_data = response.get("data", {}).get("rooms", [])
                return [RoomInfo(**room) for room in rooms_data]
            else:
                return []
                
        except Exception as e:
            print(f"[Room] Receive error: {e}")
            return []
