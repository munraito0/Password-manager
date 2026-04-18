import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate

async def get_all(db: AsyncSession):
    result = await db.execute(select(Device))
    return result.scalars().all()

async def get_by_id(db: AsyncSession, device_id: uuid.UUID):
    result = await db.execute(select(Device).where(Device.id == device_id))
    return result.scalar_one_or_none()

async def create(db: AsyncSession, data: DeviceCreate):
    device = Device(**data.model_dump())
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device

async def update(db: AsyncSession, device_id: uuid.UUID, data: DeviceUpdate):
    device = await get_by_id(db, device_id)
    if not device:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(device, field, value)
    await db.commit()
    await db.refresh(device)
    return device

async def delete(db: AsyncSession, device_id: uuid.UUID):
    device = await get_by_id(db, device_id)
    if not device:
        return False
    await db.delete(device)
    await db.commit()
    return True
