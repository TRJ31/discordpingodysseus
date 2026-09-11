import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen

HOST = "127.0.0.1"
PORT = int(os.getenv("DISCORD_BRIDGE_PORT", "8765"))
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print("[discord-bridge]", fmt % args)

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"ok": True, "configured": bool(WEBHOOK_URL)})
        else:
            self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        if self.path != "/notify":
            self._json(404, {"ok": False, "error": "not found"})
            return
        if not WEBHOOK_URL:
            self._json(503, {"ok": False, "error": "DISCORD_WEBHOOK_URL is not configured"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 10000:
                self._json(413, {"ok": False, "error": "request too large"})
                return
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            content = str(body.get("content", "")).strip()
            if not content:
                self._json(400, {"ok": False, "error": "content is required"})
                return
            if len(content) > 2000:
                self._json(400, {"ok": False, "error": "Discord content is limited to 2000 characters"})
                return
            payload = {"content": content, "allowed_mentions": {"parse": []}}
            if body.get("username"):
                payload["username"] = str(body["username"])[:80]
            if body.get("avatar_url"):
                payload["avatar_url"] = str(body["avatar_url"])
            req = Request(WEBHOOK_URL, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "User-Agent": "Odysseus-Discord-Bridge/1.0"}, method="POST")
            with urlopen(req, timeout=15) as response:
                if not 200 <= response.status < 300:
                    raise RuntimeError(f"Discord returned HTTP {response.status}")
            self._json(200, {"ok": True})
        except Exception as exc:
            self._json(502, {"ok": False, "error": str(exc)[:300]})

if __name__ == "__main__":
    print(f"Discord bridge listening on http://{HOST}:{PORT}")
    print("Webhook configured:", bool(WEBHOOK_URL))
    HTTPServer((HOST, PORT), Handler).serve_forever()
