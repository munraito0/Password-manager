import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.errors import ERROR_RESPONSES
from app.schemas.cipher_card import CipherCardCreate, CipherCardUpdate, CipherCardResponse
from app.services import cipher_card_service

router = APIRouter(prefix="/api/cipher-cards", tags=["CipherCards"])

@router.get("/", response_model=list[CipherCardResponse], responses=ERROR_RESPONSES)
async def get_cipher_cards(db: AsyncSession = Depends(get_db)):
    return await cipher_card_service.get_all(db)

@router.get("/{cipher_id}", response_model=CipherCardResponse, responses=ERROR_RESPONSES)
async def get_cipher_card(cipher_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    card = await cipher_card_service.get_by_cipher_id(db, cipher_id)
    if not card:
        raise HTTPException(status_code=404, detail="CipherCard not found")
    return card

@router.post("/", response_model=CipherCardResponse, status_code=201, responses=ERROR_RESPONSES)
async def create_cipher_card(data: CipherCardCreate, db: AsyncSession = Depends(get_db)):
    return await cipher_card_service.create(db, data)

@router.put("/{cipher_id}", response_model=CipherCardResponse, responses=ERROR_RESPONSES)
async def update_cipher_card(cipher_id: uuid.UUID, data: CipherCardUpdate, db: AsyncSession = Depends(get_db)):
    card = await cipher_card_service.update(db, cipher_id, data)
    if not card:
        raise HTTPException(status_code=404, detail="CipherCard not found")
    return card

@router.delete("/{cipher_id}", status_code=204, responses=ERROR_RESPONSES)
async def delete_cipher_card(cipher_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await cipher_card_service.delete(db, cipher_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="CipherCard not found")
