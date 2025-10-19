from typing import List, Optional, Tuple


def sma(values: List[float], window: int) -> List[Optional[float]]:
    if window <= 0:
        raise ValueError("window must be > 0")
    out: List[Optional[float]] = [None] * len(values)
    s = 0.0
    for i, v in enumerate(values):
        s += v
        if i >= window:
            s -= values[i - window]
        if i >= window - 1:
            out[i] = s / window
    return out


def ema(values: List[float], window: int) -> List[Optional[float]]:
    if window <= 0:
        raise ValueError("window must be > 0")
    out: List[Optional[float]] = [None] * len(values)
    k = 2 / (window + 1)
    ema_prev: Optional[float] = None
    for i, v in enumerate(values):
        if ema_prev is None:
            ema_prev = v
        else:
            ema_prev = v * k + ema_prev * (1 - k)
        out[i] = ema_prev
    return out


def rsi(values: List[float], window: int = 14) -> List[Optional[float]]:
    if window <= 0:
        raise ValueError("window must be > 0")
    out: List[Optional[float]] = [None] * len(values)
    gains = 0.0
    losses = 0.0
    for i in range(1, len(values)):
        change = values[i] - values[i - 1]
        gains += max(change, 0.0)
        losses += max(-change, 0.0)
        if i >= window:
            old_change = values[i - window + 1] - values[i - window]
            gains -= max(old_change, 0.0)
            losses -= max(-old_change, 0.0)
        if i >= window:
            avg_gain = gains / window
            avg_loss = losses / window
            if avg_loss == 0:
                out[i] = 100.0
            else:
                rs = avg_gain / avg_loss
                out[i] = 100.0 - (100.0 / (1 + rs))
    return out


def macd(values: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    ema_fast = ema(values, fast)
    ema_slow = ema(values, slow)
    macd_line: List[Optional[float]] = [None] * len(values)
    for i in range(len(values)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            macd_line[i] = float(ema_fast[i]) - float(ema_slow[i])
    # signal line on macd
    # compute EMA but skip None values by carrying previous; simple approach
    signal_line: List[Optional[float]] = [None] * len(values)
    k = 2 / (signal + 1)
    prev = None
    for i, v in enumerate(macd_line):
        if v is None:
            signal_line[i] = prev
        else:
            prev = v if prev is None else v * k + prev * (1 - k)
            signal_line[i] = prev
    hist: List[Optional[float]] = [None if macd_line[i] is None or signal_line[i] is None else macd_line[i] - signal_line[i] for i in range(len(values))]
    return macd_line, signal_line, hist

