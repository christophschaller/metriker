"""
Config for the flet webapp.
The config is read from env vars, .env files and default values in this order.
"""
# pylint:disable=duplicate-code
from pydantic import AnyUrl, BaseSettings


class Settings(BaseSettings):
    """
    Settings Class storing all settings passed by env vars.
    """

    class Config:
        """
        Config Class defines how settings are loaded from .env files and which prefixes define them.
        """

        env_file = "../../dev.env"
        env_file_encoding = "utf-8"
        env_prefix = "METRIKER_"

    ENVIRONMENT: str

    STRAVA_CLIENT_ID = str
    STRAVA_CLIENT_SECRET = str
    STRAVA_AUTH_ENDPOINT = AnyUrl
    STRAVA_TOKEN_ENDPOINT = AnyUrl
    STRAVA_REDIRECT_URL = AnyUrl
    STRAVA_USER_ENDPOINT = AnyUrl
    STRAVA_USER_SCOPES = str

    DB_USER = str
    DB_PASS = str
    DB_HOST = AnyUrl
    DB_PORT = int
    DB_NAME = str

    STRAVA_SERVICE_URL: AnyUrl
    STRAVA_SERVICE_TIMEOUT: int = 60

    SECRET_KEY = str

    LOGGING_CONFIG_PATH: str = "../../logging.ini"
    SENTRY_DSN: AnyUrl = None


settings = Settings()

# pylint:enable=duplicate-code
