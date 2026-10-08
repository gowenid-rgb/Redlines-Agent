import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

class RedlineHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Route root path to index.html / redline_tool.html
        if self.path in ("/", ""):
            self.path = "/index.html"
        return super().do_GET()

    def end_headers(self):
        # Ensure CORS and caching headers for web app assets
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

def run():
    # Railway provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, RedlineHandler)
    print(f"Kova Redline Studio running on http://0.0.0.0:{port}")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    run()
