"""
Vercel Serverless Function - Market Data API
Self-contained version for Vercel deployment.
"""
from http.server import BaseHTTPRequestHandler
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd

# ============ CONFIGURATION ============
ASSETS = {
    "gold": {"symbol": "GC=F", "base_price": 2680.0, "vol_base": 14.5, "type": "price"},
    "silver": {"symbol": "SI=F", "base_price": 30.50, "vol_base": 22.0, "type": "price"},
    "dxy": {"symbol": "DX-Y.NYB", "base_price": 108.5, "type": "index"},
    "us10y": {"symbol": "^TNX", "base_price": 4.60, "type": "yield"},
}

# ============ MOCK DATA GENERATION ============
def generate_mock_history(asset_key: str, days: int = 60) -> pd.DataFrame:
    config = ASSETS[asset_key]
    base = config["base_price"]
    vol = 0.015 if asset_key == "silver" else 0.01
    np.random.seed(int(datetime.now().strftime("%Y%m%d")))
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    returns = np.random.randn(days) * vol
    prices = base * np.exp(np.cumsum(returns))
    return pd.DataFrame({
        'Date': dates,
        'Close': prices,
        'Open': prices * (1 + np.random.randn(days) * 0.002),
        'High': prices * (1 + np.abs(np.random.randn(days) * 0.005)),
        'Low': prices * (1 - np.abs(np.random.randn(days) * 0.005)),
    })

def generate_mock_vol_series(asset_key: str, days: int = 40) -> List[Dict]:
    base_vol = ASSETS.get(asset_key, {}).get("vol_base", 15.0)
    np.random.seed(int(datetime.now().strftime("%Y%m%d")) + 1)
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    vols = base_vol + np.cumsum(np.random.randn(days) * 0.4)
    vols = np.clip(vols, 5, 45)
    return [{"t": d.isoformat(), "value": float(v)} for d, v in zip(dates, vols)]

def get_mock_snapshot() -> Dict:
    data = {}
    for asset_key in ASSETS:
        df = generate_mock_history(asset_key)
        latest_close = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        change_pct = ((latest_close - prev_close) / prev_close) * 100
        
        vol_current = 0.0
        if asset_key in ["gold", "silver"]:
            returns = df['Close'].pct_change().dropna()
            if len(returns) >= 20:
                vol_current = float(returns.tail(20).std() * np.sqrt(252) * 100)
            else:
                vol_current = ASSETS[asset_key].get("vol_base", 15.0)
        
        data[asset_key] = {
            "metrics": {"latest": latest_close, "change_pct": change_pct},
            "vol": {"current": vol_current},
            "is_live": False
        }
    return data

def get_snapshot_response() -> Dict:
    data = get_mock_snapshot()
    feeds = {k: "demo" for k in ["gold", "silver", "us10y", "dxy", "vol_gold", "vol_silver"]}
    
    return {
        "asOf": datetime.now().isoformat(),
        "mode": "demo",
        "feeds": feeds,
        "gold": {"price": data["gold"]["metrics"]["latest"], "pctChange": data["gold"]["metrics"]["change_pct"]},
        "silver": {"price": data["silver"]["metrics"]["latest"], "pctChange": data["silver"]["metrics"]["change_pct"]},
        "us10y": {"yield": data["us10y"]["metrics"]["latest"], "bpsChange": data["us10y"]["metrics"]["change_pct"] * 10},
        "dxy": {"value": data["dxy"]["metrics"]["latest"], "pctChange": data["dxy"]["metrics"]["change_pct"]},
        "vol": {
            "gold": {"value": data["gold"]["vol"]["current"], "change": 0.0, "type": "realized"},
            "silver": {"value": data["silver"]["vol"]["current"], "change": 0.0, "type": "realized"}
        }
    }

def get_timeseries_response(asset: str, window: str) -> Dict:
    if asset.startswith("vol_"):
        base = asset.replace("vol_", "")
        series = generate_mock_vol_series(base)
        return {"asOf": datetime.now().isoformat(), "asset": asset, "window": window, "hasOHLC": False, "series": series}
    
    if asset not in ASSETS:
        asset = "gold"
    
    df = generate_mock_history(asset)
    window_map = {"1D": 5, "5D": 10, "1M": 22, "3M": 66, "1Y": 252}
    limit = window_map.get(window, 22)
    df_subset = df.tail(limit)
    
    asset_type = ASSETS.get(asset, {}).get("type", "price")
    series = []
    for _, row in df_subset.iterrows():
        point = {"t": row['Date'].isoformat()}
        if asset_type == "price":
            point.update({"open": float(row['Open']), "high": float(row['High']), "low": float(row['Low']), "close": float(row['Close'])})
        else:
            point["value"] = float(row['Close'])
        series.append(point)
    
    return {"asOf": datetime.now().isoformat(), "asset": asset, "window": window, "hasOHLC": asset_type == "price", "series": series}

def get_explain_response(asset: str) -> Dict:
    data = get_mock_snapshot()
    asset_data = data.get(asset, data["gold"])
    change = asset_data["metrics"]["change_pct"]
    label = asset.capitalize()
    
    if abs(change) < 0.15:
        what_moved = f"{label} is trading largely unchanged."
        driver = "No dominant driver"
        takeaway = f"{label} exhibited limited price movement during this session."
    elif change > 0:
        what_moved = f"{label} has advanced {change:.2f}%."
        driver = "Interest Rates"
        takeaway = f"{label} advanced, consistent with declining Treasury yields."
    else:
        what_moved = f"{label} has declined {abs(change):.2f}%."
        driver = "U.S. Dollar"
        takeaway = f"{label} declined, consistent with dollar strength."
    
    return {
        "asOf": datetime.now().isoformat(),
        "selectedAsset": asset,
        "sections": {
            "whatMoved": what_moved,
            "mostLikelyDriver": driver,
            "chartEvidence": [
                f"The price chart shows {label}'s recent trajectory.",
                "The yield chart shows the 10-year Treasury near current levels.",
                "The dollar chart shows DXY with limited directional movement."
            ],
            "plainTakeaway": takeaway
        },
        "disclaimer": "Market analysis is provided for educational purposes only and does not constitute financial or investment advice."
    }

# ============ HANDLER ============
class handler(BaseHTTPRequestHandler):
    def send_json(self, data: Dict, status: int = 200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        path = self.path.split('?')[0]
        query = self.path.split('?')[1] if '?' in self.path else ''
        
        if path == '/api/health' or path == '/api/health/':
            self.send_json({"status": "ok"})
        elif path == '/api/market/snapshot' or path == '/api/market/snapshot/':
            self.send_json(get_snapshot_response())
        elif path.startswith('/api/market/timeseries'):
            params = dict(p.split('=') for p in query.split('&') if '=' in p) if query else {}
            asset = params.get('asset', 'gold')
            window = params.get('window', '1M')
            self.send_json(get_timeseries_response(asset, window))
        else:
            self.send_json({"error": "Not found", "path": path}, 404)
    
    def do_POST(self):
        path = self.path.split('?')[0]
        
        if path == '/api/market/explain' or path == '/api/market/explain/':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode() if content_length else '{}'
            try:
                data = json.loads(body)
            except:
                data = {}
            asset = data.get('selectedAsset', 'gold')
            self.send_json(get_explain_response(asset))
        elif path == '/api/market/refresh' or path == '/api/market/refresh/':
            self.send_json({"status": "cache_cleared"})
        else:
            self.send_json({"error": "Not found"}, 404)
