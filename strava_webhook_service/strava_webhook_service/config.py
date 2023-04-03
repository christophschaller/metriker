"""Config for the webhook service.

The config is read from env vars, .env files and default values in this order.
"""
from pydantic import AnyUrl, BaseSettings


class Settings(BaseSettings):
    """Settings Class storing all settings passed by env vars."""

    class Config:
        """Config Class defines how settings are loaded from .env files and which prefixes define them."""

        env_file = "./dev.env"
        env_file_encoding = "utf-8"
        env_prefix = "METRIKER_"

    ENVIRONMENT: str
    STRAVA_SERVICE_URL: AnyUrl
    STRAVA_SERVICE_TIMEOUT: int = 60
    LOGGING_CONFIG_PATH: str = "./logging.ini"
    SENTRY_DSN: AnyUrl = None


settings = Settings()
