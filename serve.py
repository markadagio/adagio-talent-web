"""Local preview server for the public site.

Serves this directory's static files and proxies /api/* to the backoffice,
so index.html's relative apiBase ('') behaves exactly like it will in
production behind a shared reverse proxy — no CORS involved, on either side.
"""
import http.server
import os
import urllib.error
import urllib.request

PORT = int(os.environ.get("PORT", "8080"))
BACKOFFICE_URL = os.environ.get("BACKOFFICE_URL", "http://127.0.0.1:3000")


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy()
        else:
            super().do_GET()

    def _proxy(self):
        try:
            upstream = urllib.request.urlopen(BACKOFFICE_URL + self.path, timeout=10)
        except urllib.error.HTTPError as exc:
            self.send_response(exc.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(exc.read())
            return
        self.send_response(upstream.status)
        self.send_header("Content-Type", upstream.headers.get("Content-Type", "application/json"))
        self.end_headers()
        self.wfile.write(upstream.read())


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Serving {os.getcwd()} on http://0.0.0.0:{PORT}  (proxying /api/* to {BACKOFFICE_URL})")
        httpd.serve_forever()
