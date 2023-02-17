"""
Main Api of the strava_webhook_service for metriker.
"""
import logging.config
import os
from typing import Dict

import requests
import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

# load environment variables
load_dotenv("../../dev.env")

SENTRY_DSN = os.getenv("METRIKER_SENTRY_DSN")

BASE_URL = os.getenv("METRIKER_INGESTION_SERVICE_URL")
TIMEOUT = 60

LOGGING_CONFIG_PATH = os.getenv("METRIKER_LOGGING_CONFIG_PATH", "../../logging.ini")

# setup logging
logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# setup logging to sentry
sentry_sdk.init(dsn=SENTRY_DSN)


class WebhookValidation(BaseModel):
    """
    Object expected in request from Strava to validate a webhook subscription.
    """

    mode: str = Field(..., alias="hub.mode")
    challenge: str = Field(..., alias="hub.challenge")
    verify_token: str = Field(..., alias="hub.verify_token")


class WebhookEvent(BaseModel):
    """
    Object expected in webhook request from strava.
    """

    object_type: str  # activity or athlete
    object_id: int  # activity_id if activity else user_id
    aspect_type: str  # create, update, delete
    updates: Dict
    owner_id: int  # user_id
    subscription_id: int
    event_time: int


def create(event: WebhookEvent) -> None:
    """
    Get newly created activity from strava after receiving create event.

    Args:
        event: WebhookEvent

    Returns:
        None
    """
    if event.object_type == "activity":
        user_id = str(event.owner_id)
        activity_id = str(event.object_id)
        requests.post(f"{BASE_URL}/updateUserActivityById?user_id={user_id}&activity_id={activity_id}", timeout=TIMEOUT)


def update(event: WebhookEvent) -> None:
    """
    Update athlete or activity after receiving update event.

    Args:
        event: WebhookEvent

    Returns:
        None
    """
    if event.object_type == "activity":
        user_id = str(event.owner_id)
        activity_id = str(event.object_id)
        requests.post(f"{BASE_URL}/updateUserActivityById?user_id={user_id}&activity_id={activity_id}", timeout=TIMEOUT)

    if event.object_type == "athlete":
        user_id = str(event.object_id)
        requests.post(f"{BASE_URL}/updateUserById?user_id={user_id}", timeout=TIMEOUT)


def delete(event: WebhookEvent) -> None:
    """
    Delete activity or athlete and all their activities after receiving delete event.

    Args:
        event: WebhookEvent

    Returns:
        None
    """
    if event.object_type == "activity":
        activity_id = event.object_id
        requests.delete(f"{BASE_URL}/deleteUserActivityById?activity_id={activity_id}", timeout=TIMEOUT)
    if event.object_type == "athlete":
        user_id = str(event.object_id)
        requests.delete(f"{BASE_URL}/deleteUserById?activity_id={user_id}", timeout=TIMEOUT)


app = FastAPI()


@app.get("/webhook")
def validation_webhook(webhook_validation: WebhookValidation):
    """
    Validate subscription to strava webhook by echoing challenge in response.

    Args:
        webhook_validation: WebhookValidation

    Returns:
        200, object with echo of "hub.challenge"
    """
    return {"hub.challenge": webhook_validation.challenge}


@app.post("/webhook")
def event_webhook(webhook_event: WebhookEvent):
    """
    Receive WebhookEvent from strava.

    Args:
        webhook_event: WebhookEvent

    Returns:
        200,
    """
    if webhook_event.aspect_type == "create":
        create(webhook_event)
    if webhook_event.aspect_type == "update":
        update(webhook_event)
    if webhook_event.aspect_type == "delete":
        delete(webhook_event)
