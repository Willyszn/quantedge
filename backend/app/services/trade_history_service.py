"""
TradeHistoryService (spec section 32). Returns closed research/backtest
trades from Postgres — QUANTEDGE never places or records real broker
trades, so every row here originated from a POST /backtests run. If none
have been run yet, an empty list is the correct, honest response.
"""

from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backtesting.execution import TradeDirection, TradeOutcome
from app.models.backtest import BacktestTradeModel
from app.schemas.backtest import BacktestTradeSchema


class TradeHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_trades(self, limit: int = 200) -> list[BacktestTradeSchema]:
        result = await self.db.execute(
            select(BacktestTradeModel).order_by(BacktestTradeModel.exit_date.desc()).limit(limit)
        )
        return [
            BacktestTradeSchema(
                id=t.id,
                symbol=t.symbol,
                direction=cast(TradeDirection, t.direction),
                entry_date=t.entry_date,
                exit_date=t.exit_date,
                entry_price=t.entry_price,
                exit_price=t.exit_price,
                r_multiple=t.r_multiple,
                outcome=cast(TradeOutcome, t.outcome),
                pnl_percent=t.pnl_percent,
            )
            for t in result.scalars().all()
        ]
