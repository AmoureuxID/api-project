from __future__ import annotations

import asyncio
import base64
import json
import os
import time
from typing import Any

from platforms._base import build_platform_router
from utils.upstream import UpstreamHTTPError, request_json


BASE_URL = os.getenv("DRAMADASH_BASE_URL", "https://www.dramadash.app/api")

_TOKEN_LOCK = asyncio.Lock()
_TOKEN_CACHE: dict[str, Any] = {"token": "", "expires_at": 0}


def _jwt_expiry(token: str) -> int:
    try:
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode("utf-8")))
        return int(payload.get("exp", 0))
    except Exception:
        return 0


async def _get_guest_token() -> str:
    now = int(time.time())
    cached_token = str(_TOKEN_CACHE.get("token") or "")
    cached_exp = int(_TOKEN_CACHE.get("expires_at") or 0)
    if cached_token and cached_exp - 60 > now:
        return cached_token

    async with _TOKEN_LOCK:
        now = int(time.time())
        cached_token = str(_TOKEN_CACHE.get("token") or "")
        cached_exp = int(_TOKEN_CACHE.get("expires_at") or 0)
        if cached_token and cached_exp - 60 > now:
            return cached_token

        url = f"{BASE_URL.rstrip('/')}/landing"
        payload = await request_json(
            method="POST",
            url=url,
            json_body={},
            headers={"content-type": "application/json"},
        )
        if not isinstance(payload, dict):
            raise UpstreamHTTPError(502, "Invalid token response from upstream")

        token = str(payload.get("token") or "")
        if not token:
            raise UpstreamHTTPError(502, "Unable to acquire DramaDash guest token")

        exp = _jwt_expiry(token) or now + 3600
        _TOKEN_CACHE["token"] = token
        _TOKEN_CACHE["expires_at"] = exp
        return token


async def _dramadash_auth_provider(_: str) -> dict[str, str]:
    token = await _get_guest_token()
    return {
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }


router = build_platform_router(
    platform="dramadash",
    base_url=BASE_URL,
    auth_provider=_dramadash_auth_provider,
    routes={
        "trending": {"path": "/home", "method": "GET"},
        "detail": {
            "path": "/drama/{id}",
            "method": "GET",
            "defaults": {"id": "1"},
        },
        "episodes": {
            "path": "/drama/{id}",
            "method": "GET",
            "defaults": {"id": "1"},
        },
        "search": {
            "path": "/search/{type}",
            "method": "POST",
            "defaults": {"type": "all"},
        },
    },
)
