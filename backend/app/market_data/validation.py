"""
Every candle must pass through here before it's used for analysis, storage,
or returned to the frontend. This is intentionally strict: a bad candle
silently corrupting a moving average or RSI is worse than a rejected candle.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class RawCandle:
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class CandleValidationError(ValueError):
    def __init__(self, reason: str, candle: RawCandle | None = None):
        self.reason = reason
        self.candle = candle
        super().__init__(reason)


def validate_candle(candle: RawCandle) -> None:
    """Raises CandleValidationError on the first violation found."""
    if candle.time is None:
        raise CandleValidationError("missing_timestamp", candle)

    for field_name, value in (
        ("open", candle.open),
        ("high", candle.high),
        ("low", candle.low),
        ("close", candle.close),
    ):
        if value is None or value <= 0:
            raise CandleValidationError(f"non_positive_price:{field_name}", candle)
        if value != value:  # NaN check without importing math for a single use
            raise CandleValidationError(f"nan_price:{field_name}", candle)

    if candle.volume is not None and candle.volume < 0:
        raise CandleValidationError("negative_volume", candle)

    if candle.high < candle.low:
        raise CandleValidationError("high_below_low", candle)

    if candle.high < max(candle.open, candle.close):
        raise CandleValidationError("high_below_open_close", candle)

    if candle.low > min(candle.open, candle.close):
        raise CandleValidationError("low_above_open_close", candle)


def validate_series(candles: list[RawCandle]) -> list[RawCandle]:
    """
    Validates an entire series for per-candle correctness plus ordering and
    duplicate-timestamp constraints. Returns the series unchanged if valid;
    raises on the first violation. Callers that want to *drop* bad candles
    rather than fail the whole batch should catch CandleValidationError per
    candle before calling this, then re-validate the cleaned list.
    """
    if not candles:
        return candles

    seen_timestamps: set[datetime] = set()
    previous_time: datetime | None = None

    for candle in candles:
        validate_candle(candle)

        if candle.time in seen_timestamps:
            raise CandleValidationError("duplicate_timestamp", candle)
        seen_timestamps.add(candle.time)

        if previous_time is not None and candle.time < previous_time:
            raise CandleValidationError("non_monotonic_ordering", candle)
        previous_time = candle.time

    return candles


def filter_valid_candles(
    candles: list[RawCandle],
) -> tuple[list[RawCandle], list[tuple[RawCandle, str]]]:
    """
    Lenient variant used by ingestion: keeps well-formed, monotonically
    increasing, non-duplicate candles and reports the rest with a reason,
    rather than rejecting an entire batch for one bad row.
    """
    valid: list[RawCandle] = []
    rejected: list[tuple[RawCandle, str]] = []
    seen_timestamps: set[datetime] = set()
    last_time: datetime | None = None

    for candle in candles:
        try:
            validate_candle(candle)
        except CandleValidationError as exc:
            rejected.append((candle, exc.reason))
            continue

        if candle.time in seen_timestamps:
            rejected.append((candle, "duplicate_timestamp"))
            continue

        if last_time is not None and candle.time < last_time:
            rejected.append((candle, "non_monotonic_ordering"))
            continue

        seen_timestamps.add(candle.time)
        last_time = candle.time
        valid.append(candle)

    return valid, rejected
