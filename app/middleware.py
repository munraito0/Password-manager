import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.logger import logger


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
