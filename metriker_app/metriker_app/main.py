"""
Main module and entrypoint of the metriker flet app.
"""
import os

import flet as ft
import requests
from flet.auth.oauth_provider import OAuthProvider
from dotenv import load_dotenv

from .app_layout import AppLayout
from database_utils.user_handler import StravaUserHandler, StravaUser
from database_utils.activity_handler import StravaActivityHandler


class FletApp(ft.UserControl):
    """
    This class defines the frame of the webapp and its interfaces.
    """

    def __init__(
        self,
        page: ft.Page,
        client_id: str,
        client_secret: str,
        user_handler: StravaUserHandler,
        activity_handler: StravaActivityHandler,
        strava_service_url: str,
    ):
        """
        Args:
            page: ft.Page
            client_id: strava client id for auth with strava
            client_secret: strava client secret for auth with strava
            user_handler: wrapper for user storage
            activity_handler: wrapper for activity storage
            strava_service_url: url to background service interfacing with the strava api
        """
        super().__init__()
        self.page = page
        self.page.on_route_change = self._route_change

        self.strava_service_url = strava_service_url

        self.auth_provider = OAuthProvider(
            client_id=client_id,
            client_secret=client_secret,
            authorization_endpoint="https://www.strava.com/oauth/authorize",
            token_endpoint="https://www.strava.com/oauth/token",
            redirect_url="http://localhost:8550/api/oauth/redirect",
            user_endpoint="https://www.strava.com/api/v3/athlete",
            user_scopes=["read,activity:read_all"],
            user_id_fn=lambda user: user["id"],
        )

        # populate login_button
        self.login_button = ft.FilledButton(
            text="Login",
            icon="login",
            icon_color=ft.colors.WHITE,
            style=ft.ButtonStyle(bgcolor=ft.colors.ORANGE),
            on_click=self._login,
        )
        # populate logout_button
        self.logout_button = ft.FilledTonalButton(
            text="Logout",
            icon="logout",
            icon_color=ft.colors.BLACK,
            style=ft.ButtonStyle(bgcolor=ft.colors.ORANGE),
            on_click=self._logout,
        )
        self.page.on_login = self._on_login
        self.page.on_logout = self._on_logout

        # because there is no user yet
        self.user = None
        self.user_handler = user_handler
        self.activity_handler = activity_handler

        self.back_button = ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/"))
        self.avatar = ft.CircleAvatar(
            foreground_image_url=None,
            background_image_url=None,
            content=ft.Icon(ft.icons.PERSON),
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE_GREY,
        )
        self.appbar_items = [
            ft.PopupMenuItem(content=self.logout_button),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(text="Data Privacy", on_click=lambda _: self.page.go("/data_privacy")),
        ]
        self.avatar_button = ft.PopupMenuButton(content=self.avatar, items=self.appbar_items)
        self.avatar_button.disabled = True
        self.appbar = self._build_app_bar()
        self.page.appbar = self.appbar
        self.logout_button.visible = False

        self.layout = None

        self.page.update()

    def _login(self, event):
        self.page.login(self.auth_provider)

    def _on_login(self, event):
        if not event.error:
            self.user = self.page.auth.user
            existing_user = self.user_handler.get(self.user.user_id)
            if not existing_user:
                # add new user to db
                self.user_handler.add(
                    StravaUser(
                        id=self.user.user_id,
                        name=self.user["firstname"],
                        refresh_token=self.page.auth.token.refresh_token,
                    )
                )
                # request ingestion od users activities
                requests.post(f"{self.strava_service_url}/updateUserActivities?user_id={self.user.user_id}")
            elif existing_user.refresh_token != self.page.auth.token.refresh_token:
                # update refresh token if it has changed
                self.user_handler.update(
                    StravaUser(
                        id=self.user.user_id,
                        name=self.user["firstname"],
                        refresh_token=self.page.auth.token.refresh_token,
                    )
                )

            self.avatar.foreground_image_url = self.user.get("profile_medium")
            initials = f"{self.user['firstname'][0]}{self.user['lastname'][0]}"
            self.avatar.content = ft.Text(initials)
            self.avatar.bgcolor = ft.colors.BLUE
            self.avatar.update()
            self.login_button.visible = False
            self.login_button.update()
            self.logout_button.visible = True
            self.logout_button.update()
            self.avatar_button.disabled = False
            self.avatar_button.update()
            self.page.update()
            self.page.go("/challenges")
        else:
            raise Exception(event.error)

    def _logout(self, e):
        self.user = None
        self.page.logout()

    def _on_logout(self, e):
        self.avatar.content = ft.Icon(ft.icons.PERSON)
        self.avatar.color = ft.colors.WHITE
        self.avatar.bgcolor = ft.colors.BLUE_GREY
        self.avatar.update()
        self.login_button.visible = True
        self.login_button.update()
        self.logout_button.visible = False
        self.logout_button.update()
        self.avatar_button.disabled = True
        self.avatar_button.update()
        self.page.update()
        self.page.go("/")

    def _build_app_bar(self):
        return ft.AppBar(
            leading=self.back_button,
            leading_width=75,
            title=ft.Text(f"Honigmann", font_family="sen", size=32, text_align=ft.TextAlign("center")),
            center_title=True,
            toolbar_height=75,
            bgcolor=ft.colors.WHITE,
            actions=[
                self.avatar_button,
                ft.VerticalDivider(color=ft.colors.WHITE),
                self.login_button,
                # self.logout_button,
                ft.VerticalDivider(color=ft.colors.WHITE),
            ],
        )

    def _route_change(self, route):
        troute = ft.TemplateRoute(self.page.route)
        self.back_button.visible = True
        if troute.match("/"):
            if self.user:
                self.page.go("/challenges")
            else:
                self.page.go("/login")
        elif troute.match("/user/:id"):
            if int(troute.id) not in self.user_handler.keys():
                self.page.go("/")
                return
            self.layout.set_user_view(int(troute.id))
        elif troute.match("/login"):
            self.back_button.visible = False
            self.layout.set_login_view()
        elif troute.match("/challenges"):
            self.back_button.visible = False
            self.layout.set_challenges_view()
        elif troute.match("/data_privacy"):
            self.layout.set_data_privacy_view()
        self.page.update()

    def build(self):
        self.layout = AppLayout(self, self.page, self.user_handler, self.activity_handler)
        return self.layout

    def initialize(self):
        self.page.views.clear()
        self.page.views.append(ft.View("/", [self.appbar, self.layout], padding=ft.padding.all(0), bgcolor="#fff5f5f5"))
        self.page.update()
        self.page.go("/")


