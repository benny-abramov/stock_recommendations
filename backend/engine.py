"""The Alpha Convergence Engine.

Orchestrates multi-source ingestion, calculates weighted signal scores,
determines the Daily Top 5 High-Conviction Picks, and updates the local SQLite database.
"""

from typing import List, Dict, Any
from datetime import datetime
from backend.config import DEFAULT_UNIVERSE, CONVERGENCE_WEIGHTS
from backend.market_data import (
    get_current_stock_data, generate_candles_for_timeframe,
    calculate_analyst_score, calculate_drop_reversal_score
)
from backend.technical_analysis import (
    calculate_sma, calculate_rsi, calculate_macd, score_technical_setup
)
from backend.sec_scraper import get_insider_transactions, calculate_insider_score
from backend.sentiment_scraper import get_ticker_sentiment, calculate_sentiment_score
from backend.pattern_explainer import generate_ai_pattern_explainer
from backend.database import init_db, save_recommendation, get_all_recommendations

def evaluate_stock(ticker_info: Dict[str, str]) -> Dict[str, Any]:
    """Perform full multi-signal convergence evaluation on a single stock."""
    ticker = ticker_info["ticker"]
    name = ticker_info["name"]
    sector = ticker_info["sector"]
    
    # 1. Market Data and Candlesticks (1M daily resolution for base indicators)
    quote = get_current_stock_data(ticker)
    candles = generate_candles_for_timeframe(ticker, "1M")
    closes = [c["close"] for c in candles]
    
    # Technical Indicators
    sma20 = calculate_sma(closes, 20)
    sma50 = calculate_sma(closes, 50)
    rsi_series = calculate_rsi(closes, 14)
    _, _, macd_hist = calculate_macd(closes, 12, 26, 9)
    
    tech_score = score_technical_setup(candles, rsi_series, macd_hist, sma20, sma50)
    
    # 2. Insider Activity (SEC Form 4)
    insider_trades = get_insider_transactions(ticker)
    insider_score = calculate_insider_score(ticker, insider_trades)
    
    # 3. Analyst Alignment
    analyst_consensus = {
        "rating": quote["rating"],
        "target_price": quote["target_price"],
        "current_price": quote["current_price"],
        "upside_percent": round(((quote["target_price"] - quote["current_price"]) / quote["current_price"]) * 100, 1),
        "num_analysts": quote["num_analysts"],
        "recent_shifts": quote["recent_shifts"]
    }
    analyst_score = calculate_analyst_score(analyst_consensus)
    
    # 4. Unjustified Drop Scanner
    drop_info = quote["unjustified_drop"]
    drop_metrics = {
        "is_unjustified_drop": drop_info.get("is_drop", False),
        "drop_percent_24h": drop_info.get("drop_pct", 0.0),
        "beat_earnings": drop_info.get("beat_earnings", True),
        "eps_surprise_percent": drop_info.get("eps_surprise", 0.0),
        "negative_material_news": drop_info.get("negative_news", False),
        "thesis": drop_info.get("thesis", "Strong fundamentals.")
    }
    drop_score = calculate_drop_reversal_score(drop_metrics)
    
    # 5. Financial Sentiment NLP
    sentiment_metrics = get_ticker_sentiment(ticker)
    sentiment_score = calculate_sentiment_score(sentiment_metrics)
    
    # 6. Weighted Alpha Convergence Score
    w = CONVERGENCE_WEIGHTS
    convergence_score = round(
        (w["technical"] * tech_score) +
        (w["insider"] * insider_score) +
        (w["analyst"] * analyst_score) +
        (w["drop_reversal"] * drop_score) +
        (w["sentiment"] * sentiment_score),
        1
    )
    
    # Primary Catalyst determination
    catalysts = []
    if drop_metrics["is_unjustified_drop"]:
        catalysts.append(f"Unjustified {drop_metrics['drop_percent_24h']}% Dip Post-Earnings Beat")
    if insider_score >= 75:
        catalysts.append("Form 4 Cluster Insider Buying")
    if quote["rvol"] >= 2.5:
        catalysts.append(f"{quote['rvol']}x Relative Volume Surge")
    if analyst_score >= 80:
        catalysts.append(f"Wall St Target Upside (+{analyst_consensus['upside_percent']}%)")
    if sentiment_metrics["buzz_index"] >= 75:
        catalysts.append("High-Velocity Bullish News Sentiment")
        
    primary_catalyst = " • ".join(catalysts[:2]) if catalysts else "Technical Base Consolidation"
    
    # AI Pattern Explainer
    latest_rsi = rsi_series[-1] if rsi_series and rsi_series[-1] is not None else None
    latest_hist = macd_hist[-1] if macd_hist and macd_hist[-1] is not None else None
    ai_explainer = generate_ai_pattern_explainer(
        ticker=ticker,
        quote=quote,
        candles=candles,
        rsi_val=latest_rsi,
        macd_hist_val=latest_hist,
        insider_trades=insider_trades,
        sentiment_data=sentiment_metrics,
        drop_data=drop_metrics
    )
    
    # Sparkline: last 15 closes
    sparkline = [round(c, 2) for c in closes[-15:]]
    
    return {
        "ticker": ticker,
        "name": name,
        "sector": sector,
        "current_price": quote["current_price"],
        "price_change": quote["price_change"],
        "price_change_percent": quote["price_change_percent"],
        "volume": quote["volume"],
        "avg_volume": quote["avg_volume"],
        "rvol": quote["rvol"],
        "rank": 0, # Will be set after sorting
        "primary_catalyst": primary_catalyst,
        "signal_breakdown": {
            "convergence_score": convergence_score,
            "technical_score": tech_score,
            "insider_score": insider_score,
            "analyst_score": analyst_score,
            "drop_reversal_score": drop_score,
            "sentiment_score": sentiment_score
        },
        "analyst": analyst_consensus,
        "insider_summary": insider_trades,
        "drop_scanner": drop_metrics,
        "sentiment": sentiment_metrics,
        "ai_explainer": ai_explainer,
        "sparkline": sparkline
    }

