from pydantic import BaseModel
import uuid

class CipherCardCreate(BaseModel):
    cipher_id: uuid.UUID
    cardholder_name_encrypted: str
    brand_encrypted: str
    number_encrypted: str
    exp_month_encrypted: str
    exp_year_encrypted: str
    code_encrypted: str

class CipherCardUpdate(BaseModel):
    cardholder_name_encrypted: str | None = None
    brand_encrypted: str | None = None
    number_encrypted: str | None = None
    exp_month_encrypted: str | None = None
    exp_year_encrypted: str | None = None
    code_encrypted: str | None = None

class CipherCardResponse(BaseModel):
    cipher_id: uuid.UUID
    cardholder_name_encrypted: str
    brand_encrypted: str
    number_encrypted: str
    exp_month_encrypted: str
    exp_year_encrypted: str
    code_encrypted: str

    class Config:
        from_attributes = True
