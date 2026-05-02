import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken
from app.schemas.refresh_token import RefreshTokenCreate, RefreshTokenUpdate

async def get_all(db: AsyncSession):
    result = await db.execute(select(RefreshToken))
    return result.scalars().all()

async def get_by_hash(db: AsyncSession, token_hash: str):
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    return result.scalar_one_or_none()

async def get_by_id(db: AsyncSession, token_id: uuid.UUID):
    result = await db.execute(select(RefreshToken).where(RefreshToken.id == token_id))
    return result.scalar_one_or_none()

async def create(db: AsyncSession, data: RefreshTokenCreate):
    token = RefreshToken(**data.model_dump())
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token

async def update(db: AsyncSession, token_id: uuid.UUID, data: RefreshTokenUpdate):
    token = await get_by_id(db, token_id)
    if not token:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(token, field, value)
    await db.commit()
    await db.refresh(token)
    return token

async def delete(db: AsyncSession, token_id: uuid.UUID):
    token = await get_by_id(db, token_id)
    if not token:
        return False
    await db.delete(token)
    await db.commit()
    return True
