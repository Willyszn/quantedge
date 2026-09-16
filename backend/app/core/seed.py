"""
Development seed mode (spec section 40). Populates a handful of
deterministic backtest runs on startup so /trades/history and /performance/*
have real, traceable data to show on first frontend integration, instead of
an empty screen. This is explicitly development-only test data — controlled
by SEED_ON_STARTUP and skipped entirely in production — and every row it
creates went through the same real BacktestEngine as a manually-triggered
POST /backtests call. Nothing here is fabricated differently than the
production code path; it's just triggered automatically in dev.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger
from app.market_data.mock_provider import MockMarketDataProvider
from app.models.backtest import BacktestModel
from app.schemas.backtest import BacktestConfigRequest
from app.services.backtest_service import BacktestService

logger = get_logger(__name__)

SEED_RUNS = [
    ("XAUUSD", "Momentum Breakout"),
    ("GBPUSD", "Trend Continuation"),
    ("BTCUSD", "Mean Reversion"),
]


async def seed_development_data() -> None:
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(BacktestModel.id).limit(1))
        if existing.scalar_one_or_none() is not None:
            logger.info(
                "seed_skipped",
                extra={"event": "seed_skipped", "reason": "backtests already present"},
            )
            return

        provider = MockMarketDataProvider()
        service = BacktestService(provider, db)
        end = datetime.now(UTC)
        start = end - timedelta(days=200)

        for symbol, strategy in SEED_RUNS:
            request = BacktestConfigRequest(
                symbol=symbol,
                strategy=strategy,
                start_date=start,
                end_date=end,
                initial_capital=100_000,
                risk_per_trade_percent=1.0,
                slippage_bps=2,
                commission_bps=1,
            )
            await service.run_backtest(request)

        logger.info("seed_completed", extra={"event": "seed_completed", "runs": len(SEED_RUNS)})
