import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.errors import ERROR_RESPONSES
from app.schemas.cipher_identity import CipherIdentityCreate, CipherIdentityUpdate, CipherIdentityResponse
from app.services import cipher_identity_service

router = APIRouter(prefix="/api/cipher-identities", tags=["CipherIdentities"])

@router.get("/", response_model=list[CipherIdentityResponse], responses=ERROR_RESPONSES)
async def get_cipher_identities(db: AsyncSession = Depends(get_db)):
    return await cipher_identity_service.get_all(db)

@router.get("/{cipher_id}", response_model=CipherIdentityResponse, responses=ERROR_RESPONSES)
async def get_cipher_identity(cipher_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    identity = await cipher_identity_service.get_by_cipher_id(db, cipher_id)
    if not identity:
        raise HTTPException(status_code=404, detail="CipherIdentity not found")
    return identity

@router.post("/", response_model=CipherIdentityResponse, status_code=201, responses=ERROR_RESPONSES)
async def create_cipher_identity(data: CipherIdentityCreate, db: AsyncSession = Depends(get_db)):
    return await cipher_identity_service.create(db, data)

@router.put("/{cipher_id}", response_model=CipherIdentityResponse, responses=ERROR_RESPONSES)
async def update_cipher_identity(cipher_id: uuid.UUID, data: CipherIdentityUpdate, db: AsyncSession = Depends(get_db)):
    identity = await cipher_identity_service.update(db, cipher_id, data)
    if not identity:
        raise HTTPException(status_code=404, detail="CipherIdentity not found")
    return identity

@router.delete("/{cipher_id}", status_code=204, responses=ERROR_RESPONSES)
async def delete_cipher_identity(cipher_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await cipher_identity_service.delete(db, cipher_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="CipherIdentity not found")
