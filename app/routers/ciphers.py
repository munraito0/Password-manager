import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.errors import ERROR_RESPONSES
from app.schemas.cipher import CipherCreate, CipherUpdate, CipherResponse
from app.services import cipher_service

router = APIRouter(prefix="/api/ciphers", tags=["Ciphers"])

@router.get("/", response_model=list[CipherResponse], responses=ERROR_RESPONSES)
async def get_ciphers(db: AsyncSession = Depends(get_db)):
    return await cipher_service.get_all(db)

@router.get("/{cipher_id}", response_model=CipherResponse, responses=ERROR_RESPONSES)
async def get_cipher(cipher_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    cipher = await cipher_service.get_by_id(db, cipher_id)
    if not cipher:
        raise HTTPException(status_code=404, detail="Cipher not found")
    return cipher

@router.post("/", response_model=CipherResponse, status_code=201, responses=ERROR_RESPONSES)
async def create_cipher(data: CipherCreate, db: AsyncSession = Depends(get_db)):
    return await cipher_service.create(db, data)

@router.put("/{cipher_id}", response_model=CipherResponse, responses=ERROR_RESPONSES)
async def update_cipher(cipher_id: uuid.UUID, data: CipherUpdate, db: AsyncSession = Depends(get_db)):
    cipher = await cipher_service.update(db, cipher_id, data)
    if not cipher:
        raise HTTPException(status_code=404, detail="Cipher not found")
    return cipher

@router.delete("/{cipher_id}", status_code=204, responses=ERROR_RESPONSES)
async def delete_cipher(cipher_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await cipher_service.delete(db, cipher_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cipher not found")