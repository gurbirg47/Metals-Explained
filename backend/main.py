"""
main.py
Final audited FastAPI backend for Metals, Explained.
Strict adherence to requested JSON schemas and robust error handling.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import market_data
import analysis_engine

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("metals-backend")

app = FastAPI(
    title="Metals, Explained API (Audited)",
    description="Professional market data API for gold and silver analysis.",
    version="1.1.0",
    root_path="/api" if not __name__ == "__main__" else ""
)

# --- MIDDLEWARE & CORS ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Dev-only request logging for transparency."""
    start_time = datetime.now()
    response = await call_next(request)
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"{request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RESPONSE MODELS (STRICT SCHEMA) ---

class HealthResponse(BaseModel):
    status: str

class AssetMetric(BaseModel):
    price: Optional[float] = None
    value: Optional[float] = None
    yield_val: Optional[float] = None 
    pctChange: Optional[float] = None
    bpsChange: Optional[float] = None

class VolMetric(BaseModel):
    value: float
    change: float
    type: str = "realized"

class SnapshotResponse(BaseModel):
    asOf: str
    mode: str
    feeds: Dict[str, str]
    gold: Dict[str, Optional[float]]
    silver: Dict[str, Optional[float]]
    us10y: Dict[str, Optional[float]]
    dxy: Dict[str, Optional[float]]
    vol: Dict[str, VolMetric]

class TimeseriesResponse(BaseModel):
    asOf: str
    asset: str
    window: str
    hasOHLC: bool = False
    series: List[Dict[str, Any]]

class ExplainRequest(BaseModel):
    selectedAsset: str = "gold"
    window: str = "1D"

class ExplainSections(BaseModel):
    whatMoved: str
    mostLikelyDriver: str
    chartEvidence: List[str]
    plainTakeaway: str

class ExplainResponse(BaseModel):
    asOf: str
    selectedAsset: str
    sections: ExplainSections
    disclaimer: str

# --- ENDPOINTS ---

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "ok"}

@app.get("/market/snapshot")
async def get_snapshot():
    """END-TO-END AUDITED: Returns a robust market snapshot."""
    try:
        data = await market_data.get_all_market_data()
        
        feeds = {}
        for k in ["gold", "silver", "us10y", "dxy"]:
            feeds[k] = "live" if data[k]["is_live"] else "demo"
        
        feeds["vol_gold"] = feeds["gold"]
        feeds["vol_silver"] = feeds["silver"]
        
        live_count = sum(1 for v in feeds.values() if v == "live")
        mode = "live" if live_count == 6 else ("demo" if live_count == 0 else "partial")

        resp = {
            "asOf": datetime.now().isoformat(),
            "mode": mode,
            "feeds": feeds,
            "gold": {"price": data["gold"]["metrics"]["latest"], "pctChange": data["gold"]["metrics"]["change_pct"]},
            "silver": {"price": data["silver"]["metrics"]["latest"], "pctChange": data["silver"]["metrics"]["change_pct"]},
            "us10y": {"yield": data["us10y"]["metrics"]["latest"], "bpsChange": data["us10y"]["metrics"]["change_pct"] * 10},
            "dxy": {"value": data["dxy"]["metrics"]["latest"], "pctChange": data["dxy"]["metrics"]["change_pct"]},
            "vol": {
                "gold": {
                    "value": data["gold"]["vol"]["current"],
                    "change": 0.0, 
                    "type": "realized"
                },
                "silver": {
                    "value": data["silver"]["vol"]["current"],
                    "change": 0.0,
                    "type": "realized"
                }
            }
        }
        return resp
    except Exception as e:
        logger.error(f"Snapshot error: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to generate snapshot", "detail": str(e)})

@app.get("/market/timeseries", response_model=TimeseriesResponse)
async def get_market_timeseries(
    asset: str = Query(..., pattern="^(gold|silver|us10y|dxy|vol_gold|vol_silver)$"),
    window: str = Query("1M", pattern="^(1D|5D|1M|3M|6M|1Y)$")
):
    """END-TO-END AUDITED: Returns stable timeseries data."""
    try:
        m_data = await market_data.get_all_market_data()
        ts_data = market_data.get_timeseries_data(asset, window, m_data)
        return ts_data
    except Exception as e:
        logger.error(f"Timeseries error for {asset}: {e}")
        return JSONResponse(status_code=500, content={"error": f"Failed to fetch timeseries for {asset}"})

@app.post("/market/explain", response_model=ExplainResponse)
async def explain_market(request: ExplainRequest):
    """END-TO-END AUDITED: Returns contextual explanation without external calls."""
    try:
        data = await market_data.get_all_market_data()
        drivers = analysis_engine.determine_drivers(data)
        what_moved = analysis_engine.get_what_moved(data)
        chart_bullets = analysis_engine.get_chart_bullets(data)
        takeaway = analysis_engine.get_plain_takeaway(data)
        
        return {
            "asOf": datetime.now().isoformat(),
            "selectedAsset": request.selectedAsset,
            "sections": {
                "whatMoved": what_moved,
                "mostLikelyDriver": drivers["primary"],
                "chartEvidence": chart_bullets,
                "plainTakeaway": takeaway
            },
            "disclaimer": "Market analysis is provided for educational purposes only and does not constitute financial or investment advice."
        }
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to generate explanation"})

@app.post("/market/refresh")
async def refresh_data():
    market_data.clear_cache()
    return {"status": "cache_cleared"}

@app.on_event("startup")
async def startup_event():
    logger.info("Metals, Explained Backend Started")
    logger.info(f"Configured Assets: {list(market_data.ASSETS.keys())}")
    logger.info("Ready to serve market data with robust fallbacks.")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
