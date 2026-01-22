"""
Vercel Serverless Function - Main API Entry Point
Wraps the FastAPI application for Vercel deployment.
"""
import sys
import os

# Add backend to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import asyncio

# Import our backend modules
import market_data
import analysis_engine

app = FastAPI(title="Metals, Explained API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExplainRequest(BaseModel):
    selectedAsset: str = "gold"
    window: str = "1D"

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/api/market/snapshot")
async def get_snapshot():
    try:
        data = await market_data.get_all_market_data()
        
        feeds = {}
        for k in ["gold", "silver", "us10y", "dxy"]:
            feeds[k] = "live" if data[k]["is_live"] else "demo"
        feeds["vol_gold"] = feeds["gold"]
        feeds["vol_silver"] = feeds["silver"]
        
        live_count = sum(1 for v in feeds.values() if v == "live")
        mode = "live" if live_count == 6 else ("demo" if live_count == 0 else "partial")

        return {
            "asOf": datetime.now().isoformat(),
            "mode": mode,
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
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/market/timeseries")
async def get_timeseries(
    asset: str = Query(..., pattern="^(gold|silver|us10y|dxy|vol_gold|vol_silver)$"),
    window: str = Query("1M", pattern="^(1D|5D|1M|3M|6M|1Y)$")
):
    try:
        m_data = await market_data.get_all_market_data()
        return market_data.get_timeseries_data(asset, window, m_data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/market/explain")
async def explain_market(request: ExplainRequest):
    try:
        data = await market_data.get_all_market_data()
        asset = request.selectedAsset
        drivers = analysis_engine.determine_drivers(data, asset)
        what_moved = analysis_engine.get_what_moved(data, asset)
        chart_bullets = analysis_engine.get_chart_bullets(data, asset)
        takeaway = analysis_engine.get_plain_takeaway(data, asset)
        
        return {
            "asOf": datetime.now().isoformat(),
            "selectedAsset": asset,
            "sections": {
                "whatMoved": what_moved,
                "mostLikelyDriver": drivers["primary"],
                "chartEvidence": chart_bullets,
                "plainTakeaway": takeaway
            },
            "disclaimer": "Market analysis is provided for educational purposes only and does not constitute financial or investment advice."
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/market/refresh")
async def refresh_data():
    market_data.clear_cache()
    return {"status": "cache_cleared"}

# Vercel handler
handler = Mangum(app, lifespan="off")
