"""Serve the prototype on loopback; no upload or write endpoint."""
import argparse
import functools
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8767)
    args = parser.parse_args()
    handler = functools.partial(Handler, directory=str(ROOT))
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        port = server.server_address[1]
        state = {"pid": os.getpid(), "port": port, "url": f"http://127.0.0.1:{port}/", "root": str(ROOT)}
        (ROOT / ".server.json").write_text(json.dumps(state, indent=2) + "\n")
        print(state["url"], flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
