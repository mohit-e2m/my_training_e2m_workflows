#!/usr/bin/env python3
"""
Simple HTTP server with cache control headers to prevent caching during development
"""
import http.server
import socketserver
from datetime import datetime

PORT = 8000

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add cache control headers to prevent caching
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom log format with timestamp
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), NoCacheHTTPRequestHandler) as httpd:
        print(f"✅ Frontend server running at http://localhost:{PORT}")
        print(f"   Main page: http://localhost:{PORT}/index.html")
        print(f"   Admin page: http://localhost:{PORT}/admin.html")
        print(f"   Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
