
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

BASE_DIR = os.path.dirname(__file__)

SETTINGS_FILE = os.path.join(BASE_DIR, 'settings.json')
CACHE_FILE = os.path.join(BASE_DIR, 'api_cache.json')

# --- Basic Auth Support ---
import base64

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
AUTH_DATA = _SETTINGS.get('auth_data')
ELERING_API_TOKEN_URL = _SETTINGS.get('elering_api_token_url', "https://kc.elering.ee/realms/elering-sso/protocol/openid-connect/token")
ELERING_API_URL = _SETTINGS.get('elering_api_url', "https://estfeed.elering.ee/api/public/v1/metering-data")

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
        if AUTH_DATA:
            # Obtain token
            token_resp = requests.post(
                ELERING_API_TOKEN_URL,
                data=AUTH_DATA,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
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
            resp.raise_for_status()
            data = resp.json()
        else:
            raise RuntimeError('No auth_data in settings.json')

        # Write cache atomically
        tmp = CACHE_FILE + '.tmp'
        with open(tmp, 'w') as cf:
            json.dump({'_cached_at': ts, 'data': data}, cf)
            cf.flush()
            try:
                os.fsync(cf.fileno())
            except Exception:
                pass
        os.replace(tmp, CACHE_FILE)
        print(f'Wrote cache to {CACHE_FILE}')
        return data, ts
    except Exception as e:
        print('Fetch error:', e)
        # On fetch error, try returning any cached data even if stale
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as cf:
                    cached = json.load(cf)
                return cached.get('data'), cached.get('_cached_at', None)
            except Exception as e2:
                print('Failed to read stale cache:', e2)
        return None, None

def load_data() -> Tuple[Any, float]:
    """Return (data, timestamp). If no data, returns empty list and current time."""
    data, ts = fetch_remote_data()
    if data:
        return data, ts
    return [], time.time()

def _match_eic(label: str) -> Tuple[str, Optional[str]]:
    """Return (display, color) for a given EIC label using EIC_NICKNAMES."""
    for eic_key, eic_val in EIC_NICKNAMES.items():
        nick = eic_val['nick'] if isinstance(eic_val, dict) else eic_val
        color = eic_val.get('color') if isinstance(eic_val, dict) else None
        if (eic_key and eic_key in label) or (nick and nick in label):
            return nick or label, color
    return label, None

def transform(data: Any) -> Dict[str, Any]:
    """
    Transform raw API data into structure for visualization.
    Returns dict with summary, dates, series, and total.
    """
    series = []
    totals_by_date = defaultdict(float)
    dates_set = set()

    for meter in data:
        label = meter.get('meteringPointEic') or 'unknown'
        intervals = meter.get('accountingIntervals', [])
        per_date = {}
        for it in intervals:
            period = it.get('periodStart', '')
            date = period.split('T')[0]
            val = float(it.get('consumptionKwh') or 0)
            per_date[date] = val
            totals_by_date[date] += val
            dates_set.add(date)
        display, color = _match_eic(label)
        series.append({'label': label, 'display': display, 'color': color, 'per_date': per_date})

    dates = sorted(dates_set)
    series_out = [
        {
            'label': s['label'],
            'display': s['display'],
            'color': s['color'],
            'values': [s['per_date'].get(d, 0.0) for d in dates]
        }
        for s in series
    ]
    total_values = [totals_by_date.get(d, 0.0) for d in dates]

    overall_total = sum(total_values)
    avg_per_day = overall_total / len(dates) if dates else 0
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_idx = dates.index(today_str) if today_str in dates else None
    min_candidates = [v for i, v in enumerate(total_values) if i != today_idx] if today_idx is not None else total_values
    min_day_kwh = round(min(min_candidates), 3) if min_candidates else 0
    max_day_kwh = round(max(total_values), 3) if total_values else 0
    today_kwh = total_values[today_idx] if today_idx is not None else None

    summary = {
        'total_kwh': round(overall_total, 3),
        'avg_per_day_kwh': round(avg_per_day, 3),
        'min_day_kwh': min_day_kwh,
        'max_day_kwh': max_day_kwh,
        'today_kwh': round(today_kwh, 3) if today_kwh is not None else None
    }

    return {
        'summary': summary,
        'dates': dates,
        'series': series_out,
        'total': total_values,
    }

def clear_cache() -> bool:
    """Delete the cache file if it exists. Returns True if deleted."""
    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
            return True
    except Exception:
        pass
    return False
