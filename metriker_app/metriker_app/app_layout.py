"""
This module helps to define the current View of the App.
"""
import flet as ft

from database_utils.activity_handler import StravaActivityHandler
from database_utils.user_handler import StravaUserHandler

from .pages import DataPrivacyPage, UserPage, ChallengePage, LoginPage


class AppLayout(ft.Column):
    """
    This class defines the current View of the App.
    """

    def __init__(
        self,
        app,
        page: ft.Page,
        user_handler: StravaUserHandler,
        activity_handler: StravaActivityHandler,
        *args,
        **kwargs,
    ):
        """
        Args:
            app: app instance this class manages views for
            page: main page to display on
            user_handler: wrapper for user storage
            activity_handler: wrapper for activity storage
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)
        self.app = app
        self.page = page

        self.activity_handler = activity_handler
        self.user_handler = user_handler

        self.login_view = LoginPage(app)
        self.user_view = ft.Text("user view")
        self.challenges_view = ChallengePage(self.app, self.user_handler, self.activity_handler)
        self.data_privacy_view = DataPrivacyPage(app)

        self._active_view: ft.Control = self.challenges_view
        self.controls = [self.active_view]

    @property
    def active_view(self) -> ft.Control:
        """
        Returns:
            The currently active view.
        """
        return self._active_view

    @active_view.setter
    def active_view(self, view: ft.Control) -> None:
        """
        Sets the currently active view.

        Args:
            view: UserControl
        Returns:
            None
        """
        self._active_view = view
        self.controls[-1] = self._active_view
        self.update()

    def set_user_view(self, user_id: str) -> None:
        """
        Set view to a user page.

        Args:
            user_id: id of user to display
        Returns:
            None
        """
        self.active_view = UserPage(self.app, self.user_handler[user_id])
        self.page.update()

    def set_challenges_view(self) -> None:
        """
        Set view to the challenges page.

        Returns:
            None
        """
        self.active_view = self.challenges_view
        self.page.update()

    def set_data_privacy_view(self) -> None:
        """
        Set view to the data privacy page.

        Returns:
            None
        """
        self.active_view = self.data_privacy_view
        self.page.update()

    def set_login_view(self) -> None:
        """
        Set view to the login page.

        Returns:
            None
        """
        self.active_view = self.login_view
        self.page.update()
