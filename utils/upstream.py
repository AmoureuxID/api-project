from __future__ import annotations

from typing import Any

import httpx


class UpstreamHTTPError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)


_client: httpx.AsyncClient | None = None


async def startup_upstream_client() -> None:
    global _client
    if _client is None:
        timeout = httpx.Timeout(30.0, connect=10.0)
        _client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)


async def shutdown_upstream_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def _get_client() -> httpx.AsyncClient:
    if _client is None:
        await startup_upstream_client()
    assert _client is not None
    return _client


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            for key in ("message", "msg", "error", "detail"):
                value = payload.get(key)
                if isinstance(value, str) and value:
                    return value
        return str(payload)
    except Exception:
        text = response.text.strip()
        return text or "Upstream request failed"


async def request_json(
    *,
    method: str,
    url: str,
    params: dict[str, Any] | None = None,
    json_body: Any | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    client = await _get_client()
    try:
        response = await client.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json_body,
            headers=headers,
        )
    except httpx.RequestError as exc:
        raise UpstreamHTTPError(502, f"Upstream connection failed: {exc}") from exc

    if response.status_code >= 400:
        raise UpstreamHTTPError(response.status_code, _extract_error_message(response))

    content_type = (response.headers.get("content-type") or "").lower()
    if "application/json" in content_type:
        return response.json()
    return {"raw": response.text}
