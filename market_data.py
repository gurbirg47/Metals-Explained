"""
market_data.py
Real market data fetching via yfinance with robust error handling and mock fallbacks.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import streamlit as st
import time

# Suppress yfinance error messages
import logging
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Symbol mappings with fallbacks
SYMBOLS = {
    "gold": ["GC=F", "GLD", "IAU"],
    "silver": ["SI=F", "SLV"],
    "dxy": ["DX-Y.NYB", "UUP"],
    "us10y": ["^TNX"],
    "us2y": ["^IRX"],
}

def generate_mock_price_history(base_price: float, volatility: float = 0.02, days: int = 252) -> pd.DataFrame:
    """Generate realistic-looking mock price data when API fails."""
    # Use current date as seed for variety
    seed = int(datetime.now().strftime("%Y%m%d"))
    np.random.seed(seed)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    returns = np.random.randn(days) * volatility
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Add realistic daily change for today
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

def fetch_price_history_direct(symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """Fetch price history using yfinance download (more reliable than Ticker)."""
    try:
        # Use download instead of Ticker.history - more reliable
        df = yf.download(
            symbol, 
            period=period, 
            progress=False, 
            auto_adjust=True,
            threads=False
        )
        
        if df.empty or len(df) < 5:
            return None
            
        df = df.reset_index()
        
        # Handle column names (yfinance sometimes returns MultiIndex)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Ensure 'Date' column exists
        if 'Date' not in df.columns and 'index' in df.columns:
            df = df.rename(columns={'index': 'Date'})
        
        # Handle timezone-aware datetime
        if hasattr(df['Date'].dtype, 'tz') and df['Date'].dt.tz is not None:
            df['Date'] = df['Date'].dt.tz_localize(None)
        
        df = df.sort_values('Date').drop_duplicates(subset=['Date'])
        return df
        
    except Exception as e:
        return None

@st.cache_data(ttl=30, show_spinner=False)  # 30-second cache for live feel
def fetch_price_history(symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """Fetch price history for a symbol with retry logic."""
    max_retries = 2
    
    for attempt in range(max_retries):
        df = fetch_price_history_direct(symbol, period)
        if df is not None and not df.empty:
            return df
        if attempt < max_retries - 1:
            time.sleep(0.5)  # Brief pause between retries
    
    return None

def fetch_with_fallback(asset_key: str, symbol_list: list, period: str = "1y") -> Tuple[pd.DataFrame, str, bool]:
    """
    Try each symbol in list until one works. 
    Returns (df, symbol_used, is_mock).
    If all fail, returns mock data.
    """
    for sym in symbol_list:
        df = fetch_price_history(sym, period)
        if df is not None and not df.empty and 'Close' in df.columns:
            return df, sym, False
    
    # All symbols failed - use mock data
    mock_config = MOCK_DATA.get(asset_key, {"base_price": 100.0, "volatility": 0.01})
    mock_df = generate_mock_price_history(mock_config["base_price"], mock_config["volatility"])
    return mock_df, f"{symbol_list[0]} (DEMO)", True

def calculate_metrics(df: pd.DataFrame) -> Dict:
    """Calculate key metrics from price history."""
    if df is None or df.empty or 'Close' not in df.columns:
        return {
            "latest": None,
            "prev_close": None,
            "change_pct": None,
            "ma_20": None,
            "ma_50": None,
            "above_20": None,
            "above_50": None,
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

@st.cache_data(ttl=30, show_spinner=False)  # 30-second cache for live feel
def get_all_market_data() -> Dict:
    """Fetch all market data with fallbacks."""
    data = {}
    warnings = []
    
    # Gold
    df_gold, sym_gold, is_mock_gold = fetch_with_fallback("gold", SYMBOLS["gold"])
    if is_mock_gold:
        warnings.append("Gold: using demo data (API unavailable)")
    data["gold"] = {
        "df": df_gold,
        "symbol": sym_gold,
        "metrics": calculate_metrics(df_gold),
        "is_mock": is_mock_gold,
    }
    
    # Silver
    df_silver, sym_silver, is_mock_silver = fetch_with_fallback("silver", SYMBOLS["silver"])
    if is_mock_silver:
        warnings.append("Silver: using demo data (API unavailable)")
    data["silver"] = {
        "df": df_silver,
        "symbol": sym_silver,
        "metrics": calculate_metrics(df_silver),
        "is_mock": is_mock_silver,
    }
    
    # DXY
    df_dxy, sym_dxy, is_mock_dxy = fetch_with_fallback("dxy", SYMBOLS["dxy"])
    if is_mock_dxy:
        warnings.append("DXY: using demo data (API unavailable)")
    data["dxy"] = {
        "df": df_dxy,
        "symbol": sym_dxy,
        "metrics": calculate_metrics(df_dxy),
        "is_mock": is_mock_dxy,
    }
    
    # 10Y Yield
    df_10y, sym_10y, is_mock_10y = fetch_with_fallback("us10y", SYMBOLS["us10y"])
    if is_mock_10y:
        warnings.append("10Y Yield: using demo data (API unavailable)")
    data["us10y"] = {
        "df": df_10y,
        "symbol": sym_10y,
        "metrics": calculate_metrics(df_10y),
        "is_mock": is_mock_10y,
    }
    
    # 2Y Yield
    df_2y, sym_2y, is_mock_2y = fetch_with_fallback("us2y", SYMBOLS["us2y"])
    data["us2y"] = {
        "df": df_2y,
        "symbol": sym_2y,
        "metrics": calculate_metrics(df_2y),
        "is_mock": is_mock_2y,
    }
    
    data["_warnings"] = warnings
    
    return data

def format_price(value: Optional[float], decimals: int = 2) -> str:
    """Format price for display."""
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"

def format_change(value: Optional[float]) -> Tuple[str, str]:
    """Format change percentage. Returns (formatted_str, css_class)."""
    if value is None:
        return "N/A", "muted"
    sign = "+" if value >= 0 else ""
    css = "up" if value >= 0 else "down"
    return f"{sign}{value:.2f}%", css
