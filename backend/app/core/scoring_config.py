"""
Every weight and threshold used by the quant/signal/risk engines lives here,
not inline in service code. Changing QUANTEDGE's methodology should mean
editing this file (or eventually a DB-backed config table), never hunting
through business logic for a stray number.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class QuantScoreWeights:
    """Weights for the composite Quant Score. Must sum to 1.0."""

    TREND_WEIGHT: float = 0.35
    MOMENTUM_WEIGHT: float = 0.30
    STRUCTURE_WEIGHT: float = 0.20
    VOLATILITY_WEIGHT: float = 0.15

    def __post_init__(self) -> None:
        total = self.TREND_WEIGHT + self.MOMENTUM_WEIGHT + self.STRUCTURE_WEIGHT + self.VOLATILITY_WEIGHT
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"QuantScoreWeights must sum to 1.0, got {total}")


@dataclass(frozen=True)
class SignalConfidenceWeights:
    """
    Weights for the Signal Confidence Score. This is explicitly a
    confidence score derived from the underlying factors — NOT a
    statistically calibrated win probability. See app/signals/confidence.py.
    """

    QUANT_WEIGHT: float = 0.45
    SENTIMENT_WEIGHT: float = 0.25
    RISK_WEIGHT: float = 0.30

    def __post_init__(self) -> None:
        total = self.QUANT_WEIGHT + self.SENTIMENT_WEIGHT + self.RISK_WEIGHT
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"SignalConfidenceWeights must sum to 1.0, got {total}")


@dataclass(frozen=True)
class SignalRatingThresholds:
    """Confidence thresholds mapping to a SignalRating for a given direction."""

    STRONG_THRESHOLD: float = 78.0
    ACTIONABLE_THRESHOLD: float = 60.0
    NEUTRAL_THRESHOLD: float = 45.0


@dataclass(frozen=True)
class TrendConfig:
    FAST_MA_PERIOD: int = 20
    SLOW_MA_PERIOD: int = 50
    STRUCTURE_LOOKBACK: int = 20


@dataclass(frozen=True)
class MomentumConfig:
    RSI_PERIOD: int = 14
    ROC_PERIOD: int = 10
    RSI_OVERBOUGHT: float = 70.0
    RSI_OVERSOLD: float = 30.0


@dataclass(frozen=True)
class VolatilityConfig:
    ATR_PERIOD: int = 14
    ROLLING_WINDOW: int = 20
    # ATR-as-percent-of-price thresholds separating volatility regimes.
    LOW_REGIME_MAX: float = 0.35
    NORMAL_REGIME_MAX: float = 0.9
    ELEVATED_REGIME_MAX: float = 1.8
    # (above ELEVATED_REGIME_MAX -> "extreme")


@dataclass(frozen=True)
class RiskConfig:
    """Trade-plan construction parameters."""

    ATR_STOP_MULTIPLIER: float = 1.5
    ENTRY_ZONE_ATR_FRACTION: float = 0.25
    MIN_RISK_REWARD: float = 1.5
    TARGET_RISK_REWARD: float = 2.2
    MAX_POSITION_RISK_PERCENT: float = 2.0
    DEFAULT_RISK_PER_TRADE_PERCENT: float = 1.0


@dataclass(frozen=True)
class BacktestDefaults:
    SLIPPAGE_BPS: float = 2.0
    COMMISSION_BPS: float = 1.0
    MAX_CANDLES: int = 5000


QUANT_WEIGHTS = QuantScoreWeights()
CONFIDENCE_WEIGHTS = SignalConfidenceWeights()
RATING_THRESHOLDS = SignalRatingThresholds()
TREND_CONFIG = TrendConfig()
MOMENTUM_CONFIG = MomentumConfig()
VOLATILITY_CONFIG = VolatilityConfig()
RISK_CONFIG = RiskConfig()
BACKTEST_DEFAULTS = BacktestDefaults()
