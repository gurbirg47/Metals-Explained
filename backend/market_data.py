"""
market_data.py
Robust market data fetching with asyncio parallelization, TTL caching, and reliable mock fallbacks.
"""

import asyncio
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List, Any
import logging
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress yfinance error messages
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Asset Configurations
ASSETS = {
    "gold": {"symbol": "GC=F", "base_price": 2680.0, "vol_base": 14.5, "type": "price"},
    "silver": {"symbol": "SI=F", "base_price": 30.50, "vol_base": 22.0, "type": "price"},
    "dxy": {"symbol": "DX-Y.NYB", "base_price": 108.5, "type": "index"},
    "us10y": {"symbol": "^TNX", "base_price": 4.60, "type": "yield"},
}

# Cache Settings
_cache: Dict[str, Any] = {}
_cache_time: Optional[datetime] = None
CACHE_TTL = 300  # 5 minutes

# Thread pool for yfinance (since it's blocking)
executor = ThreadPoolExecutor(max_workers=10)

def generate_mock_history(asset_key: str, days: int = 60) -> pd.DataFrame:
    """Generate professional-looking mock data for an asset."""
    config = ASSETS[asset_key]
    base = config["base_price"]
    vol = 0.015 if asset_key == "silver" else 0.01
    
    # Use date as seed for daily consistency
    np.random.seed(int(datetime.now().strftime("%Y%m%d")))
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    returns = np.random.randn(days) * vol
    prices = base * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        'Date': dates,
        'Close': prices,
        'Open': prices * (1 + np.random.randn(days) * 0.002),
        'High': prices * (1 + np.abs(np.random.randn(days) * 0.005)),
        'Low': prices * (1 - np.abs(np.random.randn(days) * 0.005)),
        'Volume': np.random.randint(100000, 500000, days)
    })
    return df

def generate_mock_vol_series(asset_key: str, days: int = 40) -> List[Dict]:
    """Generate mock volatility series."""
    base_vol = ASSETS.get(asset_key, {}).get("vol_base", 15.0)
    np.random.seed(int(datetime.now().strftime("%Y%m%d")) + 1)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    vols = base_vol + np.cumsum(np.random.randn(days) * 0.4)
    vols = np.clip(vols, 5, 45)
    
    return [{"t": d.isoformat(), "value": float(v)} for d, v in zip(dates, vols)]

def sync_fetch_yf(symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
    """Blocking yfinance fetch."""
    try:
        df = yf.download(symbol, period=period, progress=False, auto_adjust=True, timeout=8)
        if df.empty or len(df) < 2:
            return None
        df = df.reset_index()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
        if 'Date' not in df.columns and 'index' in df.columns:
            df = df.rename(columns={'index': 'Date'})
        if hasattr(df['Date'], 'dt') and df['Date'].dt.tz is not None:
            df['Date'] = df['Date'].dt.tz_localize(None)
        return df
    except Exception as e:
        logger.error(f"yfinance error for {symbol}: {e}")
        return None

async def fetch_asset_data(asset_key: str) -> Dict:
    """Fetch live data with automatic mock fallback."""
    symbol = ASSETS[asset_key]["symbol"]
    loop = asyncio.get_event_loop()
    
    df = await loop.run_in_executor(executor, sync_fetch_yf, symbol)
    
    is_live = df is not None
    if not is_live:
        logger.warning(f"Falling back to DEMO for {asset_key}")
        df = generate_mock_history(asset_key)
    
    # Calculate basic metrics
    latest_close = float(df['Close'].iloc[-1])
    prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else latest_close
    change_pct = ((latest_close - prev_close) / prev_close) * 100 if prev_close else 0
    
    ma_20 = float(df['Close'].rolling(20).mean().iloc[-1]) if len(df) >= 20 else None
    ma_50 = float(df['Close'].rolling(50).mean().iloc[-1]) if len(df) >= 50 else None
    
    # Calculate volatility if applicable
    vol_data = {"current": 0.0, "series": []}
    if asset_key in ["gold", "silver"]:
        returns = df['Close'].pct_change().dropna()
        if len(returns) >= 20:
            vol_val = float(returns.tail(20).std() * np.sqrt(252) * 100)
            vol_data["current"] = vol_val
            
            df_vol = df.tail(60).copy()
            df_vol["Vol"] = df_vol["Close"].pct_change().rolling(20).std() * np.sqrt(252) * 100
            df_vol = df_vol.dropna(subset=["Vol"])
            vol_data["series"] = [
                {"t": row['Date'].isoformat(), "value": float(row['Vol'])}
                for _, row in df_vol.tail(40).iterrows()
            ]
        else:
            vol_data["series"] = generate_mock_vol_series(asset_key)
            vol_data["current"] = vol_data["series"][-1]["value"]

    return {
        "df": df,
        "is_live": is_live,
        "metrics": {
            "latest": latest_close,
            "change_pct": change_pct,
            "ma_20": ma_20,
            "ma_50": ma_50,
            "above_50": latest_close > ma_50 if ma_50 else None
        },
        "vol": vol_data
    }

async def get_all_market_data(force_refresh: bool = False) -> Dict:
    """Async orchestrator for all data fetching."""
    global _cache, _cache_time
    
    now = datetime.now()
    if not force_refresh and _cache_time and (now - _cache_time).total_seconds() < CACHE_TTL:
        return _cache
    
    tasks = [fetch_asset_data(key) for key in ASSETS.keys()]
    results = await asyncio.gather(*tasks)
    
    data = {key: results[i] for i, key in enumerate(ASSETS.keys())}
    
    _cache = data
    _cache_time = now
    return data

def get_timeseries_data(asset_key: str, window: str, market_data: Dict) -> Dict:
    """Format timeseries from already fetched market data."""
    if asset_key.startswith("vol_"):
        base = asset_key.replace("vol_", "")
        if base in market_data:
            return {
                "asOf": datetime.now().isoformat(),
                "asset": asset_key,
                "window": window,
                "hasOHLC": False,
                "series": market_data[base]["vol"]["series"]
            }
    
    if asset_key not in market_data:
        mock_df = generate_mock_history(asset_key if asset_key in ASSETS else "gold")
        series = [{"t": r['Date'].isoformat(), "close": float(r['Close'])} for _, r in mock_df.iterrows()]
        return {"asOf": datetime.now().isoformat(), "asset": asset_key, "window": window, "hasOHLC": False, "series": series}

    df = market_data[asset_key]["df"]
    asset_type = ASSETS.get(asset_key, {}).get("type", "price")
    
    window_map = {"1D": 5, "5D": 10, "1M": 22, "3M": 66, "1Y": 252}
    limit = window_map.get(window, 22)
    df_subset = df.tail(limit)
    
    series = []
    has_ohlc = all(c in df.columns for c in ['Open', 'High', 'Low', 'Close'])
    
    for _, row in df_subset.iterrows():
        point = {"t": row['Date'].isoformat()}
        if asset_type == "price" and has_ohlc:
            point.update({
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close'])
            })
        else:
            point["value"] = float(row['Close'])
        series.append(point)
            
    return {
        "asOf": datetime.now().isoformat(),
        "asset": asset_key,
        "window": window,
        "hasOHLC": has_ohlc and asset_type == "price",
        "series": series
    }

def clear_cache():
    global _cache, _cache_time
    _cache = {}
    _cache_time = None
