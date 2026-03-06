from __future__ import annotations

import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from utils.response import error_response


def _load_api_keys() -> set[str]:
    raw = os.getenv("API_KEYS") or os.getenv("API_KEY") or "CHANGE_ME"
    return {item.strip() for item in raw.split(",") if item.strip()}


class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.api_keys = _load_api_keys()
        self.header_name = "x-api-key"
        self.exempt_paths = {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if path in self.exempt_paths or path.startswith("/docs/"):
            return await call_next(request)

        supplied_key = request.headers.get(self.header_name)
        if not supplied_key or supplied_key not in self.api_keys:
            return error_response("Unauthorized", status_code=401)

        return await call_next(request)
