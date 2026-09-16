"""
Signal Confidence Score (spec section 19).

This is a weighted blend of the quant score, sentiment score, and risk
score — NOT a statistically calibrated probability of the trade winning.
Nothing in QUANTEDGE should present it as "82% chance of winning" until a
real calibration study (comparing predicted confidence buckets against
actual historical outcomes) justifies that claim. Until then it's exactly
what it's named: a Signal Confidence Score describing how strongly the
underlying factors agree with each other.
"""

from app.core.scoring_config import CONFIDENCE_WEIGHTS
from app.quant.scoring import clamp


def compute_confidence(quant_score: float, sentiment_score: float, risk_score: float) -> float:
    confidence = (
        CONFIDENCE_WEIGHTS.QUANT_WEIGHT * quant_score
        + CONFIDENCE_WEIGHTS.SENTIMENT_WEIGHT * sentiment_score
        + CONFIDENCE_WEIGHTS.RISK_WEIGHT * risk_score
    )
    return round(clamp(confidence), 1)
