import app

if __name__ == "__main__":
    from waitress import serve
    import os
    import json
    # Load settings for host/port
    SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')
    _APP_SETTINGS = {}
    try:
        with open(SETTINGS_FILE, 'r') as sf:
            _APP_SETTINGS = json.load(sf)
    except Exception:
        _APP_SETTINGS = {}
    SERVER_PORT = int(_APP_SETTINGS.get('server_port', 8889))
    SERVER_HOST = _APP_SETTINGS.get('host', '0.0.0.0')
    print(f"Serving with Waitress on {SERVER_HOST}:{SERVER_PORT}")
    serve(app.app, host=SERVER_HOST, port=SERVER_PORT)
