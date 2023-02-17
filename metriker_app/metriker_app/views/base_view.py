import flet as ft


class BaseView(ft.View):
    def __init__(self, app, route: str = None, title: str = "Honigmann", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.route = route
        self.title = title

        # set base style for views
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.padding = ft.padding.all(0)
        self.bgcolor = "#fff5f5f5"

        # add app_bar to views
        self.app_bar = self._create_app_bar()
        self.controls = [self.app_bar]

    def extend_controls(self):
        raise NotImplementedError

    def _create_avatar(self) -> ft.Control:
        if self.app.user:
            initials = f"{self.app.user['firstname'][0]}{self.app.user['lastname'][0]}"
            return ft.CircleAvatar(
                foreground_image_url=self.app.user.get("profile_medium"),
                content=ft.Text(initials),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE,
            )
        return ft.CircleAvatar(
            foreground_image_url=None,
            background_image_url=None,
            content=ft.Icon(ft.icons.PERSON),
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE_GREY,
        )

    def _create_logout_button(self) -> ft.Control:
        return ft.FilledTonalButton(
            text="Logout",
            icon="logout",
            icon_color=ft.colors.BLACK,
            style=ft.ButtonStyle(bgcolor=ft.colors.ORANGE),
            on_click=self.app.logout,
        )

    def _create_avatar_button(self) -> ft.Control:
        if not self.app.user:
            return self._create_avatar()
        appbar_items = [
            ft.PopupMenuItem(content=self._create_logout_button()),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(text="Data Privacy", on_click=lambda _: self.app.page.go("/data_privacy")),
        ]
        return ft.PopupMenuButton(content=self._create_avatar(), items=appbar_items)

    def _create_app_bar(self) -> ft.Control:
        return ft.AppBar(
            leading=None,
            leading_width=75,
            title=ft.Text(self.title, font_family="sen", size=32, text_align=ft.TextAlign("center")),
            center_title=True,
            toolbar_height=75,
            bgcolor=ft.colors.WHITE,
            actions=[
                self._create_avatar_button(),
                ft.VerticalDivider(color=ft.colors.WHITE),
            ],
        )
