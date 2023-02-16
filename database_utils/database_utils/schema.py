"""
Module containing ORM schemas.
"""
from sqlalchemy.orm import declarative_base
import sqlalchemy as sa

Base = declarative_base()


class User(Base):
    """
    User, identified by user id and name, containing encrypted refresh token for api access.
    """

    __tablename__ = "user"

    id = sa.Column(sa.String(36), primary_key=True)
    name = sa.Column(sa.TEXT)
    refresh_token = sa.Column(sa.TEXT)

    def __repr__(self):
        return f"USER: {self.name}\tID: {self.id}"


class Activity(Base):
    """
    Activity, identified by id, belonging to user.
    """

    __tablename__ = "activity"

    id = sa.Column(sa.String(36), primary_key=True)
    user_id = sa.Column(sa.ForeignKey("user.id"))
    name = sa.Column(sa.TEXT)
    distance = sa.Column(sa.FLOAT)
    moving_time = sa.Column(sa.INTEGER)
    elapsed_time = sa.Column(sa.INTEGER)
    total_elevation_gain = sa.Column(sa.FLOAT)
    type = sa.Column(sa.TEXT)
    start_date = sa.Column(sa.TEXT)

    def __repr__(self):
        return f"ACTIVITY: {self.name}\tID: {self.id}\tDATE: {self.start_date}\tDISTANCE: {self.distance}"
