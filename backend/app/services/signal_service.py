from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import SymbolNotFoundError
from app.core.logging import get_logger
from app.core.redis_client import cache_get_json, cache_set_json
from app.market_data.registry import instrument_exists, list_instruments
from app.models.signal import SignalFactorModel, SignalModel, TradePlanModel
from app.schemas.signal import SignalFactorSchema, SignalScoreBreakdownSchema, TradeSignalSchema
from app.services.alert_service import AlertService
from app.services.signal_domain import TradeSignal
from app.services.signal_engine import SignalEngine
from app.signals.ranking import rank_primary

logger = get_logger(__name__)

SIGNAL_CACHE_TTL_SECONDS = 45
CONFIDENCE_ALERT_THRESHOLD = 6.0


def _domain_to_schema(signal: TradeSignal) -> TradeSignalSchema:
    return TradeSignalSchema(
        id=signal.id,
        symbol=signal.symbol,
        name=signal.name,
        direction=signal.direction,
        rating=signal.rating,
        confidence=signal.confidence,
        entry_low=signal.entry_low,
        entry_high=signal.entry_high,
        stop_loss=signal.stop_loss,
        target=signal.target,
        risk_reward_ratio=signal.risk_reward_ratio,
        generated_at=signal.generated_at,
        scores=SignalScoreBreakdownSchema(
            quant=signal.scores.quant,
            momentum=signal.scores.momentum,
            trend=signal.scores.trend,
            sentiment=signal.scores.sentiment,
            risk=signal.scores.risk,
        ),
        factors=[
            SignalFactorSchema(
                id=f.id,
                label=f.label,
                score=f.score,
                status=f.status,
                status_label=f.status_label,
                explanation=f.explanation,
            )
            for f in signal.factors
        ],
        narrative=signal.narrative,
        decimals=signal.decimals,
    )


