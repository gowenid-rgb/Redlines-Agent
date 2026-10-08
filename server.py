import os
import sys
import json
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler

class RedlineHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Route root path to index.html
        if self.path in ("/", ""):
            self.path = "/index.html"
            return super().do_GET()

        # Config endpoint to check for Railway environment variables
        if self.path == "/api/config":
            api_key = os.environ.get("GEMINI_API_KEY", "")
            payload = {
                "hasApiKey": bool(api_key),
                "apiKey": api_key,
                "source": "railway_env" if api_key else "none"
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        return super().do_GET()

    def do_POST(self):
        # Proxy endpoint for Gemini API using the Railway GEMINI_API_KEY
        if self.path.startswith("/api/gemini"):
            api_key = os.environ.get("GEMINI_API_KEY", "")
            
            # If not in env, check custom authorization header
            if not api_key:
                auth_header = self.headers.get("x-goog-api-key", "")
                if auth_header:
                    api_key = auth_header

            if not api_key:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "GEMINI_API_KEY environment variable is not configured on Railway."}).encode("utf-8"))
                return

            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)

            # Extract model from query param (default: gemini-2.5-flash)
            query_model = "gemini-2.5-flash"
            if "model=" in self.path:
                try:
                    query_model = self.path.split("model=")[1].split("&")[0]
                except Exception:
                    pass

            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{query_model}:generateContent?key={api_key}"
            req = urllib.request.Request(
                gemini_url,
                data=post_body,
                headers={"Content-Type": "application/json"}
            )
            try:
                with urllib.request.urlopen(req) as response:
                    resp_data = response.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(resp_data)
            except urllib.error.HTTPError as e:
                err_data = e.read()
                self.send_response(e.code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(err_data)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, x-goog-api-key")
        self.end_headers()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

def run():
    port = int(os.environ.get("PORT", 8080))
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, RedlineHandler)
    has_key = "GEMINI_API_KEY" in os.environ and bool(os.environ["GEMINI_API_KEY"])
    print(f"Kova Redline Studio running on http://0.0.0.0:{port}")
    print(f"GEMINI_API_KEY detected: {'YES (Ready)' if has_key else 'NO (Manual entry required)'}")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    run()
