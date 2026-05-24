"""
MnMCP v2 - Simple MiniWorld Server
Responds to MiniWorld protocol correctly
"""

import socket
import threading
import json
import gzip
import io
import struct
import time
import hashlib
from datetime import datetime

class SimpleMiniWorldServer:
    """Simple server that responds to MiniWorld"""
    
    def __init__(self):
        self.http_port = 8080
        self.ws_port = 8081
        self.running = False
        
        # User info
        self.user = {
            "uin": "2067729592",
            "nickname": "MnMCP_Player",
            "level": 30,
            "exp": 10000
        }
        
        # Minecraft room
        self.minecraft_room = {
            "room_id": "999999999",
            "room_name": "🎮 Minecraft Server",
            "host_name": "MnMCP Bridge",
            "host_uin": "2067729592",
            "current_players": 0,
            "max_players": 20,
            "map_name": "Minecraft World",
            "game_mode": "生存模式",
            "is_public": 1,
            "version": "1.55.0",
            "ping": 10
        }
        
        print("=" * 80)
        print("Simple MiniWorld Server")
        print("=" * 80)
        print()
        
    def start(self):
        """Start servers"""
        # HTTP server
        http_thread = threading.Thread(target=self.http_server)
        http_thread.daemon = True
        http_thread.start()
        
        # WebSocket server
        ws_thread = threading.Thread(target=self.ws_server)
        ws_thread.daemon = True
        ws_thread.start()
        
        print("[OK] Servers started!")
        print("  HTTP:  127.0.0.1:8080")
        print("  WS:    127.0.0.1:8081")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 80)
        
        self.running = True
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
    
    def http_server(self):
        """HTTP server"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.http_port))
        server.listen(100)
        
        print(f"[HTTP] Port {self.http_port}")
        
        while True:
            client, addr = server.accept()
            threading.Thread(target=self.handle_http, args=(client, addr)).start()
    
    def handle_http(self, client, addr):
        """Handle HTTP request"""
        try:
            data = client.recv(4096)
            if not data:
                client.close()
                return
            
            request = data.decode('utf-8', errors='ignore')
            lines = request.split('\r\n')
            
            if not lines:
                client.close()
                return
            
            request_line = lines[0]
            print(f"\n[HTTP] {addr[0]} - {request_line[:60]}")
            
            # Parse Host
            host = ""
            for line in lines[1:]:
                if line.lower().startswith('host:'):
                    host = line.split(':', 1)[1].strip()
                    break
            
            # Route by host
            if 'update.mini1.cn' in host:
                self.send_version(client)
            elif 'res.mini1.cn' in host:
                self.send_res(client)
            elif 'certification.mini1.cn' in host:
                self.handle_login(client, request)
            elif 'openroom.mini1.cn' in host:
                self.handle_room(client, request_line)
            else:
                self.send_ok(client)
                
        except Exception as e:
            print(f"[HTTP Error] {e}")
            try:
                client.close()
            except:
                pass
    
    def send_version(self, client):
        """Send version info"""
        print("  -> Version check")
        self.send_json(client, {
            "ret": 0,
            "msg": "success",
            "data": {
                "version": "1.55.0",
                "force_update": False,
                "need_update": False
            }
        })
        print("  -> OK")
    
    def send_res(self, client):
        """Send resource info"""
        print("  -> Resource check")
        self.send_json(client, {
            "ret": 0,
            "msg": "success",
            "data": {
                "version": "20240425",
                "need_update": False
            }
        })
        print("  -> OK")
    
    def handle_login(self, client, request):
        """Handle login"""
        print("  -> Login request")
        
        # Parse login data from body
        body = request.split('\r\n\r\n')
        if len(body) > 1:
            print(f"  -> Login data: {body[1][:100]}")
        
        self.send_json(client, {
            "ret": 0,
            "msg": "success",
            "data": {
                "uin": self.user["uin"],
                "token": f"token_{int(time.time())}",
                "nickname": self.user["nickname"],
                "level": self.user["level"],
                "exp": self.user["exp"]
            }
        })
        print(f"  -> Login: {self.user['nickname']}")
    
    def handle_room(self, client, request_line):
        """Handle room requests"""
        if 'server_config' in request_line:
            print("  -> Server config")
            self.send_json(client, {
                "config": {
                    "room": {"ip": "127.0.0.1", "port": self.ws_port},
                    "proxy": {"ip": "127.0.0.1", "port": self.ws_port}
                },
                "result": 0
            })
        else:
            print("  -> Room list")
            self.send_json(client, {
                "ret": 0,
                "msg": "success",
                "data": {
                    "room_list": [self.minecraft_room],
                    "total": 1
                }
            })
            print(f"  -> Sent Minecraft room!")
    
    def send_ok(self, client):
        """Send OK response"""
        self.send_json(client, {"ret": 0, "msg": "success"})
    
    def send_json(self, client, data):
        """Send JSON response"""
        try:
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            # Compress
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode='wb') as f:
                f.write(body)
            compressed = buf.getvalue()
            
            headers = [
                "HTTP/1.1 200 OK",
                "Content-Type: application/json; charset=utf-8",
                "Content-Encoding: gzip",
                f"Content-Length: {len(compressed)}",
                "Connection: close"
            ]
            
            response = '\r\n'.join(headers) + '\r\n\r\n'
            client.send(response.encode() + compressed)
            client.close()
        except:
            try:
                client.close()
            except:
                pass
    
    def ws_server(self):
        """WebSocket server"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.ws_port))
        server.listen(50)
        
        print(f"[WebSocket] Port {self.ws_port}")
        
        while True:
            client, addr = server.accept()
            threading.Thread(target=self.handle_ws, args=(client, addr)).start()
    
    def handle_ws(self, client, addr):
        """Handle WebSocket"""
        try:
            data = client.recv(4096)
            if not data:
                client.close()
                return
            
            request = data.decode('utf-8', errors='ignore')
            
            if 'Upgrade: websocket' not in request:
                client.close()
                return
            
            # Parse key
            key = None
            for line in request.split('\r\n'):
                if 'Sec-WebSocket-Key:' in line:
                    key = line.split(':')[1].strip()
                    break
            
            if not key:
                client.close()
                return
            
            # Handshake
            import base64
            magic = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            accept = base64.b64encode(hashlib.sha1((key + magic).encode()).digest()).decode()
            
            response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
            )
            client.send(response.encode())
            
            print(f"\n[WS] {addr} Connected")
            
            # Echo loop
            while True:
                header = client.recv(2)
                if len(header) < 2:
                    break
                
                opcode = header[0] & 0x0F
                
                if opcode == 0x8:  # Close
                    break
                
                # Skip payload
                payload_len = header[1] & 0x7F
                if payload_len == 126:
                    client.recv(2)
                elif payload_len == 127:
                    client.recv(8)
                
                if header[1] & 0x80:
                    client.recv(4)
                
                # Skip payload data
                client.recv(payload_len)
            
            client.close()
            print(f"[WS] {addr} Disconnected")
            
        except:
            try:
                client.close()
            except:
                pass

def main():
    server = SimpleMiniWorldServer()
    server.start()

if __name__ == "__main__":
    main()
