import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cipher_card import CipherCard
from app.schemas.cipher_card import CipherCardCreate, CipherCardUpdate

async def get_all(db: AsyncSession):
    result = await db.execute(select(CipherCard))
    return result.scalars().all()

async def get_by_cipher_id(db: AsyncSession, cipher_id: uuid.UUID):
    result = await db.execute(select(CipherCard).where(CipherCard.cipher_id == cipher_id))
    return result.scalar_one_or_none()

async def create(db: AsyncSession, data: CipherCardCreate):
    card = CipherCard(**data.model_dump())
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card

async def update(db: AsyncSession, cipher_id: uuid.UUID, data: CipherCardUpdate):
    card = await get_by_cipher_id(db, cipher_id)
    if not card:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(card, field, value)
    await db.commit()
    await db.refresh(card)
    return card

async def delete(db: AsyncSession, cipher_id: uuid.UUID):
    card = await get_by_cipher_id(db, cipher_id)
    if not card:
        return False
    await db.delete(card)
    await db.commit()
    return True
