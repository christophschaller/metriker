"""Entrypoint of the metriker flet app."""
import logging.config

import flet as ft
import sentry_sdk
from database_utils.activity_handler import StravaActivityHandler
from database_utils.user_handler import StravaUserHandler
from flet.auth.oauth_provider import OAuthProvider

from .config import settings
from .metriker import Metriker

# setup logging
logging.config.fileConfig(settings.LOGGING_CONFIG_PATH, disable_existing_loggers=False)
logger = logging.getLogger(__name__)
# setup logging to sentry
sentry_sdk.init(dsn=settings.SENTRY_DSN)


def main(page: ft.Page) -> None:
    """Initialize all Components of the Metriker App.

    This function is meant to be called directly by flet.

    Args:
        page: page to display Metriker App to.

    Returns:
        None
    """
    auth_provider = OAuthProvider(
        client_id=settings.STRAVA_CLIENT_ID,
        client_secret=settings.STRAVA_CLIENT_SECRET.get_secret_value(),
        authorization_endpoint=settings.STRAVA_AUTH_ENDPOINT,
        token_endpoint=settings.STRAVA_TOKEN_ENDPOINT,
        redirect_url=settings.STRAVA_REDIRECT_URL,
        user_endpoint=settings.STRAVA_USER_ENDPOINT,
        # flet auth sends as iterable
        # strava endpoints wants a formatted string
        user_scopes=[settings.STRAVA_USER_SCOPES],
        user_id_fn=lambda user: user["id"],
    )
    # pylint:disable=duplicate-code
    user_handler = StravaUserHandler(
        secret_key=settings.SECRET_KEY.get_secret_value(),
        user=settings.DB_USER,
        password=settings.DB_PASS.get_secret_value(),
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
    )
    activity_handler = StravaActivityHandler(
        user=settings.DB_USER,
        password=settings.DB_PASS.get_secret_value(),
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
    )
    # pylint:enable=duplicate-code

    app = Metriker(
        page=page,
        auth_provider=auth_provider,
        activity_handler=activity_handler,
        user_handler=user_handler,
        strava_service_url=settings.STRAVA_SERVICE_URL,
    )
    page.add(app)
    app.initialize()
