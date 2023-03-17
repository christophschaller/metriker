"""
Module holding UserView.
"""
import flet as ft

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
            [ft.Text(self.user.name), ft.Container(self.create_table("2023-01-01 00:00:05", "2023-03-03 00:00:05"))]
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
            sport_types = (
                set(
                    [
                        activity.type
                        for activity in self.app.activity_handler.get_user_activities(
                            user.id,
                            # sport_type="Ride",
                            start_date=start_date,
                            end_date=end_date,
                        )
                    ]
                )
                # / 1000
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
            print(user_distance)

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
