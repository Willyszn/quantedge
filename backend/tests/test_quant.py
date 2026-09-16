import numpy as np
import pandas as pd
import pytest

from app.quant.momentum import analyze_momentum
from app.quant.scoring import bell_score, clamp, scale_to_score
from app.quant.snapshot import build_quant_snapshot
from app.quant.structure import analyze_structure
from app.quant.trend import analyze_trend
from app.quant.volatility import analyze_volatility


def make_trending_df(n=200, start=100.0, daily_drift=0.004, noise=0.0005, seed=42) -> pd.DataFrame:
    """A steadily rising series with tiny noise — should read as a clean uptrend."""
    rng = np.random.default_rng(seed)
    closes = [start]
    for _ in range(n - 1):
        closes.append(closes[-1] * (1 + daily_drift + rng.normal(0, noise)))
    closes = np.array(closes)
    highs = closes * (1 + np.abs(rng.normal(0, noise, n)))
    lows = closes * (1 - np.abs(rng.normal(0, noise, n)))
    opens = np.roll(closes, 1)
    opens[0] = closes[0]
    index = pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC")
    return pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes, "volume": 1000}, index=index)


def make_flat_df(n=200, price=100.0, noise=0.0003, seed=7) -> pd.DataFrame:
    """A directionless, choppy series around a fixed price — should read as neutral."""
    rng = np.random.default_rng(seed)
    closes = price * (1 + rng.normal(0, noise, n)).cumprod() ** 0 * (1 + rng.normal(0, noise, n))
    closes = price + rng.normal(0, price * noise, n)
    highs = closes + np.abs(rng.normal(0, price * noise, n))
    lows = closes - np.abs(rng.normal(0, price * noise, n))
    opens = np.roll(closes, 1)
    opens[0] = closes[0]
    index = pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC")
    return pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes, "volume": 1000}, index=index)


class TestScoringHelpers:
    def test_clamp_bounds(self):
        assert clamp(150) == 100
        assert clamp(-10) == 0
        assert clamp(55) == 55

    def test_scale_to_score_linear(self):
        assert scale_to_score(0, 0, 10) == 0
        assert scale_to_score(10, 0, 10) == 100
        assert scale_to_score(5, 0, 10) == 50
        assert scale_to_score(-5, 0, 10) == 0  # clamps below range
        assert scale_to_score(15, 0, 10) == 100  # clamps above range

    def test_bell_score_peaks_at_ideal(self):
        assert bell_score(5, ideal=5, tolerance=5) == 100
        assert bell_score(0, ideal=5, tolerance=5) == 0
        assert bell_score(10, ideal=5, tolerance=5) == 0


class TestTrendAnalysis:
    def test_uptrend_is_classified_bullish_with_high_score(self):
        result = analyze_trend(make_trending_df())
        assert result.direction == "bullish"
        assert result.score > 60

    def test_downtrend_is_classified_bearish(self):
        df = make_trending_df(daily_drift=-0.004)
        result = analyze_trend(df)
        assert result.direction == "bearish"
        assert result.score > 60

    def test_flat_series_is_neutral_or_low_score(self):
        result = analyze_trend(make_flat_df())
        # A choppy, directionless series shouldn't score as a strong trend.
        assert result.score < 70

    def test_insufficient_history_returns_neutral(self):
        short_df = make_trending_df(n=10)
        result = analyze_trend(short_df)
        assert result.direction == "neutral"
        assert result.score == 50.0

    def test_score_is_native_float_not_numpy(self):
        result = analyze_trend(make_trending_df())
        assert type(result.score) is float


class TestMomentumAnalysis:
    def test_uptrend_has_bullish_momentum(self):
        result = analyze_momentum(make_trending_df())
        assert result.direction == "bullish"
        assert result.rsi > 50

    def test_downtrend_has_bearish_momentum(self):
        result = analyze_momentum(make_trending_df(daily_drift=-0.004))
        assert result.direction == "bearish"
        assert result.rsi < 50

    def test_rsi_bounded_0_to_100(self):
        result = analyze_momentum(make_trending_df())
        assert 0 <= result.rsi <= 100

    def test_strength_label_matches_score_bands(self):
        result = analyze_momentum(make_trending_df())
        if result.score >= 70:
            assert result.strength_label == "Strong"
        elif result.score >= 45:
            assert result.strength_label == "Moderate"
        else:
            assert result.strength_label == "Weak"


class TestVolatilityAnalysis:
    def test_regime_classification_is_one_of_four(self):
        result = analyze_volatility(make_trending_df())
        assert result.regime in {"low", "normal", "elevated", "extreme"}

    def test_atr_is_non_negative(self):
        result = analyze_volatility(make_trending_df())
        assert result.atr >= 0

    def test_low_noise_series_reads_low_or_normal_regime(self):
        result = analyze_volatility(make_trending_df(noise=0.0001))
        assert result.regime in {"low", "normal"}

    def test_high_noise_series_reads_elevated_or_extreme_regime(self):
        result = analyze_volatility(make_trending_df(noise=0.02))
        assert result.regime in {"elevated", "extreme"}


class TestStructureAnalysis:
    def test_uptrend_shows_bullish_structure(self):
        result = analyze_structure(make_trending_df())
        assert result.direction == "bullish"

    def test_recent_high_is_above_recent_low(self):
        result = analyze_structure(make_trending_df())
        assert result.recent_high >= result.recent_low


class TestQuantSnapshot:
    def test_composite_score_is_bounded(self):
        snapshot = build_quant_snapshot(make_trending_df())
        assert 0 <= snapshot.quant_score <= 100

    def test_dominant_direction_matches_strong_uptrend(self):
        snapshot = build_quant_snapshot(make_trending_df(daily_drift=0.006, noise=0.0002))
        assert snapshot.dominant_direction == "bullish"

    def test_dominant_direction_matches_strong_downtrend(self):
        snapshot = build_quant_snapshot(make_trending_df(daily_drift=-0.006, noise=0.0002))
        assert snapshot.dominant_direction == "bearish"

    def test_weights_sum_to_one(self):
        from app.core.scoring_config import QUANT_WEIGHTS

        total = (
            QUANT_WEIGHTS.TREND_WEIGHT
            + QUANT_WEIGHTS.MOMENTUM_WEIGHT
            + QUANT_WEIGHTS.STRUCTURE_WEIGHT
            + QUANT_WEIGHTS.VOLATILITY_WEIGHT
        )
        assert total == pytest.approx(1.0)
