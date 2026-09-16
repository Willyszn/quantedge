import pandas as pd

from app.backtesting.strategies.base import BaseStrategy
from app.quant.momentum import compute_rsi

BAND_PERIOD = 20
BAND_STD_MULTIPLIER = 2.0
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70


class MeanReversionStrategy(BaseStrategy):
    name = "Mean Reversion"
    description = (
        "Enters long when price is oversold (RSI < 30) and trading below its lower "
        "band; enters short when overbought (RSI > 70) and above its upper band."
    )

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        mean = out["close"].rolling(BAND_PERIOD).mean()
        std = out["close"].rolling(BAND_PERIOD).std()
        out["band_mid"] = mean
        out["band_upper"] = mean + BAND_STD_MULTIPLIER * std
        out["band_lower"] = mean - BAND_STD_MULTIPLIER * std
        out["rsi"] = compute_rsi(out["close"], RSI_PERIOD)
        return out

    def entry_signal(self, df: pd.DataFrame, i: int) -> str | None:
        if i < BAND_PERIOD + RSI_PERIOD:
            return None
        row = df.iloc[i]
        if pd.isna(row["band_lower"]) or pd.isna(row["rsi"]):
            return None

        if row["rsi"] < RSI_OVERSOLD and row["close"] < row["band_lower"]:
            return "long"
        if row["rsi"] > RSI_OVERBOUGHT and row["close"] > row["band_upper"]:
            return "short"
        return None
