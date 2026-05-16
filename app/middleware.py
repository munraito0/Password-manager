import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.logger import logger
from app.services import metrics_service

_RATE_LIMIT = 20
_RATE_WINDOW = 60.0

_ip_requests: dict[str, dict] = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()

        entry = _ip_requests.get(ip)
        if entry is None or now - entry["window_start"] > _RATE_WINDOW:
            _ip_requests[ip] = {"count": 1, "window_start": now}
        else:
            entry["count"] += 1
            if entry["count"] > _RATE_LIMIT:
                metrics_service.rate_limit_hits_total.inc()
                logger.warning(
                    f"Rate limit exceeded for IP: {ip} on {request.url.path}",
                    extra={"method": request.method, "path": request.url.path, "statusCode": 429},
                )
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."},
                    headers={"Retry-After": str(_RATE_WINDOW)},
                )

        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()

        logger.debug(
            f"Incoming {request.method} {request.url.path}",
            extra={"method": request.method, "path": request.url.path, "statusCode": 0},
        )

        response = await call_next(request)

        duration_ms = int((time.monotonic() - start) * 1000)
        status = response.status_code
        message = f"{request.method} {request.url.path} -> {status} ({duration_ms}ms)"

        extra = {"method": request.method, "path": request.url.path, "statusCode": status}

        if status < 400:
            logger.info(message, extra=extra)
        elif status < 500:
            logger.warning(message, extra=extra)
        else:
            logger.error(message, extra=extra)

        return response
