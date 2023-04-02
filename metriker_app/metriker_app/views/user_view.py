"""Module holding UserView."""
from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from database_utils.user_handler import StravaUser

from .base_view import BaseView


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
        """Adds username to content section.

        Overrides the extend_controls method of BaseView.

        Returns:
            None
        """
        self.controls.extend([ft.Text(self.user.name)])
