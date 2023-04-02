"""Main Api of the strava_webhook_service for metriker.

This service will wait for calls from strava telling to update our data or request new activities.
"""
# pylint:disable=duplicate-code
import logging.config

import sentry_sdk
from fastapi import FastAPI

from . import endpoints
from .config import settings

# setup logging
logging.config.fileConfig(settings.LOGGING_CONFIG_PATH, disable_existing_loggers=False)
logger = logging.getLogger(__name__)
# setup logging to sentry
sentry_sdk.init(dsn=settings.SENTRY_DSN)

SHOW_DOCS_ENVIRONMENT = ("local",)

app_config = {}
# disable openapi docs if not in local environment
if settings.ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
    app_config["openapi_url"] = None

app = FastAPI(**app_config)
app.include_router(endpoints.router)

# pylint:enable=duplicate-code
