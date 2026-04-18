from pydantic import BaseModel
import uuid

class CipherLoginCreate(BaseModel):
    cipher_id: uuid.UUID
    username_encrypted: str
    password_encrypted: str
    totp_encrypted: str | None = None
    uris_encrypted: list | dict
    password_history_encrypted: list | dict | None = None

class CipherLoginUpdate(BaseModel):
    username_encrypted: str | None = None
    password_encrypted: str | None = None
    totp_encrypted: str | None = None
    uris_encrypted: list | dict | None = None
    password_history_encrypted: list | dict | None = None

class CipherLoginResponse(BaseModel):
    cipher_id: uuid.UUID
    username_encrypted: str
    password_encrypted: str
    totp_encrypted: str | None
    uris_encrypted: list | dict
    password_history_encrypted: list | dict | None

    class Config:
        from_attributes = True
