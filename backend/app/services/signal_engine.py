"""
SignalEngine (spec sections 4, 17). The single place that combines the
independently-testable quant, sentiment, and risk engines into a complete,
explainable TradeSignal. Every number on the resulting object traces back
to a real calculation — see app/quant, app/sentiment, app/risk.
"""

import uuid
from datetime import UTC, datetime

from app.core.errors import DataUnavailableError, SymbolNotFoundError
from app.core.logging import get_logger
from app.market_data.provider_base import MarketDataProvider
from app.market_data.registry import get_instrument
from app.quant.snapshot import build_quant_snapshot
from app.quant.utils import candles_to_dataframe
from app.risk.engine import assess_risk
from app.sentiment.aggregation import SymbolSentimentResult, aggregate_sentiment
from app.sentiment.provider_base import SentimentProvider
from app.services.signal_domain import SignalScores, TradeSignal
from app.signals.confidence import compute_confidence
from app.signals.factors import build_factors, sentiment_score_from_split
from app.signals.narrative import build_narrative
from app.signals.rating import direction_for, rating_for

logger = get_logger(__name__)

MIN_CANDLES_REQUIRED = 60


class SignalEngine:
    def __init__(self, market_data: MarketDataProvider, sentiment: SentimentProvider):
        self.market_data = market_data
        self.sentiment_provider = sentiment

    async def generate_signal(self, symbol: str, timeframe: str = "1H") -> TradeSignal:
        instrument = get_instrument(symbol)
        if instrument is None:
            raise SymbolNotFoundError(f"Instrument {symbol} was not found.")

        candles = await self.market_data.get_candles(symbol, timeframe, count=200)
        if len(candles) < MIN_CANDLES_REQUIRED:
            raise DataUnavailableError(
                f"Not enough market data for {symbol} to generate a signal "
                f"({len(candles)}/{MIN_CANDLES_REQUIRED} candles available)."
            )

        df = candles_to_dataframe(candles)
        quant = build_quant_snapshot(df)

        observations = await self.sentiment_provider.get_observations(symbol)
        sentiment: SymbolSentimentResult = aggregate_sentiment(observations, symbol, datetime.now(UTC))
        sentiment_score = sentiment_score_from_split(sentiment.split)

        current_price = float(df["close"].iloc[-1])
        direction = direction_for(quant.dominant_direction)
        risk = assess_risk(direction, current_price, quant.volatility, instrument.digits)

        confidence = compute_confidence(quant.quant_score, sentiment_score, risk.risk_score)
        rating = rating_for(confidence, direction)

        factors = build_factors(quant.trend, quant.momentum, quant.volatility, quant.structure, sentiment, risk)
        narrative = build_narrative(symbol, direction, factors)

        generated_at = datetime.now(UTC)
        signal_id = f"sig-{symbol.lower()}-{int(generated_at.timestamp() * 1_000_000)}-{uuid.uuid4().hex[:6]}"

        signal = TradeSignal(
            id=signal_id,
            symbol=symbol,
            name=instrument.name,
            direction=direction,
            rating=rating,
            confidence=confidence,
            entry_low=risk.plan.entry_low,
            entry_high=risk.plan.entry_high,
            stop_loss=risk.plan.stop_loss,
            target=risk.plan.target,
            risk_reward_ratio=risk.plan.risk_reward_ratio,
            generated_at=generated_at,
            scores=SignalScores(
                quant=quant.quant_score,
                momentum=quant.momentum.score,
                trend=quant.trend.score,
                sentiment=sentiment_score,
                risk=risk.risk_score,
            ),
            factors=factors,
            narrative=narrative,
            decimals=instrument.digits,
        )

        logger.info(
            "signal_generated",
            extra={
                "event": "signal_generated",
                "symbol": symbol,
                "direction": direction,
                "rating": rating,
                "confidence": confidence,
            },
        )
        return signal
