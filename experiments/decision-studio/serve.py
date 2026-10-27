"""Loopback UX prototype with public-source cache; no application database access."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from sources import SourceService

ROOT = Path(__file__).resolve().parent / "dist"
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/refinements.css": ("refinements.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/engine.js": ("engine.js", "text/javascript; charset=utf-8"),
    "/simulation.js": ("simulation.js", "text/javascript; charset=utf-8"),
    "/brief-flow.js": ("brief-flow.js", "text/javascript; charset=utf-8"),
    "/production.js": ("production.js", "text/javascript; charset=utf-8"),
    "/sources.js": ("sources.js", "text/javascript; charset=utf-8"),
    "/data.js": ("data.js", "text/javascript; charset=utf-8"),
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        self.respond(True)

    def do_HEAD(self):
        self.respond(False)

    def do_POST(self):
        origin = f"http://127.0.0.1:{self.server.server_port}"
        if (
            self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}"
            or self.headers.get("Origin") != origin
            or self.headers.get("X-Yaparo-Source") != "local-synthetic"
            or self.headers.get("Content-Type", "").split(";")[0] != "application/json"
            or self.headers.get("Transfer-Encoding")
        ):
            self.send_error(403)
            return
        path = urlsplit(self.path).path
        if path not in {"/api/sources/status", "/api/sources/refresh"}:
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                raise ValueError
            self.connection.settimeout(10)
            body = self.rfile.read(size)
            if len(body) != size:
                raise ValueError

            def unique_object(pairs):
                result = {}
                for key, value in pairs:
                    if key in result:
                        raise ValueError
                    result[key] = value
                return result

            request = json.loads(body, object_pairs_hook=unique_object)
            if not isinstance(request, dict) or set(request) != {
                "context",
                "channels",
                "force",
                "source",
            }:
                raise ValueError
            if request["source"] not in {"tcmb", "ecb"}:
                raise ValueError
            if type(request["force"]) is not bool:
                raise ValueError
            service = self.server.source_services[request["source"]]
            method = service.refresh if path.endswith("refresh") else service.describe
            arguments = {"force": request["force"]} if path.endswith("refresh") else {}
            result = method(request["context"], request["channels"], **arguments)
            payload = json.dumps(result, ensure_ascii=False, allow_nan=False).encode(
                "utf-8"
            )
        except (ValueError, TypeError, KeyError, OSError):
            self.send_error(400)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.end_headers()
        self.wfile.write(payload)

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
            "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob:; connect-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
        }.items():
            self.send_header(key, value)
        self.end_headers()
        if include_body:
            self.wfile.write(body)


def make_server(port=0, *, sources=None):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.source_services = (
        sources
        if isinstance(sources, dict)
        else {
            "tcmb": sources if sources is not None else SourceService(provider="tcmb"),
            "ecb": SourceService(provider="ecb"),
        }
    )
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8014)
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
