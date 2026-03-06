from __future__ import annotations

import os

from platforms._base import build_platform_router


BASE_URL = os.getenv("FREEREELS_BASE_URL", "https://apiv2.free-reels.com/frv2-api")


router = build_platform_router(
    platform="freereels",
    base_url=BASE_URL,
    routes={
        "trending": {"path": "/foryou/feed", "method": "GET"},
        "detail": {"path": "/drama/info_v2", "method": "GET"},
        "episodes": {"path": "/drama/info_push_v2", "method": "GET"},
        "search": {"path": "/search/drama", "method": "GET"},
    },
)
