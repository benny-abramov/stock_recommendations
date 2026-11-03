"""SQLite database interface for the Daily Stock Recommendation Hub."""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Recommendations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        ticker TEXT PRIMARY KEY,
        name TEXT,
        sector TEXT,
        current_price REAL,
        price_change REAL,
        price_change_percent REAL,
        volume REAL,
        avg_volume REAL,
        rvol REAL,
        rank INTEGER,
        primary_catalyst TEXT,
        convergence_score REAL,
        technical_score REAL,
        insider_score REAL,
        analyst_score REAL,
        drop_reversal_score REAL,
        sentiment_score REAL,
        analyst_data TEXT,
        insider_data TEXT,
        drop_data TEXT,
        sentiment_data TEXT,
        ai_explainer_data TEXT,
        sparkline TEXT,
        updated_at TEXT
    )
    """)

    # Historical chart cache table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chart_cache (
        ticker TEXT,
        timeframe TEXT,
        data_json TEXT,
        updated_at TEXT,
        PRIMARY KEY (ticker, timeframe)
    )
    """)

    conn.commit()
    conn.close()

def save_recommendation(rec_dict: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO recommendations (
        ticker, name, sector, current_price, price_change, price_change_percent,
        volume, avg_volume, rvol, rank, primary_catalyst, convergence_score,
        technical_score, insider_score, analyst_score, drop_reversal_score, sentiment_score,
        analyst_data, insider_data, drop_data, sentiment_data, ai_explainer_data, sparkline, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        rec_dict["ticker"],
        rec_dict["name"],
        rec_dict["sector"],
        rec_dict["current_price"],
        rec_dict["price_change"],
        rec_dict["price_change_percent"],
        rec_dict["volume"],
        rec_dict["avg_volume"],
        rec_dict["rvol"],
        rec_dict["rank"],
        rec_dict["primary_catalyst"],
        rec_dict["signal_breakdown"]["convergence_score"],
        rec_dict["signal_breakdown"]["technical_score"],
        rec_dict["signal_breakdown"]["insider_score"],
        rec_dict["signal_breakdown"]["analyst_score"],
        rec_dict["signal_breakdown"]["drop_reversal_score"],
        rec_dict["signal_breakdown"]["sentiment_score"],
        json.dumps(rec_dict["analyst"]),
        json.dumps(rec_dict["insider_summary"]),
        json.dumps(rec_dict["drop_scanner"]),
        json.dumps(rec_dict["sentiment"]),
        json.dumps(rec_dict["ai_explainer"]),
        json.dumps(rec_dict["sparkline"]),
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

def get_all_recommendations() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendations ORDER BY convergence_score DESC")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        r = dict(row)
        rec = {
            "ticker": r["ticker"],
            "name": r["name"],
            "sector": r["sector"],
            "current_price": r["current_price"],
            "price_change": r["price_change"],
            "price_change_percent": r["price_change_percent"],
            "volume": r["volume"],
            "avg_volume": r["avg_volume"],
            "rvol": r["rvol"],
            "rank": r["rank"],
            "primary_catalyst": r["primary_catalyst"],
            "signal_breakdown": {
                "convergence_score": r["convergence_score"],
                "technical_score": r["technical_score"],
                "insider_score": r["insider_score"],
                "analyst_score": r["analyst_score"],
                "drop_reversal_score": r["drop_reversal_score"],
                "sentiment_score": r["sentiment_score"],
            },
            "analyst": json.loads(r["analyst_data"]),
            "insider_summary": json.loads(r["insider_data"]),
            "drop_scanner": json.loads(r["drop_data"]),
            "sentiment": json.loads(r["sentiment_data"]),
            "ai_explainer": json.loads(r["ai_explainer_data"]),
            "sparkline": json.loads(r["sparkline"]) if r["sparkline"] else [],
            "updated_at": r["updated_at"]
        }
        results.append(rec)
    return results

def get_recommendation_by_ticker(ticker: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendations WHERE ticker = ?", (ticker.upper(),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    r = dict(row)
    return {
        "ticker": r["ticker"],
        "name": r["name"],
        "sector": r["sector"],
        "current_price": r["current_price"],
        "price_change": r["price_change"],
        "price_change_percent": r["price_change_percent"],
        "volume": r["volume"],
        "avg_volume": r["avg_volume"],
        "rvol": r["rvol"],
        "rank": r["rank"],
        "primary_catalyst": r["primary_catalyst"],
        "signal_breakdown": {
            "convergence_score": r["convergence_score"],
            "technical_score": r["technical_score"],
            "insider_score": r["insider_score"],
            "analyst_score": r["analyst_score"],
            "drop_reversal_score": r["drop_reversal_score"],
            "sentiment_score": r["sentiment_score"],
        },
        "analyst": json.loads(r["analyst_data"]),
        "insider_summary": json.loads(r["insider_data"]),
        "drop_scanner": json.loads(r["drop_data"]),
        "sentiment": json.loads(r["sentiment_data"]),
        "ai_explainer": json.loads(r["ai_explainer_data"]),
        "sparkline": json.loads(r["sparkline"]) if r["sparkline"] else [],
        "updated_at": r["updated_at"]
    }
