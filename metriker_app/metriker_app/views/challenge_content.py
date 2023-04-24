"""Module holding ChallengeContent."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

import flet as ft
import pandas as pd
import plotly.express as px
from dateutil.tz import tzlocal
from flet.plotly_chart import PlotlyChart


class ChallengeContent(ft.Column):
    """contains two cointainers with a table and a graph.

    Args:
        ft (_type_): _description_
    """

    def __init__(self, app, sport_type, start_date, end_date, *args, **kwargs):
        """Class to build screens for challenges with tabels and plots.

        Args:
            app (_type_): _description_
            sport_type (str): sport_type sting from strava activity sport_type e.g. "Ride", "Run",..
            start_date (datetime): start_date
            end_date (datetime): end_date
            *args(_type_):something
            **kwargs(_type_):something
        """
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.sport_type = sport_type
        self.start_date = start_date
        self.end_date = end_date

        self.controls = [
            ft.Container(
                self.create_chart("2023-01-01 00:00:05", "2023-03-03 00:00:05"),
            ),
            ft.Container(
                self.create_table("2023-01-01 00:00:05", "2023-03-03 00:00:05"),
            ),
        ]

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
            distance = (
                sum(
                    [
                        activity.distance
                        for activity in self.app.activity_handler.get_user_activities(
                            user.id,
                            sport_type=self.sport_type,
                            start_date=start_date,
                            end_date=end_date,
                        )
                    ],
                )
                / 1000
            )
            user_distance.append((user, distance))

        sorted_user_distance = sorted(user_distance, key=lambda x: x[1], reverse=True)

        rows = []
        for i, elem in enumerate(sorted_user_distance):
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataColumn(ft.Text(i + 1)),
                        ft.DataCell(
                            ft.TextButton(
                                text=elem[0].name,
                                data=elem[0].id,
                                on_click=lambda e: self.app.page.go(
                                    f"/user/{e.control.data}",
                                ),
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
            if type(date) == str:
                return_date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=tzlocal(),
                )
            elif type(date) == datetime:
                return_date = date
            else:
                logging.error("ERROR: Date is neither str nor datetime format")

            return return_date

        start_date = convert_to_datetime(start_date)
        end_date = convert_to_datetime(end_date)

        # Month steps

        # Week steps
        all_activities = []
        for user in self.app.user_handler.values():
            week_columns = []
            user_activities = []

            # Determine the first and last day of the first week
            first_day = start_date - timedelta(days=start_date.weekday())
            last_day = first_day + timedelta(days=7) - timedelta(seconds=1)

            # Loop through each week and print the first day, last day, and ISO week number
            while first_day.date() <= end_date.date():
                year, week_num, day_num = first_day.isocalendar()
                week_columns.append(f"woche {year}-{week_num}")
                new_start_date = first_day
                new_end_date = last_day

                week_distance = (
                    sum(
                        [
                            activity.distance
                            for activity in self.app.activity_handler.get_user_activities(
                                user.id,
                                sport_type=self.sport_type,
                                start_date=new_start_date,
                                end_date=new_end_date,
                            )
                        ],
                    )
                    / 1000
                )
                user_activities.append(week_distance)

                # Increment to the next week
                first_day = last_day + timedelta(days=1)
                last_day = first_day + timedelta(days=6)
                #

                all_activities.append(user_activities)
                usernames_index = [user.name for user in self.app.user_handler.values()]
                dataframe = pd.DataFrame(
                    all_activities,
                    columns=week_columns,
                    index=usernames_index,
                )
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
        # , expand=True)# self._active_content

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
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Distance"), numeric=True),
            ],
            rows=self.get_table_rows(start_date, end_date),
        )
