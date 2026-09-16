"""
MockMarketDataProvider (spec section 5).

Used when MARKET_DATA_PROVIDER=mock (the default for local development).
Generates deterministic, seeded OHLC series and quotes — stable within a
given day so repeated requests don't jitter — and is always reported with
DataFreshness.SIMULATED so nothing downstream can mistake it for a live
feed. This is explicitly a development/demo data source, never used to
fabricate the *analysis* layer: the quant/signal/risk engines run the same
real calculations against whatever candles a provider returns, mock or not.
"""

import hashlib
import random
from datetime import UTC, datetime, timedelta

from app.market_data.provider_base import (
    DataFreshness,
    MarketDataProvider,
    MarketStatus,
    ProviderQuote,
)
from app.market_data.registry import Timeframe, get_instrument
from app.market_data.validation import RawCandle

TIMEFRAME_MINUTES = {"1m": 1, "5m": 5, "15m": 15, "1H": 60, "4H": 240, "1D": 1440}


def _seeded_random(*parts: str) -> random.Random:
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


class MockMarketDataProvider(MarketDataProvider):
    name = "mock"

    async def is_healthy(self) -> bool:
        return True

    async def get_instrument_info(self, symbol: str) -> dict | None:
        inst = get_instrument(symbol)
        if inst is None:
            return None
        return {
            "canonicalSymbol": inst.canonical_symbol,
            "name": inst.name,
            "assetClass": inst.asset_class.value,
            "digits": inst.digits,
            "baseCurrency": inst.base_currency,
            "quoteCurrency": inst.quote_currency,
            "minimumPriceIncrement": inst.minimum_price_increment,
        }

    async def get_supported_timeframes(self, symbol: str) -> list[Timeframe]:
        inst = get_instrument(symbol)
        return inst.supported_timeframes if inst else []

    async def get_quote(self, symbol: str) -> ProviderQuote | None:
        inst = get_instrument(symbol)
        if inst is None:
            return None

        day_key = datetime.now(UTC).strftime("%Y-%m-%d")
        rand = _seeded_random(inst.canonical_symbol, "quote", day_key)

        base_price = self._base_price(inst.canonical_symbol)
        change_percent = round(rand.uniform(-1.8, 1.8), 2)
        price = round(base_price * (1 + change_percent / 100), inst.digits)

        spark: list[float] = []
        value = base_price * rand.uniform(0.985, 1.015)
        for _ in range(24):
            value += value * rand.uniform(-0.003, 0.0032)
            spark.append(round(value, inst.digits + 2))

        status = MarketStatus.OPEN
        if inst.asset_class.value != "crypto":
            roll = rand.random()
            if roll > 0.85:
                status = MarketStatus.CLOSED
            elif roll > 0.75:
                status = MarketStatus.PRE_MARKET

        return ProviderQuote(
            symbol=inst.canonical_symbol,
            price=price,
            status=status,
            timestamp=datetime.now(UTC),
            freshness=DataFreshness.SIMULATED,
            spark=spark,
        )

    async def get_quotes(self, symbols: list[str]) -> list[ProviderQuote]:
        results = []
        for symbol in symbols:
            quote = await self.get_quote(symbol)
            if quote is not None:
                results.append(quote)
        return results

    async def get_candles(self, symbol: str, timeframe: str, count: int = 200) -> list[RawCandle]:
        inst = get_instrument(symbol)
        if inst is None or timeframe not in TIMEFRAME_MINUTES:
            return []

        rand = _seeded_random(inst.canonical_symbol, timeframe, "series")
        minutes = TIMEFRAME_MINUTES[timeframe]
        base_price = self._base_price(inst.canonical_symbol)
        price = base_price * rand.uniform(0.97, 1.03)
        now = datetime.now(UTC)

        candles: list[RawCandle] = []
        for i in range(count - 1, -1, -1):
            drift = rand.uniform(-0.0025, 0.0027)
            open_price = price
            close_price = open_price * (1 + drift)
            high = max(open_price, close_price) * (1 + rand.uniform(0, 0.0012))
            low = min(open_price, close_price) * (1 - rand.uniform(0, 0.0012))
            volume = round(rand.uniform(800, 6200))
            time = now - timedelta(minutes=i * minutes)

            candles.append(
                RawCandle(
                    time=time,
                    open=round(open_price, inst.digits),
                    high=round(high, inst.digits),
                    low=round(low, inst.digits),
                    close=round(close_price, inst.digits),
                    volume=volume,
                )
            )
            price = close_price

        return candles

    async def get_historical_candles(
        self, symbol: str, timeframe: str, start: datetime, end: datetime
    ) -> list[RawCandle]:
        """
        Deterministic candle generation across an arbitrary historical
        date range — used by the backtest engine. Seeded on the symbol,
        timeframe, and requested range so a given backtest configuration
        always simulates against the same synthetic history (no jitter
        between repeated runs with identical inputs).
        """
        inst = get_instrument(symbol)
        if inst is None or timeframe not in TIMEFRAME_MINUTES:
            return []

        minutes = TIMEFRAME_MINUTES[timeframe]
        total_minutes = max(0, int((end - start).total_seconds() // 60))
        count = min(total_minutes // minutes, 20000) if minutes else 0
        if count <= 0:
            return []

        rand = _seeded_random(inst.canonical_symbol, timeframe, start.isoformat(), end.isoformat())
        base_price = self._base_price(inst.canonical_symbol)
        price = base_price * rand.uniform(0.9, 1.1)

        candles: list[RawCandle] = []
        for i in range(count):
            drift = rand.uniform(-0.0025, 0.0027)
            open_price = price
            close_price = open_price * (1 + drift)
            high = max(open_price, close_price) * (1 + rand.uniform(0, 0.0012))
            low = min(open_price, close_price) * (1 - rand.uniform(0, 0.0012))
            volume = round(rand.uniform(800, 6200))
            time = start + timedelta(minutes=i * minutes)

            candles.append(
                RawCandle(
                    time=time,
                    open=round(open_price, inst.digits),
                    high=round(high, inst.digits),
                    low=round(low, inst.digits),
                    close=round(close_price, inst.digits),
                    volume=volume,
                )
            )
            price = close_price

        return candles

    @staticmethod
    def _base_price(symbol: str) -> float:
        base_prices = {
            "GBPUSD": 1.3452,
            "USDJPY": 149.82,
            "EURUSD": 1.0812,
            "GBPJPY": 201.45,
            "XAUUSD": 2419.6,
            "XAGUSD": 28.94,
            "US500": 5614.3,
            "US100": 19842.0,
            "BTCUSD": 64230.0,
            "ETHUSD": 3142.5,
        }
        return base_prices.get(symbol, 100.0)
