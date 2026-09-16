from datetime import UTC, datetime, timedelta

import pytest

from app.signals.confidence import compute_confidence
from app.signals.factors import factor_status, sentiment_score_from_split
from app.signals.narrative import build_narrative
from app.signals.ranking import rank_primary
from app.signals.rating import direction_for, rating_for


class TestFactorStatus:
    def test_high_score_is_favorable(self):
        assert factor_status(80) == "favorable"

    def test_mid_score_is_neutral(self):
        assert factor_status(50) == "neutral"

    def test_low_score_is_unfavorable(self):
        assert factor_status(20) == "unfavorable"

    def test_boundary_66_is_favorable(self):
        assert factor_status(66) == "favorable"

    def test_boundary_40_is_neutral(self):
        assert factor_status(40) == "neutral"

    def test_boundary_39_is_unfavorable(self):
        assert factor_status(39) == "unfavorable"


class TestSentimentScoreFromSplit:
    def test_all_bullish_scores_100(self):
        class Split:
            bullish, neutral, bearish = 100, 0, 0

        assert sentiment_score_from_split(Split()) == 100

    def test_all_bearish_scores_0(self):
        class Split:
            bullish, neutral, bearish = 0, 0, 100

        assert sentiment_score_from_split(Split()) == 0

    def test_all_neutral_scores_50(self):
        class Split:
            bullish, neutral, bearish = 0, 100, 0

        assert sentiment_score_from_split(Split()) == 50


class TestConfidence:
    def test_confidence_is_bounded(self):
        assert 0 <= compute_confidence(100, 100, 100) <= 100
        assert 0 <= compute_confidence(0, 0, 0) <= 100

    def test_higher_inputs_produce_higher_confidence(self):
        low = compute_confidence(20, 20, 20)
        high = compute_confidence(90, 90, 90)
        assert high > low

    def test_confidence_is_weighted_not_simple_average(self):
        from app.core.scoring_config import CONFIDENCE_WEIGHTS

        expected = (
            CONFIDENCE_WEIGHTS.QUANT_WEIGHT * 80
            + CONFIDENCE_WEIGHTS.SENTIMENT_WEIGHT * 40
            + CONFIDENCE_WEIGHTS.RISK_WEIGHT * 60
        )
        assert compute_confidence(80, 40, 60) == pytest.approx(round(expected, 1))


class TestDirectionAndRating:
    def test_bearish_quant_direction_maps_to_short(self):
        assert direction_for("bearish") == "short"

    def test_bullish_quant_direction_maps_to_long(self):
        assert direction_for("bullish") == "long"

    def test_neutral_quant_direction_defaults_to_long(self):
        assert direction_for("neutral") == "long"

    def test_high_confidence_long_is_strong_buy(self):
        assert rating_for(85, "long") == "strong-buy"

    def test_high_confidence_short_is_strong_sell(self):
        assert rating_for(85, "short") == "strong-sell"

    def test_moderate_confidence_long_is_buy(self):
        assert rating_for(65, "long") == "buy"

    def test_low_confidence_is_neutral(self):
        assert rating_for(50, "long") == "neutral"

    def test_very_low_confidence_long_is_sell(self):
        assert rating_for(20, "long") == "sell"

    def test_very_low_confidence_short_is_buy(self):
        assert rating_for(20, "short") == "buy"

    def test_ratings_are_never_mismatched_with_direction(self):
        # A "long" direction must never produce a "-sell" rating that isn't
        # the plain bearish-leaning "sell", and never "strong-sell".
        for confidence in range(0, 101, 5):
            rating = rating_for(confidence, "long")
            assert rating != "strong-sell"


class TestNarrative:
    def test_narrative_mentions_symbol(self):
        from app.signals.factors import SignalFactor

        factors = [
            SignalFactor("momentum", "Quantitative Momentum", 80, "favorable", "Strong", "explanation A"),
            SignalFactor("trend", "Trend Structure", 75, "favorable", "Bullish", "explanation B"),
            SignalFactor("volatility", "Volatility", 60, "neutral", "Favorable", "explanation C"),
            SignalFactor("sentiment-factor", "Sentiment", 55, "neutral", "Balanced", "explanation D"),
            SignalFactor("risk-conditions", "Risk Conditions", 70, "favorable", "Acceptable", "explanation E"),
        ]
        narrative = build_narrative("XAUUSD", "long", factors)
        assert "XAUUSD" in narrative
        assert len(narrative) > 20

    def test_narrative_uses_correct_article_for_upside(self):
        from app.signals.factors import SignalFactor

        factors = [SignalFactor("momentum", "Quantitative Momentum", 80, "favorable", "Strong", "x")]
        narrative = build_narrative("XAUUSD", "long", factors)
        assert "a upside" not in narrative
        assert "an upside" in narrative


class TestPrimarySignalRanking:
    def test_higher_confidence_wins_when_risk_and_recency_equal(self):
        now = datetime.now(UTC)
        signals = [
            {"confidence": 60, "risk_score": 70, "generated_at": now},
            {"confidence": 85, "risk_score": 70, "generated_at": now},
        ]
        best = rank_primary(
            signals,
            now,
            risk_score_getter=lambda s: s["risk_score"],
            generated_at_getter=lambda s: s["generated_at"],
            confidence_getter=lambda s: s["confidence"],
        )
        assert best["confidence"] == 85

    def test_poor_risk_quality_can_lose_to_slightly_lower_confidence(self):
        now = datetime.now(UTC)
        high_confidence_bad_risk = {"confidence": 90, "risk_score": 10, "generated_at": now}
        good_balance = {"confidence": 80, "risk_score": 95, "generated_at": now}
        best = rank_primary(
            [high_confidence_bad_risk, good_balance],
            now,
            risk_score_getter=lambda s: s["risk_score"],
            generated_at_getter=lambda s: s["generated_at"],
            confidence_getter=lambda s: s["confidence"],
        )
        assert best is good_balance

    def test_stale_signal_loses_to_fresher_lower_confidence_signal(self):
        now = datetime.now(UTC)
        stale = {"confidence": 90, "risk_score": 70, "generated_at": now - timedelta(hours=5)}
        fresh = {"confidence": 82, "risk_score": 70, "generated_at": now}
        best = rank_primary(
            [stale, fresh],
            now,
            risk_score_getter=lambda s: s["risk_score"],
            generated_at_getter=lambda s: s["generated_at"],
            confidence_getter=lambda s: s["confidence"],
        )
        assert best is fresh

    def test_empty_list_returns_none(self):
        result = rank_primary(
            [],
            datetime.now(UTC),
            risk_score_getter=lambda s: 0,
            generated_at_getter=lambda s: datetime.now(UTC),
            confidence_getter=lambda s: 0,
        )
        assert result is None
