#!/usr/bin/env python3
"""Small same-origin progress API for the standalone Wanjie deployment."""
from __future__ import print_function

import argparse
import hmac
import json
import os
import tempfile
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from pathlib import Path

MILESTONE_IDS = (
    "2026-brand", "2026-arch", "2026-proto", "2026-cast", "2026-loop",
    "2027-blueprint", "2027-asset", "2027-director", "2027-creator",
    "2028-coop", "2028-lod", "2028-fate", "2028-snapshot",
    "2029-market", "2029-fork", "2029-fund", "2029-share",
    "2030-society", "2030-economy", "2030-govern", "2030-persist",
    "2031-state", "2031-memory", "2031-cost", "2031-ops",
    "2032-system", "2032-gateway", "2032-memory", "2032-device",
    "2033-counter", "2033-causal", "2033-compare", "2033-open",
    "2030plus-emerge", "2030plus-cross", "2030plus-ecosystem", "2030plus-govern",
)
DEFAULT_COMPLETED = dict((identifier, identifier in ("2026-brand", "2026-arch")) for identifier in MILESTONE_IDS)
MAX_BODY_BYTES = 262144
MAX_NOTE_LENGTH = 4000
MAX_NOTES_PER_PERIOD = 100


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def default_state():
    return {"completed": dict(DEFAULT_COMPLETED), "notes": {}, "updatedAt": None}


def clean_completed(value):
    source = value if isinstance(value, dict) else {}
    return dict((identifier, source.get(identifier) is True) for identifier in MILESTONE_IDS)


def clean_notes(value):
    if not isinstance(value, dict):
        return {}
    result = {}
    for period, raw_notes in value.items():
        if not isinstance(period, str) or len(period) > 64 or not isinstance(raw_notes, list):
            continue
        cleaned = []
        for raw_note in raw_notes[:MAX_NOTES_PER_PERIOD]:
            if not isinstance(raw_note, dict):
                continue
            note_id = raw_note.get("id")
            date = raw_note.get("date")
            text = raw_note.get("text")
            if not all(isinstance(item, str) for item in (note_id, date, text)):
                continue
            text = text.strip()
            if not text or len(note_id) > 128 or len(date) > 32 or len(text) > MAX_NOTE_LENGTH:
                continue
            cleaned.append({"id": note_id, "date": date, "text": text})
        if cleaned:
            result[period] = cleaned
    return result


def credentials_match(username, password, expected_username, expected_password):
    return hmac.compare_digest(username or "", expected_username or "") and hmac.compare_digest(password or "", expected_password or "")


class ProgressStore(object):
    def __init__(self, path):
        self.path = Path(path)

    def read(self):
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                state = json.load(handle)
            return {
                "completed": clean_completed(state.get("completed")),
                "notes": clean_notes(state.get("notes")),
                "updatedAt": state.get("updatedAt") if isinstance(state.get("updatedAt"), str) else None,
            }
        except (IOError, ValueError, TypeError):
            return default_state()

    def replace(self, completed, notes):
        state = {
            "completed": clean_completed(completed),
            "notes": clean_notes(notes),
            "updatedAt": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        }
        self.path.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
        descriptor, temporary_path = tempfile.mkstemp(prefix=".progress-", suffix=".json", dir=str(self.path.parent))
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(state, handle, ensure_ascii=False, separators=(",", ":"))
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temporary_path, 0o640)
            os.replace(temporary_path, str(self.path))
        finally:
            if os.path.exists(temporary_path):
                os.unlink(temporary_path)
        return state


class ProgressHandler(BaseHTTPRequestHandler):
    store = None
    admin_username = None
    admin_password = None

    def _json(self, status, payload):
        content = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path != "/api/progress":
            self._json(404, {"error": "Not found"})
            return
        self._json(200, self.store.read())

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Allow", "GET, PUT, OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_PUT(self):
        if self.path != "/api/progress/admin":
            self._json(404, {"error": "Not found"})
            return
        if not credentials_match(
            self.headers.get("x-admin-username"),
            self.headers.get("x-admin-password"),
            self.admin_username,
            self.admin_password,
        ):
            self._json(401, {"error": "Unauthorized"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                raise ValueError("invalid body length")
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(body, dict):
                raise ValueError("body must be an object")
        except (UnicodeDecodeError, ValueError, TypeError):
            self._json(400, {"error": "Invalid JSON request"})
            return
        self._json(200, self.store.replace(body.get("completed"), body.get("notes")))

    def log_message(self, format_string, *args):
        print("%s - %s" % (self.address_string(), format_string % args))


def main():
    parser = argparse.ArgumentParser(description="Wanjie standalone progress API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=18080, type=int)
    parser.add_argument("--data-file", default=os.environ.get("WANJIE_DATA_FILE", "/var/lib/wanjie-zongheng/progress.json"))
    args = parser.parse_args()
    username = os.environ.get("WANJIE_ADMIN_USERNAME")
    password = os.environ.get("WANJIE_ADMIN_PASSWORD")
    if not username or not password:
        raise SystemExit("WANJIE_ADMIN_USERNAME and WANJIE_ADMIN_PASSWORD must be set")
    ProgressHandler.store = ProgressStore(args.data_file)
    ProgressHandler.admin_username = username
    ProgressHandler.admin_password = password
    server = ThreadingHTTPServer((args.host, args.port), ProgressHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
