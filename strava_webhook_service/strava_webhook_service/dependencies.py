"""
Logic to execute the updates and changes to our data we get from webhook events.
"""
import requests

from .schemas import WebhookEvent
from .config import settings


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
        requests.post(
            f"{settings.STRAVA_SERVICE_URL}/updateUserActivityById?user_id={user_id}&activity_id={activity_id}",
            timeout=settings.STRAVA_SERVICE_TIMEOUT,
        )


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
        requests.post(
            f"{settings.STRAVA_SERVICE_URL}/updateUserActivityById?user_id={user_id}&activity_id={activity_id}",
            timeout=settings.STRAVA_SERVICE_TIMEOUT,
        )

    if event.object_type == "athlete":
        user_id = str(event.object_id)
        requests.post(
            f"{settings.STRAVA_SERVICE_URL}/updateUserById?user_id={user_id}", timeout=settings.STRAVA_SERVICE_TIMEOUT
        )


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
        requests.delete(
            f"{settings.STRAVA_SERVICE_URL}/deleteUserActivityById?activity_id={activity_id}",
            timeout=settings.STRAVA_SERVICE_TIMEOUT,
        )
    if event.object_type == "athlete":
        user_id = str(event.object_id)
        requests.delete(
            f"{settings.STRAVA_SERVICE_URL}/deleteUserById?activity_id={user_id}",
            timeout=settings.STRAVA_SERVICE_TIMEOUT,
        )
