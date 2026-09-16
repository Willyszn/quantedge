from datetime import datetime
from typing import Literal

from app.schemas.market import CamelModel

SignalDirection = Literal["long", "short"]
SignalRating = Literal["strong-buy", "buy", "neutral", "sell", "strong-sell"]
FactorStatus = Literal["favorable", "neutral", "unfavorable"]


class SignalFactorSchema(CamelModel):
    id: str
    label: str
    score: float
    status: FactorStatus
    status_label: str
    explanation: str


class SignalScoreBreakdownSchema(CamelModel):
    quant: float
    momentum: float
    trend: float
    sentiment: float
    risk: float


class TradeSignalSchema(CamelModel):
    id: str
    symbol: str
    name: str
    direction: SignalDirection
    rating: SignalRating
    confidence: float
    entry_low: float
    entry_high: float
    stop_loss: float
    target: float
    risk_reward_ratio: float
    generated_at: datetime
    scores: SignalScoreBreakdownSchema
    factors: list[SignalFactorSchema]
    narrative: str
    decimals: int
