"""Data models and schemas for the Stock Recommendation Hub."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CandleData(BaseModel):
    time: str  # YYYY-MM-DD or ISO timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float

class IndicatorSeries(BaseModel):
    time: str
    value: Optional[float] = None
    upper: Optional[float] = None
    middle: Optional[float] = None
    lower: Optional[float] = None
    macd: Optional[float] = None
    signal: Optional[float] = None
    hist: Optional[float] = None

class ChartDataResponse(BaseModel):
    ticker: str
    timeframe: str
    candles: List[CandleData]
    sma20: List[Dict[str, Any]]
    sma50: List[Dict[str, Any]]
    sma200: List[Dict[str, Any]]
    ema20: List[Dict[str, Any]]
    bollinger: List[Dict[str, Any]]
    rsi: List[Dict[str, Any]]
    macd: List[Dict[str, Any]]
    obv: List[Dict[str, Any]]

class InsiderTransaction(BaseModel):
    date: str
    filer_name: str
    filer_title: str
    shares: int
    price: float
    total_value: float
    transaction_type: str  # e.g. "Cluster Buy", "Open Market Purchase"

class AnalystConsensus(BaseModel):
    rating: str  # "Strong Buy", "Moderate Buy", "Hold"
    target_price: float
    current_price: float
    upside_percent: float
    num_analysts: int
    recent_shifts: List[str]

class UnjustifiedDropMetrics(BaseModel):
    is_unjustified_drop: bool
    drop_percent_24h: float
    beat_earnings: bool
    eps_surprise_percent: float
    negative_material_news: bool
    thesis: str

class SentimentMetrics(BaseModel):
    buzz_index: float  # 0 to 100
    sentiment_label: str  # "Very Bullish", "Bullish", "Neutral"
    bullish_ratio: float
    total_sources: int
    top_headlines: List[Dict[str, str]]

class SignalBreakdown(BaseModel):
    technical_score: float = Field(..., description="0-100 technical & volume breakout score")
    insider_score: float = Field(..., description="0-100 SEC Form 4 insider conviction score")
    analyst_score: float = Field(..., description="0-100 Wall St consensus & upgrades score")
    drop_reversal_score: float = Field(..., description="0-100 unjustified drop reversal score")
    sentiment_score: float = Field(..., description="0-100 financial NLP & buzz score")
    convergence_score: float = Field(..., description="Weighted composite alpha convergence score")

class AIPatternExplainer(BaseModel):
    bias: str  # e.g. "High Conviction Buy", "Bullish Breakout", "Oversold Reversal"
    pattern_name: str
    support_level: float
    resistance_level: float
    target_price: float
    stop_loss: float
    risk_reward: str
    technical_summary: str
    multi_signal_confluence: str
    actionable_playbook: str

class RecommendationPick(BaseModel):
    ticker: str
    name: str
    sector: str
    current_price: float
    price_change: float
    price_change_percent: float
    volume: float
    avg_volume: float
    rvol: float  # Relative Volume
    rank: int
    primary_catalyst: str
    signal_breakdown: SignalBreakdown
    analyst: AnalystConsensus
    insider_summary: List[InsiderTransaction]
    drop_scanner: UnjustifiedDropMetrics
    sentiment: SentimentMetrics
    ai_explainer: AIPatternExplainer
    sparkline: List[float]

class TopPicksResponse(BaseModel):
    as_of: str
    total_evaluated: int
    top_picks: List[RecommendationPick]
    market_status: str

class UniverseResponse(BaseModel):
    as_of: str
    stocks: List[RecommendationPick]
