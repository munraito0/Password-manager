from pydantic import BaseModel
import uuid
from datetime import datetime

class CipherCreate(BaseModel):
    user_id: uuid.UUID
    folder_id: uuid.UUID | None = None
    type: int
    name_encrypted: str
    notes_encrypted: str | None = None
    favorite: bool = False

class CipherUpdate(BaseModel):
    folder_id: uuid.UUID | None = None
    name_encrypted: str | None = None
    notes_encrypted: str | None = None
    favorite: bool | None = None

class CipherResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    folder_id: uuid.UUID | None
    type: int
    name_encrypted: str
    favorite: bool
    deleted_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True