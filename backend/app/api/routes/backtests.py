from fastapi import APIRouter, Depends

from app.api.dependencies import get_backtest_service
from app.schemas.backtest import BacktestConfigRequest, BacktestResultSchema
from app.services.backtest_service import BacktestService

router = APIRouter(prefix="/backtests", tags=["backtests"])


@router.post(
    "",
    response_model=BacktestResultSchema,
    summary="Run a historical backtest",
    description=(
        "Runs a genuine historical simulation — entry rules, stop/target, slippage, and "
        "commission are all applied bar by bar with no look-ahead (see app/backtesting). "
        "Every metric in the response is derived from the resulting simulated trades. "
        "Backtest results are simulations and never guarantee future performance."
    ),
    responses={
        404: {"description": "Instrument not found"},
        422: {"description": "Invalid configuration or unsupported strategy"},
        503: {"description": "Not enough historical data for the requested range"},
    },
)
async def run_backtest(
    request: BacktestConfigRequest, service: BacktestService = Depends(get_backtest_service)
) -> BacktestResultSchema:
    return await service.run_backtest(request)
