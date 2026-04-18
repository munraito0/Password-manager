from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class FolderCreate(BaseModel):
    user_id: uuid.UUID
    name_encrypted: str = Field(..., min_length=1, max_length=5000)

class FolderUpdate(BaseModel):
    name_encrypted: str = Field(..., min_length=1, max_length=5000)

class FolderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name_encrypted: str
    created_at: datetime

    class Config:
        from_attributes = True
