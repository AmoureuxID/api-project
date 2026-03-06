from __future__ import annotations

import os

from platforms._base import build_platform_router


BASE_URL = os.getenv("MELOLO_BASE_URL", "https://api.tmtreader.com")


router = build_platform_router(
    platform="melolo",
    base_url=BASE_URL,
    routes={
        "trending": {"path": "/i18n_novel/search/scroll_recommend/v1/", "method": "GET"},
        "detail": {"path": "/service/settings/v3/", "method": "GET"},
        "episodes": {"path": "/i18n_novel/userapi/ab/result/", "method": "GET"},
        "search": {"path": "/i18n_novel/search/scroll_recommend/v1/", "method": "GET"},
    },
)
