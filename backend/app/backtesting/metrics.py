"""
Backtest metrics (spec section 31). Every value here is computed from the
actual list of simulated trades / equity curve produced by execution.py —
nothing is a placeholder or randomly generated.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from app.backtesting.execution import EquityPoint, SimulatedTrade

TRADING_DAYS_ANNUALIZATION = 252**0.5


@dataclass
class MonthlyReturn:
    month: str
    return_percent: float


@dataclass
class BacktestMetrics:
    total_return_percent: float
    win_rate: float
    profit_factor: float
    max_drawdown_percent: float
    sharpe_like: float
    total_trades: int
    average_trade_percent: float
    expectancy: float
    monthly_returns: list[MonthlyReturn]


def compute_metrics(
    trades: list[SimulatedTrade], equity_curve: list[EquityPoint], initial_capital: float
) -> BacktestMetrics:
    if not trades:
        return BacktestMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, [])

    wins = [t for t in trades if t.outcome == "win"]
    losses = [t for t in trades if t.outcome == "loss"]

    final_equity = equity_curve[-1].equity if equity_curve else initial_capital
    total_return_percent = (
        round(((final_equity - initial_capital) / initial_capital) * 100, 2) if initial_capital else 0.0
    )

    win_rate = round((len(wins) / len(trades)) * 100, 1)

    gross_win = sum(abs(t.pnl_percent) for t in wins)
    gross_loss = sum(abs(t.pnl_percent) for t in losses) or 1e-9
    profit_factor = round(gross_win / gross_loss, 2)

    max_drawdown_percent = round(min((p.drawdown_percent for p in equity_curve), default=0.0), 2)

    average_trade_percent = round(sum(t.pnl_percent for t in trades) / len(trades), 2)
    expectancy = round(sum(t.r_multiple for t in trades) / len(trades), 2)

    # "sharpeLike" (named to match the frontend contract honestly — see
    # spec section 19 on not overclaiming statistical rigor): mean per-trade
    # return over its standard deviation, annualized by number-of-trades as
    # a rough proxy for trade frequency. It is NOT a return-interval-aligned
    # Sharpe ratio.
    pnl_values = [t.pnl_percent for t in trades]
    mean_pnl = sum(pnl_values) / len(pnl_values)
    variance = sum((p - mean_pnl) ** 2 for p in pnl_values) / len(pnl_values)
    std_pnl = variance**0.5
    sharpe_like = round((mean_pnl / std_pnl) * TRADING_DAYS_ANNUALIZATION, 2) if std_pnl else 0.0

    monthly_returns = _compute_monthly_returns(equity_curve, initial_capital)

    return BacktestMetrics(
        total_return_percent=total_return_percent,
        win_rate=win_rate,
        profit_factor=profit_factor,
        max_drawdown_percent=max_drawdown_percent,
        sharpe_like=sharpe_like,
        total_trades=len(trades),
        average_trade_percent=average_trade_percent,
        expectancy=expectancy,
        monthly_returns=monthly_returns,
    )


def _compute_monthly_returns(equity_curve: list[EquityPoint], initial_capital: float) -> list[MonthlyReturn]:
    if not equity_curve:
        return []

    by_month: dict[str, list[EquityPoint]] = defaultdict(list)
    for point in equity_curve:
        key = point.date.strftime("%Y-%m") if isinstance(point.date, datetime) else str(point.date)[:7]
        by_month[key].append(point)

    results = []
    prior_equity = initial_capital
    for month in sorted(by_month.keys()):
        month_points = by_month[month]
        month_end_equity = month_points[-1].equity
        return_percent = ((month_end_equity - prior_equity) / prior_equity) * 100 if prior_equity else 0.0
        label = datetime.strptime(month, "%Y-%m").strftime("%b")
        results.append(MonthlyReturn(month=label, return_percent=round(return_percent, 2)))
        prior_equity = month_end_equity

    return results
