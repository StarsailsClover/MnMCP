import asyncio
import socket
import struct
import json
import time
import hashlib
from typing import Optional, Dict, Any
from ..config import MiniConfig
from .protocol import Packet, LoginPacket, RoomListPacket, JoinRoomPacket
from ..crypto.xxtea import XXTEA

class MiniWorldLoginClient:
    """MiniWorld login client with full authentication"""
    
    def __init__(self, config: MiniConfig):
        self.config = config
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.session_token: Optional[str] = None
        self.user_info: Optional[Dict[str, Any]] = None
        self.xxtea = XXTEA()
    
    async def login(self, username: str = "", password: str = "") -> bool:
        """Perform full login"""
        print("[Login] Starting authentication...")
        
        # Connect to auth server
        if not await self._connect_auth():
            print("[Login] ✗ Auth connection failed")
            return False
        
        print("[Login] ✓ Connected to auth server")
        
        # Send login request
        if not await self._send_login_request(username, password):
            print("[Login] ✗ Login request failed")
            return False
        
        print("[Login] ✓ Login request sent")
        
        # Receive response
        response = await self._recv_response()
        if not response:
            print("[Login] ✗ No response from server")
            return False
        
        print(f"[Login] ✓ Response received: {response}")
        
        # Parse response
        if response.get("ret") == 0:
            self.session_token = response.get("data", {}).get("token")
            self.user_info = response.get("data", {}).get("user_info")
            print(f"[Login] ✓ Login successful!")
            print(f"[Login]   UIN: {self.user_info.get('uin')}")
            print(f"[Login]   Nickname: {self.user_info.get('nickname')}")
            return True
        else:
            print(f"[Login] ✗ Login failed: {response.get('msg')}")
            return False
    
    async def _connect_auth(self) -> bool:
        """Connect to authentication server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            
            # Connect to auth server (certification.mini1.cn:19921)
            self.socket.connect(("116.205.254.145", 19921))
            
            self.connected = True
            return True
        except Exception as e:
            print(f"[Auth] Connection error: {e}")
            return False
    
    async def _send_login_request(self, username: str, password: str) -> bool:
        """Send encrypted login request"""
        try:
            # Build login request
            timestamp = int(time.time())
            auth = hashlib.md5(f"{self.config.uin}{timestamp}miniworld".encode()).hexdigest()[:32]
            
            login_data = {
                "uin": self.config.uin,
                "timestamp": timestamp,
                "auth": auth,
                "version": "1.55.0",
                "platform": "pc",
                "channel": "110"
            }
            
            # Encrypt with XXTEA
            json_data = json.dumps(login_data).encode()
            encrypted = self.xxtea.encrypt(json_data, self.config.xxtea_key.encode())
            
            # Build HTTP request
            request = (
                f"POST /auth/login HTTP/1.1\r\n"
                f"Host: certification.mini1.cn:19921\r\n"
                f"Content-Type: application/octet-stream\r\n"
                f"Content-Length: {len(encrypted)}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            ).encode() + encrypted
            
            # Send
            self.socket.sendall(request)
            
            return True
        except Exception as e:
            print(f"[Login] Send error: {e}")
            return False
    
    async def _recv_response(self) -> Optional[Dict]:
        """Receive and decrypt response"""
        try:
            loop = asyncio.get_event_loop()
            
            # Receive HTTP headers
            headers = b""
            while b"\r\n\r\n" not in headers:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                headers += chunk
            
            # Parse content length
            content_length = 0
            for line in headers.decode().split("\r\n"):
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":")[1].strip())
                    break
            
            # Receive body
            body = headers.split(b"\r\n\r\n")[1]
            while len(body) < content_length:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                body += chunk
            
            # Decrypt
            decrypted = self.xxtea.decrypt(body, self.config.xxtea_key.encode())
            
            # Parse JSON
            return json.loads(decrypted.decode('utf-8', errors='ignore'))
            
        except Exception as e:
            print(f"[Login] Receive error: {e}")
            return None
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            self.connected = False
