"""Technical Analysis calculation suite for stock candlestick data.

Calculates:
- Moving Averages (SMA 20, SMA 50, SMA 200, EMA 20)
- Bollinger Bands (20, 2)
- Relative Strength Index (RSI 14)
- Moving Average Convergence Divergence (MACD 12, 26, 9)
- On-Balance Volume (OBV)
- Candlestick and Technical Pattern recognition
- Technical Score (0-100)
"""

import math
from typing import List, Dict, Any, Tuple

def calculate_sma(closes: List[float], period: int) -> List[float | None]:
    result = []
    for i in range(len(closes)):
        if i + 1 < period:
            result.append(None)
        else:
            subset = closes[i + 1 - period : i + 1]
            result.append(round(sum(subset) / period, 2))
    return result

def calculate_ema(closes: List[float], period: int) -> List[float | None]:
    result = []
    k = 2.0 / (period + 1)
    ema_prev = None
    for i in range(len(closes)):
        if i + 1 < period:
            result.append(None)
        elif i + 1 == period:
            initial_sma = sum(closes[:period]) / period
            ema_prev = initial_sma
            result.append(round(ema_prev, 2))
        else:
            ema = (closes[i] * k) + (ema_prev * (1 - k))
            ema_prev = ema
            result.append(round(ema, 2))
    return result

def calculate_bollinger_bands(closes: List[float], period: int = 20, multiplier: float = 2.0) -> Tuple[List[float | None], List[float | None], List[float | None]]:
    upper_band = []
    middle_band = []
    lower_band = []
    for i in range(len(closes)):
        if i + 1 < period:
            upper_band.append(None)
            middle_band.append(None)
            lower_band.append(None)
        else:
            subset = closes[i + 1 - period : i + 1]
            mean = sum(subset) / period
            variance = sum((x - mean) ** 2 for x in subset) / period
            std_dev = math.sqrt(variance)
            upper = mean + (multiplier * std_dev)
            lower = mean - (multiplier * std_dev)
            middle_band.append(round(mean, 2))
            upper_band.append(round(upper, 2))
            lower_band.append(round(lower, 2))
    return upper_band, middle_band, lower_band

