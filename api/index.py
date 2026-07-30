"""Vercel Python entrypoint.

Vercel discovers `app` here and serves it as an ASGI function. The packages
themselves are installed from the workspace by requirements.txt, so this is a
thin adapter rather than another sys.path shim.
"""

from app_server.main import app

__all__ = ["app"]
