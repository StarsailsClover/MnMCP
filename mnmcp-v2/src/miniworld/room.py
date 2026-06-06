"""
MiniWorld Room Management Client
Handles room listing, creation, and joining
"""

import asyncio
import socket
import struct
import json
import time
import logging
from typing import List, Dict, Optional
from ..config import MiniConfig
from .room_info import RoomInfo
from .login import MiniWorldLoginClient

logger = logging.getLogger(__name__)

# Constants
MINECRAFT_ROOM_ID = "999999999"
DEFAULT_MAX_PLAYERS = 20


class MiniWorldRoomClient:
    """MiniWorld room management client"""
    
    def __init__(self, config: MiniConfig, login_client: MiniWorldLoginClient):
        self.config = config
        self.login = login_client
        self.socket: Optional[socket.socket] = None
        self.rooms: List[RoomInfo] = []
        
        # Minecraft room to inject
        self.minecraft_room = RoomInfo(
            room_id=MINECRAFT_ROOM_ID,
            room_name="🎮 Minecraft Server",
            host_name="MnMCP Bridge",
            host_uin=str(config.auth.uin),
            current_players=0,
            max_players=DEFAULT_MAX_PLAYERS,
            map_name="Minecraft World",
            game_mode="生存模式",
            version=config.auth.version,
            ping=10
        )
    
    async def get_room_list(self) -> List[RoomInfo]:
        """
        Get room list from server
        
        Returns:
            List of RoomInfo objects (including injected Minecraft room)
        """
        logger.info("Fetching room list...")
        
        # Validate login
        if not self.login.session_token:
            logger.error("Not logged in - session token is missing")
            return []
        
        # Connect to room server
        if not await self._connect_room_server():
            logger.error("Connection failed")
            return []
        
        # Send room list request
        if not await self._send_room_list_request():
            logger.error("Request failed")
            return []
        
        # Receive response
        rooms = await self._recv_room_list()
        if not rooms:
            logger.warning("No rooms received from server")
            return []
        
        # Inject Minecraft room at the top
        rooms.insert(0, self.minecraft_room)
        self.rooms = rooms
        
        logger.info(f"Got {len(rooms)} rooms (including Minecraft)")
        return rooms
    
    async def create_room(self, room_name: str, max_players: int = 6) -> Optional[str]:
        """
        Create a new room
        
        Args:
            room_name: Name of the room
            max_players: Maximum number of players
            
        Returns:
            Room ID if successful, None otherwise
        """
        logger.info(f"Creating room: {room_name}")
        
        # TODO: Implement actual room creation protocol
        # For now, return a dummy ID
        room_id = f"{int(time.time())}"
        logger.info(f"Room created: {room_id}")
        return room_id
    
    async def join_room(self, room_id: str) -> bool:
        """
        Join a room
        
        Args:
            room_id: ID of the room to join
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Joining room: {room_id}")
        
        if room_id == MINECRAFT_ROOM_ID:
            logger.info("Joining Minecraft room!")
            # TODO: Implement actual Minecraft server connection
            return True
        
        # TODO: Implement regular MiniWorld room joining
        logger.warning("Regular MiniWorld room joining not yet implemented")
        return True
    
    async def _connect_room_server(self) -> bool:
        """Connect to room server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setblocking(False)
            self.socket.settimeout(10)
            
            server_ip = self.config.room.server.ip
            server_port = self.config.room.server.port
            
            logger.debug(f"Connecting to room server: {server_ip}:{server_port}")
            
            loop = asyncio.get_event_loop()
            await loop.sock_connect(self.socket, (server_ip, server_port))
            
            logger.debug("Connected to room server")
            return True
        except socket.timeout:
            logger.error("Room server connection timeout")
            return False
        except socket.gaierror as e:
            logger.error(f"DNS resolution error: {e}")
            return False
        except ConnectionRefusedError:
            logger.error("Room server refused connection")
            return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def _send_room_list_request(self) -> bool:
        """Send room list request"""
        try:
            request = {
                "cmd": "get_room_list",
                "uin": self.config.auth.uin,
                "token": self.login.session_token,
                "timestamp": int(time.time())
            }
            
            json_data = json.dumps(request).encode()
            
            # Send length prefix + data
            loop = asyncio.get_event_loop()
            await loop.sock_sendall(
                self.socket, 
                struct.pack("!I", len(json_data)) + json_data
            )
            
            logger.debug(f"Sent room list request ({len(json_data)} bytes)")
            return True
        except socket.error as e:
            logger.error(f"Socket error during send: {e}")
            return False
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    async def _recv_room_list(self) -> List[RoomInfo]:
        """Receive room list"""
        try:
            loop = asyncio.get_event_loop()
            
            # Receive length
            length_data = await loop.sock_recv(self.socket, 4)
            if len(length_data) < 4:
                logger.error("Invalid length data received")
                return []
            
            length = struct.unpack("!I", length_data)[0]
            logger.debug(f"Expecting {length} bytes of room data")
            
            # Receive data
            data = b""
            while len(data) < length:
                chunk = await loop.sock_recv(self.socket, 4096)
                if not chunk:
                    logger.warning("Connection closed while receiving data")
                    break
                data += chunk
            
            if len(data) < length:
                logger.error(f"Incomplete data: {len(data)}/{length} bytes")
                return []
            
            # Parse response
            try:
                response = json.loads(data.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return []
            
            if response.get("ret") == 0:
                rooms_data = response.get("data", {}).get("rooms", [])
                rooms = []
                for room_data in rooms_data:
                    try:
                        room = RoomInfo(**room_data)
                        rooms.append(room)
                    except TypeError as e:
                        logger.warning(f"Invalid room data: {e}")
                        continue
                return rooms
            else:
                error_msg = response.get("msg", "Unknown error")
                logger.error(f"Server returned error: {error_msg}")
                return []
                
        except Exception as e:
            logger.error(f"Receive error: {e}")
            return []
    
    def close(self):
        """Close connection"""
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.debug(f"Error closing socket: {e}")
            finally:
                self.socket = None
