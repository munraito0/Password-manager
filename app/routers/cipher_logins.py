import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.errors import ERROR_RESPONSES
from app.schemas.cipher_login import CipherLoginCreate, CipherLoginUpdate, CipherLoginResponse
from app.services import cipher_login_service

router = APIRouter(prefix="/api/cipher-logins", tags=["CipherLogins"])

@router.get("/", response_model=list[CipherLoginResponse], responses=ERROR_RESPONSES)
async def get_cipher_logins(db: AsyncSession = Depends(get_db)):
    return await cipher_login_service.get_all(db)

@router.get("/{cipher_id}", response_model=CipherLoginResponse, responses=ERROR_RESPONSES)
async def get_cipher_login(cipher_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    login = await cipher_login_service.get_by_cipher_id(db, cipher_id)
    if not login:
        raise HTTPException(status_code=404, detail="CipherLogin not found")
    return login

@router.post("/", response_model=CipherLoginResponse, status_code=201, responses=ERROR_RESPONSES)
async def create_cipher_login(data: CipherLoginCreate, db: AsyncSession = Depends(get_db)):
    return await cipher_login_service.create(db, data)

@router.put("/{cipher_id}", response_model=CipherLoginResponse, responses=ERROR_RESPONSES)
async def update_cipher_login(cipher_id: uuid.UUID, data: CipherLoginUpdate, db: AsyncSession = Depends(get_db)):
    login = await cipher_login_service.update(db, cipher_id, data)
    if not login:
        raise HTTPException(status_code=404, detail="CipherLogin not found")
    return login

@router.delete("/{cipher_id}", status_code=204, responses=ERROR_RESPONSES)
async def delete_cipher_login(cipher_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await cipher_login_service.delete(db, cipher_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="CipherLogin not found")
