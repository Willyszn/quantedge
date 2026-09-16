from app.backtesting.strategies.base import BaseStrategy
from app.backtesting.strategies.mean_reversion import MeanReversionStrategy
from app.backtesting.strategies.momentum_breakout import MomentumBreakoutStrategy
from app.backtesting.strategies.sentiment_confluence import SentimentConfluenceStrategy
from app.backtesting.strategies.trend_continuation import TrendContinuationStrategy

STRATEGY_REGISTRY: dict[str, type[BaseStrategy]] = {
    "Momentum Breakout": MomentumBreakoutStrategy,
    "Trend Continuation": TrendContinuationStrategy,
    "Mean Reversion": MeanReversionStrategy,
    "Sentiment Confluence": SentimentConfluenceStrategy,
}


def get_strategy(name: str) -> BaseStrategy | None:
    cls = STRATEGY_REGISTRY.get(name)
    return cls() if cls else None


def list_strategy_names() -> list[str]:
    return list(STRATEGY_REGISTRY.keys())


def strategy_exists(name: str) -> bool:
    return name in STRATEGY_REGISTRY
