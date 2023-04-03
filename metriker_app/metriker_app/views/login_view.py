"""Module holding LoginView."""
from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from .base_view import BaseView

if TYPE_CHECKING:
    from ..metriker import Metriker


class LoginView(BaseView):
    """LoginView expands the BaseView with Controls to authenticate a user."""

    def __init__(self, app: Metriker, *args, **kwargs) -> None:
        """LoginView expands the BaseView with Controls to authenticate a user.

        Args:
            app: Metriker object
            *args: list of additional arguments for ft.View
            **kwargs: dict of additional keyword arguments for ft.View.
        """
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.route = "/login"

        # add controls to frame
        self.extend_controls()

    def extend_controls(self) -> None:
        """Adds login panel to content section.

        Overrides the extend_controls method of BaseView.

        Returns:
            None
        """
        self.controls.extend(
            [
                ft.Container(
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[self.create_login_button(), ft.Checkbox(label="Remember Me", value=False)],
                    ),
                    margin=10,
                    padding=10,
                    alignment=ft.alignment.center,
                    width=200,
                    height=250,
                    border_radius=10,
                    ink=True,
                    bgcolor=ft.colors.BLUE_GREY_50,
                ),
            ],
        )

    def create_login_button(self) -> ft.Control:
        """Creates a Button which initiates the login flow.

        Returns:
            ft.FilledButton
        """
        return ft.FilledButton(
            text="Login",
            icon="login",
            icon_color=ft.colors.WHITE,
            style=ft.ButtonStyle(bgcolor=ft.colors.ORANGE),
            on_click=self.app.login,
        )
