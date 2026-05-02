from pydantic import BaseModel, EmailStr, Field
import uuid
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    master_password_hash: str = Field(..., min_length=8, max_length=255)
    master_password_hint: str | None = Field(None, max_length=255)
    kdf_type: int = Field(..., ge=0, le=10)
    kdf_iterations: int = Field(..., ge=1000, le=2_000_000)

class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    master_password_hint: str | None = Field(None, max_length=255)
    two_factor_enabled: bool | None = None
    premium: bool | None = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    two_factor_enabled: bool
    premium: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
