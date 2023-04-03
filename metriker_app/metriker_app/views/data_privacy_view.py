"""Module holding DataPrivacyView."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import flet as ft

from .base_view import BaseView

if TYPE_CHECKING:
    from ..metriker import Metriker

logger = logging.getLogger(__name__)
logger.info(__name__)


class DataPrivacyView(BaseView):
    """DataPrivacyView expands the BaseView with Controls to delete and download a logged-in users' data."""

    def __init__(self, app: Metriker, *args, **kwargs) -> None:
        """DataPrivacyView expands the BaseView with Controls to delete and download a logged-in users' data.

        Args:
            app: Metriker object
            *args: list of additional arguments for ft.View
            **kwargs: dict of additional keyword arguments for ft.View.
        """
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.route = "/data_privacy"

        # add controls to frame
        self.extend_controls()

    def extend_controls(self) -> None:
        """Adds buttons to download and delete user data to content section.

        Overrides the extend_controls method of BaseView.

        Returns:
            None
        """
        self.controls.extend(
            [
                ft.Container(
                    content=ft.Column(
                        controls=[self.create_download_button(), self.create_delete_button()],
                        scroll=ft.ScrollMode.AUTO,
                        expand=True,
                    ),
                    margin=ft.margin.all(0),
                    padding=ft.padding.only(top=10, right=0),
                    height=self.app.page.height,
                ),
            ],
        )

    def create_download_button(self) -> ft.Control:
        """Creates a Button which should initiate the download of a logged-in users' data.

        Returns:
            ft.FilledButton
        """
        return ft.FilledButton(
            text="Download My Data",
            icon=ft.icons.DOWNLOAD,
            on_click=lambda event: logger.info(event.__dict__),
        )

    def create_delete_button(self) -> ft.Control:
        """Creates a Button which should initiate the deletion of a logged-in users' data and their account.

        Returns:
            ft.FilledButton
        """
        return ft.FilledTonalButton(
            text="Delete My Data",
            icon=ft.icons.DELETE,
            on_click=lambda event: logger.info(event.__dict__),
        )
