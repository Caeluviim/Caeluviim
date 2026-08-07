"""Minimal executable HTTP surface for Caeluviim.

Run: python -m caeluviim_graph.http_service
Then GET /health or POST JSON to /ingest.
No third-party web framework is required.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

HOST = os.getenv("CAELUVIIM_HOST", "127.0.0.1")
PORT = int(os.getenv("CAELUVIIM_PORT", "8787"))
DATA = Path(os.getenv("CAELUVIIM_RUNTIME_DIR", ".caeluviim-runtime"))
EVENTS = DATA / "events.jsonl"
RECEIPTS = DATA / "receipts.jsonl"


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def append(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(canonical(value).decode("utf-8") + "\n")


def ingest(payload: dict[str, Any]) -> dict[str, Any]:
    event = {
        "id": hashlib.sha256(canonical(payload)).hexdigest(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    append(EVENTS, event)
    receipt = {
        "runtime_identifier": f"http://{HOST}:{PORT}",
        "source_commit": os.getenv("CAELUVIIM_SOURCE_COMMIT", "unknown"),
        "manifest": "http-json-v1",
        "timestamp": event["timestamp"],
        "result": "accepted",
        "node_count": 1,
        "relationship_count": 0,
        "validation_result": "pass",
        "event_id": event["id"],
    }
    receipt["receipt_hash"] = hashlib.sha256(canonical(receipt)).hexdigest()
    append(RECEIPTS, receipt)
    return receipt


class Handler(BaseHTTPRequestHandler):
    def reply(self, status: int, body: dict[str, Any]) -> None:
        raw = canonical(body)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        if self.path == "/health":
            self.reply(200, {"status": "ok", "service": "caeluviim", "runtime": f"http://{HOST}:{PORT}"})
        else:
            self.reply(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/ingest":
            self.reply(404, {"error": "not_found"})
            return
        try:
            n = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object")
            self.reply(201, ingest(payload))
        except (ValueError, json.JSONDecodeError) as exc:
            self.reply(400, {"error": "invalid_request", "detail": str(exc)})

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[caeluviim] {self.address_string()} {fmt % args}")


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Caeluviim listening on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
