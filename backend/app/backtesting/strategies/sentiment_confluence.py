import pandas as pd

from app.backtesting.strategies.base import BaseStrategy
from app.quant.momentum import compute_rsi

FAST_PERIOD = 20
SLOW_PERIOD = 50
RSI_PERIOD = 14


class SentimentConfluenceStrategy(BaseStrategy):
    """
    Named "Sentiment Confluence" to match the product's four supported
    strategies, but honestly: bar-by-bar historical sentiment isn't stored
    yet (SentimentObservation only carries a `published_at` timestamp, not
    a backfilled time series per instrument — see app/sentiment). Until
    that exists, this strategy approximates "confluence" using multiple
    independent price-derived signals (trend direction, momentum direction,
    and a volume confirmation) agreeing at once, which is the same
    "multiple independent factors align" idea sentiment confluence is
    named for. Swap `entry_signal` for a real historical-sentiment lookup
    once SentimentObservation history is persisted and queryable by bar.
    """

    name = "Sentiment Confluence"
    description = (
        "Enters when trend direction, momentum direction, and volume "
        "confirmation all align — a price-derived proxy for multi-factor "
        "confluence pending historical sentiment storage (see docstring)."
    )

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["fast_ma"] = out["close"].rolling(FAST_PERIOD).mean()
        out["slow_ma"] = out["close"].rolling(SLOW_PERIOD).mean()
        out["rsi"] = compute_rsi(out["close"], RSI_PERIOD)
        out["avg_volume"] = out["volume"].rolling(FAST_PERIOD).mean()
        return out

    def entry_signal(self, df: pd.DataFrame, i: int) -> str | None:
        if i < SLOW_PERIOD + 1:
            return None
        row = df.iloc[i]
        if pd.isna(row["slow_ma"]) or pd.isna(row["avg_volume"]):
            return None

        volume_confirmed = row["volume"] > row["avg_volume"] * 1.1
        if not volume_confirmed:
            return None

        trend_bullish = row["fast_ma"] > row["slow_ma"] and row["close"] > row["fast_ma"]
        trend_bearish = row["fast_ma"] < row["slow_ma"] and row["close"] < row["fast_ma"]

        if trend_bullish and row["rsi"] > 55:
            return "long"
        if trend_bearish and row["rsi"] < 45:
            return "short"
        return None
