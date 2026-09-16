from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PerformanceSnapshotModel(Base):
    """
    A periodic rollup of portfolio-level performance, computed from
    BacktestTradeModel rows (spec section 33). Recomputed by the
    performance aggregation job/service rather than mutated in place, so
    each row is an immutable point-in-time snapshot for the equity curve.
    """

    __tablename__ = "performance_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    equity: Mapped[float] = mapped_column(Float)
    drawdown_percent: Mapped[float] = mapped_column(Float)
    scope: Mapped[str] = mapped_column(String(20), default="portfolio")
