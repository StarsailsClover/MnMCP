"""
MiniWorld WebSocket RPC Server
Implements the actual WebSocket RPC protocol used by MiniWorld

Protocol:
- WebSocket connection
- RPC format: [0, service, method, seq, ts, args]
- Response: [1, service, method, seq, ts, payload]
- Data: Protobuf (or JSON for simplicity)
"""

import asyncio
import websockets
import json
import struct
from datetime import datetime

class MiniWorldRPCServer:
    """WebSocket RPC server for MiniWorld"""
    
    def __init__(self, host='127.0.0.1', port=8081):
        self.host = host
        self.port = port
        self.clients = {}
        self.request_count = 0
        
        # Mock data
        self.rooms = [
            {
                "room_id": "999999999",
                "room_name": "🎮 Minecraft Server",
                "host_name": "MnMCP Bridge",
                "host_uin": "2056574316",
                "current_players": 1,
                "max_players": 20,
                "map_name": "Minecraft World",
                "game_mode": "生存模式",
                "is_public": 1,
                "server_ip": "127.0.0.1",
                "server_port": 25565,
                "version": "1.55.0",
                "ping": 10
            },
            {
                "room_id": "123456789",
                "room_name": "测试房间1",
                "host_name": "玩家1",
                "current_players": 2,
                "max_players": 6,
                "map_name": "测试地图",
                "game_mode": "创造模式"
            }
        ]
    
    async def start(self):
        """Start WebSocket server"""
        print("=" * 80)
        print("MiniWorld WebSocket RPC Server")
        print("=" * 80)
        print()
        print(f"[OK] Starting on ws://{self.host}:{self.port}")
        print()
        print("Protocol: WebSocket RPC")
        print("Format: [0, service, method, seq, ts, args]")
        print()
        print("Configure hosts file:")
        print("  127.0.0.1 shequ.mini1.cn")
        print("  127.0.0.1 125.88.252.175")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 80)
        print()
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client"""
        client_id = id(websocket)
        self.clients[client_id] = {
            'websocket': websocket,
            'connected_at': datetime.now()
        }
        
        print(f"[+] Client {client_id} connected from {websocket.remote_address}")
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message, client_id)
        except websockets.exceptions.ConnectionClosed:
            print(f"[-] Client {client_id} disconnected")
        finally:
            del self.clients[client_id]
    
    async def handle_message(self, websocket, message, client_id):
        """Handle RPC message"""
        self.request_count += 1
        req_id = self.request_count
        
        try:
            # Parse RPC message
            # Format: [0, service, method, seq, ts, args]
            data = json.loads(message)
            
            if not isinstance(data, list) or len(data) < 6:
                print(f"[{req_id}] Invalid message format")
                return
            
            msg_type = data[0]  # 0 = request
            service = data[1]
            method = data[2]
            seq = data[3]
            ts = data[4]
            args = data[5] if len(data) > 5 else {}
            
            print(f"[{req_id}] RPC: {service}.{method} (seq={seq})")
            
            # Route to handler
            handler = getattr(self, f'handle_{service}_{method}', None)
            
            if handler:
                result = await handler(args)
            else:
                # Default handler
                result = await self.handle_default(service, method, args)
            
            # Send response
            # Format: [1, service, method, seq, ts, payload]
            response = [1, service, method, seq, int(datetime.now().timestamp()), result]
            
            await websocket.send(json.dumps(response))
            print(f"[{req_id}] ✓ Response sent")
            
        except json.JSONDecodeError:
            print(f"[{req_id}] Invalid JSON: {message[:100]}")
        except Exception as e:
            print(f"[{req_id}] Error: {e}")
    
    async def handle_login_auth(self, args):
        """Handle login.auth"""
        print("  → Login authentication")
        
        # Return auth info
        return {
            "code": 0,
            "uin": "2056574316",
            "token": "fake_token_12345",
            "sign": "fake_sign_67890",
            "nickname": "MnMCP_User",
            "level": 30
        }
    
    async def handle_login_reg(self, args):
        """Handle login.reg (register)"""
        print("  → Register new account")
        
        return {
            "code": 0,
            "uin": "2056574317",
            "token": "new_token_12345",
            "nickname": "NewPlayer"
        }
    
    async def handle_baseinfo_update(self, args):
        """Handle baseinfo.update"""
        print("  → Update base info")
        
        return {
            "code": 0,
            "player_data": {
                "uin": "2056574316",
                "nickname": "MnMCP_User",
                "level": 30,
                "exp": 10000,
                "coins": 9999,
                "items": []
            }
        }
    
    async def handle_room_list(self, args):
        """Handle room list request"""
        print("  → Get room list")
        print(f"  → Injecting {len(self.rooms)} rooms (including Minecraft!)")
        
        return {
            "code": 0,
            "rooms": self.rooms
        }
    
    async def handle_room_join(self, args):
        """Handle room join"""
        room_id = args.get('room_id', '')
        print(f"  → Join room {room_id}")
        
        if room_id == "999999999":
            # Minecraft room!
            print("  → 🎮 Joining Minecraft room!")
            return {
                "code": 0,
                "room_id": room_id,
                "server_ip": "127.0.0.1",
                "server_port": 25565,
                "token": "minecraft_room_token"
            }
        
        return {
            "code": 0,
            "room_id": room_id,
            "server_ip": "127.0.0.1",
            "server_port": 60021,
            "token": "room_token_123"
        }
    
    async def handle_default(self, service, method, args):
        """Default handler"""
        print(f"  → {service}.{method} (default handler)")
        
        return {
            "code": 0,
            "msg": "success"
        }

def main():
    """Main function"""
    server = MiniWorldRPCServer(host='127.0.0.1', port=8081)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n\nServer stopped")

if __name__ == "__main__":
    main()
