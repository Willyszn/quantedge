"""
MockSentimentProvider (spec section 14). Generates deterministic, seeded
sentiment observations across all four source types. Used when
SENTIMENT_PROVIDER=mock — the default until a real news/social API key is
configured. Clearly a development data source: aggregation.py runs the same
real weighting/relevance logic against it as it would against
NewsSentimentProvider output.
"""

import hashlib
import random
from datetime import UTC, datetime, timedelta

from app.sentiment.provider_base import SentimentObservation, SentimentProvider, SentimentSourceType

HEADLINE_TEMPLATES: dict[SentimentSourceType, list[tuple[str, list[str], float]]] = {
    SentimentSourceType.NEWS: [
        (
            "Fed officials signal patience on rate cuts amid sticky inflation",
            ["usd", "fed", "inflation", "interest-rates"],
            -0.2,
        ),
        ("US inflation data comes in cooler than expected", ["usd", "inflation", "fed"], 0.35),
        (
            "Gold climbs as investors seek safe-haven amid geopolitical tension",
            ["gold", "safe-haven", "geopolitical"],
            0.5,
        ),
        (
            "Bank of England holds rates, cites persistent wage growth",
            ["gbp", "boe", "interest-rates"],
            -0.1,
        ),
        (
            "Tech earnings beat expectations, lifting index futures",
            ["equities", "tech-earnings"],
            0.45,
        ),
        (
            "ECB minutes reveal growing divide on pace of easing",
            ["eur", "ecb", "interest-rates"],
            -0.15,
        ),
    ],
    SentimentSourceType.COMMENTARY: [
        (
            "Strategists flag stretched positioning in dollar longs",
            ["usd", "risk-sentiment"],
            -0.25,
        ),
        ("Analysts see further upside for gold into year-end", ["gold", "safe-haven"], 0.4),
        (
            "Desk note: risk appetite improving into the session",
            ["risk-sentiment", "equities"],
            0.3,
        ),
        ("Commentary: yen weakness likely to persist near-term", ["jpy", "boj"], -0.3),
    ],
    SentimentSourceType.SOCIAL: [
        ("Retail chatter turns cautious on further USD strength", ["usd", "risk-sentiment"], -0.2),
        ("Crypto community optimism builds ahead of ETF flows data", ["crypto", "bitcoin"], 0.5),
        (
            "Social sentiment on equities ticks up after strong session",
            ["equities", "risk-sentiment"],
            0.25,
        ),
        ("Growing social skepticism around near-term ETH upside", ["ethereum", "crypto"], -0.2),
    ],
    SentimentSourceType.MACRO: [
        (
            "Macro desk: global growth data broadly resilient this quarter",
            ["risk-sentiment", "equities"],
            0.3,
        ),
        (
            "Rising geopolitical risk keeps safe-haven bid supported",
            ["geopolitical", "safe-haven", "gold"],
            0.35,
        ),
        (
            "Macro outlook: central banks converging toward easing cycle",
            ["fed", "ecb", "boe", "interest-rates"],
            0.15,
        ),
        (
            "Commodity-linked currencies pressured by softer demand outlook",
            ["risk-sentiment"],
            -0.2,
        ),
    ],
}

SOURCE_NAMES: dict[SentimentSourceType, list[str]] = {
    SentimentSourceType.NEWS: ["Reuters", "Bloomberg", "Financial Times"],
    SentimentSourceType.COMMENTARY: ["Desk Notes", "Strategy Weekly"],
    SentimentSourceType.SOCIAL: ["Social Pulse", "Retail Sentiment Tracker"],
    SentimentSourceType.MACRO: ["Macro Monitor", "Global Rates Desk"],
}


def _seeded_random(*parts: str) -> random.Random:
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


class MockSentimentProvider(SentimentProvider):
    name = "mock"

    async def is_healthy(self) -> bool:
        return True

    async def get_observations(self, symbol: str, lookback_hours: int = 24) -> list[SentimentObservation]:
        day_key = datetime.now(UTC).strftime("%Y-%m-%d")
        rand = _seeded_random(symbol, "sentiment", day_key)
        now = datetime.now(UTC)

        observations: list[SentimentObservation] = []
        obs_id = 0
        for source_type, templates in HEADLINE_TEMPLATES.items():
            names = SOURCE_NAMES[source_type]
            for headline, entities, base_score in templates:
                if rand.random() < 0.35:
                    continue  # not every template fires every day
                obs_id += 1
                jitter = rand.uniform(-0.15, 0.15)
                age_hours = rand.uniform(0.5, lookback_hours)
                observations.append(
                    SentimentObservation(
                        id=f"{symbol.lower()}-obs-{obs_id}",
                        headline=headline,
                        source_name=rand.choice(names),
                        source_type=source_type,
                        published_at=now - timedelta(hours=age_hours),
                        entities=entities,
                        raw_sentiment_score=max(-1.0, min(1.0, base_score + jitter)),
                        confidence=round(rand.uniform(0.55, 0.95), 2),
                    )
                )

        return observations
