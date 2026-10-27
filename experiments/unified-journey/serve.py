"""Loopback-only allowlisted, memory-only UX prototype; no application/database access."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent / "dist"
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/geo.js": ("geo.js", "text/javascript; charset=utf-8"),
    "/channels.js": ("channels.js", "text/javascript; charset=utf-8"),
    "/turkey-boundary.js": ("turkey-boundary.js", "text/javascript; charset=utf-8"),
    "/vendor/polygon-clipping-0.15.7.js": (
        "vendor/polygon-clipping-0.15.7.js",
        "text/javascript; charset=utf-8",
    ),
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        self.respond(True)

    def do_HEAD(self):
        self.respond(False)

    def respond(self, include_body):
        if self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}":
            self.send_error(403)
            return
        entry = ASSETS.get(urlsplit(self.path).path)
        if entry is None:
            self.send_error(404)
            return
        filename, content_type = entry
        target = ROOT / filename
        if target.resolve() != target.absolute() or not target.is_file():
            self.send_error(404)
            return
        body = target.read_bytes()
        self.send_response(200)
        for key, value in {
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
            "Cross-Origin-Resource-Policy": "same-origin",
            "X-Robots-Tag": "noindex, nofollow",
            "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob:; connect-src 'none'; font-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
        }.items():
            self.send_header(key, value)
        self.end_headers()
        if include_body:
            self.wfile.write(body)


def make_server(port=0):
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8013)
    server = make_server(parser.parse_args().port)
    print(
        f"Yaparo journey prototype: http://127.0.0.1:{server.server_port}/", flush=True
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
