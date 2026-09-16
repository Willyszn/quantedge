from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class QuantSnapshotModel(Base):
    __tablename__ = "quant_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    timeframe: Mapped[str] = mapped_column(String(5))
    quant_score: Mapped[float] = mapped_column(Float)
    trend_score: Mapped[float] = mapped_column(Float)
    trend_direction: Mapped[str] = mapped_column(String(20))
    momentum_score: Mapped[float] = mapped_column(Float)
    momentum_direction: Mapped[str] = mapped_column(String(20))
    volatility_score: Mapped[float] = mapped_column(Float)
    volatility_regime: Mapped[str] = mapped_column(String(20))
    structure_score: Mapped[float] = mapped_column(Float)
    structure_direction: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
