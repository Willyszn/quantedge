from app.core.scoring_config import RATING_THRESHOLDS
from app.signals.types import SignalDirection, SignalRating


def direction_for(dominant_direction: str) -> SignalDirection:
    """
    Maps the quant engine's dominant_direction ("bullish"/"bearish"/
    "neutral") to the frontend's SignalDirection ("long"/"short"). A
    "neutral" quant read still needs a direction to build a trade plan
    against — it defaults to whichever side the momentum score currently
    leans, so the resulting rating naturally comes out "neutral" rather
    than a confident long/short.
    """
    return "short" if dominant_direction == "bearish" else "long"


def rating_for(confidence: float, direction: SignalDirection) -> SignalRating:
    """
    direction: "long" | "short"
    Mirrors the same threshold structure used for the frontend's demo data,
    now driven by a real, weighted confidence score instead of a random one.
    """
    t = RATING_THRESHOLDS
    if direction == "long":
        if confidence >= t.STRONG_THRESHOLD:
            return "strong-buy"
        if confidence >= t.ACTIONABLE_THRESHOLD:
            return "buy"
        if confidence >= t.NEUTRAL_THRESHOLD:
            return "neutral"
        return "sell"

    if confidence >= t.STRONG_THRESHOLD:
        return "strong-sell"
    if confidence >= t.ACTIONABLE_THRESHOLD:
        return "sell"
    if confidence >= t.NEUTRAL_THRESHOLD:
        return "neutral"
    return "buy"
