import flet as ft

from .base_view import BaseView


class LoginView(BaseView):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.route = "/login"

        # add controls to frame
        self.extend_controls()

    def extend_controls(self) -> None:
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
            ]
        )

    def create_login_button(self) -> ft.Control:
        return ft.FilledButton(
            text="Login",
            icon="login",
            icon_color=ft.colors.WHITE,
            style=ft.ButtonStyle(bgcolor=ft.colors.ORANGE),
            on_click=self.app.login,
        )