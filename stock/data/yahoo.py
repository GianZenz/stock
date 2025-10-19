import json
from datetime import datetime
from typing import Dict, List, Optional
from urllib.request import urlopen, Request


def _fetch_chart(symbol: str, interval: str = "1d", range_: str = "1y", host: str = "query1") -> Optional[dict]:
    url = f"https://{host}.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_}"
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"})
        with urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def load_symbol_yahoo(symbol: str, range_: str = "1y", interval: str = "1d") -> Optional[Dict[str, List]]:
    """Fetch OHLCV from Yahoo Finance chart API and normalize to dict of lists.

    Returns None on errors.
    """
    data = _fetch_chart(symbol, interval=interval, range_=range_)
    if (not data) or ("chart" in data and data.get("chart", {}).get("error")):
        # Try secondary host
        data = _fetch_chart(symbol, interval=interval, range_=range_, host="query2")
    if not data or "chart" not in data:
        return None
    chart = data.get("chart", {})
    if chart.get("error"):
        return None
    if not chart or not chart.get("result"):
        return None
    res = chart["result"][0]
    ts = res.get("timestamp") or []
    indicators = res.get("indicators", {})
    quote = (indicators.get("quote") or [{}])[0]
    adj = (indicators.get("adjclose") or [{}])[0]

    opens = quote.get("open") or []
    highs = quote.get("high") or []
    lows = quote.get("low") or []
    closes = quote.get("close") or []
    vols = quote.get("volume") or []

    if not ts or not closes:
        # Try fallback range
        if range_ != "max":
            return load_symbol_yahoo(symbol, range_="max", interval=interval)
        return None

    dates: List = []
    o_list: List[float] = []
    h_list: List[float] = []
    l_list: List[float] = []
    c_list: List[float] = []
    v_list: List[int] = []

    for i in range(len(ts)):
        try:
            dt = datetime.utcfromtimestamp(int(ts[i])).date()
            o = float(opens[i]) if opens and opens[i] is not None else None
            h = float(highs[i]) if highs and highs[i] is not None else None
            l = float(lows[i]) if lows and lows[i] is not None else None
            c = float(closes[i]) if closes and closes[i] is not None else None
            v = int(vols[i]) if vols and vols[i] is not None else 0
        except Exception:
            continue
        if c is None:
            continue
        # Some intervals may omit OHLC; approximate if needed
        if o is None:
            o = c
        if h is None:
            h = c
        if l is None:
            l = c
        dates.append(dt)
        o_list.append(o)
        h_list.append(h)
        l_list.append(l)
        c_list.append(c)
        v_list.append(v)

    if not dates:
        return None

    return {
        "date": dates,
        "open": o_list,
        "high": h_list,
        "low": l_list,
        "close": c_list,
        "volume": v_list,
    }


def probe_yahoo(symbol: str, range_: str = "1y", interval: str = "1d") -> Dict[str, str]:
    """Return a dict with diagnostics for Yahoo chart calls."""
    data = _fetch_chart(symbol, interval=interval, range_=range_)
    host_tried = "query1"
    if not data:
        data = _fetch_chart(symbol, interval=interval, range_=range_, host="query2")
        host_tried = "query1, query2"
    if not data:
        return {"status": "error", "message": "No response (network/blocked)", "host": host_tried}
    chart = data.get("chart")
    if not chart:
        return {"status": "error", "message": "Missing chart key", "host": host_tried}
    if chart.get("error"):
        err = chart.get("error") or {}
        return {"status": "error", "message": str(err), "host": host_tried}
    res = chart.get("result") or []
    if not res:
        return {"status": "error", "message": "Empty result array", "host": host_tried}
    ts = res[0].get("timestamp") or []
    return {"status": "ok", "message": f"Received {len(ts)} bars", "host": host_tried}
