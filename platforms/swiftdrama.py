from __future__ import annotations

import os

from platforms._base import build_platform_router


BASE_URL = os.getenv("SWIFTDRAMA_BASE_URL", "https://api.dramaverses.com")


router = build_platform_router(
    platform="swiftdrama",
    base_url=BASE_URL,
    base_headers={"content-type": "application/json"},
    routes={
        "trending": {"path": "/ps/shortplay/new_list", "method": "POST"},
        "detail": {"path": "/ps/shortplay/detail", "method": "POST"},
        "episodes": {"path": "/ps/shortplay/list", "method": "POST"},
        "search": {"path": "/ps/shortplay/search", "method": "POST"},
    },
)
