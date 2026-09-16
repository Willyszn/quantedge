from fastapi import APIRouter

from app.api.routes import (
    alerts,
    backtests,
    health,
    instruments,
    markets,
    performance,
    sentiment,
    signals,
    strategies,
    trades,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(instruments.router)
api_router.include_router(strategies.router)
api_router.include_router(markets.router)
api_router.include_router(signals.router)
api_router.include_router(sentiment.router)
api_router.include_router(backtests.router)
api_router.include_router(performance.router)
api_router.include_router(trades.router)
api_router.include_router(alerts.router)
