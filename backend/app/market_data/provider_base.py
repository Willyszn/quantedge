"""
Provider abstraction (spec section 5). Every service that needs market data
depends on this interface, never on a concrete provider. Swapping from
MockMarketDataProvider to MT5MarketDataProvider — or adding a third
provider later — is a one-line change in app/api/dependencies.py.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.market_data.registry import Timeframe
from app.market_data.validation import RawCandle


class MarketStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    PRE_MARKET = "pre-market"
    AFTER_HOURS = "after-hours"


class DataFreshness(StrEnum):
    """Spec section 51 — every quote must be honest about how fresh it is."""

    LIVE = "live"
    DELAYED = "delayed"
    STALE = "stale"
    UNAVAILABLE = "unavailable"
    SIMULATED = "simulated"  # MockMarketDataProvider only — never a real feed


@dataclass
class ProviderQuote:
    symbol: str
    price: float
    status: MarketStatus
    timestamp: datetime
    freshness: DataFreshness
    spark: list[float]


class MarketDataProvider(ABC):
    """Interface every concrete market-data provider must implement."""

    name: str

    @abstractmethod
    async def get_quote(self, symbol: str) -> ProviderQuote | None: ...

    @abstractmethod
    async def get_quotes(self, symbols: list[str]) -> list[ProviderQuote]: ...

    @abstractmethod
    async def get_candles(self, symbol: str, timeframe: str, count: int = 200) -> list[RawCandle]: ...

    @abstractmethod
    async def get_historical_candles(
        self, symbol: str, timeframe: str, start: datetime, end: datetime
    ) -> list[RawCandle]: ...

    @abstractmethod
    async def get_supported_timeframes(self, symbol: str) -> list[Timeframe]: ...

    @abstractmethod
    async def get_instrument_info(self, symbol: str) -> dict | None: ...

    @abstractmethod
    async def is_healthy(self) -> bool: ...
