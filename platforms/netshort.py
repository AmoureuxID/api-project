from __future__ import annotations

import os

from platforms._base import build_platform_router


BASE_URL = os.getenv("NETSHORT_BASE_URL", "https://appsecapi.netshort.com/prod-app-api")


def _netshort_headers() -> dict[str, str]:
    headers = {
        "content-type": "application/json",
        "authorization": os.getenv("NETSHORT_AUTHORIZATION", ""),
        "device-code": os.getenv("NETSHORT_DEVICE_CODE", ""),
        "app-version": os.getenv("NETSHORT_APP_VERSION", ""),
        "content-language": os.getenv("NETSHORT_CONTENT_LANGUAGE", ""),
    }
    return {k: v for k, v in headers.items() if v}


router = build_platform_router(
    platform="netshort",
    base_url=BASE_URL,
    base_headers=_netshort_headers(),
    routes={
        "trending": {
            "path": "/video/shortPlay/recommend/load_user_recommend",
            "method": "POST",
        },
        "detail": {"path": "/video/shortPlay/base/detail_info/V2", "method": "POST"},
        "episodes": {
            "path": "/video/shortPlay/base/episode/detail_info",
            "method": "POST",
        },
        "search": {
            "path": "/video/shortPlay/recommend/loadBackRecommend",
            "method": "POST",
        },
    },
)
