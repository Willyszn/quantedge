import pandas as pd

from app.market_data.validation import RawCandle


def candles_to_dataframe(candles: list[RawCandle]) -> pd.DataFrame:
    """
    Converts a validated candle list (oldest first) into a pandas DataFrame
    indexed by time, with float columns open/high/low/close/volume. Every
    quant calculation in app/quant/* takes this DataFrame as input, so the
    provider/storage layer and the analysis layer never mix concerns.
    """
    if not candles:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

    df = pd.DataFrame(
        {
            "time": [c.time for c in candles],
            "open": [c.open for c in candles],
            "high": [c.high for c in candles],
            "low": [c.low for c in candles],
            "close": [c.close for c in candles],
            "volume": [c.volume for c in candles],
        }
    )
    df = df.set_index("time").sort_index()
    return df
