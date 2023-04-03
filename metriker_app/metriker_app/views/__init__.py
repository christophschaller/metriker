"""The vies package holds all views of the Metriker App."""
from .challenges_view import ChallengesView
from .data_privacy_view import DataPrivacyView
from .login_view import LoginView
from .user_view import UserView

__all__ = ["UserView", "ChallengesView", "LoginView", "DataPrivacyView"]
