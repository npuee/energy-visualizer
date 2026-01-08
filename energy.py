import requests
import json
import os
import time
from collections import defaultdict
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(__file__)
CACHE_FILE = os.path.join(BASE_DIR, 'api_cache.json')

# load settings if available
SETTINGS_FILE = os.path.join(BASE_DIR, 'settings.json')
_SETTINGS = {}
try:
    with open(SETTINGS_FILE, 'r') as sf:
        _SETTINGS = json.load(sf)
except Exception:
    _SETTINGS = {}


# load settings
CACHE_TTL = int(_SETTINGS.get('cache_ttl', 3600))  # seconds
EIC_NICKNAMES = _SETTINGS.get('eic_nicknames', {})
auth_data = _SETTINGS.get('auth_data')

# Elering endpoints
elering_api_token_url = "https://kc.elering.ee/realms/elering-sso/protocol/openid-connect/token"
elering_api_url = "https://estfeed.elering.ee/api/public/v1/metering-data"

def fetch_remote_data():
    ts = time.time()
    # try returning a fresh cache first
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as cf:
                cached = json.load(cf)
            cached_ts = cached.get('_cached_at', 0)
            if ts - cached_ts < CACHE_TTL:
                return cached.get('data'), cached_ts
    except Exception as e:
        print('Warning reading cache:', e)

    # fetch from remote
    try:
        # If auth_data provided, call Elering API with token and params
        if auth_data:
            # obtain token
            token_url = _SETTINGS.get('elering_api_token_url', elering_api_token_url)
            try:
                token_resp = requests.post(token_url, data=auth_data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=10)
                token_resp.raise_for_status()
                token = token_resp.json().get('access_token')
            except Exception as e:
                print('Failed to get auth token:', e)
                raise

            headers = {'Authorization': f'Bearer {token}'}
            now_dt = datetime.now(timezone.utc)
            start_of_month = now_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_iso = start_of_month.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            end_iso = now_dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            params = {
                'startDateTime': start_iso,
                'endDateTime': end_iso,
                'resolution': 'one_day'
            }
            resp = requests.get(elering_api_url, params=params, headers=headers, timeout=30)

        resp.raise_for_status()
        data = resp.json()
        # write cache atomically
        try:
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
        except Exception as e:
            print(f'Warning: failed to write cache {CACHE_FILE}: {e}')
        return data, ts
    except Exception as e:
        print('Fetch error:', e)
        # on fetch error, try returning any cached data even if stale
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r') as cf:
                    cached = json.load(cf)
                return cached.get('data'), cached.get('_cached_at', None)
        except Exception as e2:
            print('Failed to read stale cache:', e2)
    return None, None


def load_data():
    # Prefer remote data (cached or fresh). If nothing available, return empty dataset.
    data, ts = fetch_remote_data()
    if data:
        return data, ts
    # no remote data and no cache -> return empty dataset and current time
    return [], time.time()


def transform(data):
    # Build per-meter series and aggregate totals by date
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
        # try to match EIC nickname and color
        display = label
        color = None
        # EIC_NICKNAMES may map eic -> {nick, color} or eic -> nick string
        for eic_key, eic_val in EIC_NICKNAMES.items():
            try:
                nick = eic_val['nick'] if isinstance(eic_val, dict) else eic_val
            except Exception:
                nick = eic_val
            if eic_key and eic_key in label:
                display = nick or label
                color = eic_val.get('color') if isinstance(eic_val, dict) else None
                break
            if nick and nick in label:
                display = nick
                color = eic_val.get('color') if isinstance(eic_val, dict) else None
                break

        series.append({'label': label, 'display': display, 'color': color, 'per_date': per_date})

    dates = sorted(list(dates_set))
    series_out = []
    for s in series:
        values = [s['per_date'].get(d, 0.0) for d in dates]
        series_out.append({'label': s['label'], 'display': s.get('display'), 'color': s.get('color'), 'values': values})

    total_values = [totals_by_date.get(d, 0.0) for d in dates]

    overall_total = sum(total_values)
    avg_per_day = overall_total / len(dates) if dates else 0
    summary = {
        'total_kwh': round(overall_total, 3),
        'avg_per_day_kwh': round(avg_per_day, 3),
        'min_day_kwh': round(min(total_values), 3) if total_values else 0,
        'max_day_kwh': round(max(total_values), 3) if total_values else 0
    }

    return {
        'dates': dates,
        'series': series_out,
        'total': total_values,
        'summary': summary,
    }


def clear_cache():
    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
            return True
    except Exception:
        pass
    return False
