from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid

from app.core.database import get_db
from app.core.deps import get_current_farmer
from app.schemas.models import Farmer, CropHistory, Recommendation
from app.agents.orchestrator import run_farm_advisor, stream_farm_advisor

router = APIRouter()


class ChatRequest(BaseModel):
    query: str


def _farmer_to_dict(farmer: Farmer) -> dict:
    return {
        "id":              farmer.id,
        "name":            farmer.name,
        "latitude":        farmer.latitude,
        "longitude":       farmer.longitude,
        "district":        farmer.district,
        "state":           farmer.state,
        "land_area_acres": farmer.land_area_acres,
        "soil_type":       str(farmer.soil_type.value) if farmer.soil_type else "alluvial",
        "irrigation":      str(farmer.irrigation.value) if farmer.irrigation else "none",
        "language":        farmer.language,
    }


async def _load_crop_history(farmer_id, db: AsyncSession) -> list:
    result = await db.execute(
        select(CropHistory)
        .where(CropHistory.farmer_id == farmer_id)
        .order_by(CropHistory.created_at.desc())
        .limit(10)
    )
    return [
        {"crop_name": r.crop_name, "season": r.season,
         "yield_kg": r.yield_kg,  "profit_inr": r.profit_inr}
        for r in result.scalars().all()
    ]


@router.post("/ask")
async def ask_farm_advisor(
    request: ChatRequest,
    current_farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    crop_history = await _load_crop_history(current_farmer.id, db)
    farmer_dict  = _farmer_to_dict(current_farmer)

    result = await run_farm_advisor(
        query      = request.query,
        farmer     = farmer_dict,
        db_history = crop_history,
    )

    rec = Recommendation(
        id             = uuid.uuid4(),
        farmer_id      = current_farmer.id,
        query          = request.query,
        weather_data   = result.get("weather_data"),
        crop_data      = result.get("crop_data"),
        market_data    = result.get("market_data"),
        resource_data  = result.get("resource_data"),
        final_response = result.get("final_response"),
    )
    db.add(rec)
    await db.commit()

    return {
        "recommendation_id": str(rec.id),
        "response":          result["final_response"],
        "weather":           result.get("weather_data"),
        "crops":             result.get("crop_data"),
        "market":            result.get("market_data"),
        "resources":         result.get("resource_data"),
        "errors":            result.get("errors", []),
    }


@router.post("/ask/stream")
async def ask_farm_advisor_stream(
    request: ChatRequest,
    current_farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    crop_history = await _load_crop_history(current_farmer.id, db)
    farmer_dict  = _farmer_to_dict(current_farmer)

    return StreamingResponse(
        stream_farm_advisor(request.query, farmer_dict, crop_history),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history")
async def get_chat_history(
    current_farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.farmer_id == current_farmer.id)
        .order_by(Recommendation.created_at.desc())
        .limit(20)
    )
    return [
        {
            "id":       str(r.id),
            "query":    r.query,
            "response": r.final_response,
            "date":     r.created_at.isoformat(),
        }
        for r in result.scalars().all()
    ]
