from pydantic import BaseModel
import uuid

class CipherFieldCreate(BaseModel):
    cipher_id: uuid.UUID
    type: int
    name_encrypted: str
    value_encrypted: str

class CipherFieldUpdate(BaseModel):
    type: int | None = None
    name_encrypted: str | None = None
    value_encrypted: str | None = None

class CipherFieldResponse(BaseModel):
    id: uuid.UUID
    cipher_id: uuid.UUID
    type: int
    name_encrypted: str
    value_encrypted: str

    class Config:
        from_attributes = True
