"""
MiniWorld HTTP Server (Port 8080)
Handles HTTP API requests
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import gzip
import io

class MiniWorldHTTPHandler(BaseHTTPRequestHandler):
    """Handle MiniWorld HTTP API"""
    
    def do_GET(self):
        """Handle GET request"""
        self.handle_request()
    
    def do_POST(self):
        """Handle POST request"""
        self.handle_request()
    
    def handle_request(self):
        """Handle request"""
        path = self.path
        
        print(f"[HTTP] {self.command} {path}")
        
        # Route based on path
        if 'server_config' in path:
            self.send_server_config()
        elif 'room' in path.lower():
            self.send_room_list()
        else:
            self.send_default()
    
    def send_server_config(self):
        """Send server config"""
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
                "room_name": "local_mnmcp",
                "block_type": "HD",
                "area_type": 1
            },
            "result": 0
        }
        
        self.send_json_response(response)
        print("  → Sent server_config")
    
    def send_room_list(self):
        """Send room list"""
        response = {
            "ret": 0,
            "msg": "success",
            "data": {
                "room_list": [
                    {
                        "room_id": "999999999",
                        "room_name": "🎮 Minecraft Server",
                        "host_name": "MnMCP Bridge",
                        "current_players": 1,
                        "max_players": 20,
                        "map_name": "Minecraft World",
                        "game_mode": "生存模式"
                    }
                ],
                "total": 1
            }
        }
        
        self.send_json_response(response)
        print("  → Sent room_list with Minecraft room!")
    
    def send_default(self):
        """Send default response"""
        response = {"ret": 0, "msg": "success", "data": {}}
        self.send_json_response(response)
    
    def send_json_response(self, data):
        """Send JSON response"""
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        # Compress
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode='wb') as f:
            f.write(body)
        compressed = buf.getvalue()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Length', len(compressed))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(compressed)
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def main():
    """Main function"""
    print("=" * 80)
    print("MiniWorld HTTP Server (Port 8080)")
    print("=" * 80)
    print()
    
    server = HTTPServer(('127.0.0.1', 8080), MiniWorldHTTPHandler)
    
    print("[OK] HTTP server started on 127.0.0.1:8080")
    print("[OK] Press Ctrl+C to stop")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped")

if __name__ == "__main__":
    main()
