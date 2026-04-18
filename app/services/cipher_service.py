import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cipher import Cipher
from app.schemas.cipher import CipherCreate, CipherUpdate

async def get_all(db: AsyncSession):
    result = await db.execute(select(Cipher))
    return result.scalars().all()

async def get_by_id(db: AsyncSession, cipher_id: uuid.UUID):
    result = await db.execute(select(Cipher).where(Cipher.id == cipher_id))
    return result.scalar_one_or_none()

async def create(db: AsyncSession, data: CipherCreate):
    cipher = Cipher(**data.model_dump())
    db.add(cipher)
    await db.commit()
    await db.refresh(cipher)
    return cipher

async def update(db: AsyncSession, cipher_id: uuid.UUID, data: CipherUpdate):
    cipher = await get_by_id(db, cipher_id)
    if not cipher:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cipher, field, value)
    await db.commit()
    await db.refresh(cipher)
    return cipher

async def delete(db: AsyncSession, cipher_id: uuid.UUID):
    cipher = await get_by_id(db, cipher_id)
    if not cipher:
        return False
    await db.delete(cipher)
    await db.commit()
    return True