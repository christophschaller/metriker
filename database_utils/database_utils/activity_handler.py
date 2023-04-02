"""This module provides the StravaActivity dataclass and the StravaActivityHandler.

StravaActivity defines how an activity we receive from strava is modeled on our side.
StravaActivityHandler wraps basic data interactions regarding activities.
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from database_utils import DatabaseConnector
from database_utils.schema import Activity

logger = logging.getLogger(__name__)
logger.info(__name__)


@dataclass
class StravaActivity:
    """Dataclass defining how we model activities pulled from strava."""

    # we are shadowing names from the db so this is okayish here
    # pylint: disable=invalid-name
    id: str
    user_id: str
    name: str
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    type: str
    start_date: datetime
    # pylint: enable=invalid-name


def parse_activity(activity: Dict) -> StravaActivity:
    """Parse activity object received from strava api to StravaActivity object.

    Args:
        activity: detailed activity object from strava api

    Returns:
        StravaActivity
    """
    return StravaActivity(
        id=str(activity["id"]),
        user_id=str(activity["athlete"]["id"]),
        name=activity["name"],
        distance=activity.get("distance"),
        moving_time=activity["moving_time"] if activity.get("moving_time") else None,
        elapsed_time=activity["elapsed_time"] if activity.get("elapsed_time") else None,
        total_elevation_gain=activity.get("total_elevation_gain"),
        type=activity["sport_type"],
        start_date=datetime.strptime(activity["start_date"], "%Y-%m-%dT%H:%M:%SZ"),
    )


class StravaActivityHandler(DatabaseConnector):
    """StravaActivityHandler wraps basic data interactions regarding activities pulled from strava in our data."""

    def __getitem__(self, key: str) -> StravaActivity:
        """Get activity by key from data.

        Raises KeyError when activity is not available.

        Args:
            key: id of the activity on strava

        Returns:
            StravaActivity
        """
        activity = self.get(key)
        if not activity:
            raise KeyError
        return activity

    def get(self, activity_id: str) -> (None, StravaActivity):
        """Get activity by activity_id from data.

        Returns None when activity is not available.

        Args:
            activity_id: id of the activity on strava

        Returns:
            StravaActivity or None when activity with given id is not available
        """
        logger.info("Get activity: %s", activity_id)
        activity = self.session.query(Activity).filter(Activity.id == activity_id).first()
        if activity:
            return StravaActivity(
                id=activity.id,
                user_id=activity.user_id,
                name=activity.name,
                distance=activity.distance,
                moving_time=activity.moving_time,
                elapsed_time=activity.elapsed_time,
                total_elevation_gain=activity.total_elevation_gain,
                type=activity.type,
                start_date=activity.start_date,
            )
        logger.info("Unknown Activity: %s", activity_id)
        return None

    def add(self, activity: StravaActivity) -> None:
        """Add new StravaActivity to data.

        Args:
            activity: StravaActivity

        Returns:
            None
        """
        logger.info("Add activity: %s", activity.id)
        new_activity = Activity(
            id=activity.id,
            user_id=activity.user_id,
            name=activity.name,
            distance=activity.distance,
            moving_time=activity.moving_time,
            elapsed_time=activity.elapsed_time,
            total_elevation_gain=activity.total_elevation_gain,
            type=activity.type,
            start_date=activity.start_date,
        )
        self.insert(new_activity)

    def update(self, activity: StravaActivity) -> None:
        """Update existing StravaActivity in data.

        Args:
            activity: StravaActivity

        Returns:
            None
        """
        logger.info("Update activity: %s", activity.id)
        self.session.query(Activity).filter(Activity.id == activity.id).update(
            {
                Activity.id: activity.id,
                Activity.user_id: activity.user_id,
                Activity.name: activity.name,
                Activity.distance: activity.distance,
                Activity.moving_time: activity.moving_time,
                Activity.elapsed_time: activity.elapsed_time,
                Activity.total_elevation_gain: activity.total_elevation_gain,
                Activity.type: activity.type,
                Activity.start_date: activity.start_date,
            }
        )
        self.session.commit()

    def delete(self, activity_id: str) -> None:
        """Delete existing StravaActivity from data.

        Args:
            activity_id: id of the activity on strava

        Returns:
            None
        """
        logger.info("Delete activity: %s", activity_id)
        activity = self.session.query(Activity).filter(Activity.id == activity_id).first()
        self.session.delete(activity)
        self.session.commit()

    def delete_user_activities(self, user_id: str) -> None:
        """Delete all existing StravaActivity for a given user_id from data.

        Args:
            user_id: id of the user on strava

        Returns:
            None
        """
        logger.info("Delete all activities for user: %s", user_id)
        activity_id_list = self.session.query(Activity.id).filter(Activity.user_id == user_id).all()

        for activity_id in activity_id_list:
            self.delete(activity_id)
