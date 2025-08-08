"""REST API server for external BK-Integration access."""

from .server import create_app

__all__ = ["create_app"]