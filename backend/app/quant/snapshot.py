from dataclasses import dataclass

import pandas as pd

from app.core.scoring_config import QUANT_WEIGHTS
from app.quant.momentum import MomentumResult, analyze_momentum
from app.quant.scoring import clamp
from app.quant.structure import StructureResult, analyze_structure
from app.quant.trend import TrendResult, analyze_trend
from app.quant.volatility import VolatilityResult, analyze_volatility


@dataclass
class QuantSnapshot:
    quant_score: float  # 0-100 composite
    trend: TrendResult
    momentum: MomentumResult
    volatility: VolatilityResult
    structure: StructureResult

    @property
    def dominant_direction(self) -> str:
        """
        Simple majority vote across the directional components (trend,
        momentum, structure — volatility has no direction). Used by the
        signal engine to decide whether a "long" or "short" signal even
        makes sense before applying confidence/rating logic.
        """
        votes = [self.trend.direction, self.momentum.direction, self.structure.direction]
        bullish = votes.count("bullish")
        bearish = votes.count("bearish")
        if bullish > bearish:
            return "bullish"
        if bearish > bullish:
            return "bearish"
        return "neutral"


def build_quant_snapshot(df: pd.DataFrame) -> QuantSnapshot:
    """
    Runs all four analyzers against the same OHLC frame and combines their
    scores into the documented composite Quant Score:

        quant_score = TREND_WEIGHT   * trend.score
                    + MOMENTUM_WEIGHT * momentum.score
                    + STRUCTURE_WEIGHT * structure.score
                    + VOLATILITY_WEIGHT * volatility.score

    Weights are defined in app/core/scoring_config.py and must sum to 1.0.
    """
    trend = analyze_trend(df)
    momentum = analyze_momentum(df)
    volatility = analyze_volatility(df)
    structure = analyze_structure(df)

    quant_score = clamp(
        QUANT_WEIGHTS.TREND_WEIGHT * trend.score
        + QUANT_WEIGHTS.MOMENTUM_WEIGHT * momentum.score
        + QUANT_WEIGHTS.STRUCTURE_WEIGHT * structure.score
        + QUANT_WEIGHTS.VOLATILITY_WEIGHT * volatility.score
    )

    return QuantSnapshot(
        quant_score=round(quant_score, 1),
        trend=trend,
        momentum=momentum,
        volatility=volatility,
        structure=structure,
    )
