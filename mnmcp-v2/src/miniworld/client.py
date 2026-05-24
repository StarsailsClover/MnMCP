import asyncio
import socket
from typing import Optional
from ..config import MiniConfig
from .protocol import Packet

class MiniWorldClient:
    def __init__(self, config: MiniConfig):
        self.config = config
        self.socket: Optional[socket.socket] = None
        self.connected = False
    
    async def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setblocking(False)
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    async def send(self, packet: Packet) -> bool:
        if not self.connected:
            return False
        try:
            data = packet.serialize()
            loop = asyncio.get_event_loop()
            await loop.sock_sendto(
                self.socket, data, 
                (self.config.ip, self.config.port)
            )
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            return False
    
    async def recv(self) -> Optional[Packet]:
        if not self.connected:
            return None
        try:
            loop = asyncio.get_event_loop()
            data, addr = await loop.sock_recvfrom(self.socket, 65535)
            return Packet.deserialize(data)
        except Exception as e:
            print(f"Recv failed: {e}")
            return None
    
    def close(self):
        if self.socket:
            self.socket.close()
            self.connected = False
