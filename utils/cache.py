from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable


CACHE_TTLS: dict[str, int] = {
    "trending": 3600,
    "detail": 86400,
    "episodes": 86400,
    "search": 600,
}


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class ResponseCache:
    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        async with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            if entry.expires_at <= time.time():
                self._store.pop(key, None)
                return None
            return entry.value

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            return
        async with self._lock:
            self._store[key] = CacheEntry(
                value=value,
                expires_at=time.time() + ttl_seconds,
            )

    async def get_or_set(
        self,
        key: str,
        ttl_seconds: int,
        factory: Callable[[], Awaitable[Any]],
    ) -> Any:
        cached = await self.get(key)
        if cached is not None:
            return cached
        fresh = await factory()
        await self.set(key, fresh, ttl_seconds)
        return fresh


def build_cache_key(
    *,
    platform: str,
    endpoint: str,
    method: str,
    path: str,
    query: dict[str, Any] | None = None,
    body: Any | None = None,
) -> str:
    normalized = {
        "platform": platform,
        "endpoint": endpoint,
        "method": method.upper(),
        "path": path,
        "query": query or {},
        "body": body if body is not None else {},
    }
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"))


cache_store = ResponseCache()
