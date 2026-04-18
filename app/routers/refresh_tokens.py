import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.errors import ERROR_RESPONSES
from app.schemas.refresh_token import RefreshTokenCreate, RefreshTokenUpdate, RefreshTokenResponse
from app.services import refresh_token_service

router = APIRouter(prefix="/api/refresh-tokens", tags=["RefreshTokens"])

@router.get("/", response_model=list[RefreshTokenResponse], responses=ERROR_RESPONSES)
async def get_refresh_tokens(db: AsyncSession = Depends(get_db)):
    return await refresh_token_service.get_all(db)

@router.get("/{token_id}", response_model=RefreshTokenResponse, responses=ERROR_RESPONSES)
async def get_refresh_token(token_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    token = await refresh_token_service.get_by_id(db, token_id)
    if not token:
        raise HTTPException(status_code=404, detail="RefreshToken not found")
    return token

@router.post("/", response_model=RefreshTokenResponse, status_code=201, responses=ERROR_RESPONSES)
async def create_refresh_token(data: RefreshTokenCreate, db: AsyncSession = Depends(get_db)):
    return await refresh_token_service.create(db, data)

@router.put("/{token_id}", response_model=RefreshTokenResponse, responses=ERROR_RESPONSES)
async def update_refresh_token(token_id: uuid.UUID, data: RefreshTokenUpdate, db: AsyncSession = Depends(get_db)):
    token = await refresh_token_service.update(db, token_id, data)
    if not token:
        raise HTTPException(status_code=404, detail="RefreshToken not found")
    return token

@router.delete("/{token_id}", status_code=204, responses=ERROR_RESPONSES)
async def delete_refresh_token(token_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await refresh_token_service.delete(db, token_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="RefreshToken not found")
