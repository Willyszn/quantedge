from typing import Literal

from fastapi import APIRouter, Depends

from app.api.dependencies import get_performance_service
from app.schemas.backtest import EquityPointSchema
from app.schemas.performance import PerformanceBySliceSchema, PerformanceMetricsSchema
from app.services.performance_service import PerformanceService

router = APIRouter(prefix="/performance", tags=["performance"])

SliceBy = Literal["instrument", "signal-type", "month", "regime"]


@router.get(
    "/metrics",
    response_model=PerformanceMetricsSchema,
    summary="Get portfolio-level performance metrics",
    description="Computed from every stored research/backtest trade. Empty/zeroed until "
    "at least one POST /backtests run has completed.",
)
async def get_metrics(
    service: PerformanceService = Depends(get_performance_service),
) -> PerformanceMetricsSchema:
    return await service.get_metrics()


@router.get(
    "/equity-curve",
    response_model=list[EquityPointSchema],
    summary="Get the portfolio-level equity curve",
    description="A single continuous equity curve built by chaining every stored research "
    "trade's return in exit-date order, starting from a nominal $100,000.",
)
async def get_equity_curve(
    service: PerformanceService = Depends(get_performance_service),
) -> list[EquityPointSchema]:
    return await service.get_equity_curve()


@router.get(
    "/by/{slice_by}",
    response_model=list[PerformanceBySliceSchema],
    summary="Get performance broken down by a dimension",
    description=(
        "slice_by=instrument groups by symbol. slice_by=signal-type groups by trade "
        "direction (Long/Short) — research trades aren't yet linked back to the live "
        "signal rating that may have inspired them, so direction is the honest analog "
        "available today. slice_by=month groups by exit month. slice_by=regime groups by "
        "the volatility regime measured at each trade's entry."
    ),
)
async def get_performance_by(
    slice_by: SliceBy, service: PerformanceService = Depends(get_performance_service)
) -> list[PerformanceBySliceSchema]:
    handlers = {
        "instrument": service.get_by_instrument,
        "signal-type": service.get_by_signal_type,
        "month": service.get_by_month,
        "regime": service.get_by_regime,
    }
    return await handlers[slice_by]()
