"""
MarketDataService (spec section 4). The only thing API routes talk to for
market data — they never call a provider directly. Handles caching (Redis)
and best-effort persistence (Postgres) around whatever MarketDataProvider is
configured.
"""

import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import SymbolNotFoundError
from app.core.logging import get_logger
from app.core.redis_client import cache_get_json, cache_set_json
from app.market_data.provider_base import MarketDataProvider, ProviderQuote
from app.market_data.registry import Timeframe, get_instrument, instrument_exists, list_instruments
from app.market_data.validation import RawCandle
from app.models.market import MarketQuoteModel
from app.schemas.market import (
    CandleSchema,
    MarketCapabilitiesSchema,
    MarketQuoteSchema,
    MarketSeriesSchema,
)

logger = get_logger(__name__)

QUOTE_CACHE_TTL_SECONDS = 12
QUOTES_CACHE_KEY = "market:quotes:all"


def _quote_to_schema(quote: ProviderQuote) -> MarketQuoteSchema:
    instrument = get_instrument(quote.symbol)
    return MarketQuoteSchema(
        symbol=quote.symbol,
        name=instrument.name if instrument else quote.symbol,
        asset_class=instrument.asset_class.value if instrument else "forex",
        price=quote.price,
        change_percent=round(((quote.price - _reference_price(quote)) / _reference_price(quote)) * 100, 2)
        if _reference_price(quote)
        else 0.0,
        change_absolute=round(quote.price - _reference_price(quote), 6),
        status=quote.status.value,
        spark=quote.spark,
        updated_at=quote.timestamp,
    )


def _reference_price(quote: ProviderQuote) -> float:
    # First spark value approximates the period-open reference price for
    # change% / change-absolute when the provider doesn't supply one
    # directly (as MockMarketDataProvider doesn't track a broker day-open).
    return quote.spark[0] if quote.spark else quote.price


class MarketDataService:
    def __init__(self, provider: MarketDataProvider, db: AsyncSession):
        self.provider = provider
        self.db = db

    async def list_instruments_response(self):
        return list_instruments()

    async def get_quotes(self) -> list[MarketQuoteSchema]:
        cached = await cache_get_json(QUOTES_CACHE_KEY)
        if cached is not None:
            return [MarketQuoteSchema.model_validate(item) for item in cached]

        symbols = [inst.canonical_symbol for inst in list_instruments()]
        provider_quotes = await self.provider.get_quotes(symbols)
        schemas = [_quote_to_schema(q) for q in provider_quotes]

        await cache_set_json(
            QUOTES_CACHE_KEY,
            [s.model_dump(mode="json", by_alias=True) for s in schemas],
            QUOTE_CACHE_TTL_SECONDS,
        )
        await self._persist_quotes(provider_quotes)
        return schemas

    async def get_quote(self, symbol: str) -> MarketQuoteSchema:
        symbol = symbol.upper()
        if not instrument_exists(symbol):
            raise SymbolNotFoundError(f"Instrument {symbol} was not found.")

        cache_key = f"market:quote:{symbol}"
        cached = await cache_get_json(cache_key)
        if cached is not None:
            return MarketQuoteSchema.model_validate(cached)

        quote = await self.provider.get_quote(symbol)
        if quote is None:
            raise SymbolNotFoundError(f"Instrument {symbol} was not found.")

        schema = _quote_to_schema(quote)
        await cache_set_json(cache_key, schema.model_dump(mode="json", by_alias=True), QUOTE_CACHE_TTL_SECONDS)
        await self._persist_quotes([quote])
        return schema

    async def get_series(self, symbol: str, timeframe: Timeframe) -> MarketSeriesSchema:
        symbol = symbol.upper()
        instrument = get_instrument(symbol)
        if instrument is None:
            raise SymbolNotFoundError(f"Instrument {symbol} was not found.")

        candles: list[RawCandle] = await self.provider.get_candles(symbol, timeframe, count=200)
        return MarketSeriesSchema(
            symbol=symbol,
            timeframe=timeframe,
            candles=[
                CandleSchema(time=c.time, open=c.open, high=c.high, low=c.low, close=c.close, volume=c.volume)
                for c in candles
            ],
        )

    async def get_capabilities(self, symbol: str) -> MarketCapabilitiesSchema:
        symbol = symbol.upper()
        instrument = get_instrument(symbol)
        if instrument is None:
            raise SymbolNotFoundError(f"Instrument {symbol} was not found.")
        timeframes = await self.provider.get_supported_timeframes(symbol)
        return MarketCapabilitiesSchema(supported_timeframes=timeframes)

    async def _persist_quotes(self, quotes: list[ProviderQuote]) -> None:
        try:
            for quote in quotes:
                existing = await self.db.get(MarketQuoteModel, quote.symbol)
                reference = _reference_price(quote)
                change_percent = ((quote.price - reference) / reference * 100) if reference else 0.0
                if existing:
                    existing.price = quote.price
                    existing.change_percent = round(change_percent, 2)
                    existing.change_absolute = round(quote.price - reference, 6)
                    existing.status = quote.status.value
                    existing.spark = json.dumps(quote.spark)
                    existing.freshness = quote.freshness.value
                    existing.updated_at = quote.timestamp
                else:
                    self.db.add(
                        MarketQuoteModel(
                            symbol=quote.symbol,
                            price=quote.price,
                            change_percent=round(change_percent, 2),
                            change_absolute=round(quote.price - reference, 6),
                            status=quote.status.value,
                            spark=json.dumps(quote.spark),
                            freshness=quote.freshness.value,
                            updated_at=quote.timestamp,
                        )
                    )
            await self.db.commit()
        except Exception as exc:  # persistence is best-effort, never breaks a read
            await self.db.rollback()
            logger.warning("quote_persist_failed", extra={"event": "quote_persist_failed", "reason": str(exc)})
