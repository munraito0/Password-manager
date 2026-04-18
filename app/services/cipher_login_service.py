import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cipher_login import CipherLogin
from app.schemas.cipher_login import CipherLoginCreate, CipherLoginUpdate

async def get_all(db: AsyncSession):
    result = await db.execute(select(CipherLogin))
    return result.scalars().all()

async def get_by_cipher_id(db: AsyncSession, cipher_id: uuid.UUID):
    result = await db.execute(select(CipherLogin).where(CipherLogin.cipher_id == cipher_id))
    return result.scalar_one_or_none()

async def create(db: AsyncSession, data: CipherLoginCreate):
    login = CipherLogin(**data.model_dump())
    db.add(login)
    await db.commit()
    await db.refresh(login)
    return login

async def update(db: AsyncSession, cipher_id: uuid.UUID, data: CipherLoginUpdate):
    login = await get_by_cipher_id(db, cipher_id)
    if not login:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(login, field, value)
    await db.commit()
    await db.refresh(login)
    return login

async def delete(db: AsyncSession, cipher_id: uuid.UUID):
    login = await get_by_cipher_id(db, cipher_id)
    if not login:
        return False
    await db.delete(login)
    await db.commit()
    return True
