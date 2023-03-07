from dataclasses import dataclass

import flet as ft

from .base_view import BaseView


@dataclass
class Challenge:
    name: str
    icon: str
    content: ft.Control


# vari=ft.Text("run")
CHALLENGES = {
    "bike": Challenge(name="bike", icon=ft.icons.PEDAL_BIKE, content=ft.Container(content=ft.Text("run"))),
    "run": Challenge(name="run", icon=ft.icons.HIKING, content=ft.Container(content=ft.Text("run"))),
}


class ChallengesView(BaseView):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.route = "/challenges"

        # TODO: find proper place for challenge configuration
        self.challenges = CHALLENGES
        self.nav_bar = self.create_nav_bar()
        self._active_content = ft.Container()

        # add controls to frame
        self.extend_controls()

    def extend_controls(self) -> None:
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
                    # hier eine challenge
                    controls=[
                        ft.FilledButton(
                            text=f"{user.name}",
                            on_click=lambda e: self.app.page.go(f"/user/{e.control.data}"),
                            data=user.id,
                        )
                        for user in self.app.user_handler.values()
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                # self._active_content,
            ]
        )

    def set_active_challenge(self, name: str):
        self._active_content = self.challenges[name].content
        self.controls[-1] = self._active_content
        self.update()

    def on_nav_change(self, event):
        selected_challenge = list(self.challenges.values())[self.nav_bar.selected_index]
        self.page.go(f"/challenges/{selected_challenge.name}")

    def create_nav_bar(self) -> ft.NavigationBar:
        return ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=challenge.icon, label=challenge.name)
                for challenge in self.challenges.values()
            ],
            selected_index=0,
            on_change=self.on_nav_change,
        )

    def get_table_rows(self, sport):  # sport="Ride" e.g.
        user_distance = []
        for user in self.app.user_handler.values():
            distance = sum(
                [
                    activity.distance
                    for activity in self.app.activity_handler.get_user_activities(
                        user.id, sport_type=sport, start_date="2023-01-01 00:00:00", end_date="2023-01-02 00:00:00"
                    )
                    # if activity.type == sport
                ]
            )
            print(distance)
            user_distance.append((user, distance))

        sorted_user_distance = sorted(user_distance, key=lambda x: x[1], reverse=True)

        rows = []
        for i, elem in enumerate(sorted_user_distance):
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataColumn(ft.Text(i + 1)),
                        ft.DataCell(
                            ft.Text(elem[0].name), on_tap=lambda e: self.app.page.go(f"/user/{elem[0].id}")
                        ),  # TODO: find better way to link users
                        ft.DataCell(ft.Text(elem[1])),
                    ],
                ),
            )
        return rows
