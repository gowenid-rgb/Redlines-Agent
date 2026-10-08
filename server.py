import os
import sys
import json
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Supported model mapping
MODEL_ALIASES = {
    "gemini-3-flash": "gemini-3-flash-preview",
    "gemini-3.1-pro": "gemini-3.1-pro-preview",
    "gemini-2.5-flash": "gemini-3-flash-preview",
    "gemini-1.5-flash": "gemini-3-flash-preview",
    "gemini-2.0-flash": "gemini-3-flash-preview",
    "gemini-2.5-pro": "gemini-3.1-pro-preview",
    "gemini-1.5-pro": "gemini-3.1-pro-preview"
}

class RedlineHandler(SimpleHTTPRequestHandler):
    extensions_map = SimpleHTTPRequestHandler.extensions_map.copy()
    extensions_map.update({
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".css": "text/css",
        ".html": "text/html",
        ".json": "application/json",
    })

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
                "defaultModel": "gemini-3-flash",
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
        # Proxy endpoint for Gemini API
        if self.path.startswith("/api/gemini"):
            api_key = os.environ.get("GEMINI_API_KEY", "")
            
            # Fallback to authorization header if not in env
            if not api_key:
                api_key = self.headers.get("x-goog-api-key", "")

            # Fallback to query param ?key=
            if not api_key and "key=" in self.path:
                try:
                    api_key = self.path.split("key=")[1].split("&")[0]
                except Exception:
                    pass

            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)

            if not api_key:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "GEMINI_API_KEY not configured. Add GEMINI_API_KEY in Railway Variables or enter it in the UI."
                }).encode("utf-8"))
                return

            # Extract requested model
            query_model = "gemini-3-flash"
            if "model=" in self.path:
                try:
                    query_model = self.path.split("model=")[1].split("&")[0]
                except Exception:
                    pass

            target_model = MODEL_ALIASES.get(query_model, query_model)

            # Try requested model, with automatic fallback if Google returns 404
            models_to_try = [target_model, "gemini-3-flash-preview", "gemini-3.8-flash", "gemini-flash-latest"]
            # Deduplicate preserving order
            seen = set()
            models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

            last_err_data = None
            last_err_code = 500

            for model_candidate in models_to_try:
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_candidate}:generateContent?key={api_key}"
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
                        return
                except urllib.error.HTTPError as e:
                    last_err_code = e.code
                    last_err_data = e.read()
                    if e.code == 404:
                        print(f"Model {model_candidate} returned 404, trying fallback...")
                        continue
                    else:
                        break
                except Exception as e:
                    last_err_code = 500
                    last_err_data = json.dumps({"error": str(e)}).encode("utf-8")
                    break

            # If all failed, return last error
            self.send_response(last_err_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(last_err_data or b'{"error": "Failed to call Gemini API"}')
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
    print(f"GEMINI_API_KEY detected: {'YES (Ready)' if has_key else 'NO (Waiting for config)'}")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    run()
