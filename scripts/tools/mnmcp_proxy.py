"""
MnMCP Proxy Server - Replace Clash Meta
A simple HTTP/HTTPS proxy that intercepts MiniWorld API requests

No external dependencies needed!
"""

import socket
import threading
import select
import logging
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProxyHandler(BaseHTTPRequestHandler):
    """HTTP Proxy Handler"""
    
    timeout = 5
    
    def do_CONNECT(self):
        """Handle HTTPS CONNECT"""
        logger.info(f"[CONNECT] {self.path}")
        
        # For MiniWorld domains, redirect to fake API
        if 'mini1.cn' in self.path:
            host, port = self.path.split(':')
            
            if 'openroom' in host or '42.240.175.30' in host:
                logger.info(f"[INTERCEPT] Redirecting {host} to fake API")
                # Redirect to fake API server
                target_host = '127.0.0.1'
                target_port = 8080
            else:
                # Other mini1.cn domains, allow through
                target_host = host
                target_port = int(port)
        else:
            # Non-MiniWorld traffic, allow through
            host, port = self.path.split(':')
            target_host = host
            target_port = int(port)
        
        try:
            # Connect to target
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((target_host, target_port))
            
            # Send 200 Connection Established
            self.send_response(200, 'Connection Established')
            self.end_headers()
            
            # Start bidirectional forwarding
            self._forward_data(self.connection, remote_socket)
            
        except Exception as e:
            logger.error(f"[CONNECT] Error: {e}")
            self.send_error(502, f"Bad Gateway: {e}")
    
    def do_GET(self):
        """Handle HTTP GET"""
        self._handle_http_request()
    
    def do_POST(self):
        """Handle HTTP POST"""
        self._handle_http_request()
    
    def _handle_http_request(self):
        """Handle HTTP request (GET/POST)"""
        logger.info(f"[{self.command}] {self.path}")
        
        # Parse URL
        parsed = urllib.parse.urlparse(self.path)
        
        # Check if this is a MiniWorld API request
        if 'mini1.cn' in parsed.netloc or '42.240.175.30' in parsed.netloc:
            if 'openroom' in parsed.netloc or '42.240.175.30' in parsed.netloc:
                logger.info(f"[INTERCEPT] Redirecting to fake API")
                # Redirect to fake API
                self._forward_to_fake_api(parsed)
                return
        
        # Forward to real server
        self._forward_to_real_server(parsed)
    
    def _forward_to_fake_api(self, parsed):
        """Forward request to fake API server"""
        try:
            import http.client
            
            # Connect to fake API
            conn = http.client.HTTPConnection('127.0.0.1', 8080, timeout=5)
            
            # Build request path
            path = parsed.path
            if parsed.query:
                path += '?' + parsed.query
            
            # Get request body if POST
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Forward request
            conn.request(self.command, path, body, dict(self.headers))
            
            # Get response
            response = conn.getresponse()
            
            # Send response back to client
            self.send_response(response.status)
            for header, value in response.getheaders():
                if header.lower() not in ['connection', 'transfer-encoding']:
                    self.send_header(header, value)
            self.end_headers()
            
            # Send response body
            self.wfile.write(response.read())
            
            conn.close()
            
        except Exception as e:
            logger.error(f"[FAKE_API] Error: {e}")
            self.send_error(502, f"Bad Gateway: {e}")
    
    def _forward_to_real_server(self, parsed):
        """Forward request to real server"""
        try:
            import http.client
            
            # Determine if HTTPS
            is_https = parsed.scheme == 'https'
            port = parsed.port or (443 if is_https else 80)
            
            # Connect to real server
            if is_https:
                conn = http.client.HTTPSConnection(parsed.hostname, port, timeout=5)
            else:
                conn = http.client.HTTPConnection(parsed.hostname, port, timeout=5)
            
            # Build request path
            path = parsed.path
            if parsed.query:
                path += '?' + parsed.query
            
            # Get request body if POST
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Forward request
            conn.request(self.command, path, body, dict(self.headers))
            
            # Get response
            response = conn.getresponse()
            
            # Send response back to client
            self.send_response(response.status)
            for header, value in response.getheaders():
                if header.lower() not in ['connection', 'transfer-encoding']:
                    self.send_header(header, value)
            self.end_headers()
            
            # Send response body
            self.wfile.write(response.read())
            
            conn.close()
            
        except Exception as e:
            logger.error(f"[FORWARD] Error: {e}")
            self.send_error(502, f"Bad Gateway: {e}")
    
    def _forward_data(self, client_socket, remote_socket):
        """Bidirectional data forwarding"""
        sockets = [client_socket, remote_socket]
        
        while True:
            try:
                readable, _, _ = select.select(sockets, [], [], 1)
                
                if not readable:
                    continue
                
                for sock in readable:
                    data = sock.recv(4096)
                    
                    if not data:
                        return
                    
                    if sock is client_socket:
                        remote_socket.sendall(data)
                    else:
                        client_socket.sendall(data)
                        
            except Exception as e:
                logger.error(f"[FORWARD] Error: {e}")
                return
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class MnMCPProxyServer:
    """MnMCP Proxy Server"""
    
    def __init__(self, port=7890):
        self.port = port
        self.server = None
    
    def start(self):
        """Start proxy server"""
        logger.info("=" * 60)
        logger.info("MnMCP Proxy Server (Clash Meta Replacement)")
        logger.info("=" * 60)
        logger.info("")
        
        try:
            self.server = HTTPServer(('127.0.0.1', self.port), ProxyHandler)
            
            logger.info(f"[OK] Proxy server started")
            logger.info(f"  HTTP Proxy: 127.0.0.1:{self.port}")
            logger.info("")
            logger.info("Interception rules:")
            logger.info("  - openroom.mini1.cn -> 127.0.0.1:8080 (Fake API)")
            logger.info("  - 42.240.175.30 -> 127.0.0.1:8080 (Fake API)")
            logger.info("  - Other traffic -> Direct")
            logger.info("")
            logger.info("=" * 60)
            logger.info("Next steps:")
            logger.info("1. Set system proxy: 127.0.0.1:7890")
            logger.info("2. Open MiniWorld")
            logger.info("3. Check room list")
            logger.info("=" * 60)
            logger.info("")
            
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            logger.info("\nStopping proxy server...")
            if self.server:
                self.server.shutdown()
        except Exception as e:
            logger.error(f"[ERROR] Failed to start: {e}")


def main():
    """Main function"""
    proxy = MnMCPProxyServer(port=7890)
    proxy.start()


if __name__ == "__main__":
    main()
