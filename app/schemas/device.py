from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class DeviceCreate(BaseModel):
    user_id: uuid.UUID
    type: int = Field(..., ge=0, le=10)
    name: str = Field(..., min_length=1, max_length=255)
    identifier: str = Field(..., min_length=1, max_length=255, pattern=r"^[A-Za-z0-9_-]+$")
    push_token: str | None = Field(None, max_length=255)

class DeviceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    push_token: str | None = Field(None, max_length=255)
    last_login_at: datetime | None = None

class DeviceResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type: int
    name: str
    identifier: str
    push_token: str | None
    created_at: datetime
    last_login_at: datetime | None

    class Config:
        from_attributes = True
