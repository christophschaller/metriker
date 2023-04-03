"""This module provides a wrapper for the strava REST api."""
import logging
import time
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Dict, List

import requests
from database_utils.user_handler import StravaUserHandler

logger = logging.getLogger(__name__)
logger.info(__name__)


class TokenRefreshFailed(requests.RequestException):
    """No Access Token was returned."""

    def __init__(self, cause: str) -> None:
        """Init of TokenRefreshFailed Exception.

        Args:
            cause: content of the response to the token refresh request
        """
        super().__init__(f"Requesting Access Token Failed: {cause}")


class DailyRateLimitExceeded(requests.RequestException):
    """The rate limit was exceeded."""

    def __init__(self) -> None:
        """Init of DailyRateLimitExceeded Exception."""
        super().__init__("Daily Rate Limit Exceeded")


def sleep_until_next_quarter() -> None:
    """Get the time interval until the next quarter and sleep till then.

    Returns:
        None
    """
    now = datetime.now(tz=timezone.utc)
    # get timedelta to the next full 15 minutes
    delta = timedelta(minutes=15 - now.minute % 15, seconds=-now.second)
    logger.warning("Sleeping %s until next full quarter", delta.seconds)
    # add a safety second and sleep
    time.sleep(delta.seconds + 1)


class StravaHandler:
    """Wrapper for Strava REST Api."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_handler: StravaUserHandler,
    ) -> None:
        """Wrapper for Strava REST Api.

        Args:
            client_id: client_id of application on strava
            client_secret: client_secret of application on strava
            user_handler: wrapper class to handle strava users.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_handler: StravaUserHandler = user_handler

        # these values will track the usage reported in the headers of api responses
        self.limit_daily = 1000
        self.limit_15_min = 100
        self.usage_daily = 0
        self.usage_15_min = 0

        self.timeout = 15

    def _request_access_token(self, user_id: str) -> str:
        """Exchange refresh token for access token and return it.

        Args:
            user_id: user_id on strava for user to get the token for

        Returns:
            access_token
        """
        auth_url = "https://www.strava.com/oauth/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.user_handler[user_id].refresh_token,
            "grant_type": "refresh_token",
        }

        self._rate_limit()
        response = requests.request(method="post", url=auth_url, data=data, timeout=self.timeout)
        self._track_rate_limit(response)

        if response.ok:
            self.user_handler[user_id].refresh_token = response.json()["refresh_token"]
            return response.json()["access_token"]

        logger.error("Requesting Access Token Failed: %s", response.json())
        raise TokenRefreshFailed(response.content)

    def _track_rate_limit(self, response: requests.Response) -> None:
        """Read rate limits information from response header and track it in class values.

        Args:
            response: requests.Response object from strava REST Api

        Returns:
            None
        """
        limit = response.headers.get("X-RateLimit-Limit")
        if limit:
            limit_15_min, limit_daily = limit.split(",")
            self.limit_15_min, self.limit_daily = int(limit_15_min), int(limit_daily)
        else:
            logger.info("No Rate Limit Information In Headers")

        usage = response.headers.get("X-RateLimit-Usage")
        if usage:
            usage_15_min, usage_daily = usage.split(",")
            self.usage_15_min, self.usage_daily = int(usage_15_min), int(usage_daily)
        else:
            logger.info("No Usage Information In Headers")

    def _rate_limit(self) -> None:
        """Check if any rate limits are reached and throttle requests accordingly.

        Returns:
            None
        """
        if self.usage_daily >= self.limit_daily:
            logger.error("Daily Rate Limit Exceeded")
            raise DailyRateLimitExceeded

        if self.usage_15_min >= self.limit_15_min:
            logger.warning("15min Rate Limit Exceeded")
            sleep_until_next_quarter()
            self.usage_15_min = 0

    def _request(  # noqa: PLR0913 - Ignore: Too many arguments to function call
        self,
        user_id: str,
        method: str,
        url: str,
        data: Dict = None,
        params: Dict = None,
    ) -> (None, requests.Response):
        """Wrap request to strava REST Api.

        This handles rate limits and authentication.

        Args:
            user_id: id of the user on strava
            method: method of request to the api
            url: target url
            data: data to pass with request
            params: params to pass with request

        Returns:
            requests.Response
        """
        access_token = self._request_access_token(user_id)

        self._rate_limit()
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            params=params,
            timeout=self.timeout,
        )
        self._track_rate_limit(response)

        if response.ok:
            return response

        if not response.ok:
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                # 401 Unauthorized
                # we already got the access token, so this should be a scope issue,
                # or we don't know what is going on
                logger.warning("Got response: 401 Unauthorized")
            if response.status_code == HTTPStatus.FORBIDDEN:
                # Forbidden; you cannot access
                logger.warning("Got response: 403 Resource is forbidden")
            if response.status_code == HTTPStatus.NOT_FOUND:
                # Not found; the requested asset does not exist, or you are not authorized to see it
                logger.warning("Got response: 404 Resource not found")
            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                # Too Many Requests; you have exceeded rate limits
                logger.warning("Got response: 429 Requests Limit Exceeded")
            if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
                # Strava is having issues
                logger.warning("Got response: 500 Strava is probably having issues")

        return None

    def get_logged_in_athlete(self, user_id: str) -> Dict:
        """Implements getLoggedInAthlete endpoint.

        https://developers.strava.com/docs/reference/#api-Athletes-getLoggedInAthlete

        Args:
            user_id: id of the user to get information for

        Returns:
            detailed athlete object as defined by strava
            https://developers.strava.com/docs/reference/#api-models-DetailedAthlete
        """
        endpoint_url = "https://www.strava.com/api/v3/athlete"
        response = self._request(user_id=user_id, method="get", url=endpoint_url)
        return response.json()

    def get_activity_by_id(self, user_id: str, activity_id: str) -> Dict:
        """Implements getActivityById endpoint.

        https://developers.strava.com/docs/reference/#api-Activities-getActivityById

        Args:
            user_id: id of user the activity belongs to
            activity_id: id of the activity to request

        Returns:
            detailed activity object as defined on strava
            https://developers.strava.com/docs/reference/#api-models-DetailedActivity
        """
        activity_url = f"https://www.strava.com/api/v3/activities/{activity_id}"
        params = {"include_all_efforts": False}  # we don't use those
        response = self._request(user_id=user_id, method="get", url=activity_url, params=params)
        return response.json()

    def get_logged_in_athlete_activities(
        self,
        user_id: str,
        before: datetime = None,
        after: datetime = None,
    ) -> List[Dict]:
        """Implements getLoggedInAthleteActivities endpoint.

        https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities

        Args:
            user_id: id of user the activity belongs to
            before: end of time interval to return activities for
            after: start of time interval to return activities for

        Returns:
            list of detailed activity objects as defined on strava
            https://developers.strava.com/docs/reference/#api-models-DetailedActivity
        """
        activities_url = "https://www.strava.com/api/v3/athlete/activities"
        params = {
            "per_page": "200",  # defaults to 30
            "page": 1,  # defaults to 1
            "before": int(before.timestamp()) if before else None,
            "after": int(after.timestamp()) if after else None,
        }

        activities = []
        current_page = 1
        # run request new pages until we get less activities back than we requested
        while True:
            params["page"] = current_page
            response = self._request(user_id=user_id, method="get", url=activities_url, params=params)
            content = response.json()
            activities.extend(content)

            # if content len is smaller than the amount of activities we requested per
            # page we should have gotten everything available and can stop requesting
            if len(content) < int(params["per_page"]):
                break
            # increase page number
            current_page += 1
            params["page"] = current_page

        return activities
