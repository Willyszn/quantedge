from dataclasses import dataclass

import pandas as pd

from app.core.scoring_config import VOLATILITY_CONFIG
from app.quant.scoring import bell_score, clamp


@dataclass
class VolatilityResult:
    score: float  # 0-100, favorability for trading (not raw magnitude)
    atr: float
    atr_percent_of_price: float
    regime: str  # "low" | "normal" | "elevated" | "extreme"
    expanding: bool


def compute_atr(df: pd.DataFrame, period: int) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    true_range = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()


def analyze_volatility(df: pd.DataFrame) -> VolatilityResult:
    """
    ATR expressed as a percentage of price classifies the volatility
    regime. The *score* isn't "higher volatility = better" — it favors
    "normal" volatility (enough movement to reach a target, not so much
    that stops become unreliable) using a bell curve centered on the
    boundary between the low and normal regimes.
    """
    period = VOLATILITY_CONFIG.ATR_PERIOD
    if len(df) < period + 2:
        return VolatilityResult(50.0, 0.0, 0.0, "normal", False)

    atr_series = compute_atr(df, period)
    current_atr = float(atr_series.iloc[-1])
    current_price = float(df["close"].iloc[-1])
    atr_percent = (current_atr / current_price) * 100 if current_price else 0.0

    cfg = VOLATILITY_CONFIG
    if atr_percent <= cfg.LOW_REGIME_MAX:
        regime = "low"
    elif atr_percent <= cfg.NORMAL_REGIME_MAX:
        regime = "normal"
    elif atr_percent <= cfg.ELEVATED_REGIME_MAX:
        regime = "elevated"
    else:
        regime = "extreme"

    expanding = False
    if len(atr_series) > period + 5:
        expanding = bool(current_atr > float(atr_series.iloc[-5]))

    ideal = (cfg.LOW_REGIME_MAX + cfg.NORMAL_REGIME_MAX) / 2
    tolerance = cfg.ELEVATED_REGIME_MAX
    score = clamp(bell_score(atr_percent, ideal, tolerance))

    return VolatilityResult(
        score=round(score, 1),
        atr=round(current_atr, 6),
        atr_percent_of_price=round(atr_percent, 3),
        regime=regime,
        expanding=expanding,
    )
