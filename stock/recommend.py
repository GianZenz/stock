from typing import Dict, List, Tuple, Callable, Optional

from .data.csv_provider import load_symbol_csv
from .strategy.sma_crossover import evaluate_symbol


def _score(features: Dict) -> float:
    score = 0.0

    # Reward recent bull crossover
    events = features.get("events") or []
    if events:
        idx, last_type = events[-1]
        # fresher events get higher weight
        recency = max(1, 10 if idx >= len(features["sma_fast"]) - 10 else len(features["sma_fast"]) - idx)
        if last_type == "bull":
            score += 2.0 + 10.0 / recency
        else:
            score -= 1.0 + 10.0 / recency

    # Price vs 200SMA distance
    dist200 = features.get("dist_200sma_pct")
    if isinstance(dist200, (int, float)):
        score += 0.05 * dist200  # modest boost if above, penalty if below

    # 50SMA slope (uptrend)
    slope = features.get("sma50_slope")
    if isinstance(slope, (int, float)):
        score += 10.0 * slope

    return float(score)


def _decision(features: Dict) -> Tuple[str, List[str]]:
    """Return (decision, reasons). Decision is 'BUY' or 'DON'T BUY'."""
    reasons: List[str] = []
    last_signal = features.get("last_signal")
    dist200 = features.get("dist_200sma_pct")
    slope = features.get("sma50_slope")

    buy_checks = 0
    total_checks = 0

    # Check 1: Most recent signal is bullish
    total_checks += 1
    if last_signal == "bull":
        buy_checks += 1
        reasons.append("Recent bullish crossover")
    else:
        reasons.append("Last signal not bullish")

    # Check 2: Price above 200SMA
    total_checks += 1
    if isinstance(dist200, (int, float)) and dist200 >= 0:
        buy_checks += 1
        reasons.append("Price above 200SMA")
    else:
        reasons.append("Price not above 200SMA")

    # Check 3: 50SMA upward slope
    total_checks += 1
    if isinstance(slope, (int, float)) and slope > 0:
        buy_checks += 1
        reasons.append("50SMA trending up")
    else:
        reasons.append("50SMA not trending up")

    decision = "BUY" if buy_checks >= 2 else "DON'T BUY"
    return decision, reasons


def analyze_and_rank_with_loader(symbols: List[str], loader: Callable[[str], Optional[Dict]], fast: int = 50, slow: int = 200) -> List[Dict]:
    results: List[Dict] = []
    for sym in symbols:
        ts = loader(sym)
        if not ts:
            continue
        feats = evaluate_symbol(ts, fast=fast, slow=slow)
        score = _score(feats)
        decision, reasons = _decision(feats)
        results.append(
            {
                "symbol": sym,
                "score": score,
                "meta": {
                    "last_close": feats.get("last_close"),
                    "dist_200sma_pct": feats.get("dist_200sma_pct"),
                    "sma50_slope": feats.get("sma50_slope"),
                    "last_signal": feats.get("last_signal"),
                    "decision": decision,
                    "decision_reasons": reasons,
                },
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def analyze_and_rank(symbols: List[str], data_dir: str, fast: int = 50, slow: int = 200) -> List[Dict]:
    """Backward-compatible wrapper using CSV data from data_dir."""
    def loader(sym: str):
        return load_symbol_csv(sym, data_dir)

    return analyze_and_rank_with_loader(symbols, loader, fast=fast, slow=slow)
