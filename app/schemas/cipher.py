from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class CipherCreate(BaseModel):
    user_id: uuid.UUID
    folder_id: uuid.UUID | None = None
    type: int = Field(..., ge=1, le=4)
    name_encrypted: str = Field(..., min_length=1, max_length=5000)
    notes_encrypted: str | None = Field(None, max_length=20000)
    favorite: bool = False

class CipherUpdate(BaseModel):
    folder_id: uuid.UUID | None = None
    name_encrypted: str | None = Field(None, min_length=1, max_length=5000)
    notes_encrypted: str | None = Field(None, max_length=20000)
    favorite: bool | None = None

class CipherResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    folder_id: uuid.UUID | None
    type: int
    name_encrypted: str
    favorite: bool
    created_at: datetime

    class Config:
        from_attributes = True
