# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/event_notification_db"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    JWT_ALGORITHM: str = "HS256"

    # Application
    DEBUG: bool = True
    APP_NAME: str = "EduAgent"
    PROJECT_NAME: str = "College Event Notification System"
    VERSION: str = "1.0.0"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]

    # Email Settings
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: Optional[str] = None
    EMAIL_FROM_NAME: str = "EduAgent Notifications"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()