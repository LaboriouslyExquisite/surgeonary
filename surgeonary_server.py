#!/usr/bin/env python3
"""Local server for the Surgeonary demo. Python 3 standard library only.

    python surgeonary_server.py          (or double-click start-surgeonary.bat on Windows)

What it does:
  * Serves this folder at http://localhost:8765, like `python -m http.server`,
    plus HTTP Range support so videos can be scrubbed.
  * Professor Okafor's recordings live in ./videos. The Professor Okafor tab
    reads GET /api/okafor/videos and plays the files from /videos/.
  * Picks up videos uploaded from the Pi camera app. Every 2 s it asks the Pi
    which recordings are waiting, downloads each one into ./videos and tells
    the Pi it arrived. The laptop fetches from the Pi, so nothing on the
    laptop needs to accept incoming connections (no firewall changes).

The Pi's address is in surgeonary_config.json (created on first run), or set
the SURGEONARY_PI_URL environment variable.
"""
import datetime
import json
import os
import re
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote, unquote, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(ROOT, "videos")
CONFIG_PATH = os.path.join(ROOT, "surgeonary_config.json")
PORT = int(os.environ.get("SURGEONARY_PORT", "8765"))
VIDEO_EXT = (".mp4", ".webm", ".m4v", ".mov")
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
DEFAULT_PI_URLS = ["http://10.56.130.35:8000", "http://vr373.local:8000"]
POLL_SECONDS = 2.0


def load_config():
    cfg = {"pi_urls": DEFAULT_PI_URLS}
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg.update(json.load(f))
    except FileNotFoundError:
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except OSError:
            pass
    except (OSError, ValueError) as e:
        print("Could not read surgeonary_config.json (%s); using the default Pi address." % e)
    env = os.environ.get("SURGEONARY_PI_URL")
    if env:
        cfg["pi_urls"] = [env]
    cfg["pi_urls"] = [u.rstrip("/") for u in cfg["pi_urls"] if u]
    return cfg


def video_title(name):
    m = re.match(r"rec_(\d{8})_(\d{6})", name)
    if m:
        dt = datetime.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
        return "Recording · " + dt.strftime("%b %d, %Y, %I:%M %p").replace(" 0", " ")
    return os.path.splitext(name)[0].replace("_", " ")


def list_videos():
    out = []
    try:
        names = os.listdir(VIDEO_DIR)
    except FileNotFoundError:
        names = []
    for name in names:
        p = os.path.join(VIDEO_DIR, name)
        if not name.lower().endswith(VIDEO_EXT) or not os.path.isfile(p):
            continue
        st = os.stat(p)
        out.append({"name": name, "title": video_title(name), "size": st.st_size,
                    "mtime": st.st_mtime, "url": "/videos/" + quote(name)})
    out.sort(key=lambda v: v["mtime"], reverse=True)
    return out


class PiSync:
    """Pulls videos the Pi has queued for upload into ./videos."""

    def __init__(self, urls):
        self.urls = urls
        self.base = None
        self.reachable = False
        self.last_ok = None
        self.last_error = None
        self.downloading = None
        self.received = []

    def _get_json(self, base, path, timeout=4):
        with urllib.request.urlopen(base + path, timeout=timeout) as r:
            return json.load(r)

    def _post_json(self, base, path, body, timeout=6):
        req = urllib.request.Request(base + path, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)

    def _poll(self):
        bases = ([self.base] if self.base else []) + [u for u in self.urls if u != self.base]
        last = None
        for base in bases:
            try:
                data = self._get_json(base, "/api/uploads/pending")
                self.base, self.reachable, self.last_ok, self.last_error = base, True, time.time(), None
                return base, data.get("pending", [])
            except Exception as e:
                last = e
        self.reachable = False
        self.last_error = "Can't reach the Pi camera app at %s (%s)" % (" or ".join(self.urls), last)
        return None, []

    def _download(self, base, item):
        name = str(item.get("name", ""))
        if not NAME_RE.match(name) or not name.lower().endswith(VIDEO_EXT):
            return
        dest = os.path.join(VIDEO_DIR, name)
        size = item.get("size")
        if not (os.path.exists(dest) and (size is None or os.path.getsize(dest) == size)):
            self.downloading = name
            tmp = dest + ".part"
            try:
                with urllib.request.urlopen(base + "/recordings/" + quote(name), timeout=30) as r, \
                        open(tmp, "wb") as f:
                    shutil.copyfileobj(r, f, 1024 * 1024)
                if size is not None and os.path.getsize(tmp) != size:
                    raise IOError("incomplete download (%d of %d bytes)" % (os.path.getsize(tmp), size))
                os.replace(tmp, dest)
            finally:
                self.downloading = None
                if os.path.exists(tmp):
                    try:
                        os.remove(tmp)
                    except OSError:
                        pass
            self.received.append({"name": name, "at": time.time()})
            print("Received %s from the Pi camera" % name)
        self._post_json(base, "/api/uploads/ack", {"name": name})

    def run(self):
        while True:
            try:
                base, pending = self._poll()
                for item in pending:
                    try:
                        self._download(base, item)
                    except Exception as e:
                        self.last_error = "Download of %s failed: %s" % (item.get("name"), e)
            except Exception as e:      # never let the sync thread die
                self.last_error = str(e)
            time.sleep(POLL_SECONDS)

    def status(self):
        return {"pi_url": self.base or (self.urls[0] if self.urls else None),
                "pi_reachable": self.reachable,
                "last_ok": self.last_ok, "error": self.last_error,
                "downloading": self.downloading, "received": self.received[-10:],
                "now": time.time()}


