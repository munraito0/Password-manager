import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.errors import ERROR_RESPONSES
from app.schemas.audit_log import AuditLogCreate, AuditLogUpdate, AuditLogResponse
from app.services import audit_log_service

router = APIRouter(prefix="/api/audit-logs", tags=["AuditLogs"])

@router.get("/", response_model=list[AuditLogResponse], responses=ERROR_RESPONSES)
async def get_audit_logs(db: AsyncSession = Depends(get_db)):
    return await audit_log_service.get_all(db)

@router.get("/{log_id}", response_model=AuditLogResponse, responses=ERROR_RESPONSES)
async def get_audit_log(log_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    log = await audit_log_service.get_by_id(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="AuditLog not found")
    return log

@router.post("/", response_model=AuditLogResponse, status_code=201, responses=ERROR_RESPONSES)
async def create_audit_log(data: AuditLogCreate, db: AsyncSession = Depends(get_db)):
    return await audit_log_service.create(db, data)

@router.put("/{log_id}", response_model=AuditLogResponse, responses=ERROR_RESPONSES)
async def update_audit_log(log_id: uuid.UUID, data: AuditLogUpdate, db: AsyncSession = Depends(get_db)):
    log = await audit_log_service.update(db, log_id, data)
    if not log:
        raise HTTPException(status_code=404, detail="AuditLog not found")
    return log

@router.delete("/{log_id}", status_code=204, responses=ERROR_RESPONSES)
async def delete_audit_log(log_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await audit_log_service.delete(db, log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="AuditLog not found")
