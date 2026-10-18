"""Serve only the built public dashboard on loopback; never the private workspace."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);a=p.parse_args()
root=Path('dashboard/dist').resolve()
if not (root/'index.html').exists():raise SystemExit('Run scripts/build_dashboard.py first')
server=ThreadingHTTPServer(('127.0.0.1',a.port),partial(SimpleHTTPRequestHandler,directory=str(root)))
print(f'Local dashboard: http://127.0.0.1:{a.port}',flush=True)
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:server.server_close()
