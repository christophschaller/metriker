from dataclasses import dataclass

import flet as ft

from .base_view import BaseView


@dataclass
class Challenge:
    name: str
    icon: str
    content: ft.Control


CHALLENGES = {
    "bike": Challenge(name="bike", icon=ft.icons.PEDAL_BIKE, content=ft.Container(content=ft.Text("bike"))),
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
                ft.Column(
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
                self._active_content,
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
