"""Config for the flet webapp.

The config is read from env vars, .env files and default values in this order.
"""

from pydantic import AnyUrl, BaseSettings, SecretStr


class Settings(BaseSettings):
    """Settings Class storing all settings passed by env vars."""

    class Config:
        """Config Class defines how settings are loaded from .env files and which prefixes define them."""

        env_file = "./dev.env"
        env_file_encoding = "utf-8"
        env_prefix = "METRIKER_"

    ENVIRONMENT: str
    LOGGING_CONFIG_PATH: str = "./logging.ini"
    SENTRY_DSN: AnyUrl = None

    APP_PORT: int

    STRAVA_SERVICE_URL: AnyUrl
    STRAVA_SERVICE_TIMEOUT: int = 60

    STRAVA_CLIENT_ID: str
    STRAVA_CLIENT_SECRET: SecretStr
    STRAVA_AUTH_ENDPOINT: AnyUrl
    STRAVA_TOKEN_ENDPOINT: AnyUrl
    STRAVA_REDIRECT_URL: AnyUrl
    STRAVA_USER_ENDPOINT: AnyUrl
    STRAVA_USER_SCOPES: str

    DB_USER: str
    DB_PASS: SecretStr
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    SECRET_KEY: SecretStr


settings = Settings()
