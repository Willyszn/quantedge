from fastapi import APIRouter, Depends

from app.api.dependencies import get_sentiment_service
from app.schemas.sentiment import SymbolSentimentSchema
from app.services.sentiment_service import SentimentService

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


# /sentiment/market is registered before /sentiment/{symbol} for the same
# routing-order reason as /signals/primary.
@router.get(
    "/market",
    response_model=SymbolSentimentSchema,
    summary="Get aggregated market-wide sentiment",
    description="Combines sentiment observations across every supported instrument, "
    "weighted by relevance, recency, and source confidence.",
)
async def get_market_sentiment(
    service: SentimentService = Depends(get_sentiment_service),
) -> SymbolSentimentSchema:
    return await service.get_market_sentiment()


@router.get(
    "/{symbol}",
    response_model=SymbolSentimentSchema,
    summary="Get sentiment for one instrument",
    responses={404: {"description": "Instrument not found"}},
)
async def get_symbol_sentiment(
    symbol: str, service: SentimentService = Depends(get_sentiment_service)
) -> SymbolSentimentSchema:
    return await service.get_symbol_sentiment(symbol)
