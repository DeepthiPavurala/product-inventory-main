from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"

    APP_ENV: str = "local"
    LOG_LEVEL: str = "INFO"

    LOW_STOCK_THRESHOLD: int = 5
    LOW_STOCK_ALERT_TO: str = "deepthipavurala@gmail.com"
    LOW_STOCK_ALERT_FROM: str = "deepthipavurala04@gmail.com"

    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()