"""
MnMCP WebSocket Interceptor using mitmproxy
Intercept and modify WebSocket messages from MiniWorld

Installation:
pip install mitmproxy

Usage:
mitmdump -s mnmcp_websocket_interceptor.py --set block_global=false
"""

import json
import logging
from mitmproxy import http, websocket
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MnMCPWebSocketInterceptor:
    """Intercept MiniWorld WebSocket traffic"""
    
    def __init__(self):
        self.ws_connections = {}
        self.message_count = 0
        self.captured_messages = []
        
        # Target servers
        self.target_hosts = [
            "125.88.252.175",
            "shequ.mini1.cn",
            "42.240.175.30",
            "openroom.mini1.cn"
        ]
    
    def websocket_start(self, flow: websocket.WebSocketFlow):
        """Called when WebSocket connection starts"""
        host = flow.request.host
        
        if any(target in host for target in self.target_hosts):
            logger.info("=" * 80)
            logger.info(f"[WebSocket] Connection to: {host}")
            logger.info(f"[WebSocket] Path: {flow.request.path}")
            logger.info(f"[WebSocket] Headers: {dict(flow.request.headers)}")
            logger.info("=" * 80)
            
            self.ws_connections[id(flow)] = {
                'host': host,
                'path': flow.request.path,
                'start_time': datetime.now()
            }
    
    def websocket_message(self, flow: websocket.WebSocketFlow):
        """Called for each WebSocket message"""
        message = flow.messages[-1]
        
        # Check if this is a target connection
        if id(flow) not in self.ws_connections:
            return
        
        self.message_count += 1
        
        # Get message content
        content = message.content
        from_client = message.from_client
        
        direction = "→ Server" if from_client else "← Client"
        
        logger.info(f"\n[{self.message_count}] {direction}")
        logger.info(f"Type: {'Text' if message.is_text else 'Binary'}")
        logger.info(f"Length: {len(content)} bytes")
        
        # Try to parse as JSON
        if message.is_text:
            try:
                data = json.loads(content)
                logger.info("JSON Content:")
                logger.info(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Check if this is room list
                if self.is_room_list_message(data):
                    logger.info("\n" + "=" * 80)
                    logger.info("🎯 FOUND ROOM LIST MESSAGE!")
                    logger.info("=" * 80)
                    
                    # Inject Minecraft room
                    modified_data = self.inject_minecraft_room(data)
                    
                    # Modify the message
                    message.content = json.dumps(modified_data, ensure_ascii=False)
                    logger.info("✅ Injected Minecraft room!")
                
            except json.JSONDecodeError:
                logger.info(f"Text Content: {content[:200]}")
        else:
            # Binary message
            logger.info(f"Binary (hex): {content[:64].hex()}")
        
        # Save message
        self.captured_messages.append({
            'timestamp': datetime.now().isoformat(),
            'direction': 'outbound' if from_client else 'inbound',
            'type': 'text' if message.is_text else 'binary',
            'content': content.decode('utf-8', errors='ignore') if message.is_text else content.hex(),
            'length': len(content)
        })
    
    def is_room_list_message(self, data):
        """Check if this is a room list message"""
        # Common patterns for room list
        if isinstance(data, dict):
            # Check for room-related keys
            keys = str(data.keys()).lower()
            if any(keyword in keys for keyword in ['room', 'list', 'lobby', 'hall']):
                return True
            
            # Check for array of rooms
            if 'data' in data:
                if isinstance(data['data'], list) and len(data['data']) > 0:
                    first_item = data['data'][0]
                    if isinstance(first_item, dict):
                        item_keys = str(first_item.keys()).lower()
                        if any(keyword in item_keys for keyword in ['room', 'map', 'player', 'host']):
                            return True
        
        return False
    
    def inject_minecraft_room(self, data):
        """Inject Minecraft room into room list"""
        modified = data.copy()
        
        # Create fake Minecraft room
        minecraft_room = {
            "room_id": "999999999",
            "room_name": "🎮 Minecraft Server",
            "host_name": "MnMCP Bridge",
            "current_players": 1,
            "max_players": 20,
            "map_name": "Minecraft World",
            "game_mode": "Survival",
            "is_public": True,
            "ping": 10
        }
        
        # Try to inject into common structures
        if 'data' in modified and isinstance(modified['data'], list):
            modified['data'].insert(0, minecraft_room)
        elif 'rooms' in modified and isinstance(modified['rooms'], list):
            modified['rooms'].insert(0, minecraft_room)
        elif 'list' in modified and isinstance(modified['list'], list):
            modified['list'].insert(0, minecraft_room)
        
        return modified
    
    def websocket_end(self, flow: websocket.WebSocketFlow):
        """Called when WebSocket connection ends"""
        if id(flow) in self.ws_connections:
            conn_info = self.ws_connections[id(flow)]
            logger.info(f"\n[WebSocket] Connection closed: {conn_info['host']}")
            del self.ws_connections[id(flow)]
    
    def done(self):
        """Called when mitmproxy shuts down"""
        logger.info("\n" + "=" * 80)
        logger.info(f"Captured {len(self.captured_messages)} WebSocket messages")
        logger.info("=" * 80)
        
        # Save messages
        if self.captured_messages:
            filename = f"websocket_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.captured_messages, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved to: {filename}")

# Create addon instance
addons = [MnMCPWebSocketInterceptor()]
