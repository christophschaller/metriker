"""
This module provides the StravaUser dataclass and the StravaUserHandler.
StravaUser defines how a user we receive from strava is modeled on our side.
StravaUserHandler wraps basic data interactions regarding users.
"""
import logging
from dataclasses import dataclass
from typing import List

from flet.security import encrypt, decrypt

from database_utils import DatabaseConnector
from database_utils.schema import User

logger = logging.getLogger(__name__)
logger.info(__name__)


@dataclass
class StravaUser:
    """
    Dataclass defining how we model a user pulled from strava.
    """

    # we are shadowing names from the db so this is okayish here
    # pylint: disable=invalid-name
    id: str
    name: str
    refresh_token: str
    # pylint: enable=invalid-name


class StravaUserHandler(DatabaseConnector):
    """
    StravaUserHandler wraps basic data interactions regarding users pulled from strava.
    """

    def __init__(
        self,
        secret_key: str,
        user: str = None,
        password: str = None,
        host: str = None,
        port: str = None,
        database: str = None,
    ):
        """
        Args:
            secret_key: secret key for encryption of user tokens
            user: username to connect to the data service
            password: ...
            host: host url
            port: service port
            database: name of the target data
        """
        super().__init__(user=user, password=password, host=host, port=port, database=database)
        self.secret_key = secret_key

    def __getitem__(self, key: str) -> StravaUser:
        """
        Get user by key from data.
        Raises KeyError when user is not available.

        Args:
            key: id of the user on strava

        Returns:
            StravaUser
        """
        user = self.get(key)
        if not user:
            raise KeyError
        return user

    def get(self, user_id: str) -> (None, StravaUser):
        """
        Get user by user_id from data.
        Returns None when user is not available.

        Args:
            user_id: id of the user on strava

        Returns:
            StravaUser or None when user with given id is not available
        """
        logger.info("Get user: %s", user_id)
        user = self.session.query(User).filter(User.id == user_id).first()
        if user:
            return StravaUser(id=user.id, name=user.name, refresh_token=decrypt(user.refresh_token, self.secret_key))
        return None

    def add(self, user: StravaUser) -> None:
        """
        Add new StravaUser to data.

        Args:
            user: StravaUser

        Returns:
            None
        """
        logger.info("Add user: %s", user.id)
        new_user = User(id=user.id, name=user.name, refresh_token=encrypt(user.refresh_token, self.secret_key))
        self.insert(new_user)

    def update(self, user: StravaUser) -> None:
        """
        Update existing StravaUser in data.

        Args:
            user: StravaUser

        Returns:
            None
        """
        logger.info("Update user: %s", user.id)
        self.session.query(User).filter(User.id == user.id).update(
            {
                User.id: user.id,
                User.name: user.name,
                User.refresh_token: encrypt(user.refresh_token, self.secret_key),
            }
        )
        self.session.commit()

    def delete(self, user_id: str) -> None:
        """
        Delete existing StravaUser from data.

        Args:
            user_id: id of the user on strava

        Returns:
            None
        """
        logger.info("Delete user: %s", user_id)
        user = self.session.query(User).filter(User.id == user_id).first()
        self.session.delete(user)
        self.session.commit()

    def keys(self) -> List[str]:
        """
        Return a list containing all ids of users stored in the database.

        Returns:
            List of strings.
        """
        return self.session.query(User.id).all()

    def values(self) -> List[StravaUser]:
        """
        Returns a list of StravaUser objects for all users stored in the database.

        Returns:
            List of StravaUser objects.
        """
        return self.session.query(User).all()
