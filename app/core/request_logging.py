from __future__ import annotations

import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger("request_logger")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()

        try:
            response = await call_next(request)

        except Exception:
            process_time_ms = (time.perf_counter() - start_time) * 1000

            logger.exception(
                "request_failed | request_id=%s | method=%s | path=%s | duration_ms=%.2f",
                request_id,
                request.method,
                request.url.path,
                process_time_ms,
            )

            raise

        process_time_ms = (time.perf_counter() - start_time) * 1000

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed | request_id=%s | method=%s | path=%s | status_code=%s | duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            process_time_ms,
        )

        return response