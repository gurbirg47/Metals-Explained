"""
market_data.py
Real market data fetching via yfinance with robust error handling and mock fallbacks.
Optimized for performance with session-level caching and pre-computed volatility.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
import logging

# Suppress yfinance error messages
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Symbol mappings
SYMBOLS = {
    "gold": ["GC=F"],
    "silver": ["SI=F"],
    "dxy": ["DX-Y.NYB"],
    "us10y": ["^TNX"],
    "us2y": ["^IRX"],
}

# Session-level cache - persists until server restart
_session_cache: Dict[str, Dict] = {}
_volatility_cache: Dict[str, List] = {}  # Pre-computed volatility series
_session_cache_time: Optional[datetime] = None
SESSION_CACHE_TTL = 300  # 5 minutes


def generate_mock_price_history(base_price: float, volatility: float = 0.02, days: int = 60) -> pd.DataFrame:
    """Generate realistic-looking mock price data. Seed is date-based for consistency."""
    seed = int(datetime.now().strftime("%Y%m%d"))
    np.random.seed(seed)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    returns = np.random.randn(days) * volatility
    prices = base_price * np.exp(np.cumsum(returns))
    prices[-1] = prices[-2] * (1 + np.random.randn() * volatility * 2)
    
    return pd.DataFrame({
        'Date': dates,
        'Open': prices * (1 + np.random.randn(days) * 0.003),
        'High': prices * (1 + np.abs(np.random.randn(days) * 0.008)),
        'Low': prices * (1 - np.abs(np.random.randn(days) * 0.008)),
        'Close': prices,
        'Volume': np.random.randint(100000, 1000000, days)
    })


def generate_mock_volatility(base_vol: float = 15.0, days: int = 40) -> List[Dict]:
    """Generate mock volatility series instantly."""
    seed = int(datetime.now().strftime("%Y%m%d"))
    np.random.seed(seed)
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    vols = base_vol + np.cumsum(np.random.randn(days) * 0.5)
    vols = np.clip(vols, 5, 40)
    return [{"t": d.isoformat(), "c": float(v)} for d, v in zip(dates, vols)]


MOCK_DATA = {
    "gold": {"base_price": 2680.0, "volatility": 0.010, "base_vol": 14.0},
    "silver": {"base_price": 30.50, "volatility": 0.015, "base_vol": 22.0},
    "dxy": {"base_price": 108.5, "volatility": 0.004},
    "us10y": {"base_price": 4.60, "volatility": 0.015},
    "us2y": {"base_price": 4.25, "volatility": 0.012},
}


def fetch_price_history_direct(symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
    """Fetch price history with 5-second timeout."""
    try:
        df = yf.download(symbol, period=period, progress=False, auto_adjust=True, threads=False, timeout=5)
        if df.empty or len(df) < 5:
            return None
        df = df.reset_index()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        if 'Date' not in df.columns and 'index' in df.columns:
            df = df.rename(columns={'index': 'Date'})
        if hasattr(df['Date'].dtype, 'tz') and df['Date'].dt.tz is not None:
            df['Date'] = df['Date'].dt.tz_localize(None)
        return df.sort_values('Date').drop_duplicates(subset=['Date'])
    except Exception:
        return None


def compute_volatility_series(df: pd.DataFrame, window: int = 20) -> List[Dict]:
    """Compute 20-day realized volatility from price DataFrame. Returns list of {t, c} points."""
    if df is None or "Close" not in df.columns or len(df) < window + 5:
        return []
    df = df.copy()
    df["Returns"] = df["Close"].pct_change()
    df["RealizedVol"] = df["Returns"].rolling(window).std() * np.sqrt(252) * 100
    df = df.dropna(subset=["RealizedVol"])
    return [
        {"t": row['Date'].isoformat() if hasattr(row['Date'], 'isoformat') else str(row['Date']), "c": float(row['RealizedVol'])}
        for _, row in df.tail(40).iterrows()
    ]


def fetch_with_fallback(asset_key: str, symbol_list: list, period: str = "3mo") -> Tuple[pd.DataFrame, str, bool]:
    """Fetch data with immediate mock fallback."""
    if symbol_list:
        df = fetch_price_history_direct(symbol_list[0], period)
        if df is not None and not df.empty and 'Close' in df.columns:
            return df, symbol_list[0], False
    mock_config = MOCK_DATA.get(asset_key, {"base_price": 100.0, "volatility": 0.01})
    return generate_mock_price_history(mock_config["base_price"], mock_config["volatility"]), f"{asset_key} (DEMO)", True


def calculate_metrics(df: pd.DataFrame) -> Dict:
    """Calculate key metrics from price history."""
    if df is None or df.empty or 'Close' not in df.columns:
        return {"latest": None, "prev_close": None, "change_pct": None, "ma_20": None, "ma_50": None}
    try:
        latest = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else latest
        change_pct = ((latest - prev_close) / prev_close) * 100 if prev_close else 0
        ma_20 = float(df['Close'].rolling(20).mean().iloc[-1]) if len(df) >= 20 else None
        ma_50 = float(df['Close'].rolling(50).mean().iloc[-1]) if len(df) >= 50 else None
        return {"latest": latest, "prev_close": prev_close, "change_pct": change_pct, "ma_20": ma_20, "ma_50": ma_50}
    except Exception:
        return {"latest": None, "prev_close": None, "change_pct": None, "ma_20": None, "ma_50": None}


def get_all_market_data(use_cache: bool = True) -> Dict:
    """Fetch all market data with session cache. Pre-computes volatility."""
    global _session_cache, _volatility_cache, _session_cache_time
    
    if use_cache and _session_cache and _session_cache_time:
        if datetime.now() - _session_cache_time < timedelta(seconds=SESSION_CACHE_TTL):
            return _session_cache
    
    data = {}
    for asset_key in ["gold", "silver", "dxy", "us10y", "us2y"]:
        df, sym, is_mock = fetch_with_fallback(asset_key, SYMBOLS[asset_key], "3mo")
        data[asset_key] = {"df": df, "symbol": sym, "metrics": calculate_metrics(df), "is_mock": is_mock}
    
    # Pre-compute volatility for gold and silver
    for asset in ["gold", "silver"]:
        if data[asset]["df"] is not None:
            vol_series = compute_volatility_series(data[asset]["df"])
            if vol_series:
                _volatility_cache[asset] = vol_series
            else:
                _volatility_cache[asset] = generate_mock_volatility(MOCK_DATA[asset]["base_vol"])
        else:
            _volatility_cache[asset] = generate_mock_volatility(MOCK_DATA[asset]["base_vol"])
    
    _session_cache = data
    _session_cache_time = datetime.now()
    return data


def get_timeseries(asset: str, window: str = "1M") -> Dict:
    """Get timeseries for an asset. Volatility uses pre-computed cache."""
    global _session_cache, _volatility_cache
    
    # Handle volatility - return instantly from cache
    if asset in ["gold_vol", "silver_vol", "vol"]:
        base_asset = "gold" if asset in ["gold_vol", "vol"] else "silver"
        
        # Ensure data is loaded
        if not _volatility_cache or base_asset not in _volatility_cache:
            get_all_market_data()
        
        series = _volatility_cache.get(base_asset, [])
        if not series:
            series = generate_mock_volatility(MOCK_DATA.get(base_asset, {}).get("base_vol", 15.0))
            _volatility_cache[base_asset] = series
        
        return {
            "asset": asset,
            "baseAsset": base_asset,
            "window": window,
            "hasOHLC": False,
            "isMock": len(series) > 0 and _session_cache.get(base_asset, {}).get("is_mock", True),
            "series": series
        }
    
    if asset not in SYMBOLS:
        return {"error": f"Unknown asset: {asset}", "series": [], "hasOHLC": False, "isMock": True}
    
    # Use cached data
    if _session_cache and asset in _session_cache:
        df = _session_cache[asset]["df"]
        is_mock = _session_cache[asset]["is_mock"]
    else:
        df, _, is_mock = fetch_with_fallback(asset, SYMBOLS[asset], "1mo")
    
    series = []
    has_ohlc = all(col in df.columns for col in ['Open', 'High', 'Low', 'Close'])
    for _, row in df.tail(60).iterrows():
        point = {"t": row['Date'].isoformat() if hasattr(row['Date'], 'isoformat') else str(row['Date']), "c": float(row['Close']) if pd.notna(row['Close']) else None}
        if has_ohlc:
            point["o"] = float(row['Open']) if pd.notna(row['Open']) else None
            point["h"] = float(row['High']) if pd.notna(row['High']) else None
            point["l"] = float(row['Low']) if pd.notna(row['Low']) else None
        series.append(point)
    
    return {"asset": asset, "window": window, "hasOHLC": has_ohlc, "isMock": is_mock, "series": series}


def clear_cache():
    """Clear all caches."""
    global _session_cache, _volatility_cache, _session_cache_time
    _session_cache = {}
    _volatility_cache = {}
    _session_cache_time = None