class SignalService:
    def __init__(self, engine: SignalEngine, db: AsyncSession):
        self.engine = engine
        self.db = db
        self.alerts = AlertService(db)

    async def get_signal(self, symbol: str) -> TradeSignalSchema:
        symbol = symbol.upper()
        if not instrument_exists(symbol):
            raise SymbolNotFoundError(f"Instrument {symbol} was not found.")

        cache_key = f"signal:{symbol}"
        cached = await cache_get_json(cache_key)
        if cached is not None:
            return TradeSignalSchema.model_validate(cached)

        domain_signal = await self.engine.generate_signal(symbol)
        schema = _domain_to_schema(domain_signal)

        await cache_set_json(cache_key, schema.model_dump(mode="json", by_alias=True), SIGNAL_CACHE_TTL_SECONDS)
        await self._persist_signal(domain_signal)
        return schema

    async def get_signals(self) -> list[TradeSignalSchema]:
        signals = []
        for inst in list_instruments():
            try:
                signals.append(await self.get_signal(inst.canonical_symbol))
            except Exception as exc:  # a single symbol's failure shouldn't break the whole list
                logger.warning(
                    "signal_generation_failed",
                    extra={
                        "event": "signal_generation_failed",
                        "symbol": inst.canonical_symbol,
                        "reason": str(exc),
                    },
                )
        return sorted(signals, key=lambda s: s.confidence, reverse=True)

    async def get_primary_signal(self) -> TradeSignalSchema:
        signals = await self.get_signals()
        if not signals:
            raise SymbolNotFoundError("No signals are currently available.")

        best = rank_primary(
            signals,
            now=max(s.generated_at for s in signals),
            risk_score_getter=lambda s: s.scores.risk,
            generated_at_getter=lambda s: s.generated_at,
            confidence_getter=lambda s: s.confidence,
        )
        return best

    async def _persist_signal(self, signal: TradeSignal) -> None:
        try:
            existing = await self.db.get(SignalModel, signal.id)
            if existing is not None:
                return  # signal ids are timestamp-stamped; an existing row is already correct

            previous = await self._latest_prior_signal(signal.symbol, exclude_id=signal.id)

            model = SignalModel(
                id=signal.id,
                symbol=signal.symbol,
                name=signal.name,
                direction=signal.direction,
                rating=signal.rating,
                confidence=signal.confidence,
                quant_score=signal.scores.quant,
                momentum_score=signal.scores.momentum,
                trend_score=signal.scores.trend,
                sentiment_score=signal.scores.sentiment,
                risk_score=signal.scores.risk,
                narrative=signal.narrative,
                decimals=signal.decimals,
                generated_at=signal.generated_at,
            )
            model.factors = [
                SignalFactorModel(
                    factor_id=f.id,
                    label=f.label,
                    score=f.score,
                    status=f.status,
                    status_label=f.status_label,
                    explanation=f.explanation,
                )
                for f in signal.factors
            ]
            model.trade_plan = TradePlanModel(
                entry_low=signal.entry_low,
                entry_high=signal.entry_high,
                stop_loss=signal.stop_loss,
                target=signal.target,
                risk_reward_ratio=signal.risk_reward_ratio,
            )
            self.db.add(model)
            await self.db.commit()

            await self._raise_state_change_alerts(signal, previous)
        except Exception as exc:
            await self.db.rollback()
            logger.warning(
                "signal_persist_failed",
                extra={"event": "signal_persist_failed", "reason": str(exc)},
            )

    async def _latest_prior_signal(self, symbol: str, exclude_id: str) -> SignalModel | None:
        result = await self.db.execute(
            select(SignalModel)
            .where(SignalModel.symbol == symbol, SignalModel.id != exclude_id)
            .order_by(SignalModel.generated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _raise_state_change_alerts(self, signal: TradeSignal, previous: SignalModel | None) -> None:
        if previous is None:
            await self.alerts.create_alert(
                "new-signal",
                "New signal",
                f"A new {signal.rating.replace('-', ' ')} signal was generated for {signal.symbol}.",
                signal.symbol,
            )
            return

        confidence_delta = signal.confidence - previous.confidence
        if confidence_delta >= CONFIDENCE_ALERT_THRESHOLD:
            await self.alerts.create_alert(
                "confidence-up",
                "Confidence increased",
                f"{signal.symbol} confidence rose from {previous.confidence:.0f}% "
                f"to {signal.confidence:.0f}%.",
                signal.symbol,
            )
        elif confidence_delta <= -CONFIDENCE_ALERT_THRESHOLD:
            await self.alerts.create_alert(
                "confidence-down",
                "Confidence decreased",
                f"{signal.symbol} confidence fell from {previous.confidence:.0f}% "
                f"to {signal.confidence:.0f}%.",
                signal.symbol,
            )

        prev_risk_factor = next((f for f in previous.factors if f.factor_id == "risk-conditions"), None)
        new_risk_factor = next((f for f in signal.factors if f.id == "risk-conditions"), None)
        if prev_risk_factor and new_risk_factor and prev_risk_factor.status != new_risk_factor.status:
            await self.alerts.create_alert(
                "risk-change",
                "Risk condition changed",
                f"Risk conditions for {signal.symbol} shifted from "
                f"{prev_risk_factor.status} to {new_risk_factor.status}.",
                signal.symbol,
            )

        prev_sentiment_factor = next((f for f in previous.factors if f.factor_id == "sentiment-factor"), None)
        new_sentiment_factor = next((f for f in signal.factors if f.id == "sentiment-factor"), None)
        if (
            prev_sentiment_factor
            and new_sentiment_factor
            and prev_sentiment_factor.status != new_sentiment_factor.status
        ):
            await self.alerts.create_alert(
                "sentiment-change",
                "Sentiment changed",
                f"Aggregated sentiment on {signal.symbol} moved from "
                f"{prev_sentiment_factor.status} to {new_sentiment_factor.status}.",
                signal.symbol,
            )
