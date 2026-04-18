import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cipher_identity import CipherIdentity
from app.schemas.cipher_identity import CipherIdentityCreate, CipherIdentityUpdate

async def get_all(db: AsyncSession):
    result = await db.execute(select(CipherIdentity))
    return result.scalars().all()

async def get_by_cipher_id(db: AsyncSession, cipher_id: uuid.UUID):
    result = await db.execute(select(CipherIdentity).where(CipherIdentity.cipher_id == cipher_id))
    return result.scalar_one_or_none()

async def create(db: AsyncSession, data: CipherIdentityCreate):
    identity = CipherIdentity(**data.model_dump())
    db.add(identity)
    await db.commit()
    await db.refresh(identity)
    return identity

async def update(db: AsyncSession, cipher_id: uuid.UUID, data: CipherIdentityUpdate):
    identity = await get_by_cipher_id(db, cipher_id)
    if not identity:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(identity, field, value)
    await db.commit()
    await db.refresh(identity)
    return identity

async def delete(db: AsyncSession, cipher_id: uuid.UUID):
    identity = await get_by_cipher_id(db, cipher_id)
    if not identity:
        return False
    await db.delete(identity)
    await db.commit()
    return True
