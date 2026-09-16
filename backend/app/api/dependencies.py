from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.market_data.mock_provider import MockMarketDataProvider
from app.market_data.mt5_provider import MT5MarketDataProvider
from app.market_data.provider_base import MarketDataProvider
from app.sentiment.mock_provider import MockSentimentProvider
from app.sentiment.news_provider import NewsSentimentProvider
from app.sentiment.provider_base import SentimentProvider
from app.services.alert_service import AlertService
from app.services.backtest_service import BacktestService
from app.services.market_data_service import MarketDataService
from app.services.performance_service import PerformanceService
from app.services.sentiment_service import SentimentService
from app.services.signal_engine import SignalEngine
from app.services.signal_service import SignalService
from app.services.trade_history_service import TradeHistoryService

# Providers are process-lifetime singletons — cheap to construct, and the
# MT5 provider in particular wants to reuse one terminal connection rather
# than reconnecting per request.
_market_data_provider: MarketDataProvider | None = None
_sentiment_provider: SentimentProvider | None = None


def get_market_data_provider(settings: Settings = Depends(get_settings)) -> MarketDataProvider:
    global _market_data_provider
    if _market_data_provider is None:
        if settings.MARKET_DATA_PROVIDER == "mt5" and settings.MT5_ENABLED:
            _market_data_provider = MT5MarketDataProvider()
        else:
            _market_data_provider = MockMarketDataProvider()
    return _market_data_provider


def get_sentiment_provider(settings: Settings = Depends(get_settings)) -> SentimentProvider:
    global _sentiment_provider
    if _sentiment_provider is None:
        if settings.SENTIMENT_PROVIDER == "news" and settings.NEWS_API_KEY:
            _sentiment_provider = NewsSentimentProvider()
        else:
            _sentiment_provider = MockSentimentProvider()
    return _sentiment_provider


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


def get_market_data_service(
    provider: MarketDataProvider = Depends(get_market_data_provider),
    db: AsyncSession = Depends(get_db_session),
) -> MarketDataService:
    return MarketDataService(provider, db)


def get_sentiment_service(
    provider: SentimentProvider = Depends(get_sentiment_provider),
    db: AsyncSession = Depends(get_db_session),
) -> SentimentService:
    return SentimentService(provider, db)


def get_signal_service(
    market_provider: MarketDataProvider = Depends(get_market_data_provider),
    sentiment_provider: SentimentProvider = Depends(get_sentiment_provider),
    db: AsyncSession = Depends(get_db_session),
) -> SignalService:
    engine = SignalEngine(market_provider, sentiment_provider)
    return SignalService(engine, db)


def get_backtest_service(
    provider: MarketDataProvider = Depends(get_market_data_provider),
    db: AsyncSession = Depends(get_db_session),
) -> BacktestService:
    return BacktestService(provider, db)


def get_performance_service(db: AsyncSession = Depends(get_db_session)) -> PerformanceService:
    return PerformanceService(db)


def get_alert_service(db: AsyncSession = Depends(get_db_session)) -> AlertService:
    return AlertService(db)


def get_trade_history_service(db: AsyncSession = Depends(get_db_session)) -> TradeHistoryService:
    return TradeHistoryService(db)
