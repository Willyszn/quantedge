from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import SymbolNotFoundError
from app.core.logging import get_logger
from app.core.redis_client import cache_get_json, cache_set_json
from app.market_data.registry import instrument_exists, list_instruments
from app.models.sentiment import SentimentObservationModel
from app.schemas.sentiment import (
    SentimentSourceSchema,
    SentimentSplitSchema,
    SentimentTimelinePointSchema,
    SymbolSentimentSchema,
)
from app.sentiment.aggregation import SymbolSentimentResult, aggregate_sentiment
from app.sentiment.provider_base import SentimentObservation, SentimentProvider

logger = get_logger(__name__)

SENTIMENT_CACHE_TTL_SECONDS = 60


def _result_to_schema(result: SymbolSentimentResult) -> SymbolSentimentSchema:
    return SymbolSentimentSchema(
        symbol=result.symbol,
        split=SentimentSplitSchema(
            bullish=result.split.bullish, neutral=result.split.neutral, bearish=result.split.bearish
        ),
        sources=[
            SentimentSourceSchema(
                id=s.id,
                type=s.type.value,
                label=s.label,
                sentiment=s.sentiment,
                confidence=s.confidence,
                contribution_percent=s.contribution_percent,
                updated_at=s.updated_at,
            )
            for s in result.sources
        ],
        timeline=[
            SentimentTimelinePointSchema(time=t.time, label=t.label, score=t.score) for t in result.timeline
        ],
    )


class SentimentService:
    def __init__(self, provider: SentimentProvider, db: AsyncSession):
        self.provider = provider
        self.db = db

    async def get_symbol_sentiment(self, symbol: str) -> SymbolSentimentSchema:
        symbol = symbol.upper()
        if not instrument_exists(symbol):
            raise SymbolNotFoundError(f"Instrument {symbol} was not found.")
        return await self._get_and_cache(symbol)

    async def get_market_sentiment(self) -> SymbolSentimentSchema:
        """
        Aggregate sentiment across every observation for every supported
        instrument, reported under the pseudo-symbol "MARKET" — mirrors the
        frontend's "Overall Market" scope.
        """
        cache_key = "sentiment:MARKET"
        cached = await cache_get_json(cache_key)
        if cached is not None:
            return SymbolSentimentSchema.model_validate(cached)

        all_observations: list[SentimentObservation] = []
        for inst in list_instruments():
            all_observations.extend(await self.provider.get_observations(inst.canonical_symbol))

        result = aggregate_sentiment(all_observations, "MARKET", datetime.now(UTC))
        schema = _result_to_schema(result)
        await cache_set_json(cache_key, schema.model_dump(mode="json", by_alias=True), SENTIMENT_CACHE_TTL_SECONDS)
        await self._persist_observations(all_observations)
        return schema

    async def _get_and_cache(self, symbol: str) -> SymbolSentimentSchema:
        cache_key = f"sentiment:{symbol}"
        cached = await cache_get_json(cache_key)
        if cached is not None:
            return SymbolSentimentSchema.model_validate(cached)

        observations = await self.provider.get_observations(symbol)
        result = aggregate_sentiment(observations, symbol, datetime.now(UTC))
        schema = _result_to_schema(result)

        await cache_set_json(cache_key, schema.model_dump(mode="json", by_alias=True), SENTIMENT_CACHE_TTL_SECONDS)
        await self._persist_observations(observations)
        return schema

    async def _persist_observations(self, observations: list[SentimentObservation]) -> None:
        try:
            for obs in observations:
                existing = await self.db.get(SentimentObservationModel, obs.id)
                if existing is not None:
                    continue
                self.db.add(
                    SentimentObservationModel(
                        id=obs.id,
                        headline=obs.headline,
                        source_name=obs.source_name,
                        source_type=obs.source_type.value,
                        published_at=obs.published_at,
                        entities=",".join(obs.entities),
                        raw_sentiment_score=obs.raw_sentiment_score,
                        confidence=obs.confidence,
                    )
                )
            await self.db.commit()
        except Exception as exc:
            await self.db.rollback()
            logger.warning(
                "sentiment_persist_failed",
                extra={"event": "sentiment_persist_failed", "reason": str(exc)},
            )
