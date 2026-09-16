import pandas as pd

from app.backtesting.strategies.base import BaseStrategy

FAST_PERIOD = 20
SLOW_PERIOD = 50


class TrendContinuationStrategy(BaseStrategy):
    name = "Trend Continuation"
    description = (
        "Requires the fast MA to already be on the trend side of the slow MA, then "
        "enters when price pulls back to the fast MA and closes back through it in "
        "the trend direction."
    )

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["fast_ma"] = out["close"].rolling(FAST_PERIOD).mean()
        out["slow_ma"] = out["close"].rolling(SLOW_PERIOD).mean()
        return out

    def entry_signal(self, df: pd.DataFrame, i: int) -> str | None:
        if i < SLOW_PERIOD + 1:
            return None
        row, prev = df.iloc[i], df.iloc[i - 1]
        if pd.isna(row["slow_ma"]) or pd.isna(prev["fast_ma"]):
            return None

        uptrend = row["fast_ma"] > row["slow_ma"]
        downtrend = row["fast_ma"] < row["slow_ma"]

        crossed_back_above = prev["close"] <= prev["fast_ma"] and row["close"] > row["fast_ma"]
        crossed_back_below = prev["close"] >= prev["fast_ma"] and row["close"] < row["fast_ma"]

        if uptrend and crossed_back_above:
            return "long"
        if downtrend and crossed_back_below:
            return "short"
        return None
