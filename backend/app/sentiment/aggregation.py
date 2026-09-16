"""
Aggregation (spec sections 14-16). Turns a list of raw SentimentObservation
items into the exact SymbolSentiment shape the frontend expects. A single
observation never dominates: its influence is weighted by how relevant it
is to the requested symbol, how recent it is, and how confident the source
itself was — and duplicate headlines are collapsed before aggregation.
"""

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from app.sentiment.provider_base import SentimentObservation, SentimentSourceType
from app.sentiment.relevance import relevance_for_symbol

SentimentLabel = Literal["strong-positive", "positive", "neutral", "negative", "strong-negative"]

RECENCY_HALF_LIFE_HOURS = 10.0
BULLISH_THRESHOLD = 0.15
BEARISH_THRESHOLD = -0.15

SOURCE_TYPE_LABELS: dict[SentimentSourceType, str] = {
    SentimentSourceType.NEWS: "Financial News",
    SentimentSourceType.COMMENTARY: "Market Commentary",
    SentimentSourceType.SOCIAL: "Social Sentiment",
    SentimentSourceType.MACRO: "Macro Sentiment",
}


@dataclass
class WeightedObservation:
    observation: SentimentObservation
    weight: float
    normalized_score: float  # 0-100, bullish index


@dataclass
class SentimentSplitResult:
    bullish: int
    neutral: int
    bearish: int


@dataclass
class SentimentSourceResult:
    id: str
    type: SentimentSourceType
    label: str
    sentiment: SentimentLabel
    confidence: int
    contribution_percent: int
    updated_at: datetime


@dataclass
class SentimentTimelinePointResult:
    time: str
    label: SentimentLabel
    score: int


@dataclass
class SymbolSentimentResult:
    symbol: str
    split: SentimentSplitResult
    sources: list[SentimentSourceResult]
    timeline: list[SentimentTimelinePointResult]


def label_from_score(score: float) -> SentimentLabel:
    """score is 0-100 bullish index."""
    if score >= 75:
        return "strong-positive"
    if score >= 58:
        return "positive"
    if score >= 42:
        return "neutral"
    if score >= 25:
        return "negative"
    return "strong-negative"


def _dedupe(observations: list[SentimentObservation]) -> list[SentimentObservation]:
    """Keeps the most recent item per (headline, source_name) pair."""
    best: dict[tuple[str, str], SentimentObservation] = {}
    for obs in observations:
        key = (obs.headline.strip().lower(), obs.source_name)
        existing = best.get(key)
        if existing is None or obs.published_at > existing.published_at:
            best[key] = obs
    return list(best.values())


def _recency_weight(published_at: datetime, now: datetime) -> float:
    age_hours = max(0.0, (now - published_at).total_seconds() / 3600)
    return math.pow(0.5, age_hours / RECENCY_HALF_LIFE_HOURS)


def _weigh_observations(
    observations: list[SentimentObservation], symbol: str, now: datetime
) -> list[WeightedObservation]:
    weighted = []
    for obs in _dedupe(observations):
        relevance = relevance_for_symbol(obs.entities, symbol)
        recency = _recency_weight(obs.published_at, now)
        weight = relevance * obs.confidence * recency
        normalized_score = (obs.raw_sentiment_score + 1) / 2 * 100
        weighted.append(WeightedObservation(obs, weight, normalized_score))
    return weighted


def _compute_split(weighted: list[WeightedObservation]) -> SentimentSplitResult:
    total_weight = sum(w.weight for w in weighted) or 1e-9
    bullish_weight = sum(w.weight for w in weighted if w.observation.raw_sentiment_score > BULLISH_THRESHOLD)
    bearish_weight = sum(w.weight for w in weighted if w.observation.raw_sentiment_score < BEARISH_THRESHOLD)

    bullish_pct = round(bullish_weight / total_weight * 100)
    bearish_pct = round(bearish_weight / total_weight * 100)
    neutral_pct = 100 - bullish_pct - bearish_pct

    return SentimentSplitResult(bullish=bullish_pct, neutral=max(neutral_pct, 0), bearish=bearish_pct)


def _compute_sources(weighted: list[WeightedObservation]) -> list[SentimentSourceResult]:
    total_weight = sum(w.weight for w in weighted) or 1e-9
    by_type: dict[SentimentSourceType, list[WeightedObservation]] = {}
    for w in weighted:
        by_type.setdefault(w.observation.source_type, []).append(w)

    results = []
    for source_type, items in by_type.items():
        group_weight = sum(i.weight for i in items) or 1e-9
        weighted_score = sum(i.normalized_score * i.weight for i in items) / group_weight
        weighted_confidence = sum(i.observation.confidence * i.weight for i in items) / group_weight
        most_recent = max(i.observation.published_at for i in items)
        contribution = round(group_weight / total_weight * 100)

        results.append(
            SentimentSourceResult(
                id=f"src-{source_type.value}",
                type=source_type,
                label=SOURCE_TYPE_LABELS[source_type],
                sentiment=label_from_score(weighted_score),
                confidence=round(weighted_confidence * 100),
                contribution_percent=contribution,
                updated_at=most_recent,
            )
        )

    return sorted(results, key=lambda r: r.contribution_percent, reverse=True)


def _compute_timeline(
    weighted: list[WeightedObservation], now: datetime, buckets: int = 5, span_hours: int = 10
) -> list[SentimentTimelinePointResult]:
    if not weighted:
        return []

    bucket_span = span_hours / buckets
    points: list[SentimentTimelinePointResult] = []

    for i in range(buckets):
        bucket_end = now.timestamp() - (buckets - 1 - i) * bucket_span * 3600
        bucket_start = bucket_end - bucket_span * 3600
        in_bucket = [w for w in weighted if bucket_start <= w.observation.published_at.timestamp() <= bucket_end]
        if not in_bucket:
            continue

        bucket_weight = sum(w.weight for w in in_bucket) or 1e-9
        score = sum(w.normalized_score * w.weight for w in in_bucket) / bucket_weight
        bucket_time = datetime.fromtimestamp(bucket_end, tz=now.tzinfo)

        points.append(
            SentimentTimelinePointResult(
                time=bucket_time.strftime("%H:%M"),
                label=label_from_score(score),
                score=round(score),
            )
        )

    return points


def aggregate_sentiment(
    observations: list[SentimentObservation], symbol: str, now: datetime
) -> SymbolSentimentResult:
    weighted = _weigh_observations(observations, symbol, now)

    return SymbolSentimentResult(
        symbol=symbol,
        split=_compute_split(weighted),
        sources=_compute_sources(weighted),
        timeline=_compute_timeline(weighted, now),
    )
