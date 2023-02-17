"""
Login Page
"""
import flet as ft


class LoginPage(ft.UserControl):
    """
    This class describes a login page.
    """

    def __init__(self, app: ft.UserControl):
        """
        Args:
            app: app instance this class manages views for
        """
        super().__init__()

        self.app = app
        self.view = None

    def build(self):
        self.view = ft.Container(
            content=ft.Column(controls=[ft.Text("pls login")], scroll="auto", expand=True),
            data=self,
            margin=ft.margin.all(0),
            padding=ft.padding.only(top=10, right=0),
            height=self.app.page.height,
        )
        return self.view
