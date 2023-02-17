"""
Page with user information.
"""
import flet as ft

from database_utils.user_handler import StravaUser


class UserPage(ft.UserControl):
    """
    This class describes a page filled with information about a single user.
    """

    def __init__(self, app: ft.UserControl, user: StravaUser):
        """
        Args:
            app: app instance this class manages views for
            user: object with information about the user
        """
        super().__init__()

        self.app = app
        self.view = None

        self.user_id = user.id
        self.name = user.name

    def build(self) -> ft.Control:
        self.view = ft.Container(
            content=ft.Column(controls=[ft.Text(self.name)], scroll="auto", expand=True),
            data=self,
            margin=ft.margin.all(0),
            padding=ft.padding.only(top=10, right=0),
            height=self.app.page.height,
        )
        return self.view
