import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.errors import ERROR_RESPONSES
from app.schemas.cipher_field import CipherFieldCreate, CipherFieldUpdate, CipherFieldResponse
from app.services import cipher_field_service

router = APIRouter(prefix="/api/cipher-fields", tags=["CipherFields"])

@router.get("/", response_model=list[CipherFieldResponse], responses=ERROR_RESPONSES)
async def get_cipher_fields(db: AsyncSession = Depends(get_db)):
    return await cipher_field_service.get_all(db)

@router.get("/{field_id}", response_model=CipherFieldResponse, responses=ERROR_RESPONSES)
async def get_cipher_field(field_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    field = await cipher_field_service.get_by_id(db, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="CipherField not found")
    return field

@router.post("/", response_model=CipherFieldResponse, status_code=201, responses=ERROR_RESPONSES)
async def create_cipher_field(data: CipherFieldCreate, db: AsyncSession = Depends(get_db)):
    return await cipher_field_service.create(db, data)

@router.put("/{field_id}", response_model=CipherFieldResponse, responses=ERROR_RESPONSES)
async def update_cipher_field(field_id: uuid.UUID, data: CipherFieldUpdate, db: AsyncSession = Depends(get_db)):
    field = await cipher_field_service.update(db, field_id, data)
    if not field:
        raise HTTPException(status_code=404, detail="CipherField not found")
    return field

@router.delete("/{field_id}", status_code=204, responses=ERROR_RESPONSES)
async def delete_cipher_field(field_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await cipher_field_service.delete(db, field_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="CipherField not found")
