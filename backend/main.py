"""
main.py
FastAPI backend for Metals, Explained dashboard.
Provides market data and explanation endpoints.
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import numpy as np

from market_data import get_all_market_data, get_timeseries, clear_cache
from analysis_engine import (
    determine_drivers,
    get_what_moved,
    get_clean_story,
    get_why_hard_or_easy,
    get_chart_bullets,
    get_plain_takeaway,
)

app = FastAPI(
    title="Metals, Explained API",
    description="Educational market data API for gold and silver markets",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "*"  # For development; restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# RESPONSE MODELS
# ─────────────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str


class FeedStatus(BaseModel):
    isLive: bool


class AssetPrice(BaseModel):
    price: Optional[float]
    pctChange: Optional[float]


class YieldData(BaseModel):
    yield_value: Optional[float]
    bpsChange: Optional[float]


class IndexData(BaseModel):
    value: Optional[float]
    pctChange: Optional[float]


class VolData(BaseModel):
    value: Optional[float]
    label: str


class DriversData(BaseModel):
    primary: str
    secondary: str
    volLevel: str


class SnapshotResponse(BaseModel):
    asOf: str
    mode: str
    feeds: Dict[str, FeedStatus]
    gold: AssetPrice
    silver: AssetPrice
    us10y: Dict[str, Any]
    dxy: IndexData
    vol: VolData
    drivers: DriversData


class TimeseriesPoint(BaseModel):
    t: str
    c: Optional[float]
    o: Optional[float] = None
    h: Optional[float] = None
    l: Optional[float] = None


class TimeseriesResponse(BaseModel):
    asOf: str
    asset: str
    window: str
    hasOHLC: bool
    isMock: bool
    series: List[Dict[str, Any]]


class ExplainRequest(BaseModel):
    window: str = "1D"


class ExplainSections(BaseModel):
    whatMoved: str
    drivers: str
    conflictCheck: str
    chartBullets: List[str]
    plainTakeaway: str


class ExplainResponse(BaseModel):
    asOf: str
    sections: ExplainSections


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/market/snapshot", response_model=SnapshotResponse)
async def get_snapshot():
    """Get current market snapshot with all key metrics."""
    data = get_all_market_data()
    
    # Determine mode
    feeds = {
        "gold": {"isLive": not data["gold"]["is_mock"]},
        "silver": {"isLive": not data["silver"]["is_mock"]},
        "us10y": {"isLive": not data["us10y"]["is_mock"]},
        "dxy": {"isLive": not data["dxy"]["is_mock"]},
    }
    
    live_count = sum(1 for f in feeds.values() if f["isLive"])
    if live_count == len(feeds):
        mode = "live"
    elif live_count == 0:
        mode = "demo"
    else:
        mode = "partial"
    
    # Get metrics
    gold_m = data["gold"]["metrics"]
    silver_m = data["silver"]["metrics"]
    us10y_m = data["us10y"]["metrics"]
    dxy_m = data["dxy"]["metrics"]
    
    # Calculate volatility
    df_gold = data["gold"]["df"]
    vol_value = None
    if df_gold is not None and "Close" in df_gold.columns and len(df_gold) >= 20:
        returns = df_gold["Close"].pct_change().dropna()
        vol_value = float(returns.tail(20).std() * np.sqrt(252) * 100)
    
    # Get drivers
    drivers = determine_drivers(data)
    
    return {
        "asOf": datetime.now().isoformat(),
        "mode": mode,
        "feeds": feeds,
        "gold": {
            "price": gold_m.get("latest"),
            "pctChange": gold_m.get("change_pct"),
        },
        "silver": {
            "price": silver_m.get("latest"),
            "pctChange": silver_m.get("change_pct"),
        },
        "us10y": {
            "yield": us10y_m.get("latest"),
            "bpsChange": (us10y_m.get("change_pct") or 0) * 10,
        },
        "dxy": {
            "value": dxy_m.get("latest"),
            "pctChange": dxy_m.get("change_pct"),
        },
        "vol": {
            "value": vol_value,
            "label": "20D realized",
        },
        "drivers": {
            "primary": drivers["primary"],
            "secondary": drivers["secondary"],
            "volLevel": drivers["vol_level"],
        },
    }


@app.get("/market/timeseries", response_model=TimeseriesResponse)
async def get_market_timeseries(
    asset: str = Query(..., description="Asset: gold, silver, us10y, dxy, vol"),
    window: str = Query("1M", description="Window: 1D, 5D, 1M, 3M, 1Y")
):
    """Get timeseries data for charting."""
    if asset == "vol":
        # Special handling for volatility series
        data = get_all_market_data()
        df_gold = data["gold"]["df"]
        
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
                "asOf": datetime.now().isoformat(),
                "asset": "vol",
                "window": window,
                "hasOHLC": False,
                "isMock": data["gold"]["is_mock"],
                "series": series
            }
        else:
            return {
                "asOf": datetime.now().isoformat(),
                "asset": "vol",
                "window": window,
                "hasOHLC": False,
                "isMock": True,
                "series": []
            }
    
    result = get_timeseries(asset, window)
    result["asOf"] = datetime.now().isoformat()
    return result


@app.post("/market/explain", response_model=ExplainResponse)
async def explain_market(request: ExplainRequest):
    """Get structured market explanation."""
    data = get_all_market_data()
    
    what_moved = get_what_moved(data)
    clean_story = get_clean_story(data)
    why_hard = get_why_hard_or_easy(data)
    chart_bullets = get_chart_bullets(data)
    takeaway = get_plain_takeaway(data)
    
    return {
        "asOf": datetime.now().isoformat(),
        "sections": {
            "whatMoved": what_moved,
            "drivers": clean_story,
            "conflictCheck": why_hard,
            "chartBullets": chart_bullets,
            "plainTakeaway": takeaway,
        }
    }


@app.post("/market/refresh")
async def refresh_data():
    """Clear cache and force data refresh."""
    clear_cache()
    return {"status": "cache_cleared", "asOf": datetime.now().isoformat()}


# ─────────────────────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
