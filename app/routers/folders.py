import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.folder import FolderCreate, FolderUpdate, FolderResponse
from app.services import folder_service

router = APIRouter(prefix="/api/folders", tags=["Folders"])

@router.get("/", response_model=list[FolderResponse])
async def get_folders(db: AsyncSession = Depends(get_db)):
    return await folder_service.get_all(db)

@router.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(folder_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    folder = await folder_service.get_by_id(db, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder

@router.post("/", response_model=FolderResponse, status_code=201)
async def create_folder(data: FolderCreate, db: AsyncSession = Depends(get_db)):
    return await folder_service.create(db, data)

@router.put("/{folder_id}", response_model=FolderResponse)
async def update_folder(folder_id: uuid.UUID, data: FolderUpdate, db: AsyncSession = Depends(get_db)):
    folder = await folder_service.update(db, folder_id, data)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder

@router.delete("/{folder_id}", status_code=204)
async def delete_folder(folder_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await folder_service.delete(db, folder_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Folder not found")