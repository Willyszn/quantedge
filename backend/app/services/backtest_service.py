"""
BacktestService (spec sections 4, 27-28). The only layer that talks to
BacktestEngine — routes call this, never the engine directly.
"""

import uuid
from datetime import UTC

from sqlalchemy.ext.asyncio import AsyncSession

from app.backtesting.engine import BacktestEngine, BacktestRunConfig
from app.backtesting.strategies import strategy_exists
from app.core.errors import (
    DataUnavailableError,
    InvalidBacktestConfigError,
    SymbolNotFoundError,
    UnsupportedStrategyError,
)
from app.core.logging import get_logger
from app.market_data.provider_base import MarketDataProvider
from app.market_data.registry import get_instrument
from app.models.backtest import BacktestModel, BacktestTradeModel
from app.quant.utils import candles_to_dataframe
from app.schemas.backtest import (
    BacktestConfigRequest,
    BacktestConfigSchema,
    BacktestResultSchema,
    BacktestTradeSchema,
    EquityPointSchema,
    MonthlyReturnSchema,
)
from app.services.alert_service import AlertService

logger = get_logger(__name__)

MIN_CANDLES_FOR_BACKTEST = 120
BACKTEST_TIMEFRAME = "1H"


class BacktestService:
    def __init__(self, provider: MarketDataProvider, db: AsyncSession):
        self.provider = provider
        self.db = db
        self.alerts = AlertService(db)

    async def run_backtest(self, request: BacktestConfigRequest) -> BacktestResultSchema:
        instrument = get_instrument(request.symbol)
        if instrument is None:
            raise SymbolNotFoundError(f"Instrument {request.symbol} was not found.")

        if not strategy_exists(request.strategy):
            raise UnsupportedStrategyError(f"Strategy '{request.strategy}' is not supported.")

        start = request.start_date if request.start_date.tzinfo else request.start_date.replace(tzinfo=UTC)
        end = request.end_date if request.end_date.tzinfo else request.end_date.replace(tzinfo=UTC)

        if end <= start:
            raise InvalidBacktestConfigError("end_date must be after start_date.")
        if request.initial_capital <= 0:
            raise InvalidBacktestConfigError("initial_capital must be positive.")
        if not (0 < request.risk_per_trade_percent <= 10):
            raise InvalidBacktestConfigError("risk_per_trade_percent must be between 0 and 10.")

        candles = await self.provider.get_historical_candles(request.symbol, BACKTEST_TIMEFRAME, start, end)
        if len(candles) < MIN_CANDLES_FOR_BACKTEST:
            raise DataUnavailableError(
                f"Not enough historical data for {request.symbol} between {start.date()} and "
                f"{end.date()} to run a meaningful backtest "
                f"({len(candles)}/{MIN_CANDLES_FOR_BACKTEST} candles available)."
            )

        df = candles_to_dataframe(candles)
        config = BacktestRunConfig(
            symbol=request.symbol,
            strategy_name=request.strategy,
            start_date=start,
            end_date=end,
            initial_capital=request.initial_capital,
            risk_per_trade_percent=request.risk_per_trade_percent,
            slippage_bps=request.slippage_bps,
            commission_bps=request.commission_bps,
            digits=instrument.digits,
        )

        result = BacktestEngine().run(df, config)

        backtest_id = f"bt-{int(result.completed_at.timestamp() * 1_000_000)}-{uuid.uuid4().hex[:6]}"
        schema = BacktestResultSchema(
            id=backtest_id,
            config=BacktestConfigSchema(
                symbol=request.symbol,
                strategy=request.strategy,
                start_date=start,
                end_date=end,
                initial_capital=request.initial_capital,
                risk_per_trade_percent=request.risk_per_trade_percent,
                slippage_bps=request.slippage_bps,
                commission_bps=request.commission_bps,
            ),
            total_return_percent=result.metrics.total_return_percent,
            win_rate=result.metrics.win_rate,
            profit_factor=result.metrics.profit_factor,
            max_drawdown_percent=result.metrics.max_drawdown_percent,
            sharpe_like=result.metrics.sharpe_like,
            total_trades=result.metrics.total_trades,
            average_trade_percent=result.metrics.average_trade_percent,
            expectancy=result.metrics.expectancy,
            equity_curve=[
                EquityPointSchema(date=p.date, equity=p.equity, drawdown_percent=p.drawdown_percent)
                for p in result.equity_curve
            ],
            monthly_returns=[
                MonthlyReturnSchema(month=m.month, return_percent=m.return_percent)
                for m in result.metrics.monthly_returns
            ],
            trades=[
                BacktestTradeSchema(
                    id=t.id,
                    symbol=t.symbol,
                    direction=t.direction,
                    entry_date=t.entry_date,
                    exit_date=t.exit_date,
                    entry_price=t.entry_price,
                    exit_price=t.exit_price,
                    r_multiple=t.r_multiple,
                    outcome=t.outcome,
                    pnl_percent=t.pnl_percent,
                )
                for t in result.trades
            ],
            completed_at=result.completed_at,
        )

        await self._persist(backtest_id, request, start, end, result)
        await self.alerts.create_alert(
            "backtest-complete",
            "Backtest completed",
            f"{request.strategy} backtest on {request.symbol} finished: "
            f"{result.metrics.total_trades} trades, {result.metrics.total_return_percent:+.2f}% return.",
            request.symbol,
        )
        logger.info(
            "backtest_completed",
            extra={
                "event": "backtest_completed",
                "symbol": request.symbol,
                "strategy": request.strategy,
                "trades": result.metrics.total_trades,
                "total_return_percent": result.metrics.total_return_percent,
            },
        )
        return schema

    async def _persist(self, backtest_id: str, request: BacktestConfigRequest, start, end, result) -> None:
        try:
            model = BacktestModel(
                id=backtest_id,
                symbol=request.symbol,
                strategy=request.strategy,
                start_date=start,
                end_date=end,
                initial_capital=request.initial_capital,
                risk_per_trade_percent=request.risk_per_trade_percent,
                slippage_bps=request.slippage_bps,
                commission_bps=request.commission_bps,
                total_return_percent=result.metrics.total_return_percent,
                win_rate=result.metrics.win_rate,
                profit_factor=result.metrics.profit_factor,
                max_drawdown_percent=result.metrics.max_drawdown_percent,
                sharpe_like=result.metrics.sharpe_like,
                total_trades=result.metrics.total_trades,
                average_trade_percent=result.metrics.average_trade_percent,
                expectancy=result.metrics.expectancy,
                completed_at=result.completed_at,
            )
            model.trades = [
                BacktestTradeModel(
                    id=f"{backtest_id}-{t.id}",
                    backtest_id=backtest_id,
                    symbol=t.symbol,
                    direction=t.direction,
                    entry_date=t.entry_date,
                    exit_date=t.exit_date,
                    entry_price=t.entry_price,
                    exit_price=t.exit_price,
                    r_multiple=t.r_multiple,
                    outcome=t.outcome,
                    pnl_percent=t.pnl_percent,
                    regime=t.regime,
                )
                for t in result.trades
            ]
            self.db.add(model)
            await self.db.commit()
        except Exception as exc:
            await self.db.rollback()
            logger.warning(
                "backtest_persist_failed",
                extra={"event": "backtest_persist_failed", "reason": str(exc)},
            )
