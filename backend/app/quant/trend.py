from dataclasses import dataclass

import pandas as pd

from app.core.scoring_config import TREND_CONFIG
from app.quant.scoring import clamp, scale_to_score


@dataclass
class TrendResult:
    direction: str  # "bullish" | "bearish" | "neutral"
    score: float  # 0-100
    fast_ma: float
    slow_ma: float
    ma_spread_percent: float
    price_above_fast_ma: bool
    consistency_percent: float  # % of lookback window price spent on the trend side of slow MA


def analyze_trend(df: pd.DataFrame) -> TrendResult:
    """
    Trend direction comes from the fast/slow moving-average relationship and
    where price sits relative to both. Trend *strength* (the score) blends
    how wide that MA spread is (a wide, expanding spread means a decisive
    trend) with how consistently price has respected the trend over the
    lookback window (a trend that keeps getting violated is a weak one even
    if the MAs are currently separated).
    """
    close = df["close"]
    fast_period = TREND_CONFIG.FAST_MA_PERIOD
    slow_period = TREND_CONFIG.SLOW_MA_PERIOD

    if len(close) < slow_period + 1:
        # Not enough history for a reliable read — report neutral rather
        # than guessing.
        last_price = float(close.iloc[-1]) if len(close) else 0.0
        return TrendResult("neutral", 50.0, last_price, last_price, 0.0, True, 50.0)

    fast_ma = close.rolling(fast_period).mean()
    slow_ma = close.rolling(slow_period).mean()

    current_fast = float(fast_ma.iloc[-1])
    current_slow = float(slow_ma.iloc[-1])
    current_price = float(close.iloc[-1])

    spread_percent = ((current_fast - current_slow) / current_slow) * 100 if current_slow else 0.0

    if current_fast > current_slow and current_price >= current_fast:
        direction = "bullish"
    elif current_fast < current_slow and current_price <= current_fast:
        direction = "bearish"
    else:
        direction = "neutral"

    lookback = min(TREND_CONFIG.STRUCTURE_LOOKBACK, len(close) - slow_period)
    window_price = close.iloc[-lookback:]
    window_slow = slow_ma.iloc[-lookback:]
    if direction == "bullish":
        consistency = float((window_price > window_slow).mean() * 100)
    elif direction == "bearish":
        consistency = float((window_price < window_slow).mean() * 100)
    else:
        consistency = 50.0

    spread_score = scale_to_score(abs(spread_percent), 0.0, 2.5)
    score = clamp(0.6 * spread_score + 0.4 * consistency)
    if direction == "neutral":
        score = clamp(score * 0.6 + 20)  # neutral trends cap out lower

    return TrendResult(
        direction=direction,
        score=round(float(score), 1),
        fast_ma=round(current_fast, 6),
        slow_ma=round(current_slow, 6),
        ma_spread_percent=round(spread_percent, 3),
        price_above_fast_ma=current_price >= current_fast,
        consistency_percent=round(consistency, 1),
    )
