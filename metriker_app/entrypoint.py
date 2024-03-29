"""Entrypoint of the metriker flet app."""
import flet as ft

from metriker_app.config import settings
from metriker_app.main import main

if __name__ == "__main__":
    ft.app(target=main, port=settings.APP_PORT, view=ft.WEB_BROWSER)
