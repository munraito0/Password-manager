from pydantic import BaseModel
import uuid

class CipherIdentityCreate(BaseModel):
    cipher_id: uuid.UUID
    title_encrypted: str
    first_name_encrypted: str
    last_name_encrypted: str
    email_encrypted: str
    phone_encrypted: str
    address_encrypted: str
    ssn_encrypted: str

class CipherIdentityUpdate(BaseModel):
    title_encrypted: str | None = None
    first_name_encrypted: str | None = None
    last_name_encrypted: str | None = None
    email_encrypted: str | None = None
    phone_encrypted: str | None = None
    address_encrypted: str | None = None
    ssn_encrypted: str | None = None

class CipherIdentityResponse(BaseModel):
    cipher_id: uuid.UUID
    title_encrypted: str
    first_name_encrypted: str
    last_name_encrypted: str
    email_encrypted: str
    phone_encrypted: str
    address_encrypted: str
    ssn_encrypted: str

    class Config:
        from_attributes = True
