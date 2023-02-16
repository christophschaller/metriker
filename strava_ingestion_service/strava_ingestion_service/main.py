"""
Main Api of the strava_ingestion_service for metriker.
"""
import logging.config
import os

import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI

from database_utils.activity_handler import StravaActivityHandler, parse_activity
from database_utils.user_handler import StravaUserHandler
from .strava_handler import StravaHandler

# load environment variables
load_dotenv("../../dev.env")

SENTRY_DSN = os.getenv("METRIKER_SENTRY_DSN")

STRAVA_CLIENT_ID = os.getenv("METRIKER_STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("METRIKER_STRAVA_CLIENT_SECRET")

DB_USER = os.getenv("METRIKER_DB_USER")
DB_PASS = os.getenv("METRIKER_DB_PASS")
DB_HOST = os.getenv("METRIKER_DB_HOST")
DB_PORT = os.getenv("METRIKER_DB_PORT")
DB_NAME = os.getenv("METRIKER_DB_NAME")

SECRET_KEY = os.getenv("METRIKER_SECRET_KEY")

LOGGING_CONFIG_PATH = os.getenv("METRIKER_LOGGING_CONFIG_PATH", "../../logging.ini")

# setup logging
logging.config.fileConfig(LOGGING_CONFIG_PATH, disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# setup logging to sentry
sentry_sdk.init(dsn=SENTRY_DSN)

# initiate database wrappers
user_handler = StravaUserHandler(
    secret_key=SECRET_KEY, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, database=DB_NAME
)
activity_handler = StravaActivityHandler(user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, database=DB_NAME)
strava_handler = StravaHandler(
    client_id=STRAVA_CLIENT_ID, client_secret=STRAVA_CLIENT_SECRET, user_handler=user_handler
)

# create app
app = FastAPI()


@app.post("/updateUserById")
def update_user_by_id(user_id: str):
    """
    Request information about a user from the strava api.

    Args:
        user_id: id of the user on strava

    Returns:
        200,
    """
    old_user = user_handler.get(user_id)
    new_user = strava_handler.get_logged_in_athlete(user_id=user_id)
    old_user.name = new_user["firstname"]
    user_handler.update(old_user)


@app.post("/updateUserActivityById")
def update_user_activity_by_id(activity_id: str, user_id: str):
    """
    Request a single activity from the strava api.
    The activity is defined by activity_id and belongs to user_id.

    Args:
        activity_id: id of the activity on strava
        user_id: id of the user the activity belongs to on strava

    Returns:
        200,
    """
    activity = strava_handler.get_activity_by_id(user_id=user_id, activity_id=activity_id)
    activity_handler.add(parse_activity(activity))


@app.post("/updateUserActivities")
def update_user_activities(user_id: str):
    """
    Request all activities of a user from the strava api.

    Args:
        user_id: id of the user on strava

    Returns:
        200,
    """
    activities = strava_handler.get_logged_in_athlete_activities(user_id)
    for activity in activities:
        activity_handler.add(parse_activity(activity))


@app.delete("/deleteUserActivityById")
def delete_user_activity_by_id(activity_id: str):
    """
    Request all activities of a user from the strava api.

    Args:
        activity_id: id of the user on strava

    Returns:
        200,
    """
    activity_handler.delete(activity_id)


@app.delete("/deleteUserById")
def delete_user_by_id(user_id: str):
    """
    Request all activities of a user from the strava api.

    Args:
        user_id: id of the user on strava

    Returns:
        200,
    """
    activity_handler.delete_user_activities(user_id)
    user_handler.delete(user_id)
