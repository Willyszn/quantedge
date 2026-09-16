from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration. Every tunable value in QUANTEDGE lives here or in
    app/core/scoring_config.py (for the quant/signal weight constants) —
    never scattered as magic numbers through services.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    ENVIRONMENT: Literal["development", "test", "production"] = "development"
    SECRET_KEY: str = "dev-secret-change-me"
    API_V1_PREFIX: str = ""

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://quantedge:quantedge@localhost:5432/quantedge"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://quantedge:quantedge@localhost:5432/quantedge"

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # --- Market data provider ---
    MARKET_DATA_PROVIDER: Literal["mock", "mt5"] = "mock"
    MT5_ENABLED: bool = False
    MT5_SERVER: str = ""
    MT5_LOGIN: str = ""
    MT5_PASSWORD: str = ""

    # --- Sentiment provider ---
    SENTIMENT_PROVIDER: Literal["mock", "news"] = "mock"
    NEWS_PROVIDER: str = ""
    NEWS_API_KEY: str = ""

    # --- Seeding ---
    SEED_ON_STARTUP: bool = True

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
