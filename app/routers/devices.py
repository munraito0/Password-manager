import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.errors import ERROR_RESPONSES
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse
from app.services import device_service

router = APIRouter(prefix="/api/devices", tags=["Devices"])

@router.get("/", response_model=list[DeviceResponse], responses=ERROR_RESPONSES)
async def get_devices(db: AsyncSession = Depends(get_db)):
    return await device_service.get_all(db)

@router.get("/{device_id}", response_model=DeviceResponse, responses=ERROR_RESPONSES)
async def get_device(device_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    device = await device_service.get_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.post("/", response_model=DeviceResponse, status_code=201, responses=ERROR_RESPONSES)
async def create_device(data: DeviceCreate, db: AsyncSession = Depends(get_db)):
    return await device_service.create(db, data)

@router.put("/{device_id}", response_model=DeviceResponse, responses=ERROR_RESPONSES)
async def update_device(device_id: uuid.UUID, data: DeviceUpdate, db: AsyncSession = Depends(get_db)):
    device = await device_service.update(db, device_id, data)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.delete("/{device_id}", status_code=204, responses=ERROR_RESPONSES)
async def delete_device(device_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await device_service.delete(db, device_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Device not found")
