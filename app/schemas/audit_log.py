from pydantic import BaseModel
import uuid
from datetime import datetime

class AuditLogCreate(BaseModel):
    user_id: uuid.UUID
    event_type: int
    ip_address: str
    device_info: str
    meta: dict | list | None = None

class AuditLogUpdate(BaseModel):
    event_type: int | None = None
    ip_address: str | None = None
    device_info: str | None = None
    meta: dict | list | None = None

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    event_type: int
    ip_address: str
    device_info: str
    event_at: datetime
    meta: dict | list | None

    class Config:
        from_attributes = True
