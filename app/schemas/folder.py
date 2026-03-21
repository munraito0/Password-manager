from pydantic import BaseModel
import uuid
from datetime import datetime

class FolderCreate(BaseModel):
    user_id: uuid.UUID
    name_encrypted: str

class FolderUpdate(BaseModel):
    name_encrypted: str

class FolderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name_encrypted: str
    created_at: datetime

    class Config:
        from_attributes = True