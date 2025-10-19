import json
import os
import time
from datetime import datetime
from typing import Callable, Dict, List, Optional


def _encode_timeseries(ts: Dict[str, List]) -> Dict[str, List]:
    out: Dict[str, List] = {}
    for k, v in ts.items():
        if k == "date":
            out[k] = [d.isoformat() if hasattr(d, "isoformat") else str(d) for d in v]
        else:
            out[k] = v
    return out


def _decode_timeseries(data: Dict[str, List]) -> Dict[str, List]:
    out: Dict[str, List] = {}
    for k, v in data.items():
        if k == "date":
            conv = []
            for s in v:
                try:
                    conv.append(datetime.strptime(str(s), "%Y-%m-%d").date())
                except Exception:
                    conv.append(str(s))
            out[k] = conv
        else:
            out[k] = v
    return out


def make_cached_loader(
    inner_loader: Callable[[str], Optional[Dict[str, List]]],
    source: str,
    cache_dir: str = ".cache",
    ttl_hours: int = 24,
    throttle_ms: int = 400,
) -> Callable[[str], Optional[Dict[str, List]]]:
    """Wrap a loader with on-disk caching and simple throttling.

    Cache layout: <cache_dir>/<source>/<SYMBOL>.json
    """
    src = (source or "misc").lower()
    base = os.path.join(cache_dir, src)
    os.makedirs(base, exist_ok=True)
    ttl_secs = max(0, ttl_hours) * 3600
    last_call = 0.0

    def _load(symbol: str) -> Optional[Dict[str, List]]:
        nonlocal last_call
        sym = symbol.upper().strip()
        path = os.path.join(base, f"{sym}.json")

        # Try cache first
        try:
            if os.path.exists(path) and (time.time() - os.path.getmtime(path) <= ttl_secs):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return _decode_timeseries(data)
        except Exception:
            pass

        # Throttle
        now = time.time()
        wait = (throttle_ms / 1000.0) - (now - last_call)
        if wait > 0:
            time.sleep(wait)
        last_call = time.time()

        ts = inner_loader(sym)
        if ts:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(_encode_timeseries(ts), f)
            except Exception:
                pass
        return ts

    return _load

