from __future__ import annotations

import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from .context import bind_request_context, clear_request_context

REQUEST_ID_HEADER = "X-Request-ID"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, *, access_log_enabled: bool = True) -> None:
        super().__init__(app)
        self.access_log_enabled = access_log_enabled
        self.logger = logging.getLogger("app.access")

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid4().hex
        client_ip = request.client.host if request.client else "-"
        token = bind_request_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
        )
        started_at = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            status_code = 500
            raise
        finally:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            bind_request_context(status_code=status_code, duration_ms=duration_ms)
            if self.access_log_enabled:
                self.logger.info(
                    "request completed",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        "request_id": request_id,
                        "client_ip": client_ip,
                    },
                )
            clear_request_context(token)
