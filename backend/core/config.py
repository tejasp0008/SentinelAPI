"""SentinelAPI — Application Configuration."""

import secrets
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "SentinelAPI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # Database (SQLite for local dev; set env var for Postgres in Docker)
    DATABASE_URL: str = "sqlite:///./sentinel_dev.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # JWT Authentication
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # Rate Limiting
    RATE_LIMIT: str = "60/minute"

    # AI Engine
    AI_RISK_THRESHOLD: int = 75
    CNN_WEIGHT: float = 0.4
    NLP_WEIGHT: float = 0.3
    ISOLATION_FOREST_WEIGHT: float = 0.3

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