def run_full_pipeline() -> List[Dict[str, Any]]:
    """Execute complete ingestion and scoring pipeline for entire universe."""
    init_db()
    results = []
    for item in DEFAULT_UNIVERSE:
        evaluated = evaluate_stock(item)
        results.append(evaluated)
        
    # Sort by convergence score descending
    results.sort(key=lambda x: x["signal_breakdown"]["convergence_score"], reverse=True)
    
    # Assign ranks and save to DB
    for rank, item in enumerate(results, start=1):
        item["rank"] = rank
        save_recommendation(item)
        
    return results

def get_top_5_picks() -> List[Dict[str, Any]]:
    """Retrieve or compute the Daily Top 5 High-Conviction Picks."""
    cached = get_all_recommendations()
    if not cached or len(cached) < 5:
        cached = run_full_pipeline()
    return cached[:5]

def add_and_evaluate_ticker(ticker: str, name: str = None, sector: str = None) -> Dict[str, Any]:
    """Add a new ticker to universe, evaluate its multi-signal confluence, and re-rank."""
    ticker_clean = ticker.upper().strip()
    if not name:
        name = f"{ticker_clean} Corporation"
    if not sector:
        sector = "Growth & Technology"
        
    item = {"ticker": ticker_clean, "name": name, "sector": sector}
    evaluated = evaluate_stock(item)
    save_recommendation(evaluated)
    
    # Re-rank entire evaluated universe
    all_recs = get_all_recommendations()
    all_recs.sort(key=lambda x: x["signal_breakdown"]["convergence_score"], reverse=True)
    for rank, rec in enumerate(all_recs, start=1):
        rec["rank"] = rank
        save_recommendation(rec)
        
    return evaluated
