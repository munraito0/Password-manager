import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.folder import Folder
from app.schemas.folder import FolderCreate, FolderUpdate

async def get_all(db: AsyncSession):
    result = await db.execute(select(Folder))
    return result.scalars().all()

async def get_by_id(db: AsyncSession, folder_id: uuid.UUID):
    result = await db.execute(select(Folder).where(Folder.id == folder_id))
    return result.scalar_one_or_none()

async def create(db: AsyncSession, data: FolderCreate):
    folder = Folder(**data.model_dump())
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder

async def update(db: AsyncSession, folder_id: uuid.UUID, data: FolderUpdate):
    folder = await get_by_id(db, folder_id)
    if not folder:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(folder, field, value)
    await db.commit()
    await db.refresh(folder)
    return folder

async def delete(db: AsyncSession, folder_id: uuid.UUID):
    folder = await get_by_id(db, folder_id)
    if not folder:
        return False
    await db.delete(folder)
    await db.commit()
    return True

