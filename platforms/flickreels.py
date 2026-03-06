from __future__ import annotations

import os

from platforms._base import build_platform_router


BASE_URL = os.getenv("FLICKREELS_BASE_URL", "https://api.farsunpteltd.com")


router = build_platform_router(
    platform="flickreels",
    base_url=BASE_URL,
    base_headers={"content-type": "application/json"},
    routes={
        "trending": {"path": "/app/playlet/forYou", "method": "POST"},
        "detail": {"path": "/app/playlet/play", "method": "POST"},
        "episodes": {"path": "/app/playlet/chapterList", "method": "POST"},
        "search": {"path": "/app/user_search/search", "method": "POST"},
    },
)
