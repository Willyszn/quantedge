from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SentimentObservationModel(Base):
    __tablename__ = "sentiment_observations"

    id: Mapped[str] = mapped_column(String(200), primary_key=True)
    headline: Mapped[str] = mapped_column(String(500))
    source_name: Mapped[str] = mapped_column(String(120))
    source_type: Mapped[str] = mapped_column(String(20))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    entities: Mapped[str] = mapped_column(String(500))  # comma-separated
    raw_sentiment_score: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
