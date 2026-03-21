from pydantic import BaseModel
import uuid
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    name: str
    master_password_hash: str
    master_password_hint: str | None = None
    kdf_type: int
    kdf_iterations: int

class UserUpdate(BaseModel):
    name: str | None = None
    master_password_hint: str | None = None
    two_factor_enabled: bool | None = None
    premium: bool | None = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    two_factor_enabled: bool
    premium: bool
    created_at: datetime

    class Config:
        from_attributes = True