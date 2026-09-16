from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


def to_camel(snake: str) -> str:
    first, *rest = snake.split("_")
    return first + "".join(word.capitalize() for word in rest)


class CamelModel(BaseModel):
    """Base for every response schema — the frontend's TypeScript contracts
    are camelCase, so every schema serializes as camelCase while staying
    snake_case (idiomatic) internally."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


AssetClass = Literal["forex", "metals", "index", "crypto"]
MarketStatus = Literal["open", "closed", "pre-market", "after-hours"]
Timeframe = Literal["1m", "5m", "15m", "1H", "4H", "1D"]


class MarketQuoteSchema(CamelModel):
    symbol: str
    name: str
    asset_class: AssetClass
    price: float
    change_percent: float
    change_absolute: float
    status: MarketStatus
    spark: list[float]
    updated_at: datetime


class CandleSchema(CamelModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketSeriesSchema(CamelModel):
    symbol: str
    timeframe: Timeframe
    candles: list[CandleSchema]


class MarketCapabilitiesSchema(CamelModel):
    supported_timeframes: list[Timeframe]


class InstrumentSchema(CamelModel):
    """Backing GET /instruments — see spec follow-up: the frontend still
    imports its instrument list from src/mocks/instruments.ts even with
    demo mode off. This endpoint is the intended future single source of
    truth; wiring the frontend to it is a follow-up, not a blocker for
    this backend build."""

    symbol: str
    name: str
    asset_class: AssetClass
    digits: int
    base_currency: str | None
    quote_currency: str
    minimum_price_increment: float
    supported_timeframes: list[Timeframe]
