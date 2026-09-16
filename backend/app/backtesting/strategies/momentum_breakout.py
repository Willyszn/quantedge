import pandas as pd

from app.backtesting.strategies.base import BaseStrategy
from app.quant.momentum import compute_rsi

BREAKOUT_LOOKBACK = 20
RSI_PERIOD = 14


class MomentumBreakoutStrategy(BaseStrategy):
    name = "Momentum Breakout"
    description = (
        "Enters long when price closes above its prior N-bar high with RSI "
        "confirming bullish momentum; enters short on the mirrored breakdown."
    )

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        # shift(1) so the rolling high/low excludes the current (not-yet-closed) bar.
        out["prior_high"] = out["high"].rolling(BREAKOUT_LOOKBACK).max().shift(1)
        out["prior_low"] = out["low"].rolling(BREAKOUT_LOOKBACK).min().shift(1)
        out["rsi"] = compute_rsi(out["close"], RSI_PERIOD)
        return out

    def entry_signal(self, df: pd.DataFrame, i: int) -> str | None:
        if i < BREAKOUT_LOOKBACK + RSI_PERIOD:
            return None
        row = df.iloc[i]
        if pd.isna(row["prior_high"]) or pd.isna(row["rsi"]):
            return None

        if row["close"] > row["prior_high"] and row["rsi"] > 55:
            return "long"
        if row["close"] < row["prior_low"] and row["rsi"] < 45:
            return "short"
        return None
