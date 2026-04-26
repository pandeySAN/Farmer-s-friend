from sqlalchemy import (
    Column, String, Float, Integer, DateTime,
    ForeignKey, Text, Enum, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
from datetime import datetime
import uuid
import enum


# ── Enums ────────────────────────────────────────────────────────────────────

class SoilType(str, enum.Enum):
    alluvial  = "alluvial"   # Most of North India, very fertile
    black     = "black"      # Deccan plateau, good for cotton
    red       = "red"        # South India, iron-rich
    laterite  = "laterite"   # Hilly areas
    sandy     = "sandy"      # Rajasthan / coastal
    clay      = "clay"       # Waterlogged areas


class Season(str, enum.Enum):
    kharif = "kharif"   # June–Nov (rice, maize, cotton)
    rabi   = "rabi"     # Nov–Apr (wheat, mustard, peas)
    zaid   = "zaid"     # Apr–Jun (watermelon, cucumber)


class IrrigationType(str, enum.Enum):
    drip      = "drip"
    flood     = "flood"
    sprinkler = "sprinkler"
    none      = "none"


# ── Tables ────────────────────────────────────────────────────────────────────

class Farmer(Base):
    __tablename__ = "farmers"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email            = Column(String(255), unique=True, nullable=False, index=True)
    phone            = Column(String(20),  unique=True, nullable=True)
    name             = Column(String(100), nullable=False)
    hashed_password  = Column(String(255), nullable=False)

    # Location — used for weather and market data
    latitude         = Column(Float, nullable=True)
    longitude        = Column(Float, nullable=True)
    district         = Column(String(100), nullable=True)
    state            = Column(String(100), nullable=True)

    # Farm details — used by crop recommendation agent
    land_area_acres  = Column(Float, nullable=True)
    soil_type        = Column(Enum(SoilType), nullable=True)
    irrigation       = Column(Enum(IrrigationType), default=IrrigationType.none)

    # Preferences
    language         = Column(String(10), default="hi")
    is_active        = Column(Boolean, default=True)
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recommendations  = relationship("Recommendation", back_populates="farmer", cascade="all, delete")
    crop_history     = relationship("CropHistory",    back_populates="farmer", cascade="all, delete")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id      = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False, index=True)

    query          = Column(Text, nullable=False)

    # Agent outputs stored as flexible JSON
    weather_data   = Column(JSONB, nullable=True)
    crop_data      = Column(JSONB, nullable=True)
    market_data    = Column(JSONB, nullable=True)
    resource_data  = Column(JSONB, nullable=True)

    # Final combined response from Gemini
    final_response = Column(Text, nullable=True)

    created_at     = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="recommendations")


class CropHistory(Base):
    __tablename__ = "crop_history"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id   = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False, index=True)

    crop_name   = Column(String(100), nullable=False)
    season      = Column(Enum(Season), nullable=True)
    year        = Column(Integer, nullable=True)
    yield_kg    = Column(Float, nullable=True)
    area_acres  = Column(Float, nullable=True)
    profit_inr  = Column(Float, nullable=True)
    notes       = Column(Text, nullable=True)

    created_at  = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="crop_history")
