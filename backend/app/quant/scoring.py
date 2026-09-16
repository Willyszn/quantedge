def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def scale_to_score(value: float, low: float, high: float) -> float:
    """
    Linearly maps `value` from [low, high] to a 0-100 score, clamping
    outside the range. Used throughout the quant engine to turn a raw
    indicator (e.g. an RSI-distance-from-50, or an MA spread percentage)
    into a bounded, comparable score.
    """
    if high == low:
        return 50.0
    fraction = (value - low) / (high - low)
    return clamp(fraction * 100)


def bell_score(value: float, ideal: float, tolerance: float) -> float:
    """
    Peaks at 100 when `value == ideal` and falls off symmetrically as it
    moves `tolerance` away in either direction. Used for volatility, where
    both too little and too much movement are unfavorable.
    """
    distance = abs(value - ideal)
    fraction = max(0.0, 1 - (distance / tolerance))
    return clamp(fraction * 100)
