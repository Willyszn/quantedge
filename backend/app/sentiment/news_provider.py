"""
NewsSentimentProvider (spec section 14). Real integration point for a news
API. Two things kept honest here:

1. Without NEWS_API_KEY configured, this provider raises ProviderError
   rather than returning fabricated observations — the sentiment service
   falls back to MockSentimentProvider only when SENTIMENT_PROVIDER=mock is
   explicitly configured, never silently.
2. Scoring/labeling raw article text (raw_sentiment_score) is left as a
   pluggable `_score_headline` hook. A production deployment would plug in
   a real financial sentiment model (e.g. a FinBERT-style classifier) here;
   this file focuses on the provider *contract* — fetching, normalizing,
   and rate-limiting — since committing to a specific model is a product
   decision beyond this backend build.
"""

from datetime import UTC, datetime

import httpx

from app.core.config import get_settings
from app.core.errors import ProviderError
from app.core.logging import get_logger
from app.sentiment.provider_base import SentimentObservation, SentimentProvider, SentimentSourceType

logger = get_logger(__name__)


class NewsSentimentProvider(SentimentProvider):
    name = "news"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def is_healthy(self) -> bool:
        return bool(self.settings.NEWS_API_KEY and self.settings.NEWS_PROVIDER)

    async def get_observations(self, symbol: str, lookback_hours: int = 24) -> list[SentimentObservation]:
        if not self.settings.NEWS_API_KEY or not self.settings.NEWS_PROVIDER:
            raise ProviderError(
                "News sentiment provider is not configured. Set NEWS_PROVIDER and "
                "NEWS_API_KEY, or set SENTIMENT_PROVIDER=mock for development.",
                code="SENTIMENT_PROVIDER_NOT_CONFIGURED",
            )

        # Example against a generic "everything" style news search API.
        # Adjust the request shape to match whichever NEWS_PROVIDER is used.
        params = {
            "q": symbol,
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": self.settings.NEWS_API_KEY,
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(f"https://{self.settings.NEWS_PROVIDER}/v2/everything", params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError as exc:
            logger.warning("news_provider_error", extra={"event": "news_provider_error", "reason": str(exc)})
            raise ProviderError("News provider request failed.", code="NEWS_PROVIDER_UNAVAILABLE") from exc

        observations = []
        for article in payload.get("articles", []):
            headline = article.get("title", "")
            observations.append(
                SentimentObservation(
                    id=article.get("url", headline),
                    headline=headline,
                    source_name=article.get("source", {}).get("name", "Unknown"),
                    source_type=SentimentSourceType.NEWS,
                    published_at=self._parse_time(article.get("publishedAt")),
                    entities=[symbol.lower()],
                    raw_sentiment_score=self._score_headline(headline),
                    confidence=0.6,
                )
            )
        return observations

    @staticmethod
    def _parse_time(value: str | None) -> datetime:
        if not value:
            return datetime.now(UTC)
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now(UTC)

    @staticmethod
    def _score_headline(headline: str) -> float:
        """
        Minimal placeholder keyword scorer so this provider is runnable
        end-to-end without a model dependency. Replace with a real
        financial sentiment classifier before relying on this in
        production — see module docstring.
        """
        positive_words = {
            "beat",
            "beats",
            "climb",
            "climbs",
            "rally",
            "rallies",
            "surge",
            "gains",
            "optimism",
            "cooler",
        }
        negative_words = {
            "fall",
            "falls",
            "drop",
            "drops",
            "slump",
            "slumps",
            "fear",
            "fears",
            "sticky",
            "concern",
            "concerns",
        }
        words = set(headline.lower().split())
        score = len(words & positive_words) - len(words & negative_words)
        return max(-1.0, min(1.0, score * 0.3))
