import os
import re
from typing import List, Tuple


def discover_symbols(data_dir: str) -> List[str]:
    symbols = []
    try:
        for name in os.listdir(data_dir):
            path = os.path.join(data_dir, name)
            if os.path.isfile(path) and name.lower().endswith(".csv"):
                symbols.append(os.path.splitext(name)[0])
    except FileNotFoundError:
        pass
    return sorted(symbols)


# --- Symbol helpers ---

COMMON_TICKERS: List[str] = [
    "MSFT",
    "AAPL",
    "AMZN",
    "GOOGL",
    "META",
    "TSLA",
    "NVDA",
    "IBM",
    "NFLX",
    "AMD",
    "INTC",
    "ORCL",
    "UBER",
    "SHOP",
    "BA",
    "DIS",
    "V",
    "MA",
    "JPM",
    "WMT",
]


def parse_symbols(text: str) -> List[str]:
    return [s.strip().upper() for s in (text or "").split(",") if s.strip()]


_SYMBOL_RE = re.compile(r"^[A-Z][A-Z0-9.\-]{0,5}$")


def is_plausible_symbol(sym: str) -> bool:
    return bool(_SYMBOL_RE.match(sym))


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev = dp[0]
        dp[0] = i
        for j, cb in enumerate(b, 1):
            cur = dp[j]
            cost = 0 if ca == cb else 1
            dp[j] = min(
                dp[j] + 1,      # deletion
                dp[j - 1] + 1,  # insertion
                prev + cost,    # substitution
            )
            prev = cur
    return dp[-1]


def suggest_symbol(sym: str) -> str | None:
    # Offer suggestion if close to a common ticker (edit distance <= 2)
    best = None
    best_d = 10**9
    for cand in COMMON_TICKERS:
        d = _levenshtein(sym, cand)
        if d < best_d:
            best = cand
            best_d = d
    return best if best is not None and best_d <= 2 else None


def validate_and_suggest(symbols: List[str]) -> Tuple[List[str], List[Tuple[str, str | None]]]:
    valid: List[str] = []
    issues: List[Tuple[str, str | None]] = []
    for s in symbols:
        if is_plausible_symbol(s):
            valid.append(s)
        else:
            issues.append((s, suggest_symbol(s)))
    return valid, issues

