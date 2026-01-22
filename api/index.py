from flask import Flask, request, jsonify
import json
from datetime import datetime
import numpy as np
import pandas as pd

app = Flask(__name__)

# ============ CONFIGURATION ============
ASSETS = {
    "gold": {"symbol": "GC=F", "base_price": 2680.0, "vol_base": 14.5, "type": "price"},
    "silver": {"symbol": "SI=F", "base_price": 30.50, "vol_base": 22.0, "type": "price"},
    "dxy": {"symbol": "DX-Y.NYB", "base_price": 108.5, "type": "index"},
    "us10y": {"symbol": "^TNX", "base_price": 4.60, "type": "yield"},
}

def generate_mock_history(asset_key, days=60):
    config = ASSETS[asset_key]
    base = config["base_price"]
    vol = 0.015 if asset_key == "silver" else 0.01
    np.random.seed(int(datetime.now().strftime("%Y%m%d")))
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    returns = np.random.randn(days) * vol
    prices = base * np.exp(np.cumsum(returns))
    return pd.DataFrame({
        'Date': dates, 'Close': prices,
        'Open': prices * (1 + np.random.randn(days) * 0.002),
        'High': prices * (1 + np.abs(np.random.randn(days) * 0.005)),
        'Low': prices * (1 - np.abs(np.random.randn(days) * 0.005)),
    })

def generate_mock_vol_series(asset_key, days=40):
    base_vol = ASSETS.get(asset_key, {}).get("vol_base", 15.0)
    np.random.seed(int(datetime.now().strftime("%Y%m%d")) + 1)
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    vols = base_vol + np.cumsum(np.random.randn(days) * 0.4)
    vols = np.clip(vols, 5, 45)
    return [{"t": d.isoformat(), "value": float(v)} for d, v in zip(dates, vols)]

def get_mock_snapshot():
    data = {}
    for asset_key in ASSETS:
        df = generate_mock_history(asset_key)
        latest = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])
        change = ((latest - prev) / prev) * 100
        vol_current = 0.0
        if asset_key in ["gold", "silver"]:
            returns = df['Close'].pct_change().dropna()
            vol_current = float(returns.tail(20).std() * np.sqrt(252) * 100) if len(returns) >= 20 else ASSETS[asset_key].get("vol_base", 15.0)
        data[asset_key] = {"metrics": {"latest": latest, "change_pct": change}, "vol": {"current": vol_current}, "is_live": False}
    return data

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/market/snapshot', methods=['GET'])
def snapshot():
    data = get_mock_snapshot()
    feeds = {k: "demo" for k in ["gold", "silver", "us10y", "dxy", "vol_gold", "vol_silver"]}
    return jsonify({
        "asOf": datetime.now().isoformat(), "mode": "demo", "feeds": feeds,
        "gold": {"price": data["gold"]["metrics"]["latest"], "pctChange": data["gold"]["metrics"]["change_pct"]},
        "silver": {"price": data["silver"]["metrics"]["latest"], "pctChange": data["silver"]["metrics"]["change_pct"]},
        "us10y": {"yield": data["us10y"]["metrics"]["latest"], "bpsChange": data["us10y"]["metrics"]["change_pct"] * 10},
        "dxy": {"value": data["dxy"]["metrics"]["latest"], "pctChange": data["dxy"]["metrics"]["change_pct"]},
        "vol": {
            "gold": {"value": data["gold"]["vol"]["current"], "change": 0.0, "type": "realized"},
            "silver": {"value": data["silver"]["vol"]["current"], "change": 0.0, "type": "realized"}
        }
    })

@app.route('/api/market/timeseries', methods=['GET'])
def timeseries():
    asset = request.args.get('asset', 'gold')
    window = request.args.get('window', '1M')
    
    if asset.startswith("vol_"):
        base = asset.replace("vol_", "")
        series = generate_mock_vol_series(base if base in ASSETS else "gold")
        return jsonify({"asOf": datetime.now().isoformat(), "asset": asset, "window": window, "hasOHLC": False, "series": series})
    
    if asset not in ASSETS:
        asset = "gold"
    df = generate_mock_history(asset)
    window_map = {"1D": 5, "5D": 10, "1M": 22, "3M": 66, "1Y": 252}
    df_subset = df.tail(window_map.get(window, 22))
    asset_type = ASSETS.get(asset, {}).get("type", "price")
    series = []
    for _, row in df_subset.iterrows():
        point = {"t": row['Date'].isoformat()}
        if asset_type == "price":
            point.update({"open": float(row['Open']), "high": float(row['High']), "low": float(row['Low']), "close": float(row['Close'])})
        else:
            point["value"] = float(row['Close'])
        series.append(point)
    return jsonify({"asOf": datetime.now().isoformat(), "asset": asset, "window": window, "hasOHLC": asset_type == "price", "series": series})

@app.route('/api/market/explain', methods=['POST'])
def explain():
    data = request.get_json() or {}
    asset = data.get('selectedAsset', 'gold')
    mock = get_mock_snapshot()
    change = mock.get(asset, mock["gold"])["metrics"]["change_pct"]
    label = asset.capitalize()
    
    if abs(change) < 0.15:
        what_moved, driver, takeaway = f"{label} is trading largely unchanged.", "No dominant driver", f"{label} exhibited limited price movement."
    elif change > 0:
        what_moved, driver, takeaway = f"{label} has advanced {change:.2f}%.", "Interest Rates", f"{label} advanced, consistent with declining Treasury yields."
    else:
        what_moved, driver, takeaway = f"{label} has declined {abs(change):.2f}%.", "U.S. Dollar", f"{label} declined, consistent with dollar strength."
    
    return jsonify({
        "asOf": datetime.now().isoformat(), "selectedAsset": asset,
        "sections": {"whatMoved": what_moved, "mostLikelyDriver": driver, "chartEvidence": [f"{label}'s price chart shows recent movement.", "Yield chart shows current Treasury levels.", "DXY chart shows dollar index."], "plainTakeaway": takeaway},
        "disclaimer": "Market analysis is provided for educational purposes only and does not constitute financial or investment advice."
    })

@app.route('/api/market/refresh', methods=['POST'])
def refresh():
    return jsonify({"status": "cache_cleared"})
