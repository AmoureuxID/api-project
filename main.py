from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from platforms.dramabox import router as dramabox_router
from platforms.dramadash import router as dramadash_router
from platforms.flickreels import router as flickreels_router
from platforms.freereels import router as freereels_router
from platforms.melolo import router as melolo_router
from platforms.moviebox import router as moviebox_router
from platforms.netshort import router as netshort_router
from platforms.swiftdrama import router as swiftdrama_router
from utils.response import error_response, success_response
from utils.security import APIKeyMiddleware
from utils.upstream import shutdown_upstream_client, startup_upstream_client


app = FastAPI(
    title="Teras Dracin API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(APIKeyMiddleware)

app.include_router(dramabox_router)
app.include_router(netshort_router)
app.include_router(flickreels_router)
app.include_router(freereels_router)
app.include_router(melolo_router)
app.include_router(swiftdrama_router)
app.include_router(dramadash_router)
app.include_router(moviebox_router)


@app.on_event("startup")
async def on_startup() -> None:
    await startup_upstream_client()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await shutdown_upstream_client()


@app.get("/health")
async def health() -> dict:
    return success_response(platform="system", data={"service": "ok"})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    if exc.status_code == 404:
        return error_response("Endpoint not found", status_code=404)
    return error_response(detail, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, __: RequestValidationError):
    return error_response("Invalid request parameters", status_code=422)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, __: Exception):
    return error_response("Internal server error", status_code=500)
