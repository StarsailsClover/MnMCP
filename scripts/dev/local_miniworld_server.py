"""
Local MiniWorld Server
Mimics MiniWorld API and injects Minecraft room

Listens on:
- Port 8080: openroom.mini1.cn API
- Port 8081: shequ.mini1.cn API (WebSocket/HTTP)
"""

import socket
import threading
import json
import gzip
import io
from datetime import datetime

class LocalMiniWorldServer:
    """Local server mimicking MiniWorld"""
    
    def __init__(self):
        self.servers = {}
        self.running = False
        self.request_count = 0
        
        # Minecraft room to inject
        self.minecraft_room = {
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
            "ping": 10,
            "mc_host": "127.0.0.1",
            "mc_port": 25565
        }
    
    def start(self):
        """Start all servers"""
        print("=" * 80)
        print("Local MiniWorld Server")
        print("=" * 80)
        print()
        
        # Start servers
        self.start_server(8080, "openroom.mini1.cn")
        self.start_server(8081, "shequ.mini1.cn")
        
        print()
        print("=" * 80)
        print("[OK] All servers started!")
        print("=" * 80)
        print()
        print("Servers:")
        print("  - Port 8080: openroom.mini1.cn (Server config)")
        print("  - Port 8081: shequ.mini1.cn (Room list)")
        print()
        print("Features:")
        print("  - Mimics real MiniWorld API")
        print("  - Injects Minecraft room into room list")
        print("  - Logs all requests")
        print()
        print("Next steps:")
        print("  1. Make sure hosts file is modified")
        print("  2. Open MiniWorld")
        print("  3. Check room list - you should see Minecraft room!")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 80)
        print()
        
        self.running = True
        
        try:
            while self.running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
            self.stop()
    
    def start_server(self, port, name):
        """Start a server on specific port"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', port))
        server.listen(10)
        
        self.servers[port] = server
        
        thread = threading.Thread(target=self.accept_connections, args=(server, port, name))
        thread.daemon = True
        thread.start()
        
        print(f"[OK] {name} listening on port {port}")
    
    def accept_connections(self, server, port, name):
        """Accept connections"""
        while self.running:
            try:
                client_socket, addr = server.accept()
                
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, addr, port, name)
                )
                thread.daemon = True
                thread.start()
                
            except:
                break
    
    def handle_client(self, client_socket, addr, port, name):
        """Handle client connection"""
        self.request_count += 1
        req_id = self.request_count
        
        try:
            # Read request
            data = client_socket.recv(4096)
            
            if not data:
                client_socket.close()
                return
            
            request = data.decode('utf-8', errors='ignore')
            
            # Parse request
            lines = request.split('\r\n')
            if not lines:
                client_socket.close()
                return
            
            request_line = lines[0]
            
            print(f"[{req_id}] {name}:{port} - {request_line}")
            
            # Handle CONNECT (HTTPS)
            if request_line.startswith('CONNECT'):
                self.handle_connect(client_socket, request_line, req_id)
            else:
                # Handle HTTP request
                self.handle_http(client_socket, request, req_id, port)
                
        except Exception as e:
            print(f"[{req_id}] [ERROR] {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def handle_connect(self, client_socket, request_line, req_id):
        """Handle HTTPS CONNECT"""
        # For now, just close - we'll handle TLS later
        # Or we can try to do TLS passthrough
        
        parts = request_line.split()
        if len(parts) >= 2:
            target = parts[1]
            print(f"[{req_id}] CONNECT {target}")
        
        # Send 200 OK
        try:
            client_socket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            
            # For now, just close the connection
            # In full implementation, we'd forward to real server or handle TLS
            print(f"[{req_id}] CONNECT accepted (TLS passthrough not implemented)")
            
        except:
            pass
        
        client_socket.close()
    
    def handle_http(self, client_socket, request, req_id, port):
        """Handle HTTP request"""
        # Parse request
        lines = request.split('\r\n')
        request_line = lines[0]
        
        # Parse path
        parts = request_line.split()
        if len(parts) < 2:
            self.send_error(client_socket, 400, "Bad Request")
            return
        
        method = parts[0]
        path = parts[1]
        
        print(f"[{req_id}] {method} {path}")
        
        # Route based on path
        if 'server_config' in path or 'server/room' in path:
            self.handle_server_config(client_socket, req_id)
        elif 'room' in path.lower() or 'list' in path.lower():
            self.handle_room_list(client_socket, req_id)
        else:
            # Default response
            self.handle_default(client_socket, req_id)
    
    def handle_server_config(self, client_socket, req_id):
        """Handle server config request"""
        response = {
            "config": {
                "room": {
                    "ip": "127.0.0.1",
                    "port": 8081
                },
                "proxy": {
                    "ip": "127.0.0.1",
                    "port": 8081
                },
                "punch": {
                    "ip": "127.0.0.1",
                    "port": 60021
                },
                "network_type": 1,
                "room_name": "local_mnmcp_server",
                "block_type": "HD",
                "area_type": 1
            },
            "result": 0
        }
        
        self.send_json_response(client_socket, response)
        print(f"[{req_id}] ✓ Sent server_config")
    
    def handle_room_list(self, client_socket, req_id):
        """Handle room list request - INJECT MINECRAFT ROOM!"""
        
        # Create fake room list with Minecraft room
        rooms = [
            self.minecraft_room,  # Minecraft room first!
            {
                "room_id": "123456789",
                "room_name": "Test Room 1",
                "host_name": "Player1",
                "current_players": 2,
                "max_players": 6,
                "map_name": "Test Map",
                "game_mode": "创造模式"
            },
            {
                "room_id": "987654321",
                "room_name": "Test Room 2",
                "host_name": "Player2",
                "current_players": 3,
                "max_players": 8,
                "map_name": "Another Map",
                "game_mode": "生存模式"
            }
        ]
        
        response = {
            "ret": 0,
            "msg": "success",
            "data": {
                "room_list": rooms,
                "total": len(rooms),
                "page": 1,
                "page_size": 50
            }
        }
        
        self.send_json_response(client_socket, response)
        print(f"[{req_id}] ✓ Sent room_list with {len(rooms)} rooms (including Minecraft!)")
    
    def handle_default(self, client_socket, req_id):
        """Handle default request"""
        response = {
            "ret": 0,
            "msg": "success",
            "data": {}
        }
        
        self.send_json_response(client_socket, response)
        print(f"[{req_id}] ✓ Sent default response")
    
    def send_json_response(self, client_socket, data):
        """Send JSON response"""
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        # Compress if large
        if len(body) > 1024:
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode='wb') as f:
                f.write(body)
            body = buf.getvalue()
            content_encoding = "gzip"
        else:
            content_encoding = None
        
        headers = [
            "HTTP/1.1 200 OK",
            "Content-Type: application/json; charset=utf-8",
            f"Content-Length: {len(body)}",
            "Access-Control-Allow-Origin: *",
            "Connection: close"
        ]
        
        if content_encoding:
            headers.insert(2, f"Content-Encoding: {content_encoding}")
        
        response = '\r\n'.join(headers) + '\r\n\r\n'
        response_bytes = response.encode('utf-8') + body
        
        client_socket.send(response_bytes)
    
    def send_error(self, client_socket, code, message):
        """Send error response"""
        response = f"HTTP/1.1 {code} {message}\r\n\r\n"
        client_socket.send(response.encode())
        client_socket.close()
    
    def stop(self):
        """Stop all servers"""
        self.running = False
        
        for port, server in self.servers.items():
            try:
                server.close()
            except:
                pass
        
        print()
        print("=" * 80)
        print(f"Server stopped. Total requests: {self.request_count}")
        print("=" * 80)

def main():
    """Main function"""
    server = LocalMiniWorldServer()
    server.start()

if __name__ == "__main__":
    main()
