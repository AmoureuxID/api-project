from __future__ import annotations

import json
import re
from typing import Any, Awaitable, Callable

from fastapi import APIRouter, Request

from utils.cache import CACHE_TTLS, build_cache_key, cache_store
from utils.response import error_response, normalize_upstream_data, success_response
from utils.upstream import UpstreamHTTPError, request_json


RouteSpec = dict[str, Any]
AuthProvider = Callable[[str], Awaitable[dict[str, str]]]


def _parse_body(raw_body: bytes) -> Any:
    if not raw_body:
        return {}
    try:
        return json.loads(raw_body.decode("utf-8"))
    except Exception:
        return {}


def _build_path(
    *,
    template: str,
    query_params: dict[str, str],
    defaults: dict[str, Any] | None = None,
) -> tuple[str, dict[str, str]]:
    merged_params: dict[str, Any] = {}
    if defaults:
        merged_params.update(defaults)
    merged_params.update(query_params)
    consumed: set[str] = set()

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        value = merged_params.get(key)
        if value is None or value == "":
            raise ValueError(f"Missing required query parameter: {key}")
        consumed.add(key)
        return str(value)

    rendered = re.sub(r"{([a-zA-Z0-9_]+)}", replacer, template)
    remaining_query = {k: v for k, v in query_params.items() if k not in consumed}
    return rendered, remaining_query


def _apply_param_aliases(
    query_params: dict[str, str],
    aliases: dict[str, str] | None,
) -> dict[str, str]:
    if not aliases:
        return query_params
    merged = dict(query_params)
    for source_key, target_key in aliases.items():
        source_value = merged.get(source_key)
        if source_value is not None and target_key not in merged:
            merged[target_key] = source_value
    return merged


def build_platform_router(
    *,
    platform: str,
    base_url: str,
    routes: dict[str, RouteSpec],
    base_headers: dict[str, str] | None = None,
    auth_provider: AuthProvider | None = None,
) -> APIRouter:
    router = APIRouter(prefix=f"/{platform}", tags=[platform])
    headers = dict(base_headers or {})

    async def handle_action(action: str, request: Request):
        spec = routes.get(action)
        if spec is None:
            return error_response("Endpoint not found", status_code=404)

        method = str(spec.get("method", "GET")).upper()
        template = str(spec.get("path", "/"))
        route_headers = dict(spec.get("headers", {}))
        defaults = spec.get("defaults")
        route_base_url = str(spec.get("base_url", base_url))
        alias_map = spec.get("param_alias")
        send_query = bool(spec.get("send_query", False))

        raw_query = dict(request.query_params)
        query_params = _apply_param_aliases(raw_query, alias_map)
        raw_body = await request.body()
        body_payload = _parse_body(raw_body)

        try:
            rendered_path, remaining_query = _build_path(
                template=template,
                query_params=query_params,
                defaults=defaults,
            )
        except ValueError as exc:
            return error_response(str(exc), status_code=400)

        cache_ttl = CACHE_TTLS.get(action, 0)
        cache_key = build_cache_key(
            platform=platform,
            endpoint=action,
            method=method,
            path=rendered_path,
            query=remaining_query,
            body=body_payload,
        )

        async def fetch_data():
            request_headers = dict(headers)
            request_headers.update(route_headers)
            if auth_provider is not None:
                request_headers.update(await auth_provider(action))

            url = f"{route_base_url.rstrip('/')}/{rendered_path.lstrip('/')}"
            params: dict[str, str] | None = None
            json_body: Any | None = None

            if method == "GET":
                params = remaining_query
            else:
                if isinstance(body_payload, dict) and body_payload:
                    json_body = body_payload
                else:
                    json_body = remaining_query
                if send_query:
                    params = remaining_query

            upstream_payload = await request_json(
                method=method,
                url=url,
                params=params,
                json_body=json_body,
                headers=request_headers,
            )
            return normalize_upstream_data(upstream_payload)

        try:
            data = await cache_store.get_or_set(cache_key, cache_ttl, fetch_data)
        except UpstreamHTTPError as exc:
            upstream_status = exc.status_code
            if upstream_status >= 500:
                upstream_status = 502
            return error_response(exc.message, status_code=upstream_status)
        except Exception:
            return error_response("Upstream processing failed", status_code=502)

        return success_response(platform=platform, data=data)

    @router.api_route("/trending", methods=["GET", "POST"])
    async def trending(request: Request):
        return await handle_action("trending", request)

    @router.api_route("/detail", methods=["GET", "POST"])
    async def detail(request: Request):
        return await handle_action("detail", request)

    @router.api_route("/episodes", methods=["GET", "POST"])
    async def episodes(request: Request):
        return await handle_action("episodes", request)

    @router.api_route("/search", methods=["GET", "POST"])
    async def search(request: Request):
        return await handle_action("search", request)

    return router
