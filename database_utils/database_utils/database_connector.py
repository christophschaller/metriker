"""Module containing DatabaseConnector class, managing connections to a SQL Database."""
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from .schema import Base


class DatabaseConnector:
    """Class managing the connection to SQL data."""

    def __init__(  # noqa: PLR0913 - Ignore: Too many arguments to function call
        self,
        user: str = None,
        password: str = None,
        host: str = None,
        port: str = None,
        database: str = None,
    ) -> None:
        """Init of DatabaseConnector.

        Args:
            user: username to connect to the data service
            password: ...
            host: host url
            port: service port
            database: name of the target data.
        """
        self.engine = None
        self.session = None

        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        self._connect()
        # create schema in db if it does not exist
        Base.metadata.create_all(self.engine)

    def _connect(self) -> None:
        """Initiate the connection to the data service and populate the necessary obj variables."""
        uri = f"sqlite:///{self.database}.db"
        if self.host:
            uri = f"mariadb+mariadbconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = sa.create_engine(uri)

        session = sessionmaker(self.engine)
        self.session = session()

    def insert(self, element: Base) -> None:
        """Insert a db object.

        Args:
            element: db object inheriting from Base specified in tei_sql_schema
        """
        self.session.add(element)
        self.session.commit()