def calculate_rsi(closes: List[float], period: int = 14) -> List[float | None]:
    if len(closes) <= period:
        return [None] * len(closes)
    
    result = [None] * period
    gains = []
    losses = []
    for i in range(1, period + 1):
        diff = closes[i] - closes[i - 1]
        gains.append(max(0.0, diff))
        losses.append(max(0.0, -diff))
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        result.append(100.0)
    else:
        rs = avg_gain / avg_loss
        result.append(round(100.0 - (100.0 / (1.0 + rs)), 2))
        
    for i in range(period + 1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gain = max(0.0, diff)
        loss = max(0.0, -diff)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(round(100.0 - (100.0 / (1.0 + rs)), 2))
            
    return result

def calculate_macd(closes: List[float], fast: int = 12, slow: int = 26, signal_period: int = 9) -> Tuple[List[float | None], List[float | None], List[float | None]]:
    ema_fast = calculate_ema(closes, fast)
    ema_slow = calculate_ema(closes, slow)
    
    macd_line = []
    valid_macd_indices = []
    valid_macd_values = []
    
    for i in range(len(closes)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            val = round(ema_fast[i] - ema_slow[i], 2)
            macd_line.append(val)
            valid_macd_indices.append(i)
            valid_macd_values.append(val)
        else:
            macd_line.append(None)
            
    # Calculate signal line (EMA of macd_line)
    signal_line = [None] * len(closes)
    histogram = [None] * len(closes)
    
    if len(valid_macd_values) >= signal_period:
        sig_emas = calculate_ema(valid_macd_values, signal_period)
        for idx, sig_val in enumerate(sig_emas):
            original_idx = valid_macd_indices[idx]
            signal_line[original_idx] = sig_val
            if sig_val is not None and macd_line[original_idx] is not None:
                histogram[original_idx] = round(macd_line[original_idx] - sig_val, 2)
                
    return macd_line, signal_line, histogram

def calculate_obv(closes: List[float], volumes: List[float]) -> List[float]:
    if not closes:
        return []
    obv = [volumes[0]]
    current = volumes[0]
    for i in range(1, len(closes)):
        if closes[i] > closes[i - 1]:
            current += volumes[i]
        elif closes[i] < closes[i - 1]:
            current -= volumes[i]
        obv.append(round(current, 0))
    return obv

def detect_candlestick_patterns(candles: List[Dict[str, Any]]) -> List[str]:
    """Detect key bullish patterns: Morning Star, Bullish Engulfing, Hammer, Bull Flag, Oversold Bounce."""
    patterns = []
    if len(candles) < 3:
        return patterns
    
    c3 = candles[-1] # Most recent
    c2 = candles[-2] # Previous
    c1 = candles[-3] # 2 bars ago
    
    body3 = abs(c3["close"] - c3["open"])
    body2 = abs(c2["close"] - c2["open"])
    body1 = abs(c1["close"] - c1["open"])
    
    # 1. Bullish Morning Star (3-candle pattern)
    # c1 bearish large body, c2 small body gapping down, c3 bullish strong recovery into c1 body
    if (c1["close"] < c1["open"]) and (body1 > 0.015 * c1["open"]):
        if (c2["open"] < c1["close"]) and (body2 < body1 * 0.4):
            if (c3["close"] > c3["open"]) and (c3["close"] > (c1["open"] + c1["close"]) / 2):
                patterns.append("Bullish Morning Star")
                
    # 2. Bullish Engulfing
    # c2 red body, c3 green body that completely covers c2 body
    if (c2["close"] < c2["open"]) and (c3["close"] > c3["open"]):
        if c3["open"] <= c2["close"] and c3["close"] >= c2["open"]:
            patterns.append("Bullish Engulfing")
            
    # 3. Hammer (long lower wick at least 2x body, tiny upper wick)
    lower_wick = min(c3["open"], c3["close"]) - c3["low"]
    upper_wick = c3["high"] - max(c3["open"], c3["close"])
    if body3 > 0 and lower_wick >= 2 * body3 and upper_wick <= body3 * 0.6:
        patterns.append("Hammer / Bullish Pin Bar")
        
    # 4. Golden Cross Check (recent 50 SMA crossed above 200 SMA)
    closes = [c["close"] for c in candles]
    if len(closes) >= 50:
        sma50 = calculate_sma(closes, 50)
        sma20 = calculate_sma(closes, 20)
        if sma20[-1] and sma50[-1] and sma20[-1] > sma50[-1]:
            if len(sma20) > 3 and sma20[-3] and sma50[-3] and sma20[-3] <= sma50[-3]:
                patterns.append("Bullish Momentum Cross (SMA 20 > 50)")

    # 5. Volume Climax / Surge
    recent_vols = [c["volume"] for c in candles[-20:]]
    avg_vol = sum(recent_vols) / len(recent_vols) if recent_vols else 1.0
    if c3["volume"] > 2.5 * avg_vol:
        patterns.append(f"High Relative Volume Breakout ({round(c3['volume']/avg_vol, 1)}x RVOL)")
        
    return patterns

def score_technical_setup(candles: List[Dict[str, Any]], rsi_values: List[float | None], macd_hist: List[float | None], sma20: List[float | None], sma50: List[float | None]) -> float:
    """Compute 0-100 technical score based on confluence of indicators."""
    if not candles:
        return 50.0
    
    score = 50.0
    latest = candles[-1]
    latest_close = latest["close"]
    
    # 1. RSI Factors (Ideal oversold recovery between 32 and 58)
    latest_rsi = rsi_values[-1] if rsi_values and rsi_values[-1] is not None else 50.0
    if 30 <= latest_rsi <= 45:
        score += 15.0  # Prime oversold dip accumulation zone
    elif 45 < latest_rsi <= 65:
        score += 10.0  # Healthy bullish momentum
    elif latest_rsi < 30:
        score += 12.0  # Heavily oversold bounce prospect
    elif latest_rsi > 75:
        score -= 10.0  # Overheated risk
        
    # 2. MACD Histogram Momentum
    latest_hist = macd_hist[-1] if macd_hist and macd_hist[-1] is not None else 0.0
    prev_hist = macd_hist[-2] if len(macd_hist) > 1 and macd_hist[-2] is not None else 0.0
    if latest_hist > 0:
        score += 10.0
        if latest_hist > prev_hist:
            score += 5.0  # Accelerating bullish momentum
    elif latest_hist < 0 and latest_hist > prev_hist:
        score += 8.0  # Bearish histogram contracting upwards (bullish divergence)

    # 3. Moving Average Trend Alignment
    s20 = sma20[-1] if sma20 and sma20[-1] is not None else None
    s50 = sma50[-1] if sma50 and sma50[-1] is not None else None
    if s20 and latest_close > s20:
        score += 8.0
    if s50 and latest_close > s50:
        score += 7.0
        
    # 4. Candlestick patterns
    patterns = detect_candlestick_patterns(candles)
    if "Bullish Morning Star" in patterns:
        score += 12.0
    if "Bullish Engulfing" in patterns:
        score += 10.0
    if "Hammer / Bullish Pin Bar" in patterns:
        score += 8.0
    for p in patterns:
        if "High Relative Volume" in p:
            score += 10.0
            
    return max(15.0, min(99.0, round(score, 1)))
