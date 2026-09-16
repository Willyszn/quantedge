from fastapi import APIRouter, Depends

from app.api.dependencies import get_signal_service
from app.schemas.signal import TradeSignalSchema
from app.services.signal_service import SignalService

router = APIRouter(prefix="/signals", tags=["signals"])


# /signals/primary is registered before /signals/{symbol} so it isn't
# swallowed by the dynamic symbol route.
@router.get(
    "/primary",
    response_model=TradeSignalSchema,
    summary="Get the strongest currently active signal",
    description="Ranked by confidence, risk quality, and recency — see app/signals/ranking.py — "
    "not simply the first row generated.",
)
async def get_primary_signal(
    service: SignalService = Depends(get_signal_service),
) -> TradeSignalSchema:
    return await service.get_primary_signal()


@router.get(
    "",
    response_model=list[TradeSignalSchema],
    summary="List current signals for every supported instrument",
    description="Sorted by confidence, descending.",
)
async def get_signals(
    service: SignalService = Depends(get_signal_service),
) -> list[TradeSignalSchema]:
    return await service.get_signals()


@router.get(
    "/{symbol}",
    response_model=TradeSignalSchema,
    summary="Get the current signal for one instrument",
    responses={
        404: {"description": "Instrument not found"},
        503: {"description": "Not enough market data to generate a signal"},
    },
)
async def get_signal(symbol: str, service: SignalService = Depends(get_signal_service)) -> TradeSignalSchema:
    return await service.get_signal(symbol)
