from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SignalModel(Base):
    __tablename__ = "signals"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(String(120))
    direction: Mapped[str] = mapped_column(String(10))
    rating: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[float] = mapped_column(Float)

    quant_score: Mapped[float] = mapped_column(Float)
    momentum_score: Mapped[float] = mapped_column(Float)
    trend_score: Mapped[float] = mapped_column(Float)
    sentiment_score: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[float] = mapped_column(Float)

    narrative: Mapped[str] = mapped_column(String(2000))
    decimals: Mapped[int]
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    factors: Mapped[list["SignalFactorModel"]] = relationship(
        back_populates="signal", cascade="all, delete-orphan"
    )
    trade_plan: Mapped["TradePlanModel"] = relationship(
        back_populates="signal", cascade="all, delete-orphan", uselist=False
    )


class SignalFactorModel(Base):
    __tablename__ = "signal_factors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    signal_id: Mapped[str] = mapped_column(ForeignKey("signals.id"))
    factor_id: Mapped[str] = mapped_column(String(40))
    label: Mapped[str] = mapped_column(String(80))
    score: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20))
    status_label: Mapped[str] = mapped_column(String(40))
    explanation: Mapped[str] = mapped_column(String(500))

    signal: Mapped["SignalModel"] = relationship(back_populates="factors")


class TradePlanModel(Base):
    __tablename__ = "trade_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    signal_id: Mapped[str] = mapped_column(ForeignKey("signals.id"), unique=True)
    entry_low: Mapped[float] = mapped_column(Float)
    entry_high: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float] = mapped_column(Float)
    target: Mapped[float] = mapped_column(Float)
    risk_reward_ratio: Mapped[float] = mapped_column(Float)

    signal: Mapped["SignalModel"] = relationship(back_populates="trade_plan")
