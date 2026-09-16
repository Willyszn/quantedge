"""
Signal factors (spec section 20). Every factor's score, status, and
explanation is derived directly from the quant/sentiment/risk engines —
never invented. Factor IDs are fixed and must match the frontend exactly:
momentum, trend, volatility, sentiment-factor, risk-conditions.
"""

from dataclasses import dataclass

from app.quant.momentum import MomentumResult
from app.quant.structure import StructureResult
from app.quant.trend import TrendResult
from app.quant.volatility import VolatilityResult
from app.risk.engine import RiskAssessment
from app.sentiment.aggregation import SymbolSentimentResult
from app.signals.types import FactorStatus


@dataclass
class SignalFactor:
    id: str
    label: str
    score: float
    status: FactorStatus
    status_label: str
    explanation: str


def factor_status(score: float) -> FactorStatus:
    if score >= 66:
        return "favorable"
    if score >= 40:
        return "neutral"
    return "unfavorable"


def sentiment_score_from_split(split) -> float:
    """Collapses a bullish/neutral/bearish split into a single 0-100 index."""
    return round(split.bullish + split.neutral * 0.5, 1)


def _momentum_factor(momentum: MomentumResult) -> SignalFactor:
    status = factor_status(momentum.score)
    explanation = (
        f"RSI is at {momentum.rsi:.0f} with a {momentum.rate_of_change_percent:+.2f}% "
        f"rate of change over the recent window"
        f"{', and momentum is accelerating' if momentum.accelerating else ''}."
    )
    return SignalFactor(
        id="momentum",
        label="Quantitative Momentum",
        score=momentum.score,
        status=status,
        status_label=momentum.strength_label,
        explanation=explanation,
    )


def _trend_factor(trend: TrendResult, structure: StructureResult) -> SignalFactor:
    status = factor_status(trend.score)
    status_label = {"bullish": "Bullish", "bearish": "Bearish", "neutral": "Transitional"}[trend.direction]
    explanation = (
        f"Price is trading {'above' if trend.price_above_fast_ma else 'below'} its fast moving "
        f"average with {trend.consistency_percent:.0f}% consistency over the recent window"
        f"{', and structure confirms a ' + structure.direction + ' breakout' if structure.breakout else ''}."
    )
    return SignalFactor(
        id="trend",
        label="Trend Structure",
        score=trend.score,
        status=status,
        status_label=status_label,
        explanation=explanation,
    )


def _volatility_factor(volatility: VolatilityResult) -> SignalFactor:
    status = factor_status(volatility.score)
    status_label = {
        "low": "Quiet",
        "normal": "Favorable",
        "elevated": "Elevated",
        "extreme": "Erratic",
    }[volatility.regime]
    explanation = (
        f"ATR is running at {volatility.atr_percent_of_price:.2f}% of price "
        f"({volatility.regime} regime){', and expanding' if volatility.expanding else ''}, "
        f"which {'supports' if status == 'favorable' else 'complicates'} a defined stop and target."
    )
    return SignalFactor(
        id="volatility",
        label="Volatility",
        score=volatility.score,
        status=status,
        status_label=status_label,
        explanation=explanation,
    )


def _sentiment_factor(sentiment: SymbolSentimentResult) -> SignalFactor:
    score = sentiment_score_from_split(sentiment.split)
    status = factor_status(score)
    status_label = {"favorable": "Positive", "neutral": "Balanced", "unfavorable": "Negative"}[status]
    top_source = sentiment.sources[0] if sentiment.sources else None
    explanation = (
        f"Aggregated sentiment is {sentiment.split.bullish}% bullish / "
        f"{sentiment.split.neutral}% neutral / {sentiment.split.bearish}% bearish"
        f"{f', led by {top_source.label.lower()}' if top_source else ''}."
    )
    return SignalFactor(
        id="sentiment-factor",
        label="Sentiment",
        score=score,
        status=status,
        status_label=status_label,
        explanation=explanation,
    )


def _risk_factor(risk: RiskAssessment) -> SignalFactor:
    status = factor_status(risk.risk_score)
    status_label = {"favorable": "Acceptable", "neutral": "Watch", "unfavorable": "Elevated"}[status]
    explanation = (
        f"Stop distance is {risk.stop_distance_percent:.2f}% of price with an expected "
        f"risk/reward of 1:{risk.expected_risk_reward:.1f} under {risk.volatility_regime} volatility."
    )
    return SignalFactor(
        id="risk-conditions",
        label="Risk Conditions",
        score=risk.risk_score,
        status=status,
        status_label=status_label,
        explanation=explanation,
    )


def build_factors(
    trend: TrendResult,
    momentum: MomentumResult,
    volatility: VolatilityResult,
    structure: StructureResult,
    sentiment: SymbolSentimentResult,
    risk: RiskAssessment,
) -> list[SignalFactor]:
    return [
        _momentum_factor(momentum),
        _trend_factor(trend, structure),
        _volatility_factor(volatility),
        _sentiment_factor(sentiment),
        _risk_factor(risk),
    ]
