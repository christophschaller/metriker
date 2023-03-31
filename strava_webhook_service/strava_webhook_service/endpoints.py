"""
Endpoints of the strava_webhook_service for metriker.
"""

from fastapi import APIRouter

from .schemas import WebhookValidation, WebhookEvent
from .dependencies import create, update, delete

router = APIRouter()


@router.get("/webhook")
def validation_webhook(webhook_validation: WebhookValidation):
    """
    Validate subscription to strava webhook by echoing challenge in response.

    Args:
        webhook_validation: WebhookValidation

    Returns:
        200, object with echo of "hub.challenge"
    """
    return {"hub.challenge": webhook_validation.challenge}


@router.post("/webhook")
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
