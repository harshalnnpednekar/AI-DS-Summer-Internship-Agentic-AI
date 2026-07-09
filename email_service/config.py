import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

    SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)
    EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "EduAgent Notifications")

    SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8002))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    PROMETHEUS_METRICS_PATH = os.getenv("PROMETHEUS_METRICS_PATH", "/metrics")

    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", 5))


config = Config()
