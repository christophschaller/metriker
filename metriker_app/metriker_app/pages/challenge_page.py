"""
Page with challenge information.
"""
import flet as ft

from database_utils.user_handler import StravaUserHandler
from database_utils.activity_handler import StravaActivityHandler


class ChallengePage(ft.UserControl):
    """
    This class describes a page filled with information about challenges.
    """

    def __init__(self, app: ft.UserControl, user_handler: StravaUserHandler, activity_handler: StravaActivityHandler):
        """
        Args:
            app: app instance this class manages views for
            user_handler: wrapper for user storage
            activity_handler: wrapper for activity storage
        """
        super().__init__()

        self.app = app
        self.view = None

        self.activity_handler = activity_handler
        self.user_handler = user_handler

    def build(self):
        self.view = ft.Container(
            content=ft.Column(
                controls=[
                    ft.FilledButton(
                        text=f"{user.name}_{user.id}",
                        on_click=lambda e: self.app.page.go(f"/user/{e.control.data}"),
                        data=user.id,
                    )
                    for user in self.user_handler.values()
                ],
                scroll="auto",
                expand=True,
            ),
            data=self,
            margin=ft.margin.all(0),
            padding=ft.padding.only(top=10, right=0),
            height=self.app.page.height,
        )
        return self.view
