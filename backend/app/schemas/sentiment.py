from datetime import datetime
from typing import Literal

from app.schemas.market import CamelModel

SentimentLabel = Literal["strong-positive", "positive", "neutral", "negative", "strong-negative"]
SentimentSourceType = Literal["news", "commentary", "social", "macro"]


class SentimentSplitSchema(CamelModel):
    bullish: int
    neutral: int
    bearish: int


class SentimentSourceSchema(CamelModel):
    id: str
    type: SentimentSourceType
    label: str
    sentiment: SentimentLabel
    confidence: int
    contribution_percent: int
    updated_at: datetime


class SentimentTimelinePointSchema(CamelModel):
    time: str
    label: SentimentLabel
    score: int


class SymbolSentimentSchema(CamelModel):
    symbol: str
    split: SentimentSplitSchema
    sources: list[SentimentSourceSchema]
    timeline: list[SentimentTimelinePointSchema]
