from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_farmer
from app.schemas.models import Farmer, CropHistory
from app.schemas.auth import FarmerProfile, FarmerResponse

router = APIRouter()


@router.get("/me", response_model=FarmerResponse)
async def get_my_profile(current_farmer: Farmer = Depends(get_current_farmer)):
    return current_farmer


@router.patch("/me", response_model=FarmerResponse)
async def update_my_profile(
    updates: FarmerProfile,
    current_farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(current_farmer, field, value)
    db.add(current_farmer)
    await db.commit()
    await db.refresh(current_farmer)
    return current_farmer


@router.get("/me/history")
async def get_crop_history(
    current_farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CropHistory)
        .where(CropHistory.farmer_id == current_farmer.id)
        .order_by(CropHistory.created_at.desc())
    )
    return result.scalars().all()


@router.post("/me/history")
async def add_crop_history(
    data: dict,
    current_farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    record = CropHistory(
        farmer_id  = current_farmer.id,
        crop_name  = data.get("crop_name"),
        season     = data.get("season"),
        year       = data.get("year"),
        yield_kg   = data.get("yield_kg"),
        area_acres = data.get("area_acres"),
        profit_inr = data.get("profit_inr"),
        notes      = data.get("notes"),
    )
    db.add(record)
    await db.commit()
    return {"message": "Crop history added", "id": str(record.id)}
