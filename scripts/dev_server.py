from __future__ import annotations

import http.client
import http.server
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PORT = int(os.getenv('FRONTEND_PORT', '3000'))
API_PORT = int(os.getenv('API_PORT', '8000'))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _proxy(self):
        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length) if length else None
        conn = http.client.HTTPConnection('127.0.0.1', API_PORT, timeout=95)
        try:
            conn.request(self.command, self.path, body=body, headers={k: v for k, v in self.headers.items() if k.lower() not in {'host', 'connection'}})
            response = conn.getresponse()
            payload = response.read()
            self.send_response(response.status, response.reason)
            for key, value in response.getheaders():
                if key.lower() not in {'transfer-encoding', 'connection', 'content-length'}:
                    self.send_header(key, value)
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        finally:
            conn.close()

    def do_GET(self):
        if urlsplit(self.path).path.startswith('/api/'):
            self._proxy()
        else:
            super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path.startswith('/api/'):
            self._proxy()
        else:
            self.send_error(405, 'Method Not Allowed')


def main():
    api = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'api.index:app', '--host', '127.0.0.1', '--port', str(API_PORT)])
    try:
        print(f'Orange Test: http://127.0.0.1:{PORT}')
        print(f'API:         http://127.0.0.1:{API_PORT}')
        http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
    finally:
        api.terminate()
        api.wait(timeout=5)

if __name__ == '__main__':
    main()
