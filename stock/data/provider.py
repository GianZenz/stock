from typing import Callable, Optional, List

from .csv_provider import load_symbol_csv
from ..utils import discover_symbols


def get_loader(source: str, data_dir: Optional[str] = None, api_key: Optional[str] = None) -> Callable[[str], Optional[dict]]:
    """Return a callable that loads a symbol's OHLCV time series.

    - source: 'csv' or 'alphavantage'
    - data_dir: required for 'csv'
    - api_key: required for 'alphavantage'
    """
    src = (source or "csv").lower()
    if src == "csv":
        def _csv_loader(symbol: str):
            if data_dir is None:
                return None
            return load_symbol_csv(symbol, data_dir)
        return _csv_loader
    elif src == "alphavantage":
        from .alpha_vantage import load_symbol_alphavantage

        def _av_loader(symbol: str):
            if not api_key:
                return None
            return load_symbol_alphavantage(symbol, api_key)

        return _av_loader
    elif src == "yahoo":
        from .yahoo import load_symbol_yahoo

        def _yh_loader(symbol: str):
            return load_symbol_yahoo(symbol)

        return _yh_loader
    else:
        # Unknown source; return a loader that always yields None
        def _noop(_symbol: str):
            return None
        return _noop


def get_universe(source: str, data_dir: Optional[str] = None, api_key: Optional[str] = None, max_symbols: int = 20) -> List[str]:
    """Return a list of symbols to analyze for the given source.

    - csv: discovers from data_dir
    - alphavantage: uses LISTING_STATUS (active) limited to max_symbols and filtered to major exchanges
    """
    src = (source or "csv").lower()
    if src == "csv":
        return discover_symbols(data_dir or "data")
    if src == "alphavantage":
        if not api_key:
            return []
        try:
            from .alpha_vantage import list_symbols_alphavantage
            # Limit to liquid US exchanges to reduce noise
            return list_symbols_alphavantage(api_key, state="active", max_symbols=max_symbols, exchanges=["NYSE", "NASDAQ"])
        except Exception:
            return []
    if src == "yahoo":
        try:
            from ..universe import SP100
            return SP100[: max_symbols]
        except Exception:
            return []
    return []
