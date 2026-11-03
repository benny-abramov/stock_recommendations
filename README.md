# Alpha Convergence Engine & Daily Stock Recommendation Hub

An institutional-grade, AI-driven Daily Stock Recommendation & Technical Analysis Hub built in accordance with [instructions.txt](file:///c:/benny/source/projects/stock_recommendations/instructions.txt).

The application merges **Concept 1: 'The Alpha Convergence Engine'** and **Concept 2: 'The AI-Powered Technical Playbook'** into a unified, high-performance dark-mode trading terminal.

---

## Key Capabilities

### 1. The Alpha Convergence Engine (Signal Confluence)
Rather than raw noise, the engine identifies stocks where multiple asymmetric indicators align on the same day:
- **Daily Top 5 High-Conviction Picks**: Dynamic feed featuring the top convergence setups with live score meters, primary catalysts, and 5-axis signal distributions.
- **Multi-Signal Ingestion Pipeline**:
  - **Analyst Alignment**: Consensus ratings, Wall Street price targets, upside percentages, and recent rating shifts.
  - **SEC Form 4 Insider Tracking**: Scrapes open-market cluster purchases (Transaction Code `P`) by CEOs, CFOs, and Board Directors.
  - **The 'Unjustified Drop' Scanner**: Flags stocks trading down >5% in 24 hours despite beating earnings expectations and having zero negative material filings.
  - **Volume & Technical Breakouts**: Relative volume (RVOL >= 2.5x–3.5x average), RSI oversold bounces, MACD histogram crossovers, and 20/50/200 MA trend alignments.
  - **Sentiment Scraper**: Financial headline parsing using NLP sentiment polarity to calculate a daily Bullish Buzz Index.
- **5-Axis Convergence Radar**: Custom interactive radar polygon mapping out the 5 signal vectors for the selected stock.

### 2. The AI-Powered Technical Playbook & Advanced Charting Suite
- **Interactive Multi-Timeframe Charting**:
  - Responsive resolution timeframe tabs: **`1D`**, **`5D`**, **`1M`**, **`6M`**, **`1Y`**, **`YTD`**.
  - Crisp candlestick rendering and bottom volume histogram bars.
  - Dynamic **TA Overlays** (toggleable on/off):
    - SMA 20 (Cyan)
    - SMA 50 (Amber)
    - SMA 200 (Purple)
    - EMA 20 (Light Blue)
    - Bollinger Bands (20, 2 with shaded volatility cloud)
  - **Sub-Chart Indicators** (switchable on-the-fly):
    - **RSI (14)** with 70/30 overbought/oversold guide levels
    - **MACD (12, 26, 9)** with colored histogram and signal line
    - **On-Balance Volume (OBV)** trendline
  - **Interactive Crosshair HUD**: Inspects OHLCV and indicator values on candle hover.
- **Automated Pattern Explainer AI Panel**:
  - Synthesizes chart patterns (e.g., *Bullish Morning Star at Lower Bollinger Band Support*, *High RVOL Breakout*).
  - Outlines **Key Support, Resistance, Target Price, and Stop-Loss Levels**.
  - Calculates the **Risk/Reward Ratio** (e.g., `1 : 3.4`).
  - Generates an actionable execution playbook with entry window, sizing, and profit targets.

### 3. Universe Screener
- Interactive table of the evaluated universe with search and filtering by:
  - *All Evaluated Stocks*
  - *High Confluence Picks (Score > 75)*
  - *Unjustified Drops*
  - *Heavy Insider Cluster Buys*
  - *Volume Breakouts (RVOL > 2x)*
  - *Bullish Sentiment Buzz*

---

## Architecture

```
stock_recommendations/
├── backend/
│   ├── config.py             # Stock universe definition and scoring weights
│   ├── database.py           # SQLite persistence layer
│   ├── engine.py             # Alpha Convergence pipeline & ranking engine
│   ├── market_data.py        # Candlestick generator (1D, 5D, 1M, 6M, 1Y, YTD)
│   ├── models.py             # Pydantic data schemas
│   ├── pattern_explainer.py  # AI Technical Playbook generator
│   ├── sec_scraper.py        # SEC Form 4 insider transaction tracker
│   ├── sentiment_scraper.py  # Financial headlines NLP sentiment analyzer
│   ├── technical_analysis.py # Pure-Python TA calculations (SMA, EMA, BB, RSI, MACD, OBV)
│   └── main.py               # FastAPI application & REST endpoints
├── frontend/
│   ├── index.html            # Trading terminal HTML5 UI
│   ├── css/
│   │   └── style.css         # Modern dark terminal design system & typography
│   └── js/
│       ├── api.js            # REST API client
│       ├── chart.js          # High-performance canvas charting engine
│       ├── radar.js          # Custom 5-axis convergence radar chart
│       └── app.js            # Main controller and UI coordinator
├── run.py                    # Single-command launcher
├── requirements.txt          # Python dependencies
└── instructions.txt          # Original architectural guide
```

---

## Running the Application

1. **Activate the virtual environment**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Launch the server**:
   ```powershell
   python run.py
   ```

3. **Open in browser**:
   Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000)

4. **Explore the Interactive REST API**:
   Navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
