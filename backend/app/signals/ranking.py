"""
Primary signal ranking (spec section 22). Combines confidence, risk
quality, and recency into a single rank score rather than just returning
the highest-confidence signal in isolation — a very high confidence signal
sitting on poor risk conditions shouldn't automatically outrank a slightly
lower-confidence signal with a cleaner trade plan.
"""

from datetime import datetime

from app.quant.scoring import clamp

RANK_CONFIDENCE_WEIGHT = 0.55
RANK_RISK_WEIGHT = 0.30
RANK_RECENCY_WEIGHT = 0.15
RECENCY_FULL_CREDIT_MINUTES = 15.0


def _recency_score(generated_at: datetime, now: datetime) -> float:
    age_minutes = max(0.0, (now - generated_at).total_seconds() / 60)
    return clamp(100 - (age_minutes / RECENCY_FULL_CREDIT_MINUTES) * 100)


def rank_score(confidence: float, risk_score: float, generated_at: datetime, now: datetime) -> float:
    return clamp(
        RANK_CONFIDENCE_WEIGHT * confidence
        + RANK_RISK_WEIGHT * risk_score
        + RANK_RECENCY_WEIGHT * _recency_score(generated_at, now)
    )


def rank_primary(signals: list, now: datetime, risk_score_getter, generated_at_getter, confidence_getter):
    """
    Generic ranking helper decoupled from a specific signal type so it's
    trivially unit-testable. `*_getter` callables extract the relevant field
    from whatever signal object is passed in (dataclass or ORM model).
    """
    if not signals:
        return None

    best = max(
        signals,
        key=lambda s: rank_score(confidence_getter(s), risk_score_getter(s), generated_at_getter(s), now),
    )
    return best
