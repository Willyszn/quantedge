from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BacktestModel(Base):
    __tablename__ = "backtests"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    strategy: Mapped[str] = mapped_column(String(60))
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    initial_capital: Mapped[float] = mapped_column(Float)
    risk_per_trade_percent: Mapped[float] = mapped_column(Float)
    slippage_bps: Mapped[float] = mapped_column(Float)
    commission_bps: Mapped[float] = mapped_column(Float)

    total_return_percent: Mapped[float] = mapped_column(Float)
    win_rate: Mapped[float] = mapped_column(Float)
    profit_factor: Mapped[float] = mapped_column(Float)
    max_drawdown_percent: Mapped[float] = mapped_column(Float)
    sharpe_like: Mapped[float] = mapped_column(Float)
    total_trades: Mapped[int]
    average_trade_percent: Mapped[float] = mapped_column(Float)
    expectancy: Mapped[float] = mapped_column(Float)

    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    trades: Mapped[list["BacktestTradeModel"]] = relationship(
        back_populates="backtest", cascade="all, delete-orphan"
    )


class BacktestTradeModel(Base):
    __tablename__ = "backtest_trades"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    backtest_id: Mapped[str] = mapped_column(ForeignKey("backtests.id"), index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    direction: Mapped[str] = mapped_column(String(10))
    entry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    exit_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    entry_price: Mapped[float] = mapped_column(Float)
    exit_price: Mapped[float] = mapped_column(Float)
    r_multiple: Mapped[float] = mapped_column(Float)
    outcome: Mapped[str] = mapped_column(String(20))
    pnl_percent: Mapped[float] = mapped_column(Float)
    regime: Mapped[str] = mapped_column(String(20))

    backtest: Mapped["BacktestModel"] = relationship(back_populates="trades")