SYNC = PiSync(load_config()["pi_urls"])


class Handler(SimpleHTTPRequestHandler):
    # Windows' registry can map .js to text/plain; pin the types this app needs.
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      ".js": "application/javascript", ".mjs": "application/javascript",
                      ".html": "text/html", ".css": "text/css", ".json": "application/json",
                      ".mp4": "video/mp4", ".m4v": "video/mp4", ".webm": "video/webm",
                      ".mov": "video/quicktime", ".jpg": "image/jpeg", ".png": "image/png",
                      ".svg": "image/svg+xml", ".wasm": "application/wasm"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, fmt, *args):
        pass                                    # keep the console readable

    def end_headers(self):
        if self.path.startswith("/videos/"):
            self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/okafor/videos":
            return self._json({"videos": list_videos(), "sync": SYNC.status()})
        if path == "/api/okafor/status":
            return self._json(SYNC.status())
        if path.startswith("/videos/") and self.headers.get("Range"):
            return self._send_range(path)
        try:
            return super().do_GET()
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            pass

    def _send_range(self, path):
        name = unquote(path[len("/videos/"):])
        fpath = os.path.join(VIDEO_DIR, name)
        if not NAME_RE.match(name) or not os.path.isfile(fpath):
            return self.send_error(404)
        size = os.path.getsize(fpath)
        m = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
        if not m or (not m.group(1) and not m.group(2)):
            return super().do_GET()
        if m.group(1):
            start = int(m.group(1))
            end = int(m.group(2)) if m.group(2) else size - 1
        else:                                   # suffix range: last N bytes
            start, end = max(0, size - int(m.group(2))), size - 1
        end = min(end, size - 1)
        if start > end or start >= size:
            self.send_response(416)
            self.send_header("Content-Range", "bytes */%d" % size)
            self.end_headers()
            return
        length = end - start + 1
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(fpath))
        self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Length", str(length))
        self.end_headers()
        try:
            with open(fpath, "rb") as f:
                f.seek(start)
                while length > 0:
                    chunk = f.read(min(256 * 1024, length))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    length -= len(chunk)
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            pass


def main():
    os.makedirs(VIDEO_DIR, exist_ok=True)
    url = "http://localhost:%d/index.html#okafor" % PORT
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        print("Port %d is already in use. If Surgeonary is already running, use the window that is open." % PORT)
        if "--no-browser" not in sys.argv:
            webbrowser.open(url)
        return
    server.daemon_threads = True
    threading.Thread(target=SYNC.run, daemon=True).start()
    print("Surgeonary is running at http://localhost:%d/index.html" % PORT)
    print("Professor Okafor's videos: %s" % VIDEO_DIR)
    print("Picking up uploads from the Pi camera at: %s" % ", ".join(SYNC.urls))
    print("Keep this window open while you use Surgeonary. Close it to stop.")
    if "--no-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
