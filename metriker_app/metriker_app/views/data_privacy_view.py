import flet as ft

from .base_view import BaseView


class DataPrivacyView(BaseView):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.route = "/data_privacy"

        # add controls to frame
        self.extend_controls()

    def extend_controls(self) -> None:
        self.controls.extend(
            [
                ft.Container(
                    content=ft.Column(
                        controls=[self.create_download_button(), self.create_delete_button()],
                        scroll="auto",
                        expand=True,
                    ),
                    margin=ft.margin.all(0),
                    padding=ft.padding.only(top=10, right=0),
                    height=self.app.page.height,
                )
            ]
        )

    def create_download_button(self) -> ft.Control:
        return ft.FilledButton(
            text="Download My Data",
            icon=ft.icons.DOWNLOAD,
            on_click=lambda event: print(event.__dict__),  # TODO: serve download
        )

    def create_delete_button(self) -> ft.Control:
        return ft.FilledTonalButton(
            text="Delete My Data",
            icon=ft.icons.DELETE,
            on_click=lambda event: print(event.__dict__),  # TODO: delete data
        )
