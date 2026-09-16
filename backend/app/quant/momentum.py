from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.core.scoring_config import MOMENTUM_CONFIG
from app.quant.scoring import clamp, scale_to_score


@dataclass
class MomentumResult:
    direction: str  # "bullish" | "bearish" | "neutral"
    score: float  # 0-100
    rsi: float
    rate_of_change_percent: float
    accelerating: bool
    strength_label: str  # "Strong" | "Moderate" | "Weak"


def compute_rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    # avg_loss == 0 means every recent bar gained (or was flat) — RSI should
    # read as maximally overbought (100), not neutral. The previous
    # implementation divided by NaN in this case and silently fell back to
    # 50, which is the opposite of correct on a clean, strong uptrend.
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.where(avg_loss != 0, other=100.0)
    rsi = rsi.where(~((avg_loss == 0) & (avg_gain == 0)), other=50.0)
    return rsi.fillna(50.0)


def analyze_momentum(df: pd.DataFrame) -> MomentumResult:
    """
    RSI captures overbought/oversold pressure; rate of change captures raw
    velocity. The momentum score rewards RSI that's decisively away from 50
    in one direction *and* a meaningful rate of change in that same
    direction — RSI alone can be misleading in a slow grind, and ROC alone
    ignores overextension.
    """
    close = df["close"]
    period = MOMENTUM_CONFIG.RSI_PERIOD
    roc_period = MOMENTUM_CONFIG.ROC_PERIOD

    if len(close) < period + 2:
        return MomentumResult("neutral", 50.0, 50.0, 0.0, False, "Weak")

    rsi_series = compute_rsi(close, period)
    current_rsi = float(rsi_series.iloc[-1])

    if len(close) > roc_period:
        roc = ((close.iloc[-1] - close.iloc[-roc_period - 1]) / close.iloc[-roc_period - 1]) * 100
    else:
        roc = 0.0
    roc = float(roc)

    # Acceleration: is the most recent ROC larger in magnitude than the
    # prior one, in the same direction?
    accelerating = False
    if len(close) > roc_period * 2:
        prior_roc = (
            (close.iloc[-roc_period - 1] - close.iloc[-2 * roc_period - 1]) / close.iloc[-2 * roc_period - 1]
        ) * 100
        accelerating = (roc > 0 and roc > float(prior_roc)) or (roc < 0 and roc < float(prior_roc))

    rsi_distance = abs(current_rsi - 50)
    if current_rsi > 55:
        direction = "bullish"
    elif current_rsi < 45:
        direction = "bearish"
    else:
        direction = "neutral"

    rsi_score = scale_to_score(rsi_distance, 0, 35)
    roc_score = scale_to_score(abs(roc), 0, 1.5)
    score = clamp(0.55 * rsi_score + 0.45 * roc_score)
    if accelerating:
        score = clamp(score + 6)

    if score >= 70:
        strength_label = "Strong"
    elif score >= 45:
        strength_label = "Moderate"
    else:
        strength_label = "Weak"

    return MomentumResult(
        direction=direction,
        score=round(score, 1),
        rsi=round(current_rsi, 1),
        rate_of_change_percent=round(roc, 3),
        accelerating=accelerating,
        strength_label=strength_label,
    )
