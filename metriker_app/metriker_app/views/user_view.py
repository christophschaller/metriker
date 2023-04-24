"""Module holding UserView."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import flet as ft
import pandas as pd
import plotly.express as px
from dateutil.tz import tzlocal
from flet.plotly_chart import PlotlyChart

from .base_view import BaseView

logger = logging.getLogger(__name__)
logger.info(__name__)

if TYPE_CHECKING:
    from database_utils.user_handler import StravaUser

    from ..metriker import Metriker


class UserView(BaseView):
    """UserView expands the BaseView with information about a users activities."""

    def __init__(self, app: Metriker, user_id: str, *args, **kwargs) -> None:
        """UserView expands the BaseView with information about a users activities.

        Args:
            app: Metriker object
            user_id: id of the user to display information for
            *args: list of additional arguments for ft.View
            **kwargs: dict of additional keyword arguments for ft.View.
        """
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.route = f"/user/{user_id}"
        self.user: StravaUser = self.app.user_handler.get(user_id)

        # add controls to frame
        self.extend_controls()

    def extend_controls(self) -> None:
        """Body."""
        self.controls.extend(
            [
                ft.Text(self.user.name),
                ft.Container(
                    self.create_chart(
                        "2023-01-01 00:00:05",
                        "2023-03-03 00:00:05",
                        "frame",
                    ),
                ),
                ft.Container(
                    self.create_table("2023-01-01 00:00:05", "2023-03-03 00:00:05"),
                ),
            ],
        )

    def create_table(self, start_date, end_date):
        """Creates a ft.DataTable with get_table_rows function.

        Args:
            start_date (datetime): start_date
            end_date (datetime): end_date

        Returns:
            create_table(ft.DataTable): datatable for highscores
        """
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Place"), numeric=True),
                ft.DataColumn(ft.Text("Sporttype")),
                ft.DataColumn(ft.Text("Distance"), numeric=True),
            ],
            rows=self.get_table_rows(start_date, end_date),
        )

    def get_table_rows(self, start_date, end_date):
        """Returns flet datarows for a flet table.

        Args:
            start_date (datetime): start_date
            end_date (datetime): end_date

        Returns:
            get_table_rows(list): list of ft.DataRow
        """
        user_distance = []
        for user in self.app.user_handler.values():
            sport_types = {
                activity.sport_type
                for activity in self.app.activity_handler.get_user_activities(
                    user.id,
                    start_date=start_date,
                    end_date=end_date,
                )
            }

            for sport_type in sport_types:
                distance = (
                    sum(
                        [
                            activity.distance
                            for activity in self.app.activity_handler.get_user_activities(
                                user.id,
                                sport_type=sport_type,
                                start_date=start_date,
                                end_date=end_date,
                            )
                        ],
                    )
                    / 1000
                )

                user_distance.append((sport_type, distance))

        sorted_user_distance = sorted(user_distance, key=lambda x: x[1], reverse=True)

        rows = []
        for i, elem in enumerate(sorted_user_distance):
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataColumn(ft.Text(i + 1)),
                        ft.DataCell(
                            ft.Text(
                                elem[0],
                            ),
                        ),
                        ft.DataCell(ft.Text(elem[1])),
                    ],
                ),
            )
        return rows

    def get_sport_plot(self, start_date, end_date):
        """Returns all values for a plot with plotly in a pd dataframe format.

        Args:
            start_date (datetime): start_date
            end_date (datetime): end_date

        Returns:
            get_sport_plot(pandas dataframe): dataframe for plotly chart
        """

        def convert_to_datetime(date):
            """Converts string to datetime object if needet and reises error if type isnt str or datetime.

            Args:
                date (any): _description_

            Returns:
                datetime: "%Y-%m-%d %H:%M:%S"
            """
            if isinstance(date, str):
                return_date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=tzlocal(),
                )
            elif isinstance(date, datetime):
                return_date = date
            else:
                logger.error("Date is neither str nor datetime format")
                raise TypeError

            return return_date

        start_date = convert_to_datetime(start_date)
        end_date = convert_to_datetime(end_date)

        all_activities = []
        for user in self.app.user_handler.values():
            week_columns = []

            sport_types = list(
                {
                    activity.sport_type
                    for activity in self.app.activity_handler.get_user_activities(
                        user.id,
                        start_date=start_date,
                        end_date=end_date,
                    )
                },
            )

            # Determine the first and last day of the first week
            first_day = start_date - timedelta(days=start_date.weekday())
            last_day = first_day + timedelta(days=7) - timedelta(seconds=1)

            # Loop through each week and print the first day, last day, and ISO week number
            while first_day.date() <= end_date.date():
                year, week_num, day_num = first_day.isocalendar()
                week_columns.append(f"woche {year}-{week_num}")
                new_start_date = first_day
                new_end_date = last_day

                user_week_activities = []
                for sport_type in sport_types:
                    week_distance = (
                        sum(
                            [
                                activity.distance
                                for activity in self.app.activity_handler.get_user_activities(
                                    user.id,
                                    sport_type=sport_type,
                                    start_date=new_start_date,
                                    end_date=new_end_date,
                                )
                            ],
                        )
                        / 1000
                    )
                    user_week_activities.append(week_distance)

                # Increment to the next week
                first_day = last_day + timedelta(days=1)
                last_day = first_day + timedelta(days=6)

                all_activities.append(user_week_activities)

            dataframe = pd.DataFrame(
                all_activities,
                index=week_columns,
                columns=sport_types,
            ).transpose()

        return dataframe

    def create_chart(self, start_date, end_date):
        """Uses the function get_sport_plot to generate a dataframe and creates a PlotlyChart with that.

        Args:
            start_date (datetime): start_date
            end_date (datetime): end_date.

        Returns:
            (datetime)(PlotlyChart): chart with values
        """
        return PlotlyChart(
            px.line(
                self.get_sport_plot(start_date, end_date).transpose(),
                template="simple_white",
                line_shape="spline",
                labels={"value": "Kilometer", "index": "Monate"},
            ),
        )
