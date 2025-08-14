#!/usr/bin/env python3
"""
Simple HTTP server to test the frontend UI
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse
import json

class FrontendHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve the frontend files and mock API responses"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=".", **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Route handling
        if path == "/":
            self.serve_file("static/index.html")
        elif path == "/dashboard":
            self.serve_file("static/index.html")
        elif path == "/dashboard/content":
            self.serve_file("static/templates/content-debug.html")
        elif path == "/api-keys":
            self.serve_file("static/templates/api-keys.html")
        elif path.startswith("/static/"):
            # Serve static files
            file_path = path[1:]  # Remove leading slash
            self.serve_file(file_path)
        elif path.startswith("/api/"):
            # Mock API responses
            self.handle_api_request(path)
        else:
            super().do_GET()
    
    def serve_file(self, file_path):
        """Serve a specific file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Set content type based on file extension
                if file_path.endswith('.html'):
                    content_type = 'text/html'
                elif file_path.endswith('.css'):
                    content_type = 'text/css'
                elif file_path.endswith('.js'):
                    content_type = 'application/javascript'
                else:
                    content_type = 'application/octet-stream'
                
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Content-length', len(content))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, f"File not found: {file_path}")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def handle_api_request(self, path):
        """Handle mock API requests"""
        mock_responses = {
            "/api/v1/auth/me": {"username": "demo_user", "email": "demo@example.com"},
            "/api/v1/analytics/overview": {
                "total_publications": 25,
                "total_views": 125000,
                "total_engagement": 8500,
                "engagement_rate": 6.8
            },
            "/api/v1/content/queue": {"queue": [], "count": 4},
            "/api/v1/services/status": {"services": []},
            "/health": {"status": "healthy", "version": "1.0.0"},
            "/health/detailed": {
                "status": "healthy",
                "database": "connected",
                "redis": "connected",
                "services": "operational"
            }
        }
        
        response_data = mock_responses.get(path, {"message": "Mock API response", "path": path})
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())
    
    def log_message(self, format, *args):
        """Custom log message format"""
        print(f"[{self.date_time_string()}] {format % args}")

def main():
    port = 8000
    
    # Change to the project directory
    project_dir = "/home/runner/work/social-media-automation/social-media-automation"
    os.chdir(project_dir)
    
    try:
        with socketserver.TCPServer(("", port), FrontendHandler) as httpd:
            print(f"🚀 Frontend server running at http://localhost:{port}")
            print(f"📊 Dashboard: http://localhost:{port}/dashboard")
            print(f"🔧 Content Debug: http://localhost:{port}/dashboard/content")
            print(f"🔑 API Keys: http://localhost:{port}/api-keys")
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()