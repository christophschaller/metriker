"""
Data Privacy Page
"""
import flet as ft


class DataPrivacyPage(ft.UserControl):
    """
    This class describes a data privacy page.
    """

    def __init__(self, app: ft.UserControl):
        """
        Args:
            app: app instance this class manages views for
        """
        super().__init__()

        self.app = app
        self.view = None

        self.download_button = None
        self.delete_button = None

        self.download_button = ft.FilledButton(text="Download My Data", icon=ft.icons.DOWNLOAD)
        self.delete_button = ft.FilledTonalButton(text="Delete My Data", icon=ft.icons.DELETE)

        self.controls = [self.download_button, self.delete_button]

    def build(self):
        self.view = ft.Container(
            content=ft.Column(controls=[self.download_button, self.delete_button], scroll="auto", expand=True),
            data=self,
            margin=ft.margin.all(0),
            padding=ft.padding.only(top=10, right=0),
            height=self.app.page.height,
        )
        return self.view
