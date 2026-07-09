import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    EMAIL_SERVICE_URL = os.getenv("EMAIL_SERVICE_URL", "http://localhost:8002")
    SCHEDULER_INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", 5))
    SCHEDULER_INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", 5))
    NOTIFICATION_WINDOW_DAYS = int(os.getenv("NOTIFICATION_WINDOW_DAYS", 3))
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MOCK_API_ENABLED = os.getenv("MOCK_API_ENABLED", "false").lower() == "true"
    MOCK_API_PORT = int(os.getenv("MOCK_API_PORT", 8001))


class DevelopmentConfig(Config):
    DEBUG = True
    MOCK_API_ENABLED = True


class ProductionConfig(Config):
    DEBUG = False
    MOCK_API_ENABLED = False


config = DevelopmentConfig() if os.getenv("ENV") == "development" else ProductionConfig()
