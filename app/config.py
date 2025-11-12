"""
Configuration management for Stock Screener application.
Handles environment variables and application settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application
    APP_NAME: str = "Stock Screener"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Rate Limiting for YFinance
    YFINANCE_REQUESTS_PER_MINUTE: int = 2000
    YFINANCE_DELAY_BETWEEN_REQUESTS: float = 0.5  # seconds

    # LLM Configuration
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_API_URL: str = "https://api.openai.com/v1/chat/completions"

    # Data Configuration
    HISTORICAL_DATA_YEARS: int = 2

    # Redis Keys
    REDIS_STOCK_LIST_KEY: str = "stocks:list"
    REDIS_STOCK_DATA_PREFIX: str = "stocks:data:"
    REDIS_RADAR_QUEUE_KEY: str = "stocks:radar"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
