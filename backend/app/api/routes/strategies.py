from fastapi import APIRouter

from app.backtesting.strategies import STRATEGY_REGISTRY
from app.schemas.strategy import StrategySchema

router = APIRouter(tags=["strategies"])


@router.get(
    "/strategies",
    response_model=list[StrategySchema],
    summary="List supported backtest strategies",
    description=(
        "Every strategy the backtest engine can run, with a human-readable description "
        "of its entry rules. Intended as the eventual single source of truth for the "
        "Backtesting page's strategy dropdown (currently still sourced from "
        "src/mocks/backtests.ts); wiring that over is a frontend follow-up."
    ),
)
async def get_strategies() -> list[StrategySchema]:
    return [StrategySchema(name=name, description=cls().description) for name, cls in STRATEGY_REGISTRY.items()]
