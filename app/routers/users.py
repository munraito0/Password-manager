import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.errors import ERROR_RESPONSES, NotFoundException
from app.logger import logger
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services import user_service

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse], responses=ERROR_RESPONSES)
async def get_users(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    users = await user_service.get_all(db)
    logger.info(
        f"Retrieved {len(users)} users",
        extra={"method": "GET", "path": "/api/users", "statusCode": 200},
    )
    return users


@router.get("/{user_id}", response_model=UserResponse, responses=ERROR_RESPONSES)
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    user = await user_service.get_by_id(db, user_id)
    if not user:
        logger.warning(
            f"User {user_id} not found",
            extra={"method": "GET", "path": f"/api/users/{user_id}", "statusCode": 404},
        )
        raise NotFoundException(f"User {user_id} not found")
    return user


@router.post("/", response_model=UserResponse, status_code=201, responses=ERROR_RESPONSES)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    user = await user_service.create(db, data)
    logger.info(
        "User successfully created",
        extra={"method": "POST", "path": "/api/users", "statusCode": 201},
    )
    return user


@router.put("/{user_id}", response_model=UserResponse, responses=ERROR_RESPONSES)
async def update_user(user_id: uuid.UUID, data: UserUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    user = await user_service.update(db, user_id, data)
    if not user:
        raise NotFoundException(f"User {user_id} not found")
    logger.info(
        f"User {user_id} successfully updated",
        extra={"method": "PUT", "path": f"/api/users/{user_id}", "statusCode": 200},
    )
    return user


@router.delete("/{user_id}", status_code=204, responses=ERROR_RESPONSES)
async def delete_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    deleted = await user_service.delete(db, user_id)
    if not deleted:
        raise NotFoundException(f"User {user_id} not found")
    logger.info(
        f"User {user_id} successfully deleted",
        extra={"method": "DELETE", "path": f"/api/users/{user_id}", "statusCode": 204},
    )
