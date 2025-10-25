Stock Trend Advisor

Overview

- Analyze stock trends and rank buy candidates using a simple, transparent SMA crossover strategy (Fast vs. Slow moving averages).
- Three ways to use it:
  - Web UI (FastAPI + Jinja) — modern, easiest to use
  - Desktop GUI (Tkinter) — lightweight, no extra deps
  - CLI — scriptable and fast

Quick Start (Web UI)

1) Run the web app (auto-installs FastAPI deps if needed):
   - `python -m stock.web`
2) Open http://127.0.0.1:8000/
3) Choose options and click Analyze:
   - Source: Yahoo (no key), Alpha Vantage (API key), or CSV
   - Preset (Yahoo): S&P 100 or NASDAQ 100
   - Auto Count: 20/50/80/All
   - Strategy Preset: Conservative (50/200) or Responsive (20/50) or Custom
   - Optional: toggle “Manual symbols” to enter tickers
   - Use “Buy only” or “Compact view”; click “Guide” for a short strategy explainer

Other Ways To Run

- Desktop GUI (Tkinter)
  - `python -m stock.gui`
  - Source-driven controls: Preset + Auto (Yahoo) / Auto (API) / Discover (CSV)

- CLI examples
  - Auto Yahoo universe (no typing):
    - `python main.py --source yahoo --auto 20 --decision-only`
  - Specific tickers (Yahoo):
    - `python main.py --source yahoo --symbols AAPL,MSFT --fast 50 --slow 200`
  - Alpha Vantage (with your key):
    - `python main.py --source alphavantage --apikey YOUR_KEY --auto 10 --top 10`
    - `python main.py --source alphavantage --apikey YOUR_KEY --symbols AAPL,MSFT`
  - CSV folder:
    - `python main.py --data-dir data --symbols AAPL,MSFT --top 10`

Data Sources

- Yahoo Finance (no key)
  - Uses the chart JSON endpoint; practical rate limits apply.
  - Best for quick exploration. Throttle + caching help a lot.
- Alpha Vantage (free API key)
  - Official API; free tier is 5 requests/minute. Demo key returns MSFT only.
- CSV
  - Drop daily OHLCV files in `data/` as `<SYMBOL>.csv` with headers (case‑insensitive):
    - `Date,Open,High,Low,Close,Volume` (Date format: YYYY‑MM‑DD)

Strategy: How BUY Is Decided

- The app checks three simple trend signals:
  - Latest bullish crossover (Fast SMA crossed above Slow SMA)
  - Price above Slow SMA (e.g., 200‑day) — trend confirmation
  - Fast SMA slope positive — short‑term uptrend
- Decision = BUY if at least 2 of 3 checks pass; otherwise DON’T BUY
- Score combines crossover recency + price distance vs 200SMA + 50SMA slope (higher is better)

Good Starting Values

- Conservative trend: Fast=50, Slow=200 (fewer, steadier signals)
- Responsive trend: Fast=20, Slow=50 (more signals, more noise)
- Daily data ops: Cache TTL=24h, Throttle=400ms (increase if you hit limits)

Troubleshooting

- “0 of 0” results:
  - Yahoo: likely rate‑limited or blocked. Try a single symbol (e.g., MSFT), wait 30–60s, or raise throttle.
  - Alpha Vantage: rate‑limited or invalid key. Try MSFT only; wait 60s; verify key.
  - CSV: verify headers/date format; see schema above.
- Cache lives under `.cache/`. Data refreshes after TTL hours.

Windows EXE (shareable)

- Build a single-file executable (includes Python runtime):
  - PowerShell: `scripts/build_exe.ps1`
  - or CMD: `scripts\build_web_exe.bat`
  - Output: `dist/StockAdvisor-Web.exe`
- Run the EXE; it starts the web app at http://127.0.0.1:8000/
- For Italian users, a simple launcher is provided: `scripts/start_web_it.bat`

Project Layout

- `main.py` — CLI entrypoint
- `stock/cli.py` — CLI logic and flags
- `stock/gui.py` — Tkinter GUI
- `stock/web/` — FastAPI app (run with `python -m stock.web`)
- `stock/data/` — Data loaders (csv, yahoo, alpha_vantage) + caching
- `stock/recommend.py` — Scoring and BUY/DON’T BUY decision
- `stock/strategy/sma_crossover.py` — Strategy features and events
- `stock/indicators.py` — SMA/EMA/RSI/MACD helpers
- `stock/universe.py` — Preset universes (S&P 100, NASDAQ 100)

CSV Example

Date,Open,High,Low,Close,Volume
2024-01-02,100.0,101.5,99.2,101.0,12345678
2024-01-03,101.0,103.1,100.5,102.7,9876543

Notes

- For research/education; not financial advice. Use at your own risk.
