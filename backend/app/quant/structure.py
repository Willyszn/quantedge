from dataclasses import dataclass

import pandas as pd

from app.core.scoring_config import TREND_CONFIG
from app.quant.scoring import clamp


@dataclass
class StructureResult:
    direction: str  # "bullish" | "bearish" | "neutral"
    score: float  # 0-100
    recent_high: float
    recent_low: float
    breakout: str | None  # "bullish-breakout" | "bearish-breakdown" | None
    distance_to_high_percent: float
    distance_to_low_percent: float


def analyze_structure(df: pd.DataFrame) -> StructureResult:
    """
    Looks at the most recent swing high/low over the lookback window and
    classifies structure by the pattern of highs and lows within it
    (higher-highs/higher-lows vs lower-highs/lower-lows), plus whether the
    latest close just broke outside the prior range. Structure quality
    (the score) rewards a clean, one-directional sequence of highs/lows
    over a choppy, overlapping one.
    """
    lookback = TREND_CONFIG.STRUCTURE_LOOKBACK
    if len(df) < lookback + 2:
        last_close = float(df["close"].iloc[-1]) if len(df) else 0.0
        return StructureResult("neutral", 50.0, last_close, last_close, None, 0.0, 0.0)

    window = df.iloc[-lookback:]
    prior_window = df.iloc[-lookback - 1 : -1]

    recent_high = float(window["high"].max())
    recent_low = float(window["low"].min())
    current_close = float(df["close"].iloc[-1])

    prior_high = float(prior_window["high"].max())
    prior_low = float(prior_window["low"].min())

    breakout = None
    if current_close > prior_high:
        breakout = "bullish-breakout"
    elif current_close < prior_low:
        breakout = "bearish-breakdown"

    # Split the window into halves and compare swing extremes to classify
    # higher-highs/higher-lows vs lower-highs/lower-lows.
    mid = len(window) // 2
    first_half, second_half = window.iloc[:mid], window.iloc[mid:]
    higher_highs = second_half["high"].max() > first_half["high"].max()
    higher_lows = second_half["low"].min() > first_half["low"].min()
    lower_highs = second_half["high"].max() < first_half["high"].max()
    lower_lows = second_half["low"].min() < first_half["low"].min()

    if higher_highs and higher_lows:
        direction = "bullish"
        quality = 100.0
    elif lower_highs and lower_lows:
        direction = "bearish"
        quality = 100.0
    elif higher_highs or lower_lows:
        direction = "bullish" if higher_highs else "bearish"
        quality = 55.0
    elif lower_highs or higher_lows:
        direction = "bearish" if lower_highs else "bullish"
        quality = 55.0
    else:
        direction = "neutral"
        quality = 35.0

    breakout_bonus = 15.0 if breakout else 0.0
    score = clamp(quality + breakout_bonus)

    return StructureResult(
        direction=direction,
        score=round(score, 1),
        recent_high=round(recent_high, 6),
        recent_low=round(recent_low, 6),
        breakout=breakout,
        distance_to_high_percent=round((recent_high - current_close) / current_close * 100, 3)
        if current_close
        else 0.0,
        distance_to_low_percent=round((current_close - recent_low) / current_close * 100, 3)
        if current_close
        else 0.0,
    )
