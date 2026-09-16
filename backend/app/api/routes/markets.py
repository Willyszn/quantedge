from typing import cast

from fastapi import APIRouter, Depends

from app.api.dependencies import get_market_data_service
from app.core.errors import UnsupportedTimeframeError
from app.market_data.registry import ALL_TIMEFRAMES, Timeframe
from app.schemas.market import MarketCapabilitiesSchema, MarketQuoteSchema, MarketSeriesSchema
from app.services.market_data_service import MarketDataService

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get(
    "/quotes",
    response_model=list[MarketQuoteSchema],
    summary="Get current quotes for every supported instrument",
    description="Returns a MarketQuote for each instrument in the registry. Backed by Redis "
    "caching (~12s TTL) in front of the configured market data provider.",
)
async def get_quotes(
    service: MarketDataService = Depends(get_market_data_service),
) -> list[MarketQuoteSchema]:
    return await service.get_quotes()


@router.get(
    "/quotes/{symbol}",
    response_model=MarketQuoteSchema,
    summary="Get the current quote for one instrument",
    responses={404: {"description": "Instrument not found"}},
)
async def get_quote(
    symbol: str, service: MarketDataService = Depends(get_market_data_service)
) -> MarketQuoteSchema:
    return await service.get_quote(symbol)


@router.get(
    "/{symbol}/series",
    response_model=MarketSeriesSchema,
    summary="Get OHLC candle series for an instrument",
    description="Timeframe must be one of the values reported by GET /markets/{symbol}/capabilities.",
    responses={
        404: {"description": "Instrument not found"},
        422: {"description": "Unsupported timeframe"},
    },
)
async def get_series(
    symbol: str, timeframe: str, service: MarketDataService = Depends(get_market_data_service)
) -> MarketSeriesSchema:
    if timeframe not in ALL_TIMEFRAMES:
        raise UnsupportedTimeframeError(f"Timeframe '{timeframe}' is not a recognized QUANTEDGE timeframe.")
    return await service.get_series(symbol, cast(Timeframe, timeframe))


@router.get(
    "/{symbol}/capabilities",
    response_model=MarketCapabilitiesSchema,
    summary="Get supported chart timeframes for an instrument",
    description="The frontend uses this to decide which timeframe buttons to render — "
    "never claims a timeframe the configured provider can't actually supply.",
    responses={404: {"description": "Instrument not found"}},
)
async def get_capabilities(
    symbol: str, service: MarketDataService = Depends(get_market_data_service)
) -> MarketCapabilitiesSchema:
    return await service.get_capabilities(symbol)
