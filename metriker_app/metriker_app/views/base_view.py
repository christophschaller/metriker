"""This module holds the BaseView class for the Metriker App.

Defining Core functionality for every view the App offers.
"""
import flet as ft


class BaseView(ft.View):
    """BaseView serves as the Base class for all views in the Metriker App.

    It defines an AppBar on the top for navigation and basic requirements for auth flows.
    """

    def __init__(self, app: Metriker, *args, route: str = None, title: str = "Honigmann", **kwargs) -> None:
        """Init of BaseView.

        Args:
            app: Metriker object
            *args: list of additional arguments for ft.View
            route: route of the view
            title: title displayed in the AppBar
            **kwargs: dict of additional keyword arguments for ft.View.
        """
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

    def extend_controls(self) -> None:
        """This has to be implemented by Child classes.

        It must extend the controls of the underlying ft.View object to hold the content to be displayed.

        Example:
            self.controls.extend([])

        Returns:
            None
        """
        # self.controls.extend([])
        raise NotImplementedError

    def _create_avatar(self) -> ft.Control:
        """Creates an avatar icon for the logged-in user.

        Returns:
            ft.CircleAvatar holding the avatar representation.
        """
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
        """Creates as Button to trigger the logout flow.

        Returns:
            ft.FilledTonalButton
        """
        return ft.FilledTonalButton(
            text="Logout",
            icon="logout",
            icon_color=ft.colors.BLACK,
            style=ft.ButtonStyle(bgcolor=ft.colors.ORANGE),
            on_click=self.app.logout,
        )

    def _create_avatar_button(self) -> ft.Control:
        """Create PopupMenuButton which combines the user avatar and logout button controls.

        Returns:
            ft.PopupMenuButton
        """
        if not self.app.user:
            return self._create_avatar()
        appbar_items = [
            ft.PopupMenuItem(content=self._create_logout_button()),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(text="Data Privacy", on_click=lambda _: self.app.page.go("/data_privacy")),
        ]
        return ft.PopupMenuButton(content=self._create_avatar(), items=appbar_items)

    def _create_app_bar(self) -> ft.Control:
        """Creates and ft.AppBar Control containing a popup avatar button.

        This combines the other controls defined in methods of this class.

        Returns:
            ft.AppBar
        """
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
