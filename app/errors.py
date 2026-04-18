from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


def _body(status: int, message: str, details=None):
    return {"status": status, "message": message, "details": details or []}


def register_exception_handlers(app):
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        details = [
            {"field": ".".join(str(x) for x in e["loc"][1:]), "error": e["msg"]}
            for e in exc.errors()
        ]
        return JSONResponse(status_code=400, content=_body(400, "Validation failed", details))

    @app.exception_handler(HTTPException)
    async def http_handler(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content=_body(exc.status_code, str(exc.detail)))

    @app.exception_handler(SQLAlchemyError)
    async def db_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(status_code=500, content=_body(500, "Internal server error"))


_ERROR_EXAMPLE = {
    "application/json": {
        "example": {"status": 400, "message": "Validation failed", "details": []}
    }
}
ERROR_RESPONSES = {
    400: {"description": "Validation failed", "content": _ERROR_EXAMPLE},
    404: {"description": "Not found", "content": _ERROR_EXAMPLE},
    500: {"description": "Internal server error", "content": _ERROR_EXAMPLE},
}
