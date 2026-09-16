from fastapi import APIRouter, Depends

from app.api.dependencies import get_trade_history_service
from app.schemas.backtest import BacktestTradeSchema
from app.services.trade_history_service import TradeHistoryService

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get(
    "/history",
    response_model=list[BacktestTradeSchema],
    summary="Get closed research/backtest trades",
    description=(
        "Returns trades produced by POST /backtests runs, most recent first. These are "
        "research/simulation trades, never real broker-executed trades — QUANTEDGE is a "
        "manual decision-support tool and never places orders. Empty until at least one "
        "backtest has been run."
    ),
)
async def get_trade_history(
    service: TradeHistoryService = Depends(get_trade_history_service),
) -> list[BacktestTradeSchema]:
    return await service.list_trades()
