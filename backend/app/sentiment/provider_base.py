"""
Sentiment provider abstraction (spec sections 5, 14-16). Mirrors the market
data provider pattern: services depend on SentimentProvider, never on a
concrete implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class SentimentSourceType(StrEnum):
    NEWS = "news"
    COMMENTARY = "commentary"
    SOCIAL = "social"
    MACRO = "macro"


@dataclass
class SentimentObservation:
    """
    One raw sentiment data point (spec section 15). `entities` is the set of
    topic/instrument keywords this item touches (e.g. ["USD", "inflation",
    "fed"]) — app/sentiment/relevance.py turns that into a per-symbol
    relevance weight rather than assuming an item is equally relevant to
    every instrument.
    """

    id: str
    headline: str
    source_name: str
    source_type: SentimentSourceType
    published_at: datetime
    entities: list[str]
    raw_sentiment_score: float  # -1.0 (very bearish) .. +1.0 (very bullish)
    confidence: float  # 0.0 - 1.0, the source model's own confidence


class SentimentProvider(ABC):
    name: str

    @abstractmethod
    async def get_observations(self, symbol: str, lookback_hours: int = 24) -> list[SentimentObservation]: ...

    @abstractmethod
    async def is_healthy(self) -> bool: ...
