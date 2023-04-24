"""Module holding ChallengesView."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft
from challenge_content import ChallengeContent

from .base_view import BaseView

if TYPE_CHECKING:
    from ..metriker import Metriker


class ChallengesView(BaseView):
    """ChallengesView expands the BaseView with a NavBar on the bottom of the page.

    The content of every challenge is displayed in the center and can be changed with the NavBAr.
    """

    def __init__(self, app: Metriker, *args, **kwargs) -> None:
        """Init of ChallengesView.

        Args:
            app: Metriker object
            *args: list of additional arguments for ft.View
            **kwargs: dict of additional keyword arguments for ft.View.
        """
        super().__init__(app, *args, **kwargs)
        self.scroll = ft.ScrollMode.AUTO
        self.app = app
        self.route = "/challenges"

        # TODO: find proper place for challenge configuration
        self.challenges = {
            "bike": Challenge(
                name="bike",
                icon=ft.icons.PEDAL_BIKE,
                content=ChallengeContent(
                    self.app,
                    "Ride",
                    "2023-01-01 00:00:01",
                    "2023-03-03 00:00:05",
                ),
            ),
            "run": Challenge(
                name="run",
                icon=ft.icons.HIKING,
                content=ChallengeContent(
                    self.app,
                    "Run",
                    "2023-01-01 00:00:01",
                    "2023-03-03 00:00:05",
                ),
            ),
        }
        self.nav_bar = self._create_nav_bar()
        self._active_content = ft.Container()

        self.extend_controls()

    def extend_controls(self) -> None:
        """Extends the contents of the page.

        Adds buttons leading to each user to the content section and a NavBar to the bottom of the page.
        Overrides the extend_controls method of BaseView.

        Returns:
            None
        """
        self.controls.extend(
            [
                self.nav_bar,
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Place"), numeric=True),
                        ft.DataColumn(ft.Text("Name")),
                        ft.DataColumn(ft.Text("Distance"), numeric=True),
                    ],
                    rows=self.get_table_rows("Ride"),
                ),
                ft.Column(
                    controls=[
                        ft.FilledButton(
                            text=f"{user.name}",
                            on_click=lambda e: self.app.page.go(
                                f"/user/{e.control.data}",
                            ),
                            data=user.id,
                        )
                        for user in self.app.user_handler.values()
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                # self._active_content,
            ],
        )

    def _create_nav_bar(self) -> ft.NavigationBar:
        """Creates and ft.NavigationBar Control containing the available challenges.

        Returns:
            ft.NavigationBar
        """
        return ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=challenge.icon, label=challenge.name)
                for challenge in self.challenges.values()
            ],
            selected_index=0,
            on_change=self.on_nav_change,
        )

    def set_active_challenge(self, name: str) -> None:
        """Sets the active challenge to be displayed.

        Args:
            name: key of the challenge.

        Returns:
            None
        """
        self._active_content = self.challenges[name].content
        self.controls[-1] = self._active_content
        self.update()

    def on_nav_change(self, _: ft.RouteChangeEvent) -> None:
        """Trigger flow when selected challenge on NavBar changes.

        Args:
            _: unused event provided by NavBar.

        Returns:
            None
        """
        selected_challenge = list(self.challenges.values())[self.nav_bar.selected_index]
        self.page.go(f"/challenges/{selected_challenge.name}")

    def get_table_rows(self, sport):  # sport="Ride" e.g.
        """Returns all content rows for the table depending on which sport.

        Args:
            sport (string): run, ride,...

        Returns:
            list of ft.DataRows: _description_
        """
        user_distance = []
        for user in self.app.user_handler.values():
            distance = sum(
                [
                    activity.distance
                    for activity in self.app.activity_handler.get_user_activities(
                        user.id,
                        sport_type=sport,
                        start_date="2023-01-01 00:00:00",
                        end_date="2023-01-02 00:00:00",
                    )
                    # if activity.sport_type == sport
                ],
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
                            ft.Text(elem[0].name),
                            on_tap=self.app.page.go(f"/user/{elem[0].id}"),
                        ),  # TODO: find better way to link users
                        ft.DataCell(ft.Text(elem[1])),
                    ],
                ),
            )
        return rows
