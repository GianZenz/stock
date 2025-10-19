from typing import Dict, List, Optional, Tuple

from ..indicators import sma


def _crossovers(fast: List[Optional[float]], slow: List[Optional[float]]) -> List[Tuple[int, str]]:
    """Return list of (index, 'bull'|'bear') crossover events."""
    events: List[Tuple[int, str]] = []
    prev_diff: Optional[float] = None
    for i in range(len(fast)):
        f = fast[i]
        s = slow[i]
        if f is None or s is None:
            continue
        diff = f - s
        if prev_diff is not None:
            if prev_diff <= 0 and diff > 0:
                events.append((i, "bull"))
            elif prev_diff >= 0 and diff < 0:
                events.append((i, "bear"))
        prev_diff = diff
    return events


def evaluate_symbol(ts: Dict[str, List], fast: int = 50, slow: int = 200) -> Dict:
    closes: List[float] = ts["close"]
    sma_fast = sma(closes, fast)
    sma_slow = sma(closes, slow)
    events = _crossovers(sma_fast, sma_slow)

    last_signal: Optional[str] = None
    if events:
        last_signal = events[-1][1]

    # Distance of last close vs slow SMA
    last_close = closes[-1] if closes else None
    last_slow = sma_slow[-1] if sma_slow else None
    dist_200sma_pct: Optional[float] = None
    if last_close is not None and last_slow is not None and last_slow != 0:
        dist_200sma_pct = (last_close - float(last_slow)) / float(last_slow) * 100.0

    # 50SMA slope approximation via last N diffs
    slope_window = 5
    slope: Optional[float] = None
    if len(sma_fast) >= slope_window and sma_fast[-1] is not None and sma_fast[-slope_window] is not None:
        slope = (float(sma_fast[-1]) - float(sma_fast[-slope_window])) / slope_window

    return {
        "sma_fast": sma_fast,
        "sma_slow": sma_slow,
        "events": events,
        "last_signal": last_signal,
        "last_close": last_close,
        "dist_200sma_pct": dist_200sma_pct,
        "sma50_slope": slope,
    }

