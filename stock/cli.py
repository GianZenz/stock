import argparse
import os
from typing import List

from .recommend import analyze_and_rank, analyze_and_rank_with_loader
from .utils import discover_symbols
from .data.provider import get_loader


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze stock trends from CSVs and suggest buys.")
    parser.add_argument("--data-dir", default="data", help="Directory containing <SYMBOL>.csv files (default: data)")
    parser.add_argument("--symbols", default="", help="Comma-separated list of symbols to analyze (default: discover all CSVs)")
    parser.add_argument("--top", type=int, default=10, help="How many top candidates to display")
    parser.add_argument("--fast", type=int, default=50, help="Fast SMA window (default: 50)")
    parser.add_argument("--slow", type=int, default=200, help="Slow SMA window (default: 200)")
    parser.add_argument("--source", choices=["csv", "alphavantage", "yahoo"], default="csv", help="Data source (default: csv)")
    parser.add_argument("--apikey", default="", help="API key (required for alphavantage)")
    parser.add_argument("--decision-only", action="store_true", help="Only display BUY decisions")
    parser.add_argument("--auto", type=int, default=0, help="Auto-scan N symbols from the data source (API listing for alphavantage)")
    args = parser.parse_args()

    if args.symbols.strip():
        symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    else:
        if args.auto > 0 and args.source == "alphavantage":
            from .data.provider import get_universe
            api_key = (args.apikey or os.getenv("ALPHAVANTAGE_API_KEY", "")).strip()
            symbols = get_universe("alphavantage", api_key=api_key, max_symbols=args.auto)
            if not symbols:
                print("Auto-scan returned no symbols (check API key or rate limits). Falling back to CSV discovery.")
                symbols = discover_symbols(args.data_dir)
        elif args.auto > 0 and args.source == "yahoo":
            from .data.provider import get_universe
            symbols = get_universe("yahoo", max_symbols=args.auto)
        elif args.source == "yahoo":
            from .data.provider import get_universe
            symbols = get_universe("yahoo", max_symbols=10)
            if not symbols:
                symbols = discover_symbols(args.data_dir)
        else:
            symbols = discover_symbols(args.data_dir)

    if not symbols:
        print(f"No symbols found. Place CSVs in {args.data_dir} or pass --symbols.")
        return

    # Build loader based on source
    api_key = args.apikey or os.getenv("ALPHAVANTAGE_API_KEY", "")
    loader = get_loader(args.source, data_dir=args.data_dir, api_key=api_key)
    # Wrap with cache + throttle
    try:
        from .data.cache import make_cached_loader
        loader = make_cached_loader(loader, source=args.source, cache_dir=".cache", ttl_hours=24, throttle_ms=400)
    except Exception:
        pass

    ranked = analyze_and_rank_with_loader(symbols, loader, fast=args.fast, slow=args.slow)
    if args.decision_only:
        ranked = [r for r in ranked if (r.get("meta", {}).get("decision") == "BUY")]
    if not ranked:
        print("No analyzable data found.")
        if args.source == "alphavantage" and symbols:
            print("Hint: API may be rate-limited or key invalid. Try a single symbol (e.g., MSFT with --apikey demo), wait 60s, or verify your ALPHAVANTAGE_API_KEY.")
        if args.source == "yahoo" and symbols:
            print("Hint: Yahoo may be blocked or rate-limited. Try a single symbol (e.g., MSFT), wait 30s, or check network. If issues persist, try CSV files.")
        return

    print(f"Top {min(args.top, len(ranked))} candidates (higher score = better):")
    print("SYMBOL\tSCORE\tDECISION\tLAST_CLOSE\tDIST_200SMA%\t50SMA_SLOPE\tLAST_SIGNAL")
    for i, item in enumerate(ranked[: args.top], start=1):
        meta = item["meta"]
        last_close = meta.get("last_close")
        dist200 = meta.get("dist_200sma_pct")
        slope50 = meta.get("sma50_slope")
        last_signal = meta.get("last_signal")
        decision = meta.get("decision") or "DON'T BUY"
        last_close_s = f"{last_close:.2f}" if isinstance(last_close, (int, float)) else "nan"
        dist200_s = f"{dist200:.2f}" if isinstance(dist200, (int, float)) else "nan"
        slope50_s = f"{slope50:.4f}" if isinstance(slope50, (int, float)) else "nan"
        print(f"{item['symbol']}\t{item['score']:.3f}\t{decision}\t{last_close_s}\t{dist200_s}\t{slope50_s}\t{last_signal or 'none'}")
