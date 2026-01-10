from flask import Flask, render_template, jsonify, request, Response
import time
import os
import json
import energy
def require_basic_auth():
    creds = energy.get_basic_auth_creds()
    if not creds:
        return  # No auth required
    auth = request.headers.get('Authorization')
    if not energy.check_basic_auth(auth):
        return Response(
            'Authentication required',
            401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        )


import logging
import sys
app = Flask(__name__, template_folder='templates')

# load server settings early so logging can be controlled via settings.json
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')
_APP_SETTINGS = {}
try:
    with open(SETTINGS_FILE, 'r') as sf:
        _APP_SETTINGS = json.load(sf)
except Exception:
    _APP_SETTINGS = {}

# Configure request logging only when enabled in settings.json
if _APP_SETTINGS.get('enable_request_logging', False):
    # Configure logging to stdout so logs appear in container logs and under Waitress
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
    stdout_handler.setLevel(logging.INFO)

    # Replace handlers to ensure consistent stdout output
    app.logger.handlers[:] = []
    app.logger.addHandler(stdout_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False

    # Ensure Werkzeug and Waitress loggers also use stdout
    for lg_name in ('werkzeug', 'waitress'):
        lg = logging.getLogger(lg_name)
        lg.handlers[:] = []
        lg.addHandler(stdout_handler)
        lg.setLevel(logging.INFO)
        lg.propagate = False

    from flask import g
    @app.before_request
    def _log_request_start():
        g._req_start = time.time()
        try:
            qs = ('?' + request.query_string.decode()) if request.query_string else ''
            hdrs = dict(request.headers)
            hdrs.pop('Authorization', None)
            app.logger.info(f"[REQUEST] {request.remote_addr} {request.method} {request.path}{qs} headers={hdrs}")
        except Exception:
            app.logger.info(f"[REQUEST] {request.method} {request.path}")

    @app.after_request
    def _log_request_end(response):
        try:
            start = getattr(g, '_req_start', None)
            duration = (time.time() - start) if start else 0
        except Exception:
            duration = 0
        app.logger.info(f"[RESPONSE] {request.remote_addr} {request.method} {request.path} -> {response.status_code} {duration:.3f}s")
        return response

# load server settings
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')
_APP_SETTINGS = {}
try:
    with open(SETTINGS_FILE, 'r') as sf:
        _APP_SETTINGS = json.load(sf)
except Exception:
    _APP_SETTINGS = {}

SERVER_PORT = int(_APP_SETTINGS.get('server_port', 8889))


@app.route('/')
def index():
    auth_resp = require_basic_auth()
    if auth_resp:
        return auth_resp
    return render_template('index.html')


@app.route('/data')
def data():
    auth_resp = require_basic_auth()
    if auth_resp:
        return auth_resp
    # support clearing cache via query param `?clear_cache=1` or `?refresh=1`
    clear = request.args.get('clear_cache') or request.args.get('refresh')
    if clear:
        try:
            energy.clear_cache()
        except Exception:
            pass

    raw, ts = energy.load_data()
    out = energy.transform(raw)
    # attach fetched timestamp in ISO UTC
    try:
        fetched_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ts))
    except Exception:
        fetched_iso = None
    out['fetched_at'] = fetched_iso
    out['fetched_at_ts'] = ts
    if clear:
        out['cache_cleared'] = True
    return jsonify(out)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVER_PORT)
