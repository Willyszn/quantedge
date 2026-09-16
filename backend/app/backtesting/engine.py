"""
BacktestEngine (spec section 27). Deliberately has zero FastAPI/HTTP
dependency — it's a plain callable that takes historical candles and a
config and returns results, so it can be exercised directly in tests or
from a background job, not just from the API route.

    API -> BacktestService -> BacktestEngine -> Historical Data -> Strategy -> ExecutionSimulator -> Metrics
"""

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from app.backtesting.execution import EquityPoint, SimulatedTrade, run_execution
from app.backtesting.metrics import BacktestMetrics, compute_metrics
from app.backtesting.strategies import get_strategy
from app.backtesting.strategies.base import BaseStrategy


@dataclass
class BacktestRunConfig:
    symbol: str
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    risk_per_trade_percent: float
    slippage_bps: float
    commission_bps: float
    digits: int


@dataclass
class BacktestRunResult:
    config: BacktestRunConfig
    metrics: BacktestMetrics
    trades: list[SimulatedTrade]
    equity_curve: list[EquityPoint]
    completed_at: datetime


class BacktestEngine:
    def run(self, df: pd.DataFrame, config: BacktestRunConfig) -> BacktestRunResult:
        strategy: BaseStrategy | None = get_strategy(config.strategy_name)
        if strategy is None:
            raise ValueError(f"Unknown strategy: {config.strategy_name}")

        execution = run_execution(
            df=df,
            strategy=strategy,
            symbol=config.symbol,
            initial_capital=config.initial_capital,
            risk_per_trade_percent=config.risk_per_trade_percent,
            slippage_bps=config.slippage_bps,
            commission_bps=config.commission_bps,
            digits=config.digits,
        )

        metrics = compute_metrics(execution.trades, execution.equity_curve, config.initial_capital)

        return BacktestRunResult(
            config=config,
            metrics=metrics,
            trades=execution.trades,
            equity_curve=execution.equity_curve,
            completed_at=datetime.now(config.start_date.tzinfo),
        )
