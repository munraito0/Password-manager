import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

async def get_all(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

async def get_by_id(db: AsyncSession, user_id: uuid.UUID):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def create(db: AsyncSession, data: UserCreate):
    user = User(**data.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update(db: AsyncSession, user_id: uuid.UUID, data: UserUpdate):
    user = await get_by_id(db, user_id)
    if not user:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user

async def delete(db: AsyncSession, user_id: uuid.UUID):
    user = await get_by_id(db, user_id)
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True

