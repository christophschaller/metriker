"""Main module of the metriker flet app."""
import logging.config

import flet as ft
import requests
import sentry_sdk
from database_utils.activity_handler import StravaActivityHandler
from database_utils.user_handler import StravaUser, StravaUserHandler
from flet.auth.oauth_provider import OAuthProvider

from .config import settings
from .views import ChallengesView, DataPrivacyView, LoginView, UserView

# setup logging
logging.config.fileConfig(settings.LOGGING_CONFIG_PATH, disable_existing_loggers=False)
logger = logging.getLogger(__name__)
# setup logging to sentry
sentry_sdk.init(dsn=settings.SENTRY_DSN)


class Metriker(ft.UserControl):
    """This class defines the frame of the webapp and its interfaces."""

    def __init__(  # noqa: PLR0913 - Ignore: Too many arguments to function call
        self,
        page: ft.Page,
        auth_provider: OAuthProvider,
        user_handler: StravaUserHandler,
        activity_handler: StravaActivityHandler,
        strava_service_url: str,
    ):
        """Init of Metriker.

        Args:
            page: ft.Page
            auth_provider: flet OAuthProvider to manage auth flow
            user_handler: wrapper for user storage
            activity_handler: wrapper for activity storage
            strava_service_url: url to background service interfacing with the strava api.
        """
        super().__init__()
        self.page = page

        # general settings
        self.page.title = "Honigmann"
        self.page.padding = 0
        self.page.theme = ft.Theme(font_family="Verdana")
        self.page.theme.page_transitions.windows = "cupertino"
        self.page.fonts = {"Pacifico": "/Pacifico-Regular.ttf"}
        self.page.bgcolor = "#fff5f5f5"

        # auth provider for strava login
        self.auth_provider = auth_provider
        # database wrappers
        self.user_handler = user_handler
        self.activity_handler = activity_handler

        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        self.page.on_login = self.on_login
        self.page.on_logout = self.on_logout

        # flet user object
        self.user = None
        # url of server interfacing with strava api to request activities
        self.strava_service_url = strava_service_url

        self.challenges_view = ChallengesView(self)

    def build(self) -> ft.Column:
        """Method required to create initial site.

        This adds an empty column to the site.
        All it does it fulfilling the requirement of overriding ft.UserControl.build

        Returns:
            None
        """
        return ft.Column()

    def login(self, _: ft.ControlEvent) -> None:
        """Initiate Login.

        Args:
            _: unused event from caller

        Returns:
            None
        """
        self.page.login(self.auth_provider)

    def on_login(self, event: ft.LoginEvent) -> None:
        """Flow triggered on successful login.

        Args:
            event: login event from caller

        Returns:
            None
        """
        if not event.error:
            # set user
            self.user = self.page.auth.user
            # initialise challenges view
            self.challenges_view = ChallengesView(self)
            existing_user = self.user_handler.get(self.user.id)
            if not existing_user:
                # add new user to db
                self.user_handler.add(
                    StravaUser(
                        id=self.user.id,
                        name=self.user["firstname"],
                        refresh_token=self.page.auth.token.refresh_token,
                    ),
                )
                # request ingestion existing user activities
                requests.post(
                    f"{self.strava_service_url}/updateUserActivities?user_id={self.user.id}",
                    timeout=settings.STRAVA_SERVICE_TIMEOUT,
                )
            elif existing_user.refresh_token != self.page.auth.token.refresh_token:
                # update refresh token if it changed
                self.user_handler.update(
                    StravaUser(
                        id=self.user.id,
                        name=self.user["firstname"],
                        refresh_token=self.page.auth.token.refresh_token,
                    ),
                )
            self.page.update()
            self.page.go("/challenges")
        else:
            logger.error(event.error)

    def logout(self, _: ft.ControlEvent) -> None:
        """Initiate Logout.

        Args:
            _: unused event from caller

        Returns:
            None
        """
        self.user = None
        self.challenges_view = None
        self.page.logout()

    def on_logout(self, _: ft.LoginEvent) -> None:
        """Flow triggered on logout.

        Args:
            _: unused logout event from caller

        Returns:
            None
        """
        self.page.update()
        self.page.go("/")

    def route_change(self, _: ft.RouteChangeEvent) -> None:  # noqa: C901 - Ignore: `route_change` is too complex
        """Handle route changes by setting appropriate views and content.

        Args:
            _: unused route provided by on_route_change

        Returns:
            None
        """
        template_route = ft.TemplateRoute(self.page.route)

        # redirect from / depending on login status
        if template_route.match("/"):
            if self.user:
                self.page.go("/challenges")
            else:
                self.page.go("/login")

        # make sure login is only visible for logged out users
        if template_route.match("/login"):
            if not self.user:
                self.page.views.clear()
                self.page.views.append(LoginView(self))
                self.page.update()
            else:
                self.page.go("/")

        # handle challenges views
        if template_route.match("/challenges*"):
            # redirect to first challenge
            if template_route.match("/challenges"):
                self.page.views.clear()
                self.page.views.append(self.challenges_view)
                self.page.update()
                first_challenge = list(self.challenges_view.challenges.values())[0]
                self.page.go(f"/challenges/{first_challenge.name}")
            # set internal content of the challenges view to match the selected challenge
            if template_route.match("/challenges/:challenge_name"):
                # attributes are assigned dynamically
                challenge_name = template_route.challenge_name
                self.challenges_view.set_active_challenge(challenge_name)

        # handle user views
        if template_route.match("/user/:user_id"):
            # attributes are assigned dynamically
            user_id = template_route.user_id
            if user_id not in self.user_handler.keys():
                self.page.go("/")
                return
            self.page.views.append(UserView(self, user_id=user_id))

        # handle data privacy view
        if template_route.match("/data_privacy"):
            self.page.views.append(DataPrivacyView(self))

    def view_pop(self, _: ft.ViewPopEvent) -> None:
        """Flow triggered on view pop.

        Args:
            _: unused view provided by on_view_pop

        Returns:
            None
        """
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def initialize(self) -> None:
        """Initialize the Metriker App.

        This should run after adding a page object to a Metriker object.

        Returns:
            None
        """
        self.page.views.clear()
        self.page.update()
        self.page.go("/")