if __name__ == "__main__":
    load_dotenv("../../dev.env")
    SENTRY_DSN = os.getenv("METRIKER_SENTRY_DSN")

    STRAVA_CLIENT_ID = os.getenv("METRIKER_STRAVA_CLIENT_ID")
    STRAVA_CLIENT_SECRET = os.getenv("METRIKER_STRAVA_CLIENT_SECRET")

    DB_USER = os.getenv("METRIKER_DB_USER")
    DB_PASS = os.getenv("METRIKER_DB_PASS")
    DB_HOST = os.getenv("METRIKER_DB_HOST")
    DB_PORT = os.getenv("METRIKER_DB_PORT")
    DB_NAME = os.getenv("METRIKER_DB_NAME")

    STRAVA_SERVICE_URL = os.getenv("METRIKER_STRAVA_SERVICE_URL")

    SECRET_KEY = os.getenv("METRIKER_SECRET_KEY")

    def main(page: ft.Page):
        user_handler = StravaUserHandler(
            secret_key=SECRET_KEY, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, database=DB_NAME
        )
        activity_handler = StravaActivityHandler(
            user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, database=DB_NAME
        )

        page.title = "Honigmann"
        page.padding = 0
        page.theme = ft.theme.Theme(font_family="Verdana")
        page.theme.page_transitions.windows = "cupertino"
        page.fonts = {"Pacifico": "/Pacifico-Regular.ttf"}
        page.bgcolor = "#fff5f5f5"
        app = FletApp(
            page=page,
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            activity_handler=activity_handler,
            user_handler=user_handler,
            strava_service_url=STRAVA_SERVICE_URL,
        )
        page.add(app)
        page.update()
        app.initialize()
        page.go("/")

    ft.app(target=main, port=8550, view=ft.WEB_BROWSER)
