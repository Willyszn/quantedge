"""
AlertService (spec section 34). Alerts are only ever created in response to
a real, detected state change — see the call sites in SignalService
(new-signal / confidence-up / confidence-down / risk-change /
sentiment-change, detected by comparing a freshly generated signal against
the most recently persisted one for that symbol) and BacktestService
(backtest-complete, fired the moment a real backtest run finishes).

Note: entry-zone alerts (price crossing into a signal's proposed entry
zone) genuinely need two consecutive price observations over time to detect
a *crossing* rather than a static state — that's a background-job/scheduler
concern (spec section 39, Phase 8), not something a single request/response
cycle can honestly produce. Left as a documented gap rather than faked here.
"""

import uuid
from datetime import UTC, datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.alert import AlertModel
from app.schemas.alert import AlertItemSchema, AlertType

logger = get_logger(__name__)


def _to_schema(model: AlertModel) -> AlertItemSchema:
    return AlertItemSchema(
        id=model.id,
        # AlertModel.type is a plain DB text column — cast at this one
        # boundary rather than threading a Literal through SQLAlchemy's
        # Mapped[] typing. Every write path (create_alert below) only ever
        # passes a valid AlertType, so this reflects a real invariant.
        type=cast(AlertType, model.type),
        title=model.title,
        description=model.description,
        symbol=model.symbol,
        created_at=model.created_at,
        read=model.read,
    )


class AlertService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_alerts(self, limit: int = 50) -> list[AlertItemSchema]:
        result = await self.db.execute(select(AlertModel).order_by(AlertModel.created_at.desc()).limit(limit))
        return [_to_schema(m) for m in result.scalars().all()]

    async def create_alert(
        self, alert_type: AlertType, title: str, description: str, symbol: str | None = None
    ) -> None:
        try:
            model = AlertModel(
                id=f"alert-{uuid.uuid4().hex[:12]}",
                type=alert_type,
                title=title,
                description=description,
                symbol=symbol,
                created_at=datetime.now(UTC),
                read=False,
            )
            self.db.add(model)
            await self.db.commit()
        except Exception as exc:
            await self.db.rollback()
            logger.warning("alert_persist_failed", extra={"event": "alert_persist_failed", "reason": str(exc)})
