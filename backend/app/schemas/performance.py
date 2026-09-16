from app.schemas.backtest import EquityPointSchema
from app.schemas.market import CamelModel

__all__ = ["PerformanceMetricsSchema", "PerformanceBySliceSchema", "EquityPointSchema"]


class PerformanceMetricsSchema(CamelModel):
    total_return_percent: float
    win_rate: float
    profit_factor: float
    max_drawdown_percent: float
    average_r: float
    expectancy: float
    best_trade_percent: float
    worst_trade_percent: float


class PerformanceBySliceSchema(CamelModel):
    label: str
    return_percent: float
    win_rate: float
    trades: int
