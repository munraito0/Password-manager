import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import engine, Base
from app.errors import register_exception_handlers
from app.middleware import LoggingMiddleware, RateLimitMiddleware
from app.routers import (
    users, folders, ciphers, devices, refresh_tokens,
    cipher_logins, cipher_cards, cipher_identities,
    cipher_fields, audit_logs, demo,
)
from app.routers import auth

app = FastAPI()

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
register_exception_handlers(app)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(folders.router)
app.include_router(ciphers.router)
app.include_router(devices.router)
app.include_router(refresh_tokens.router)
app.include_router(cipher_logins.router)
app.include_router(cipher_cards.router)
app.include_router(cipher_identities.router)
app.include_router(cipher_fields.router)
app.include_router(audit_logs.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)
