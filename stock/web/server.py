from typing import List, Optional, Dict
import os
import sys

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..recommend import analyze_and_rank_with_loader
from ..data.provider import get_loader, get_universe
from ..data.cache import make_cached_loader
from ..utils import discover_symbols, parse_symbols
from ..universe import PRESETS, get_preset


app = FastAPI(title="Stock Trend Advisor")

# Resolve templates directory for normal and PyInstaller-frozen runs
def _templates_dir() -> str:
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, "stock", "web", "templates")
    # project root = ../../ from this file
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    return os.path.join(root, "stock", "web", "templates")

templates = Jinja2Templates(directory=_templates_dir())


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "presets": list(PRESETS.keys()),
            "defaults": {
                "source": "yahoo",
                "preset": "S&P 100",
                "count": "20",
                "fast": 50,
                "slow": 200,
                "top": 10,
                "decision_only": False,
                "data_dir": "data",
                "symbols": "",
                "apikey": "",
                "ttl_hours": 24,
                "throttle_ms": 400,
                "strategy_preset": "custom",
            },
        },
    )


@app.get("/help", response_class=HTMLResponse)
def help_page(request: Request):
    return templates.TemplateResponse(
        "help.html",
        {
            "request": request,
        },
    )


@app.get("/help-it", response_class=HTMLResponse)
def help_page_it(request: Request):
    return templates.TemplateResponse(
        "help_it.html",
        {
            "request": request,
        },
    )


# -------- Italian UI --------

@app.get("/it", response_class=HTMLResponse)
def index_it(request: Request):
    return templates.TemplateResponse(
        "index_it.html",
        {
            "request": request,
            "presets": list(PRESETS.keys()),
            "defaults": {
                "source": "yahoo",
                "preset": "S&P 100",
                "count": "20",
                "fast": 50,
                "slow": 200,
                "top": 10,
                "decision_only": False,
                "data_dir": "data",
                "symbols": "",
                "apikey": "",
                "ttl_hours": 24,
                "throttle_ms": 400,
                "strategy_preset": "custom",
            },
        },
    )


@app.post("/analyze-it", response_class=HTMLResponse)
def analyze_it(
    request: Request,
    source: str = Form("yahoo"),
    preset: str = Form("S&P 100"),
    count: str = Form("20"),
    strategy_preset: str = Form("custom"),
    fast: int = Form(50),
    slow: int = Form(200),
    top: int = Form(10),
    decision_only: Optional[str] = Form(None),
    data_dir: str = Form("data"),
    apikey: str = Form(""),
    symbols: str = Form(""),
    ttl_hours: int = Form(24),
    throttle_ms: int = Form(400),
):
    # Prepare symbols according to user inputs
    symbols_list: List[str] = []
    if symbols.strip():
        symbols_list = parse_symbols(symbols)
    else:
        if source == "yahoo":
            base = get_preset(preset)
            max_syms = 1000 if count.lower() == "all" else max(1, int(count))
            symbols_list = base[: max_syms]
        elif source == "alphavantage":
            max_syms = 10 if count.lower() == "all" else max(1, int(count))
            symbols_list = get_universe("alphavantage", api_key=apikey.strip(), max_symbols=max_syms)
        else:  # csv
            symbols_list = discover_symbols(data_dir)

    # Build loader with cache/throttle
    loader = get_loader(source, data_dir=data_dir, api_key=apikey.strip())
    loader = make_cached_loader(loader, source=source, cache_dir=".cache", ttl_hours=ttl_hours, throttle_ms=throttle_ms)

    ranked = analyze_and_rank_with_loader(symbols_list, loader, fast=fast, slow=slow)
    if decision_only is not None:
        ranked = [r for r in ranked if (r.get("meta", {}).get("decision") == "BUY")]

    hint = None
    if not ranked and symbols_list:
        if source == "alphavantage":
            hint = "Alpha Vantage potrebbe essere limitato o la chiave non valida. Prova un singolo simbolo o attendi 60s."
        elif source == "yahoo":
            hint = "Yahoo potrebbe essere limitato o bloccato dalla rete. Prova un simbolo come MSFT o attendi 30s."

    return templates.TemplateResponse(
        "index_it.html",
        {
            "request": request,
            "presets": list(PRESETS.keys()),
            "defaults": {
                "source": source,
                "preset": preset,
                "count": count,
                "strategy_preset": strategy_preset,
                "fast": fast,
                "slow": slow,
                "top": top,
                "decision_only": decision_only is not None,
                "data_dir": data_dir,
                "symbols": ",".join(symbols_list),
                "apikey": apikey,
                "ttl_hours": ttl_hours,
                "throttle_ms": throttle_ms,
            },
            "ranked": ranked[: max(1, top)],
            "hint": hint,
        },
    )


@app.post("/analyze", response_class=HTMLResponse)
def analyze(
    request: Request,
    source: str = Form("yahoo"),
    preset: str = Form("S&P 100"),
    count: str = Form("20"),
    strategy_preset: str = Form("custom"),
    fast: int = Form(50),
    slow: int = Form(200),
    top: int = Form(10),
    decision_only: Optional[str] = Form(None),
    data_dir: str = Form("data"),
    apikey: str = Form(""),
    symbols: str = Form(""),
    ttl_hours: int = Form(24),
    throttle_ms: int = Form(400),
):
    # Prepare symbols according to user inputs
    symbols_list: List[str] = []
    if symbols.strip():
        symbols_list = parse_symbols(symbols)
    else:
        if source == "yahoo":
            base = get_preset(preset)
            max_syms = 1000 if count.lower() == "all" else max(1, int(count))
            symbols_list = base[: max_syms]
        elif source == "alphavantage":
            max_syms = 10 if count.lower() == "all" else max(1, int(count))
            symbols_list = get_universe("alphavantage", api_key=apikey.strip(), max_symbols=max_syms)
        else:  # csv
            symbols_list = discover_symbols(data_dir)

    # Build loader with cache/throttle
    loader = get_loader(source, data_dir=data_dir, api_key=apikey.strip())
    loader = make_cached_loader(loader, source=source, cache_dir=".cache", ttl_hours=ttl_hours, throttle_ms=throttle_ms)

    ranked = analyze_and_rank_with_loader(symbols_list, loader, fast=fast, slow=slow)
    if decision_only is not None:
        ranked = [r for r in ranked if (r.get("meta", {}).get("decision") == "BUY")]

    hint = None
    if not ranked and symbols_list:
        if source == "alphavantage":
            hint = "Alpha Vantage may be rate-limited or key invalid. Try a single symbol or wait 60s."
        elif source == "yahoo":
            hint = "Yahoo may be rate-limited or blocked by network. Try a single symbol like MSFT or wait 30s."

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "presets": list(PRESETS.keys()),
            "defaults": {
                "source": source,
                "preset": preset,
                "count": count,
                "strategy_preset": strategy_preset,
                "fast": fast,
                "slow": slow,
                "top": top,
                "decision_only": decision_only is not None,
                "data_dir": data_dir,
                "symbols": ",".join(symbols_list),
                "apikey": apikey,
                "ttl_hours": ttl_hours,
                "throttle_ms": throttle_ms,
            },
            "ranked": ranked[: max(1, top)],
            "hint": hint,
        },
    )


def main():
    # Convenience to run with `python -m stock.web.server`
    import uvicorn

    uvicorn.run("stock.web.server:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
