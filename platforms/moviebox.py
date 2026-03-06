from __future__ import annotations

import os

from platforms._base import build_platform_router


API_BASE_URL = os.getenv(
    "MOVIEBOX_API_BASE_URL",
    "https://h5-api.aoneroom.com/wefeed-h5api-bff",
)
PLAY_BASE_URL = os.getenv(
    "MOVIEBOX_PLAY_BASE_URL",
    "https://123movienow.cc/wefeed-h5api-bff",
)

TIMEZONE = os.getenv("MOVIEBOX_TIMEZONE", "Asia/Jakarta")
ORIGIN = os.getenv("MOVIEBOX_ORIGIN", "https://moviebox.ph")
REFERER = os.getenv("MOVIEBOX_REFERER", "https://moviebox.ph/")
LANG = os.getenv("MOVIEBOX_LANG", "en")

BASE_HEADERS = {
    "accept": "application/json",
    "x-client-info": f'{{"timezone":"{TIMEZONE}"}}',
    "origin": ORIGIN,
    "referer": REFERER,
    "x-request-lang": LANG,
}


router = build_platform_router(
    platform="moviebox",
    base_url=API_BASE_URL,
    base_headers=BASE_HEADERS,
    routes={
        "trending": {"path": "/subject/trending", "method": "GET"},
        "detail": {
            "path": "/detail",
            "method": "GET",
            "param_alias": {"id": "detailPath"},
        },
        "episodes": {
            "path": "/subject/play",
            "method": "GET",
            "base_url": PLAY_BASE_URL,
            "param_alias": {"id": "subjectId"},
        },
        "search": {
            "path": "/subject/search",
            "method": "GET",
            "param_alias": {"q": "keyword"},
        },
    },
)
