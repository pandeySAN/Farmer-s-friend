from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.models import Farmer
from app.schemas.auth import FarmerRegister, FarmerLogin, TokenResponse

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: FarmerRegister, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Farmer).where(Farmer.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    farmer = Farmer(
        name            = data.name,
        email           = data.email,
        hashed_password = hash_password(data.password),
        phone           = data.phone,
        state           = data.state,
        district        = data.district,
        language        = data.language or "hi",
    )
    db.add(farmer)
    await db.flush()

    token = create_access_token({"sub": str(farmer.id)})
    await db.commit()

    return TokenResponse(
        access_token = token,
        farmer_id    = str(farmer.id),
        name         = farmer.name,
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: FarmerLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Farmer).where(Farmer.email == data.email))
    farmer = result.scalar_one_or_none()

    if not farmer or not verify_password(data.password, farmer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not farmer.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token({"sub": str(farmer.id)})

    return TokenResponse(
        access_token = token,
        farmer_id    = str(farmer.id),
        name         = farmer.name,
    )
