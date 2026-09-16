from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from app.schemas.market import CamelModel

TradeOutcome = Literal["win", "loss", "breakeven"]


class BacktestConfigRequest(CamelModel):
    symbol: str
    strategy: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = Field(gt=0)
    risk_per_trade_percent: float = Field(gt=0, le=10)
    slippage_bps: float = Field(ge=0, le=100)
    commission_bps: float = Field(ge=0, le=100)

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, end_date: datetime, info) -> datetime:
        start_date = info.data.get("start_date")
        if start_date and end_date <= start_date:
            raise ValueError("end_date must be after start_date")
        return end_date


class BacktestConfigSchema(CamelModel):
    symbol: str
    strategy: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    risk_per_trade_percent: float
    slippage_bps: float
    commission_bps: float


class BacktestTradeSchema(CamelModel):
    id: str
    symbol: str
    direction: Literal["long", "short"]
    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    r_multiple: float
    outcome: TradeOutcome
    pnl_percent: float


class EquityPointSchema(CamelModel):
    date: datetime
    equity: float
    drawdown_percent: float


class MonthlyReturnSchema(CamelModel):
    month: str
    return_percent: float


class BacktestResultSchema(CamelModel):
    id: str
    config: BacktestConfigSchema
    total_return_percent: float
    win_rate: float
    profit_factor: float
    max_drawdown_percent: float
    sharpe_like: float
    total_trades: int
    average_trade_percent: float
    expectancy: float
    equity_curve: list[EquityPointSchema]
    monthly_returns: list[MonthlyReturnSchema]
    trades: list[BacktestTradeSchema]
    completed_at: datetime
