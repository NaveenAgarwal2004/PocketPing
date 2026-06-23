"""Lightweight HTTP health server for Render Free Web Service."""

from flask import Flask

from config import PORT

health_app: Flask = Flask(__name__)


@health_app.get("/")
def home() -> tuple[str, int]:
    return "Bot is running", 200


@health_app.get("/health")
def health() -> tuple[str, int]:
    return "OK", 200


def run_health_server() -> None:
    """Start Flask dev server. Intended to run in a daemon thread."""
    health_app.run(host="0.0.0.0", port=PORT, use_reloader=False)
