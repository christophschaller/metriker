import flet as ft

from database_utils.user_handler import StravaUser

from .base_view import BaseView


class UserView(BaseView):
    def __init__(self, app, user_id: str, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.route = f"/user/{user_id}"
        self.user: StravaUser = self.app.user_handler.get(user_id)

        # add controls to frame
        self.extend_controls()

    def extend_controls(self) -> None:
        self.controls.extend([ft.Text(self.user.name)])
