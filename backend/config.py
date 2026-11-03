"""Configuration and Universe definitions for the Daily Stock Recommendation Hub."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(BASE_DIR, "market_data.sqlite3")

# Universe of high-interest tickers across tech, semiconductors, AI, software, fintech, and growth
DEFAULT_UNIVERSE = [
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Semiconductors"},
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Consumer Electronics"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Software & Cloud"},
    {"ticker": "AMD", "name": "Advanced Micro Devices", "sector": "Semiconductors"},
    {"ticker": "PLTR", "name": "Palantir Technologies", "sector": "AI & Enterprise Software"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Automotive & Clean Energy"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "E-Commerce & Cloud"},
    {"ticker": "META", "name": "Meta Platforms Inc.", "sector": "Social Media & AI"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Search & Cloud"},
    {"ticker": "COIN", "name": "Coinbase Global", "sector": "Fintech & Crypto"},
    {"ticker": "ARM", "name": "Arm Holdings plc", "sector": "Semiconductors"},
    {"ticker": "CRWD", "name": "CrowdStrike Holdings", "sector": "Cybersecurity"},
    {"ticker": "SNOW", "name": "Snowflake Inc.", "sector": "Cloud Data Platform"},
    {"ticker": "SMCI", "name": "Super Micro Computer", "sector": "Server Infrastructure"},
    {"ticker": "HOOD", "name": "Robinhood Markets", "sector": "Fintech & Brokerage"},
    {"ticker": "UBER", "name": "Uber Technologies", "sector": "Mobility & Delivery"},
]

# Scoring Weights for the Alpha Convergence Engine (Total = 1.0)
CONVERGENCE_WEIGHTS = {
    "technical": 0.25,     # Volume breakout, RSI bounces, MACD, MA crosses
    "insider": 0.25,       # SEC Form 4 cluster buys, executive buying volume
    "analyst": 0.20,       # Consensus upgrades, target price upside
    "drop_reversal": 0.15, # 'Unjustified drop' scanner (oversold high-margin beat)
    "sentiment": 0.15,     # NLP financial headline & buzz index
}
