from __future__ import annotations

import os

from platforms._base import build_platform_router


BASE_URL = os.getenv("DRAMABOX_BASE_URL", "https://sapi.dramaboxdb.com/drama-box")


def _dramabox_headers() -> dict[str, str]:
    headers = {
        "content-type": "application/json; charset=UTF-8",
        "tn": os.getenv("DRAMABOX_TN", ""),
        "sn": os.getenv("DRAMABOX_SN", ""),
        "device-id": os.getenv("DRAMABOX_DEVICE_ID", ""),
        "android-id": os.getenv("DRAMABOX_ANDROID_ID", ""),
        "instanceid": os.getenv("DRAMABOX_INSTANCE_ID", ""),
        "userid": os.getenv("DRAMABOX_USER_ID", ""),
        "version": os.getenv("DRAMABOX_VERSION", "531"),
        "pline": os.getenv("DRAMABOX_PLINE", "ANDROID"),
    }
    return {k: v for k, v in headers.items() if v}


router = build_platform_router(
    platform="dramabox",
    base_url=BASE_URL,
    base_headers=_dramabox_headers(),
    routes={
        "trending": {"path": "/he001/rank", "method": "POST"},
        "detail": {"path": "/chapterv2/detail", "method": "POST"},
        "episodes": {"path": "/chapterv2/batch/load", "method": "POST"},
        "search": {"path": "/search/search", "method": "POST"},
    },
)
