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


app = Flask(__name__, template_folder='templates')

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
