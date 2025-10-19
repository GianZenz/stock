import csv
import os
from datetime import datetime
from typing import Dict, List, Optional


Row = Dict[str, object]


def load_symbol_csv(symbol: str, data_dir: str) -> Optional[Dict[str, List]]:
    """
    Load OHLCV for a symbol from <data_dir>/<symbol>.csv
    Columns: Date, Open, High, Low, Close, Volume
    Returns dict of lists: date (datetime.date), open, high, low, close (float), volume (int)
    """
    path = os.path.join(data_dir, f"{symbol}.csv")
    if not os.path.exists(path):
        return None

    dates: List = []
    opens: List[float] = []
    highs: List[float] = []
    lows: List[float] = []
    closes: List[float] = []
    vols: List[int] = []

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Normalize headers by lower-casing
        field_map = {name.lower(): name for name in reader.fieldnames or []}
        required = ["date", "open", "high", "low", "close", "volume"]
        if not all(col in field_map for col in required):
            return None

        for row in reader:
            try:
                d = row[field_map["date"]]
                dt = datetime.strptime(d.strip(), "%Y-%m-%d").date()
                o = float(row[field_map["open"]])
                h = float(row[field_map["high"]])
                l = float(row[field_map["low"]])
                c = float(row[field_map["close"]])
                v_raw = row[field_map["volume"]]
                v = int(float(v_raw)) if v_raw not in (None, "") else 0
            except Exception:
                # Skip malformed rows
                continue

            dates.append(dt)
            opens.append(o)
            highs.append(h)
            lows.append(l)
            closes.append(c)
            vols.append(v)

    if not dates:
        return None

    return {
        "date": dates,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": vols,
    }

