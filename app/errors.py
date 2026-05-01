import logging
from datetime import datetime, timezone

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.logger import logger

_STATUS_TEXT = {
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    409: "Conflict",
    500: "Internal Server Error",
}


class NotFoundException(Exception):
    def __init__(self, message: str = "Resource not found"):
        self.message = message


class ForbiddenException(Exception):
    def __init__(self, message: str = "Access denied"):
        self.message = message


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _body(request: Request, status: int, message: str, details=None) -> dict:
    body = {
        "timestamp": _now(),
        "status": status,
        "error": _STATUS_TEXT.get(status, "Error"),
        "message": message,
        "path": request.url.path,
    }
    if details:
        body["details"] = details
    return body


def register_exception_handlers(app) -> None:

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        details = [
            {"field": ".".join(str(x) for x in e["loc"][1:]), "error": e["msg"]}
            for e in exc.errors()
        ]
        logger.warning(
            "Validation error",
            extra={"method": request.method, "path": request.url.path, "statusCode": 400},
        )
        return JSONResponse(
            status_code=400,
            content=_body(request, 400, "Validation failed", details),
        )

    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: NotFoundException):
        logger.warning(
            exc.message,
            extra={"method": request.method, "path": request.url.path, "statusCode": 404},
        )
        return JSONResponse(status_code=404, content=_body(request, 404, exc.message))

    @app.exception_handler(ForbiddenException)
    async def forbidden_handler(request: Request, exc: ForbiddenException):
        logger.warning(
            exc.message,
            extra={"method": request.method, "path": request.url.path, "statusCode": 403},
        )
        return JSONResponse(status_code=403, content=_body(request, 403, exc.message))

    @app.exception_handler(HTTPException)
    async def http_handler(request: Request, exc: HTTPException):
        level = logging.WARNING if exc.status_code < 500 else logging.ERROR
        logger.log(
            level,
            str(exc.detail),
            extra={"method": request.method, "path": request.url.path, "statusCode": exc.status_code},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(request, exc.status_code, str(exc.detail)),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_handler(request: Request, exc: IntegrityError):
        logger.warning(
            f"Integrity error: {type(exc).__name__}",
            extra={"method": request.method, "path": request.url.path, "statusCode": 409},
        )
        return JSONResponse(status_code=409, content=_body(request, 409, "Resource already exists"))

    @app.exception_handler(SQLAlchemyError)
    async def db_handler(request: Request, exc: SQLAlchemyError):
        logger.error(
            f"Database error: {type(exc).__name__}: {exc.args[0] if exc.args else exc}",
            extra={"method": request.method, "path": request.url.path, "statusCode": 500},
        )
        return JSONResponse(status_code=500, content=_body(request, 500, "Internal server error"))

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled exception: {type(exc).__name__}",
            extra={"method": request.method, "path": request.url.path, "statusCode": 500},
        )
        return JSONResponse(status_code=500, content=_body(request, 500, "Internal server error"))


_ERROR_EXAMPLE = {
    "application/json": {
        "example": {
            "timestamp": "2024-03-01T12:00:00.000Z",
            "status": 400,
            "error": "Bad Request",
            "message": "Validation failed",
            "path": "/api/resource",
        }
    }
}

ERROR_RESPONSES = {
    400: {"description": "Validation failed", "content": _ERROR_EXAMPLE},
    403: {"description": "Forbidden", "content": _ERROR_EXAMPLE},
    404: {"description": "Not found", "content": _ERROR_EXAMPLE},
    500: {"description": "Internal server error", "content": _ERROR_EXAMPLE},
}
