from datetime import UTC, datetime, timedelta

import pytest

from app.sentiment.aggregation import aggregate_sentiment, label_from_score
from app.sentiment.provider_base import SentimentObservation, SentimentSourceType
from app.sentiment.relevance import relevance_for_symbol

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def make_observation(
    score=0.5,
    confidence=0.8,
    hours_ago=1.0,
    entities=None,
    source_type=SentimentSourceType.NEWS,
    headline="test headline",
    source_name="Test Source",
    obs_id="obs-1",
) -> SentimentObservation:
    return SentimentObservation(
        id=obs_id,
        headline=headline,
        source_name=source_name,
        source_type=source_type,
        published_at=NOW - timedelta(hours=hours_ago),
        entities=entities or ["usd"],
        raw_sentiment_score=score,
        confidence=confidence,
    )


class TestLabelFromScore:
    def test_boundaries(self):
        assert label_from_score(90) == "strong-positive"
        assert label_from_score(60) == "positive"
        assert label_from_score(50) == "neutral"
        assert label_from_score(30) == "negative"
        assert label_from_score(5) == "strong-negative"


class TestRelevance:
    def test_gold_entity_is_highly_relevant_to_xauusd(self):
        assert relevance_for_symbol(["gold"], "XAUUSD") > 0.9

    def test_gold_entity_is_low_relevance_to_ethusd(self):
        assert relevance_for_symbol(["gold"], "ETHUSD") < 0.2

    def test_unknown_entity_falls_back_to_baseline(self):
        score = relevance_for_symbol(["some-unmapped-topic"], "XAUUSD")
        assert 0 < score < 0.5

    def test_multiple_entities_take_the_max_relevance(self):
        score = relevance_for_symbol(["gold", "some-unmapped-topic"], "XAUUSD")
        assert score > 0.9


class TestAggregation:
    def test_all_bullish_observations_produce_high_bullish_split(self):
        observations = [make_observation(score=0.8, entities=["gold"]) for _ in range(5)]
        result = aggregate_sentiment(observations, "XAUUSD", NOW)
        assert result.split.bullish > result.split.bearish
        assert result.split.bullish + result.split.neutral + result.split.bearish == 100

    def test_all_bearish_observations_produce_high_bearish_split(self):
        observations = [make_observation(score=-0.8, entities=["gold"]) for _ in range(5)]
        result = aggregate_sentiment(observations, "XAUUSD", NOW)
        assert result.split.bearish > result.split.bullish

    def test_empty_observations_produce_neutral_split(self):
        result = aggregate_sentiment([], "XAUUSD", NOW)
        assert result.split.bullish == 0
        assert result.split.bearish == 0

    def test_recent_observation_outweighs_stale_one(self):
        recent_bullish = make_observation(score=0.9, hours_ago=0.5, entities=["gold"], obs_id="a")
        stale_bearish = make_observation(score=-0.9, hours_ago=200, entities=["gold"], obs_id="b")
        result = aggregate_sentiment([recent_bullish, stale_bearish], "XAUUSD", NOW)
        assert result.split.bullish > result.split.bearish

    def test_irrelevant_observation_has_little_influence(self):
        relevant_bearish = make_observation(score=-0.8, entities=["gold"], obs_id="a")
        irrelevant_bullish = make_observation(score=0.9, entities=["ethereum"], obs_id="b")
        result = aggregate_sentiment([relevant_bearish, irrelevant_bullish], "XAUUSD", NOW)
        # The gold-relevant bearish item should dominate for XAUUSD despite
        # the irrelevant (crypto) item being more bullish in isolation.
        assert result.split.bearish > result.split.bullish

    def test_duplicate_headlines_are_not_double_counted(self):
        obs1 = make_observation(score=0.9, headline="Same Headline", source_name="Reuters", obs_id="a")
        obs2 = make_observation(score=0.9, headline="Same Headline", source_name="Reuters", obs_id="b")
        distinct = make_observation(score=-0.9, headline="Different Headline", source_name="Reuters", obs_id="c")

        with_dupe = aggregate_sentiment([obs1, obs2, distinct], "XAUUSD", NOW)
        without_dupe = aggregate_sentiment([obs1, distinct], "XAUUSD", NOW)

        # Deduping means the two results should be identical, not have the
        # duplicate's weight counted twice.
        assert with_dupe.split.bullish == without_dupe.split.bullish
        assert with_dupe.split.bearish == without_dupe.split.bearish

    def test_source_contribution_percentages_sum_to_roughly_100(self):
        observations = [
            make_observation(source_type=SentimentSourceType.NEWS, entities=["gold"], obs_id="a"),
            make_observation(source_type=SentimentSourceType.SOCIAL, entities=["gold"], obs_id="b"),
        ]
        result = aggregate_sentiment(observations, "XAUUSD", NOW)
        total_contribution = sum(s.contribution_percent for s in result.sources)
        assert total_contribution == pytest.approx(100, abs=2)

    def test_sources_are_sorted_by_contribution_descending(self):
        observations = [
            make_observation(source_type=SentimentSourceType.NEWS, entities=["gold"], confidence=0.95, obs_id="a"),
            make_observation(
                source_type=SentimentSourceType.SOCIAL, entities=["gold"], confidence=0.1, obs_id="b"
            ),
        ]
        result = aggregate_sentiment(observations, "XAUUSD", NOW)
        contributions = [s.contribution_percent for s in result.sources]
        assert contributions == sorted(contributions, reverse=True)
