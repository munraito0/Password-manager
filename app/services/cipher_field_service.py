import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cipher_field import CipherField
from app.schemas.cipher_field import CipherFieldCreate, CipherFieldUpdate

async def get_all(db: AsyncSession):
    result = await db.execute(select(CipherField))
    return result.scalars().all()

async def get_by_id(db: AsyncSession, field_id: uuid.UUID):
    result = await db.execute(select(CipherField).where(CipherField.id == field_id))
    return result.scalar_one_or_none()

async def create(db: AsyncSession, data: CipherFieldCreate):
    field = CipherField(**data.model_dump())
    db.add(field)
    await db.commit()
    await db.refresh(field)
    return field

async def update(db: AsyncSession, field_id: uuid.UUID, data: CipherFieldUpdate):
    field = await get_by_id(db, field_id)
    if not field:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(field, k, v)
    await db.commit()
    await db.refresh(field)
    return field

async def delete(db: AsyncSession, field_id: uuid.UUID):
    field = await get_by_id(db, field_id)
    if not field:
        return False
    await db.delete(field)
    await db.commit()
    return True
