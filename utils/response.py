from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse


def normalize_upstream_data(payload: Any) -> Any:
    if payload is None:
        return []
    if isinstance(payload, dict):
        if "data" in payload:
            return payload.get("data", [])
        if "result" in payload:
            return payload.get("result", [])
    return payload


def success_response(*, platform: str, data: Any) -> dict[str, Any]:
    return {
        "status": "success",
        "platform": platform,
        "data": data if data is not None else [],
    }


def error_response(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message,
        },
    )
