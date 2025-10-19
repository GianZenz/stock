Stock Trend Advisor (Starter)

Overview

- CLI app that analyzes historical OHLCV data from CSV files to compute common indicators and suggest buy candidates using a simple SMA crossover strategy.
- Pure-Python implementation (no external packages) to work in restricted environments. You can later switch to pandas or add live data providers.

Quick Start

1) Put daily candles in `data/` as CSVs named like `AAPL.csv`, one per symbol.
   Required headers (case-insensitive): Date, Open, High, Low, Close, Volume
   Date format: YYYY-MM-DD

2) Run the CLI to analyze all CSVs in `data/` and list top ideas:

   `python main.py --data-dir data --top 10`

3) Or specify a subset of symbols:

   `python main.py --data-dir data --symbols AAPL,MSFT,NVDA --top 5`

GUI

- Launch the GUI (Tkinter-based, no extra dependencies):

  `python -m stock.gui`

- In the GUI you can:
  - Browse to select the `data/` directory
  - Discover symbols (auto-detect CSVs)
  - Enter custom symbols (comma-separated)
  - Set SMA windows and Top N
  - Click Analyze to see ranked results
  - Auto (API): with Source=alphavantage and your API key, click Auto (API) to fetch a small list of active symbols from Alpha Vantage, fill the Symbols field, and then Analyze.
  - Web UI (FastAPI): see FastAPI section below to run a local modern UI.

API Data (Alpha Vantage)

- You can fetch data automatically using Alpha Vantage without adding dependencies.
- CLI example (uses env var if `--apikey` is omitted):

  `set ALPHAVANTAGE_API_KEY=YOUR_KEY && python main.py --source alphavantage --symbols AAPL,MSFT --fast 50 --slow 200`

  or

  `python main.py --source alphavantage --apikey YOUR_KEY --symbols AAPL --fast 50 --slow 200`

- GUI: choose `Source = alphavantage` and paste your API key, then Analyze.
- Notes: Free tier is rate-limited; large symbol lists may throttle.

Troubleshooting (Alpha Vantage)

- If GUI status shows "Done. Shown 0 of 0 symbols":
  - Enter symbols explicitly (e.g., `AAPL,MSFT`). Discovery only works with CSV.
  - Test connectivity with the public demo key: `Source = alphavantage`, `API Key = demo`, `Symbols = MSFT`.
  - Try a single symbol to avoid rate limits.
  - Wait ~60 seconds and retry (free tier: 5 req/min).
  - Verify your key (no extra spaces) and internet connectivity.

Auto-discovery from API

- CLI: auto-scan N symbols from Alpha Vantage listing (active only):

  `python main.py --source alphavantage --apikey YOUR_KEY --auto 10 --top 10`

  This fetches up to 10 active symbols (NYSE/NASDAQ), then analyzes them. Due to rate limits, not all may return data immediately; try smaller N or rerun.

- GUI: click "Auto (API)" (Source=alphavantage, provide key) to populate symbols automatically.

FastAPI Web UI (modern)

- Install deps (once):

  pip install fastapi uvicorn jinja2

- Run the web app:

  python -m stock.web

- Open your browser at:

  http://127.0.0.1:8000/

- Features:
  - Source selection: Yahoo (no key), Alpha Vantage (API key), or CSV
  - Preset selector (S&P 100, NASDAQ 100) for Yahoo
  - Auto Count (20/50/80/All)
  - Strategy params: Fast/Slow SMA, Top N
  - Cache TTL and Throttle per request to manage rate limits
  - Results table with BUY/score and key metrics

Buy/Don't Buy Decision

- The app now produces an explicit decision based on simple checks:
  - Recent bullish SMA crossover
  - Price above 200SMA
  - 50SMA slope trending up
- Decision is `BUY` if at least 2 of 3 checks pass; otherwise `DON'T BUY`.
- CLI: add `--decision-only` to list only BUYs.

Scoring (initial heuristic)

- Favors recent bullish 50/200 SMA crossovers.
- Rewards positive distance of price vs. 200SMA and uptrend in 50SMA.
- Outputs a combined score to rank symbols; tune weights in code.

Project Layout

- `stock/cli.py` � CLI entrypoint / argument parsing
- `stock/data/csv_provider.py` — CSV loader for OHLCV
- `stock/indicators.py` — SMA, EMA, RSI, MACD helpers
- `stock/strategy/sma_crossover.py` — Signals + scoring features
- `stock/recommend.py` — Aggregates features to a score and ranks
- `main.py` — Thin wrapper calling the CLI
- `data/` — Your CSV files live here

CSV Format Example

Date,Open,High,Low,Close,Volume
2024-01-02,100.0,101.5,99.2,101.0,12345678
2024-01-03,101.0,103.1,100.5,102.7,9876543

Notes

- No brokerage or API integration is included yet. This starter focuses on offline CSV analysis so you can iterate anywhere.
- Backtesting is not wired yet; the strategy file returns events you can use to add it.
- This is NOT financial advice. Use at your own risk.




