"""
Module holding UserView.
"""
from datetime import datetime, timedelta

import flet as ft
import pandas as pd
import plotly.express as px
from flet.plotly_chart import PlotlyChart

from database_utils.user_handler import StravaUser

from .base_view import BaseView


class UserView(BaseView):
    """
    UserView expands the BaseView with information about a users activities.
    """

    def __init__(self, app, user_id: str, *args, **kwargs):
        """
        Args:
            app: Metriker object
            user_id: id of the user to display information for
            *args: list of additional arguments for ft.View
            **kwargs: dict of additional keyword arguments for ft.View
        """
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.route = f"/user/{user_id}"
        self.user: StravaUser = self.app.user_handler.get(user_id)

        # add controls to frame
        self.extend_controls()

    def extend_controls(self) -> None:
        self.controls.extend(
            [
                ft.Text(self.user.name),
                ft.Container(self.create_chart("2023-01-01 00:00:05", "2023-03-03 00:00:05", "frame")),
                ft.Container(self.create_table("2023-01-01 00:00:05", "2023-03-03 00:00:05")),
            ]
        )

    def create_table(self, start_date, end_date):
        """creates a ft.DataTable with get_table_rows function

        Args:
            start_date (str in format "%Y-%m-%d %H:%M:%S"): start_date
            end_date (str in format "%Y-%m-%d %H:%M:%S"): end_date

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
        """returns flet datarows for a flet table

        Args:
            start_date (str in format "%Y-%m-%d %H:%M:%S"): start_date
            end_date (str in format "%Y-%m-%d %H:%M:%S"): end_date

        Returns:
            get_table_rows(list): list of ft.DataRow
        """
        user_distance = []
        for user in self.app.user_handler.values():
            sport_types = set(
                [
                    activity.type
                    for activity in self.app.activity_handler.get_user_activities(
                        user.id,
                        start_date=start_date,
                        end_date=end_date,
                    )
                ]
            )

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
                        ]
                    )
                    / 1000
                )

                user_distance.append((sport_type, distance))
            # print(user_distance)

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
                            )
                        ),
                        ft.DataCell(ft.Text(elem[1])),
                    ],
                ),
            )
        return rows

    def get_sport_plot(self, start_date, end_date, frame):
        """returns all values for a plot with plotly in a pd dataframe format

        Args:
            start_date (str in format "%Y-%m-%d %H:%M:%S"): start_date
            end_date (str in format "%Y-%m-%d %H:%M:%S"): end_date
            frame(str): month or empty changes the detail leve of the plot (weeks or months)

        Returns:
            get_sport_plot(pandas dataframe): dataframe for plotly chart
        """
        start_date = datetime.strptime(str(start_date), "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(str(end_date), "%Y-%m-%d %H:%M:%S")

        """# Month steps
        if frame == "month":
            all_activities = []
            for user in self.app.user_handler.values():
                month_list = []
                for month in range(end_date.month - start_date.month + 1):
                    month_list.append(start_date.month + month)

                user_activities = []
                for month in month_list:
                    new_start_date = datetime(2023, month, 1, 0, 0, 0)
                    new_end_date = datetime(2023, month + 1, 1, 0, 0, 0) - timedelta(seconds=1)

                    month_distance = (
                        sum(
                            [
                                activity.distance
                                for activity in self.app.activity_handler.get_user_activities(
                                    user.id,
                                    sport_type="Ride",
                                    start_date=new_start_date,
                                    end_date=new_end_date,
                                )
                            ]
                        )
                        / 1000
                    )
                    user_activities.append(month_distance)
                all_activities.append(user_activities)

            month_columns = []
            for i in range(0, end_date.month - start_date.month + 1):
                next_month = start_date + relativedelta(months=i)
                next_month_name = next_month.strftime("%B")
                month_columns.append(next_month_name)

            sport_type_index = [user.name for user in self.app.user_handler.values()]
            dataframe = pd.DataFrame(all_activities, columns=month_columns, index=sport_type_index)

        # Week steps
        else:"""
        all_activities = []
        for user in self.app.user_handler.values():
            week_columns = []

            sport_types = list(
                set(
                    [
                        activity.type
                        for activity in self.app.activity_handler.get_user_activities(
                            user.id,
                            start_date=start_date,
                            end_date=end_date,
                        )
                    ]
                )
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
                            ]
                        )
                        / 1000
                    )
                    user_week_activities.append(week_distance)

                # Increment to the next week
                first_day = last_day + timedelta(days=1)
                last_day = first_day + timedelta(days=6)

                all_activities.append(user_week_activities)

            dataframe = pd.DataFrame(all_activities, index=week_columns, columns=sport_types).transpose()

        return dataframe

    def create_chart(self, start_date, end_date, frame):
        """uses the function get_sport_plot to generate a dataframe and creates a PlotlyChart with that
        Args:
            start_date (str in format "%Y-%m-%d %H:%M:%S"): start_date
            end_date (str in format "%Y-%m-%d %H:%M:%S"): end_date

        Returns:
            (str in format "%Y-%m-%d %H:%M:%S")(PlotlyChart): chart with values
        """
        return PlotlyChart(
            px.line(
                self.get_sport_plot(start_date, end_date, frame).transpose(),
                template="simple_white",
                line_shape="spline",
                labels={"value": "Kilometer", "index": "Monate"},
            )
        )
