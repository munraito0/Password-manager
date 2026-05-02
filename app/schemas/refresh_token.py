from pydantic import BaseModel
import uuid
from datetime import datetime

class RefreshTokenCreate(BaseModel):
    user_id: uuid.UUID
    device_id: uuid.UUID | None = None
    token_hash: str
    expires_at: datetime

class RefreshTokenUpdate(BaseModel):
    token_hash: str | None = None
    expires_at: datetime | None = None

class RefreshTokenResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    device_id: uuid.UUID | None
    token_hash: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
