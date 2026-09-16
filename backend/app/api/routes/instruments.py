from fastapi import APIRouter

from app.market_data.registry import list_instruments
from app.schemas.market import InstrumentSchema

router = APIRouter(tags=["instruments"])


@router.get(
    "/instruments",
    response_model=list[InstrumentSchema],
    summary="List supported instruments",
    description=(
        "The canonical instrument registry — every symbol QUANTEDGE supports, with its "
        "asset class, price precision, and supported chart timeframes. Intended as the "
        "eventual single source of truth for the frontend's instrument list (currently "
        "still sourced from src/mocks/instruments.ts); wiring that over is a frontend "
        "follow-up, not required for this API to function."
    ),
)
async def get_instruments() -> list[InstrumentSchema]:
    return [
        InstrumentSchema(
            symbol=inst.canonical_symbol,
            name=inst.name,
            asset_class=inst.asset_class.value,
            digits=inst.digits,
            base_currency=inst.base_currency,
            quote_currency=inst.quote_currency,
            minimum_price_increment=inst.minimum_price_increment,
            supported_timeframes=inst.supported_timeframes,
        )
        for inst in list_instruments()
    ]
