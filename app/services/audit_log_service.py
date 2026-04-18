import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate, AuditLogUpdate

async def get_all(db: AsyncSession):
    result = await db.execute(select(AuditLog))
    return result.scalars().all()

async def get_by_id(db: AsyncSession, log_id: uuid.UUID):
    result = await db.execute(select(AuditLog).where(AuditLog.id == log_id))
    return result.scalar_one_or_none()

async def create(db: AsyncSession, data: AuditLogCreate):
    log = AuditLog(**data.model_dump())
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log

async def update(db: AsyncSession, log_id: uuid.UUID, data: AuditLogUpdate):
    log = await get_by_id(db, log_id)
    if not log:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    await db.commit()
    await db.refresh(log)
    return log

async def delete(db: AsyncSession, log_id: uuid.UUID):
    log = await get_by_id(db, log_id)
    if not log:
        return False
    await db.delete(log)
    await db.commit()
    return True
