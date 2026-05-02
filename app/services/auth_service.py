import hashlib
from datetime import datetime, timezone, timedelta

import bcrypt
from fastapi import HTTPException
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import config
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.refresh_token import RefreshTokenCreate
from app.services import refresh_token_service


def validate_password(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password does not meet security requirements")
    if not any(c.isalpha() for c in password):
        raise HTTPException(status_code=400, detail="Password does not meet security requirements")
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="Password does not meet security requirements")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)


def create_access_token(user_id: str, email: str) -> str:
    return _create_token(
        {"sub": user_id, "email": email, "type": "access"},
        timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        {"sub": user_id, "type": "refresh"},
        timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS),
    )


async def register(db: AsyncSession, data: RegisterRequest) -> dict:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")

    validate_password(data.password)

    user = User(
        email=data.email,
        name=data.name,
        master_password_hash=hash_password(data.password),
        kdf_type=0,
        kdf_iterations=600000,
    )
    db.add(user)
    await db.commit()

    return {"message": "User successfully registered"}


async def login(db: AsyncSession, data: LoginRequest) -> dict:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.master_password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_id = str(user.id)
    access_token = create_access_token(user_id, user.email)
    refresh_token = create_refresh_token(user_id)

    expires_at = datetime.now(timezone.utc) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    await refresh_token_service.create(db, RefreshTokenCreate(
        user_id=user.id,
        token_hash=_hash_token(refresh_token),
        expires_at=expires_at,
    ))

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


async def refresh(db: AsyncSession, refresh_token_str: str) -> dict:
    credentials_error = HTTPException(status_code=401, detail="Invalid or expired refresh token")
    try:
        payload = jwt.decode(refresh_token_str, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_error
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_error
    except JWTError:
        raise credentials_error

    token_hash = _hash_token(refresh_token_str)
    existing = await refresh_token_service.get_by_hash(db, token_hash)
    if not existing:
        raise credentials_error

    result = await db.execute(select(User).where(User.id == existing.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise credentials_error

    await refresh_token_service.delete(db, existing.id)

    new_access = create_access_token(str(user.id), user.email)
    new_refresh = create_refresh_token(str(user.id))
    expires_at = datetime.now(timezone.utc) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    await refresh_token_service.create(db, RefreshTokenCreate(
        user_id=user.id,
        token_hash=_hash_token(new_refresh),
        expires_at=expires_at,
    ))

    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}


async def logout(db: AsyncSession, refresh_token_str: str) -> None:
    try:
        payload = jwt.decode(refresh_token_str, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if payload.get("type") != "refresh":
            return
    except JWTError:
        return

    token_hash = _hash_token(refresh_token_str)
    existing = await refresh_token_service.get_by_hash(db, token_hash)
    if existing:
        await refresh_token_service.delete(db, existing.id)
