"""
MiniWorld Login Client
Handles authentication with MiniWorld servers
"""

import asyncio
import socket
import struct
import json
import time
import hashlib
import logging
from typing import Optional, Dict, Any
from ..config import MiniConfig
from ..crypto.xxtea import XXTEA

logger = logging.getLogger(__name__)


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
        """
        Perform full login
        
        Args:
            username: MiniWorld username
            password: MiniWorld password
            
        Returns:
            True if login successful, False otherwise
        """
        logger.info("Starting authentication...")
        
        # Validate configuration
        if not self._validate_config():
            return False
        
        # Connect to auth server
        if not await self._connect_auth():
            logger.error("Auth connection failed")
            return False
        
        logger.info("Connected to auth server")
        
        # Send login request
        if not await self._send_login_request(username, password):
            logger.error("Login request failed")
            return False
        
        logger.info("Login request sent")
        
        # Receive response
        response = await self._recv_response()
        if not response:
            logger.error("No response from server")
            return False
        
        logger.debug(f"Response received: {response}")
        
        # Parse response
        if response.get("ret") == 0:
            self.session_token = response.get("data", {}).get("token")
            self.user_info = response.get("data", {}).get("user_info")
            logger.info("Login successful!")
            logger.info(f"  UIN: {self.user_info.get('uin')}")
            logger.info(f"  Nickname: {self.user_info.get('nickname')}")
            return True
        else:
            logger.error(f"Login failed: {response.get('msg')}")
            return False
    
    def _validate_config(self) -> bool:
        """Validate configuration before login"""
        errors = []
        
        if self.config.auth.uin == 0:
            errors.append("UIN is not configured")
        if not self.config.auth.xxtea_key:
            errors.append("XXTEA key is not configured")
        
        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        return True
    
    async def _connect_auth(self) -> bool:
        """Connect to authentication server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            
            # Connect to auth server (from config)
            server_ip = self.config.auth.server.ip
            server_port = self.config.auth.server.port
            
            logger.debug(f"Connecting to auth server: {server_ip}:{server_port}")
            self.socket.connect((server_ip, server_port))
            
            self.connected = True
            return True
        except socket.timeout:
            logger.error("Auth server connection timeout")
            return False
        except socket.gaierror as e:
            logger.error(f"DNS resolution error: {e}")
            return False
        except ConnectionRefusedError:
            logger.error("Auth server refused connection")
            return False
        except Exception as e:
            logger.error(f"Auth connection error: {e}")
            return False
    
    async def _send_login_request(self, username: str, password: str) -> bool:
        """Send encrypted login request"""
        try:
            # Build login request
            timestamp = int(time.time())
            
            # Use configured auth sign key or fallback (for backward compatibility)
            auth_key = self.config.auth.auth_sign_key or "miniworld"
            auth = hashlib.md5(
                f"{self.config.auth.uin}{timestamp}{auth_key}".encode()
            ).hexdigest()[:32]
            
            login_data = {
                "uin": self.config.auth.uin,
                "timestamp": timestamp,
                "auth": auth,
                "version": self.config.auth.version,
                "platform": self.config.auth.platform,
                "channel": self.config.auth.channel
            }
            
            # Encrypt with XXTEA
            json_data = json.dumps(login_data).encode()
            encrypted = self.xxtea.encrypt(
                json_data, 
                self.config.auth.xxtea_key.encode()
            )
            
            # Build HTTP request
            host = f"{self.config.auth.server.host}:{self.config.auth.server.port}"
            request = (
                f"POST /auth/login HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                f"Content-Type: application/octet-stream\r\n"
                f"Content-Length: {len(encrypted)}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            ).encode() + encrypted
            
            # Send
            self.socket.sendall(request)
            
            return True
        except socket.error as e:
            logger.error(f"Socket error during send: {e}")
            return False
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    async def _recv_response(self) -> Optional[Dict]:
        """Receive and decrypt response"""
        try:
            # Receive HTTP headers
            headers = b""
            while b"\r\n\r\n" not in headers:
                chunk = self.socket.recv(4096)
                if not chunk:
                    logger.warning("Connection closed while receiving headers")
                    break
                headers += chunk
            
            if not headers:
                logger.error("No headers received")
                return None
            
            # Parse content length
            content_length = 0
            for line in headers.decode('utf-8', errors='ignore').split("\r\n"):
                if line.lower().startswith("content-length:"):
                    try:
                        content_length = int(line.split(":")[1].strip())
                    except ValueError:
                        logger.warning(f"Invalid content-length: {line}")
                    break
            
            # Receive body
            body_parts = headers.split(b"\r\n\r\n")
            body = body_parts[1] if len(body_parts) > 1 else b""
            
            while len(body) < content_length:
                chunk = self.socket.recv(4096)
                if not chunk:
                    logger.warning("Connection closed while receiving body")
                    break
                body += chunk
            
            if not body:
                logger.error("Empty response body")
                return None
            
            # Decrypt
            decrypted = self.xxtea.decrypt(body, self.config.auth.xxtea_key.encode())
            
            # Parse JSON
            return json.loads(decrypted.decode('utf-8', errors='ignore'))
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Receive error: {e}")
            return None
    
    def close(self):
        """Close connection"""
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.debug(f"Error closing socket: {e}")
            finally:
                self.connected = False
                self.socket = None
