"""Schemas for the Object expected in webhook events and validation."""
from typing import Dict

from pydantic import BaseModel, Field


class WebhookValidation(BaseModel):
    """Object expected in request from Strava to validate a webhook subscription."""

    mode: str = Field(..., alias="hub.mode")
    challenge: str = Field(..., alias="hub.challenge")
    verify_token: str = Field(..., alias="hub.verify_token")


class WebhookEvent(BaseModel):
    """Object expected in webhook request from strava."""

    object_type: str  # activity or athlete
    object_id: int  # activity_id if activity else user_id
    aspect_type: str  # create, update, delete
    updates: Dict
    owner_id: int  # user_id
    subscription_id: int
    event_time: int
