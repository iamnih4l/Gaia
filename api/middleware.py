"""API Middleware — custom logging, CORS, error handling, and latency tracking."""

from __future__ import annotations

import time
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingAndTimingMiddleware(BaseHTTPMiddleware):
    """Log incoming HTTP requests, track execution latency, and handle uncaught exceptions."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        client_host = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url.path)

        logger.info(f"API Request: {method} {url} from {client_host}")

        try:
            response = await call_next(request)
            process_time_ms = (time.time() - start_time) * 1000.0
            response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
            logger.info(
                f"API Response: {method} {url} - Status: {response.status_code} "
                f"- Latency: {process_time_ms:.2f}ms"
            )
            return response
        except Exception as exc:
            process_time_ms = (time.time() - start_time) * 1000.0
            logger.exception(f"Unhandled API Error during {method} {url}: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "detail": str(exc),
                    "latency_ms": round(process_time_ms, 2),
                },
            )
