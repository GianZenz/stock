import json
from datetime import datetime
from typing import Dict, List, Optional
from urllib.request import urlopen
from urllib.parse import urlencode
import csv


def _fetch_json(params: Dict[str, str]) -> Optional[dict]:
    url = "https://www.alphavantage.co/query?" + urlencode(params)
    try:
        with urlopen(url, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def load_symbol_alphavantage(symbol: str, api_key: str, outputsize: str = "compact") -> Optional[Dict[str, List]]:
    """Fetch daily OHLCV from Alpha Vantage and return csv-like dict of lists.

    Uses TIME_SERIES_DAILY_ADJUSTED. 'outputsize' can be 'compact' (~100 bars) or 'full'.
    Returns None if any error occurs.
    """
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "outputsize": outputsize,
        "apikey": api_key,
    }
    data = _fetch_json(params)
    if data is None:
        return None

    key = None
    for k in data.keys():
        if "Time Series" in k:
            key = k
            break
    if not key or key not in data:
        # Fallback to non-adjusted endpoint
        params["function"] = "TIME_SERIES_DAILY"
        data = _fetch_json(params) or {}
        key = next((k for k in data.keys() if "Time Series" in k), None)
        if not key or key not in data:
            return None

    ts = data[key]
    dates = []
    opens: List[float] = []
    highs: List[float] = []
    lows: List[float] = []
    closes: List[float] = []
    vols: List[int] = []

    # Alpha Vantage dates are in descending order by default; collect and sort ascending
    rows = []
    for ds, row in ts.items():
        try:
            dt = datetime.strptime(ds, "%Y-%m-%d").date()
            o = float(row.get("1. open"))
            h = float(row.get("2. high"))
            l = float(row.get("3. low"))
            c = float(row.get("4. close"))
            v = int(float(row.get("6. volume", 0)))
            rows.append((dt, o, h, l, c, v))
        except Exception:
            continue

    if not rows:
        return None

    rows.sort(key=lambda r: r[0])
    for r in rows:
        dates.append(r[0])
        opens.append(r[1])
        highs.append(r[2])
        lows.append(r[3])
        closes.append(r[4])
        vols.append(r[5])

    return {
        "date": dates,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": vols,
    }


def probe_alphavantage(symbol: str, api_key: str, outputsize: str = "compact") -> Dict[str, str]:
    """Return a dict with diagnostics from Alpha Vantage for a symbol.

    Keys: status ('ok'|'error'), message, meta (optional)
    """
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "outputsize": outputsize,
        "apikey": api_key,
    }
    url = "https://www.alphavantage.co/query?" + urlencode(params)
    try:
        with urlopen(url, timeout=20) as resp:
            text = resp.read().decode("utf-8")
            try:
                data = json.loads(text)
            except Exception:
                return {"status": "error", "message": "Non-JSON response (possible network/proxy)", "raw": text[:200]}
    except Exception as e:
        return {"status": "error", "message": f"Network/parse error: {e}"}

    if isinstance(data, dict):
        if any(k.lower() == "note" for k in data.keys()):
            return {"status": "error", "message": data.get("Note") or "Rate limit / Note from API"}
        if any(k.lower() == "error message" for k in data.keys()):
            return {"status": "error", "message": data.get("Error Message") or "Error from API"}
        if any(k.lower() == "information" for k in data.keys()):
            return {"status": "error", "message": data.get("Information") or "Information from API"}
        if any(k.lower() == "message" for k in data.keys()):
            return {"status": "error", "message": data.get("Message") or "Message from API"}
        ts_key = next((k for k in data.keys() if "Time Series" in k), None)
        if ts_key and isinstance(data.get(ts_key), dict):
            bars = len(data[ts_key])
            return {"status": "ok", "message": f"Received {bars} bars", "meta": ts_key}

    # Provide keys seen to aid troubleshooting
    keys = ", ".join(list(data.keys())[:6]) if isinstance(data, dict) else "(non-dict)"
    return {"status": "error", "message": f"Unexpected API response", "keys": keys}


def list_symbols_alphavantage(api_key: str, state: str = "active", max_symbols: int = 50, exchanges: Optional[List[str]] = None) -> List[str]:
    """Fetch a list of symbols from Alpha Vantage LISTING_STATUS (CSV).

    - state: 'active' or 'delisted'
    - exchanges: optional allowlist (e.g., ['NYSE', 'NASDAQ'])
    - max_symbols: cap to avoid huge scans and rate limits downstream
    Returns list of symbol strings.
    """
    params = {
        "function": "LISTING_STATUS",
        "state": state,
        "apikey": api_key,
        "datatype": "csv",
    }
    url = "https://www.alphavantage.co/query?" + urlencode(params)
    symbols: List[str] = []
    try:
        with urlopen(url, timeout=30) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return symbols

    # Parse CSV
    try:
        reader = csv.DictReader(text.splitlines())
        for row in reader:
            sym = (row.get("symbol") or "").strip().upper()
            exch = (row.get("exchange") or "").strip().upper()
            status = (row.get("status") or "").strip().lower()
            if not sym:
                continue
            if state and status and status != state:
                continue
            if exchanges:
                if exch.upper() not in [e.upper() for e in exchanges]:
                    continue
            symbols.append(sym)
            if len(symbols) >= max_symbols:
                break
    except Exception:
        return []

    return symbols
