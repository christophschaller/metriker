"""Endpoints of the strava_ingestion_service for metriker."""

from database_utils.activity_handler import StravaActivityHandler, parse_activity
from database_utils.user_handler import StravaUserHandler
from fastapi import APIRouter

from .config import settings
from .strava_handler import StravaHandler

# initiate database wrappers
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

# initiate strava api wrapper
strava_handler = StravaHandler(
    client_id=settings.STRAVA_CLIENT_ID,
    client_secret=settings.STRAVA_CLIENT_SECRET.get_secret_value(),
    user_handler=user_handler,
)

router = APIRouter()


@router.post("/updateUserById")
def update_user_by_id(user_id: str) -> None:
    """Request information about a user from the strava api.

    Args:
        user_id: id of the user on strava

    Returns:
        200, None
    """
    old_user = user_handler.get(user_id)
    new_user = strava_handler.get_logged_in_athlete(user_id=user_id)
    old_user.name = new_user["firstname"]
    user_handler.update(old_user)


@router.post("/updateUserActivityById")
def update_user_activity_by_id(activity_id: str, user_id: str) -> None:
    """Request a single activity from the strava api.

    The activity is defined by activity_id and belongs to user_id.

    Args:
        activity_id: id of the activity on strava
        user_id: id of the user the activity belongs to on strava

    Returns:
        200, None
    """
    activity = strava_handler.get_activity_by_id(user_id=user_id, activity_id=activity_id)
    activity_handler.add(parse_activity(activity))


@router.post("/updateUserActivities")
def update_user_activities(user_id: str) -> None:
    """Request all activities of a user from the strava api.

    Args:
        user_id: id of the user on strava

    Returns:
        200, None
    """
    activities = strava_handler.get_logged_in_athlete_activities(user_id)
    for activity in activities:
        activity_handler.add(parse_activity(activity))


@router.delete("/deleteUserActivityById")
def delete_user_activity_by_id(activity_id: str) -> None:
    """Request all activities of a user from the strava api.

    Args:
        activity_id: id of the user on strava

    Returns:
        200, None
    """
    activity_handler.delete(activity_id)


@router.delete("/deleteUserById")
def delete_user_by_id(user_id: str) -> None:
    """Request all activities of a user from the strava api.

    Args:
        user_id: id of the user on strava

    Returns:
        200, None
    """
    activity_handler.delete_user_activities(user_id)
    user_handler.delete(user_id)
