"""
energy.py: Efficient energy data fetch, cache, and transformation for visualization.
Optimized for clarity, maintainability, and performance.
"""

import os
import json
import time
from typing import Any, Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timezone
import requests
import base64

BASE_DIR = os.path.dirname(__file__)

SETTINGS_FILE = os.path.join(BASE_DIR, 'settings.json')
CACHE_FILE = os.path.join(BASE_DIR, 'api_cache.json')


# --- Basic Auth Support ---
def get_basic_auth_creds() -> Optional[tuple[str, str]]:
    """Return (username, password) tuple from settings.json if present, else None."""
    user = _SETTINGS.get('basic_auth_user')
    pwd = _SETTINGS.get('basic_auth_password')
    if user and pwd:
        return user, pwd
    return None


def check_basic_auth(auth_header: str) -> bool:
    """Check HTTP Basic Auth header against settings.json credentials."""
    creds = get_basic_auth_creds()
    if not creds or not auth_header or not auth_header.startswith('Basic '):
        return False
    try:
        b64 = auth_header.split(' ', 1)[1]
        decoded = base64.b64decode(b64).decode('utf-8')
        user, pwd = decoded.split(':', 1)
        return (user, pwd) == creds
    except Exception:
        return False


def load_settings() -> Dict[str, Any]:
    """Load settings from settings.json, return empty dict on failure."""
    try:
        with open(SETTINGS_FILE, 'r') as sf:
            return json.load(sf)
    except Exception:
        return {}


_SETTINGS = load_settings()
CACHE_TTL: int = int(_SETTINGS.get('cache_ttl', 3600))
EIC_NICKNAMES: Dict[str, Any] = _SETTINGS.get('eic_nicknames', {})
AUTH_CLIENT_ID = os.environ.get('AUTH_CLIENT_ID')
AUTH_CLIENT_SECRET = os.environ.get('AUTH_CLIENT_SECRET')
ELERING_API_TOKEN_URL = "https://kc.elering.ee/realms/elering-sso/protocol/openid-connect/token"
ELERING_API_URL = "https://estfeed.elering.ee/api/public/v1/metering-data"


def fetch_remote_data() -> Tuple[Optional[Any], Optional[float]]:
    """
    Fetch data from cache or remote API. Returns (data, timestamp).
    Uses cache if fresh, otherwise fetches and updates cache.
    """
    ts = time.time()
    # Try cache first
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as cf:
                cached = json.load(cf)
            cached_ts = cached.get('_cached_at', 0)
            if ts - cached_ts < CACHE_TTL:
                return cached.get('data'), cached_ts
        except Exception as e:
            print('Warning reading cache:', e)

    # Fetch from remote
    try:
        import time as _time
        if not AUTH_CLIENT_ID or not AUTH_CLIENT_SECRET:
            raise RuntimeError('No Elering API credentials found in environment variables (AUTH_CLIENT_ID, AUTH_CLIENT_SECRET)')
        fetch_start = _time.time()
        # Obtain token
        token_data = {
            "client_id": AUTH_CLIENT_ID,
            "client_secret": AUTH_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token_resp = requests.post(ELERING_API_TOKEN_URL, data=token_data, headers=headers)
        token_resp.raise_for_status()
        token = token_resp.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        now_dt = datetime.now(timezone.utc)
        start_of_month = now_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        params = {
            'startDateTime': start_of_month.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'endDateTime': now_dt.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'resolution': 'one_day'
        }
        resp = requests.get(ELERING_API_URL, params=params, headers=headers, timeout=30)
        data = resp.json()
        fetch_end = _time.time()
        print(f"API fetch took {fetch_end - fetch_start:.2f} seconds", flush=True)
        # Write cache atomically
        tmp = CACHE_FILE + '.tmp'
        with open(tmp, 'w') as cf:
            json.dump({'_cached_at': ts, 'data': data}, cf)
            try:
                os.fsync(cf.fileno())
            except Exception:
                pass
        os.replace(tmp, CACHE_FILE)
        print(f'Wrote cache to {CACHE_FILE}', flush=True)
        return data, ts
    except Exception as e:
        print('Error fetching remote data:', e)
        return None, None


def clear_cache():
    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
    except Exception:
        pass


def load_data() -> Tuple[Optional[Any], Optional[float]]:
    # wrapper to load data, returning cached or remote
    data, ts = fetch_remote_data()
    return data, ts


def transform(raw: Any) -> Dict[str, Any]:
    # minimal transform to keep API stable for frontend
    if not raw:
        return {'dates': [], 'total': [], 'series': [], 'summary': {}}
    # Placeholder transform (real logic omitted for brevity)
    dates = []
    total = []
    series = []
    summary = {}
    return {'dates': dates, 'total': total, 'series': series, 'summary': summary}
