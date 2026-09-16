from dataclasses import dataclass
from datetime import datetime

from app.signals.factors import SignalFactor
from app.signals.types import SignalDirection, SignalRating


@dataclass
class SignalScores:
    quant: float
    momentum: float
    trend: float
    sentiment: float
    risk: float


@dataclass
class TradeSignal:
    """Domain-level representation matching the frontend's TradeSignal contract exactly."""

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
    scores: SignalScores
    factors: list[SignalFactor]
    narrative: str
    decimals: int

    @property
    def risk_score(self) -> float:
        return self.scores.risk
