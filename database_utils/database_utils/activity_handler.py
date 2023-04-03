"""This module provides the StravaActivity dataclass and the StravaActivityHandler.

StravaActivity defines how an activity we receive from strava is modeled on our side.
StravaActivityHandler wraps basic data interactions regarding activities.
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List

from database_utils import DatabaseConnector
from database_utils.schema import Activity

logger = logging.getLogger(__name__)
logger.info(__name__)


@dataclass
class StravaActivity:
    """Dataclass defining how we model activities pulled from strava."""

    # we are shadowing names from the db so this is okayish here
    id: str  # noqa: A003
    user_id: str
    name: str
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    sport_type: str
    start_date: datetime


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
        sport_type=activity["sport_type"],
        # the timezone we get from strava for this key is always utc
        start_date=datetime.strptime(activity["start_date"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc),
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
                sport_type=activity.sport_type,
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
            sport_type=activity.sport_type,
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
                Activity.sport_type: activity.sport_type,
                Activity.start_date: activity.start_date,
            },
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

    def get_user_activities(
        self,
        user_id: str,
        sport_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> List[StravaActivity]:
        """
         Return activity information for a userid

        Args:
            user_id: id of the user
            sport_type: sport type for e.g."Ride" (optional input, otherwise all sport types)
            start_date: start activity date for query (optional input, otherwise no starting date)
            end_date: end activity date for query (optional input, otherwise no ending date)

        Returns:
            StravaActivities which matches the specified input
        """
        query = self.session.query(Activity).filter(Activity.user_id == user_id)  # .all()

        if sport_type is not None:
            query = query.filter(Activity.sport_type == sport_type)
        if start_date is not None:
            query = query.filter(Activity.start_date >= start_date)
        if end_date is not None:
            query = query.filter(Activity.start_date <= end_date)

        activities = query.all()

        logger.info("got %s activities for user %s", len(activities), user_id)
        print("got %s activities for user %s", len(activities), user_id)

        return [
            StravaActivity(
                id=activity.id,
                user_id=activity.user_id,
                name=activity.name,
                distance=activity.distance,
                moving_time=activity.moving_time,
                elapsed_time=activity.elapsed_time,
                total_elevation_gain=activity.total_elevation_gain,
                sport_type=activity.sport_type,
                start_date=activity.start_date,
            )
            for activity in activities
        ]

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
