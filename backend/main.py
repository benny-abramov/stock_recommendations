"""FastAPI Application for the AI-driven Daily Stock Recommendation & Technical Analysis Hub."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime
import os

from backend.engine import run_full_pipeline, get_top_5_picks
from backend.database import init_db, get_all_recommendations, get_recommendation_by_ticker
from backend.market_data import get_chart_data

app = FastAPI(
    title="Alpha Convergence Engine - Daily Stock Recommendation Hub",
    description="AI-driven multi-signal stock confluence and technical analysis platform",
    version="2.0.0"
)

# Enable CORS for flexible local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

@app.on_event("startup")
async def startup_event():
    """Initialize DB and run initial universe scan if needed."""
    init_db()
    existing = get_all_recommendations()
    if not existing:
        run_full_pipeline()

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "engine": "Alpha Convergence Engine v2.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/recommendations/top")
def get_top_recommendations():
    """Retrieve Top 5 High-Conviction Confluence Picks."""
    import importlib
    import backend.market_data
    importlib.reload(backend.market_data)

    top_picks = get_top_5_picks()
    for s in top_picks:
        live = backend.market_data.get_current_stock_data(s["ticker"])
        if live:
            s["current_price"] = live["current_price"]
            s["price_change"] = live["price_change"]
            s["price_change_percent"] = live["price_change_percent"]
    return {
        "as_of": datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC"),
        "total_evaluated": len(get_all_recommendations()),
        "market_status": "Market Open - Intraday Confluence Active",
        "top_picks": top_picks
    }

@app.get("/api/recommendations/all")
def get_all_stocks():
    """Retrieve full universe scored and ranked."""
    import importlib
    import backend.market_data
    importlib.reload(backend.market_data)

    stocks = get_all_recommendations()
    if not stocks:
        stocks = run_full_pipeline()
    for s in stocks:
        live = backend.market_data.get_current_stock_data(s["ticker"])
        if live:
            s["current_price"] = live["current_price"]
            s["price_change"] = live["price_change"]
            s["price_change_percent"] = live["price_change_percent"]
    return {
        "as_of": datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC"),
        "total": len(stocks),
        "stocks": stocks
    }

@app.get("/api/stocks/{ticker}")
def get_stock_detail(ticker: str):
    """Retrieve full profile, metrics, insider trades, and sentiment for a ticker."""
    import importlib
    import backend.market_data
    importlib.reload(backend.market_data)

    stock = get_recommendation_by_ticker(ticker)
    if not stock:
        from backend.engine import add_and_evaluate_ticker
        stock = add_and_evaluate_ticker(ticker)
        
    # Always sync with fresh live quote
    live = backend.market_data.get_current_stock_data(ticker)
    if live and live.get("current_price"):
        stock["current_price"] = live["current_price"]
        stock["price_change"] = live["price_change"]
        stock["price_change_percent"] = live["price_change_percent"]
        stock["volume"] = live["volume"]
        stock["rvol"] = live["rvol"]
        if live.get("target_price"):
            stock["analyst"]["target_price"] = live["target_price"]
            stock["analyst"]["upside_percent"] = round(((live["target_price"] - live["current_price"]) / live["current_price"]) * 100, 1)

    return stock

@app.get("/api/stocks/{ticker}/chart")
def get_ticker_chart(
    ticker: str,
    timeframe: str = Query("1M", pattern="^(1D|5D|1M|6M|1Y|YTD)$")
):
    """Retrieve OHLCV candles, moving averages, Bollinger bands, RSI, MACD, and OBV."""
    import importlib
    import backend.market_data
    importlib.reload(backend.market_data)

    try:
        return backend.market_data.get_chart_data(ticker, timeframe)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute chart data: {str(e)}")

@app.get("/api/stocks/{ticker}/ai-analysis")
def get_ticker_ai_analysis(ticker: str):
    """Retrieve the AI Pattern Explainer and actionable trading playbook."""
    stock = get_recommendation_by_ticker(ticker)
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {ticker} not found.")
    return {
        "ticker": ticker.upper(),
        "ai_explainer": stock["ai_explainer"],
        "primary_catalyst": stock["primary_catalyst"],
        "signal_breakdown": stock["signal_breakdown"]
    }

@app.post("/api/scan/trigger")
def trigger_pipeline_scan():
    """Manually trigger full multi-signal pipeline ingestion and rescoring."""
    updated = run_full_pipeline()
    return {
        "status": "success",
        "message": f"Pipeline successfully rescanned and scored {len(updated)} stocks.",
        "as_of": datetime.utcnow().isoformat()
    }

@app.post("/api/tickers/add")
def add_custom_ticker(
    ticker: str = Query(..., description="Stock ticker symbol (e.g. NFLX, INTC, AVGO)"),
    name: str = Query(None, description="Company name (optional)"),
    sector: str = Query(None, description="Industry sector (optional)")
):
    """Add any custom ticker to the evaluated universe on-the-fly."""
    try:
        from backend.engine import add_and_evaluate_ticker
        evaluated = add_and_evaluate_ticker(ticker, name, sector)
        return {
            "status": "success",
            "message": f"Successfully added and evaluated {ticker.upper()}",
            "stock": evaluated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add ticker: {str(e)}")

# Mount static files for frontend
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Alpha Convergence Engine Backend is running. Frontend index.html not yet initialized."}
