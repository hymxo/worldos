#!/usr/bin/env python3
"""万界纵横本地站点服务：静态 SPA + /api/progress API（合并单进程）。

静态根目录: current/standalone-dist
API 实现复用 current/standalone/progress_server.py 的 ProgressHandler
"""
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE / "current" / "standalone-dist"
sys.path.insert(0, str((BASE / "current" / "standalone")))

import progress_server as ps  # noqa: E402


class Handler(ps.ProgressHandler, SimpleHTTPRequestHandler):
    """MRO: ProgressHandler 提供 _json / do_PUT 逻辑，SimpleHTTP 提供静态服务。"""

    def __init__(self, *args, **kwargs):
        kwargs["directory"] = str(ROOT)
        SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)

    def _path(self):
        return self.path.split("?", 1)[0]

    def do_GET(self):
        if self._path() == "/api/progress":
            return ps.ProgressHandler.do_GET(self)
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_HEAD(self):
        return SimpleHTTPRequestHandler.do_HEAD(self)

    def do_PUT(self):
        if self._path() == "/api/progress/admin":
            return ps.ProgressHandler.do_PUT(self)
        self.send_error(405, "Method Not Allowed")

    def send_head(self):
        # SPA fallback: 不存在的路径交给 index.html
        translated = self.translate_path(self.path)
        if not os.path.exists(translated):
            self.path = "/index.html"
        return SimpleHTTPRequestHandler.send_head(self)

    def log_message(self, format, *args):
        sys.stdout.write("%s - %s\n" % (self.address_string(), format % args))
        sys.stdout.flush()


def main():
    host = os.environ.get("WANJIE_HOST", "0.0.0.0")
    port = int(os.environ.get("WANJIE_PORT", "8080"))
    data_file = os.environ.get("WANJIE_DATA_FILE", str(BASE / "data" / "progress.json"))
    username = os.environ.get("WANJIE_ADMIN_USERNAME")
    password = os.environ.get("WANJIE_ADMIN_PASSWORD")
    if not username or not password:
        raise SystemExit("WANJIE_ADMIN_USERNAME / WANJIE_ADMIN_PASSWORD 未设置")

    Handler.store = ps.ProgressStore(data_file)
    Handler.admin_username = username
    Handler.admin_password = password

    server = ThreadingHTTPServer((host, port), Handler)
    print("万界纵横本地站点: http://%s:%d/  (root=%s, data=%s)" % (host, port, ROOT, data_file))
    sys.stdout.flush()
    server.serve_forever()


if __name__ == "__main__":
    main()
