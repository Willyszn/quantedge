"""
PerformanceService (spec section 33). Every number here is computed from
BacktestTradeModel rows actually stored in Postgres — run at least one
backtest via POST /backtests before these endpoints have anything to
aggregate. An empty result set (rather than a fabricated one) is the
correct, honest response when no research trades exist yet.
"""

from collections import defaultdict
from datetime import UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backtest import BacktestTradeModel
from app.schemas.backtest import EquityPointSchema
from app.schemas.performance import PerformanceBySliceSchema, PerformanceMetricsSchema

NOMINAL_STARTING_EQUITY = 100_000.0


class PerformanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _all_trades(self) -> list[BacktestTradeModel]:
        result = await self.db.execute(select(BacktestTradeModel).order_by(BacktestTradeModel.exit_date))
        return list(result.scalars().all())

    async def get_metrics(self) -> PerformanceMetricsSchema:
        trades = await self._all_trades()
        if not trades:
            return PerformanceMetricsSchema(
                total_return_percent=0.0,
                win_rate=0.0,
                profit_factor=0.0,
                max_drawdown_percent=0.0,
                average_r=0.0,
                expectancy=0.0,
                best_trade_percent=0.0,
                worst_trade_percent=0.0,
            )

        equity_curve = self._build_equity_curve(trades)
        wins = [t for t in trades if t.outcome == "win"]
        losses = [t for t in trades if t.outcome == "loss"]
        gross_win = sum(abs(t.pnl_percent) for t in wins)
        gross_loss = sum(abs(t.pnl_percent) for t in losses) or 1e-9

        final_equity = equity_curve[-1].equity if equity_curve else NOMINAL_STARTING_EQUITY
        total_return_percent = round(((final_equity - NOMINAL_STARTING_EQUITY) / NOMINAL_STARTING_EQUITY) * 100, 2)

        return PerformanceMetricsSchema(
            total_return_percent=total_return_percent,
            win_rate=round((len(wins) / len(trades)) * 100, 1),
            profit_factor=round(gross_win / gross_loss, 2),
            max_drawdown_percent=round(min((p.drawdown_percent for p in equity_curve), default=0.0), 2),
            average_r=round(sum(t.r_multiple for t in trades) / len(trades), 2),
            expectancy=round(sum(t.r_multiple for t in trades) / len(trades), 2),
            best_trade_percent=round(max(t.pnl_percent for t in trades), 2),
            worst_trade_percent=round(min(t.pnl_percent for t in trades), 2),
        )

    async def get_equity_curve(self) -> list[EquityPointSchema]:
        trades = await self._all_trades()
        points = self._build_equity_curve(trades)
        return [
            EquityPointSchema(date=p.date, equity=p.equity, drawdown_percent=p.drawdown_percent) for p in points
        ]

    async def get_by_instrument(self) -> list[PerformanceBySliceSchema]:
        trades = await self._all_trades()
        return self._slice_by(trades, key_fn=lambda t: t.symbol)

    async def get_by_signal_type(self) -> list[PerformanceBySliceSchema]:
        # Backtest trades come from a strategy's mechanical rules, not a
        # rated live signal, so there's no genuine "Strong Buy"/"Buy" tier
        # to group by yet without fabricating one. Direction (Long/Short)
        # is the honest analog available today; a future version that
        # links research trades back to the live TradeSignal rating that
        # inspired them could group by rating instead.
        trades = await self._all_trades()
        return self._slice_by(trades, key_fn=lambda t: "Long" if t.direction == "long" else "Short")

    async def get_by_month(self) -> list[PerformanceBySliceSchema]:
        trades = await self._all_trades()
        return self._slice_by(trades, key_fn=lambda t: t.exit_date.strftime("%b %Y"))

    async def get_by_regime(self) -> list[PerformanceBySliceSchema]:
        trades = await self._all_trades()
        return self._slice_by(trades, key_fn=lambda t: t.regime.capitalize())

    @staticmethod
    def _slice_by(trades: list[BacktestTradeModel], key_fn) -> list[PerformanceBySliceSchema]:
        groups: dict[str, list[BacktestTradeModel]] = defaultdict(list)
        for t in trades:
            groups[key_fn(t)].append(t)

        slices = []
        for label, group in groups.items():
            wins = [t for t in group if t.outcome == "win"]
            slices.append(
                PerformanceBySliceSchema(
                    label=label,
                    return_percent=round(sum(t.pnl_percent for t in group), 2),
                    win_rate=round((len(wins) / len(group)) * 100, 0) if group else 0.0,
                    trades=len(group),
                )
            )
        return slices

    @staticmethod
    def _build_equity_curve(trades: list[BacktestTradeModel]):
        from app.backtesting.execution import EquityPoint

        equity = NOMINAL_STARTING_EQUITY
        peak = equity
        points = []
        for t in trades:
            equity *= 1 + t.pnl_percent / 100
            peak = max(peak, equity)
            drawdown = ((equity - peak) / peak) * 100 if peak else 0.0
            date = t.exit_date if t.exit_date.tzinfo else t.exit_date.replace(tzinfo=UTC)
            points.append(EquityPoint(date=date, equity=round(equity, 2), drawdown_percent=round(drawdown, 2)))
        return points
