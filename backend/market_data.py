"""
market_data.py
Real market data fetching via yfinance with robust error handling and mock fallbacks.
Optimized for performance with session-level caching.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import time
import logging

# Suppress yfinance error messages
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Symbol mappings with fallbacks
SYMBOLS = {
    "gold": ["GC=F", "GLD", "IAU"],
    "silver": ["SI=F", "SLV"],
    "dxy": ["DX-Y.NYB", "UUP"],
    "us10y": ["^TNX"],
    "us2y": ["^IRX"],
}

# Session-level cache - persists until server restart
_session_cache: Dict[str, Dict] = {}
_session_cache_time: Optional[datetime] = None
SESSION_CACHE_TTL = 300  # 5 minutes


def generate_mock_price_history(base_price: float, volatility: float = 0.02, days: int = 60) -> pd.DataFrame:
    """Generate realistic-looking mock price data when API fails. Smaller default window."""
    seed = int(datetime.now().strftime("%Y%m%d"))
    np.random.seed(seed)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    returns = np.random.randn(days) * volatility
    prices = base_price * np.exp(np.cumsum(returns))
    
    today_change = np.random.randn() * volatility * 2
    prices[-1] = prices[-2] * (1 + today_change)
    
    return pd.DataFrame({
        'Date': dates,
        'Open': prices * (1 + np.random.randn(days) * 0.003),
        'High': prices * (1 + np.abs(np.random.randn(days) * 0.008)),
        'Low': prices * (1 - np.abs(np.random.randn(days) * 0.008)),
        'Close': prices,
        'Volume': np.random.randint(100000, 1000000, days)
    })


MOCK_DATA = {
    "gold": {"base_price": 2680.0, "volatility": 0.010},
    "silver": {"base_price": 30.50, "volatility": 0.015},
    "dxy": {"base_price": 108.5, "volatility": 0.004},
    "us10y": {"base_price": 4.60, "volatility": 0.015},
    "us2y": {"base_price": 4.25, "volatility": 0.012},
}


def fetch_price_history_direct(symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
    """Fetch price history using yfinance download. Uses shorter default period."""
    try:
        df = yf.download(
            symbol, 
            period=period, 
            progress=False, 
            auto_adjust=True,
            threads=False,
            timeout=5  # 5 second timeout
        )
        
        if df.empty or len(df) < 5:
            return None
            
        df = df.reset_index()
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        if 'Date' not in df.columns and 'index' in df.columns:
            df = df.rename(columns={'index': 'Date'})
        
        if hasattr(df['Date'].dtype, 'tz') and df['Date'].dt.tz is not None:
            df['Date'] = df['Date'].dt.tz_localize(None)
        
        df = df.sort_values('Date').drop_duplicates(subset=['Date'])
        return df
        
    except Exception:
        return None


def fetch_with_fallback(asset_key: str, symbol_list: list, period: str = "3mo") -> Tuple[pd.DataFrame, str, bool]:
    """Try each symbol until one works. Returns (df, symbol_used, is_mock). Fast fallback to mock."""
    # Only try first symbol with short timeout
    if symbol_list:
        df = fetch_price_history_direct(symbol_list[0], period)
        if df is not None and not df.empty and 'Close' in df.columns:
            return df, symbol_list[0], False
    
    # Immediate fallback to mock data
    mock_config = MOCK_DATA.get(asset_key, {"base_price": 100.0, "volatility": 0.01})
    mock_df = generate_mock_price_history(mock_config["base_price"], mock_config["volatility"])
    return mock_df, f"{symbol_list[0]} (DEMO)", True


def calculate_metrics(df: pd.DataFrame) -> Dict:
    """Calculate key metrics from price history."""
    if df is None or df.empty or 'Close' not in df.columns:
        return {
            "latest": None, "prev_close": None, "change_pct": None,
            "ma_20": None, "ma_50": None, "above_20": None, "above_50": None,
        }
    
    try:
        latest = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else latest
        change_pct = ((latest - prev_close) / prev_close) * 100 if prev_close else 0
        
        ma_20 = float(df['Close'].rolling(20).mean().iloc[-1]) if len(df) >= 20 else None
        ma_50 = float(df['Close'].rolling(50).mean().iloc[-1]) if len(df) >= 50 else None
        
        return {
            "latest": latest,
            "prev_close": prev_close,
            "change_pct": change_pct,
            "ma_20": ma_20,
            "ma_50": ma_50,
            "above_20": latest > ma_20 if ma_20 else None,
            "above_50": latest > ma_50 if ma_50 else None,
        }
    except Exception:
        return {
            "latest": None, "prev_close": None, "change_pct": None,
            "ma_20": None, "ma_50": None, "above_20": None, "above_50": None,
        }


def get_all_market_data(use_cache: bool = True) -> Dict:
    """Fetch all market data with session-level caching."""
    global _session_cache, _session_cache_time
    
    # Return cached data if valid
    if use_cache and _session_cache and _session_cache_time:
        if datetime.now() - _session_cache_time < timedelta(seconds=SESSION_CACHE_TTL):
            return _session_cache
    
    data = {}
    
    # Fetch all assets - fast fallback to mock
    for asset_key in ["gold", "silver", "dxy", "us10y", "us2y"]:
        df, sym, is_mock = fetch_with_fallback(asset_key, SYMBOLS[asset_key], "3mo")
        data[asset_key] = {
            "df": df,
            "symbol": sym,
            "metrics": calculate_metrics(df),
            "is_mock": is_mock,
        }
    
    # Cache the result
    _session_cache = data
    _session_cache_time = datetime.now()
    
    return data


def get_timeseries(asset: str, window: str = "1M") -> Dict:
    """Get timeseries data for a specific asset. Uses cached data when available."""
    global _session_cache
    
    # Map window to yfinance period
    period_map = {
        "1D": "5d",
        "5D": "5d", 
        "1M": "1mo",
        "3M": "3mo",
        "1Y": "1y",
    }
    yf_period = period_map.get(window, "1mo")
    
    if asset not in SYMBOLS and asset != "vol":
        return {"error": f"Unknown asset: {asset}", "series": [], "hasOHLC": False, "isMock": True}
    
    # For volatility, use cached gold data
    if asset == "vol":
        if _session_cache and "gold" in _session_cache:
            df_gold = _session_cache["gold"]["df"]
            is_mock = _session_cache["gold"]["is_mock"]
        else:
            data = get_all_market_data()
            df_gold = data["gold"]["df"]
            is_mock = data["gold"]["is_mock"]
        
        if df_gold is not None and "Close" in df_gold.columns and len(df_gold) >= 25:
            df_vol = df_gold.copy()
            df_vol["Returns"] = df_vol["Close"].pct_change()
            df_vol["RealizedVol"] = df_vol["Returns"].rolling(20).std() * np.sqrt(252) * 100
            df_vol = df_vol.dropna(subset=["RealizedVol"])
            
            series = []
            for _, row in df_vol.iterrows():
                series.append({
                    "t": row['Date'].isoformat() if hasattr(row['Date'], 'isoformat') else str(row['Date']),
                    "c": float(row['RealizedVol']),
                })
            
            return {
                "asset": "vol",
                "window": window,
                "hasOHLC": False,
                "isMock": is_mock,
                "series": series[-60:]  # Last 60 points only
            }
        else:
            return {"asset": "vol", "window": window, "hasOHLC": False, "isMock": True, "series": []}
    
    # Use cached data if available
    if _session_cache and asset in _session_cache:
        df = _session_cache[asset]["df"]
        is_mock = _session_cache[asset]["is_mock"]
    else:
        df, _, is_mock = fetch_with_fallback(asset, SYMBOLS[asset], yf_period)
    
    # Build series with OHLC - limit to 60 points for performance
    series = []
    has_ohlc = all(col in df.columns for col in ['Open', 'High', 'Low', 'Close'])
    
    df_limited = df.tail(60)  # Last 60 days only
    
    for _, row in df_limited.iterrows():
        point = {
            "t": row['Date'].isoformat() if hasattr(row['Date'], 'isoformat') else str(row['Date']),
            "c": float(row['Close']) if pd.notna(row['Close']) else None,
        }
        if has_ohlc:
            point["o"] = float(row['Open']) if pd.notna(row['Open']) else None
            point["h"] = float(row['High']) if pd.notna(row['High']) else None
            point["l"] = float(row['Low']) if pd.notna(row['Low']) else None
        series.append(point)
    
    return {
        "asset": asset,
        "window": window,
        "hasOHLC": has_ohlc,
        "isMock": is_mock,
        "series": series
    }


def clear_cache():
    """Clear session cache."""
    global _session_cache, _session_cache_time
    _session_cache = {}
    _session_cache_time = None
