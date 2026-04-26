from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from uuid import UUID
import re


class FarmerRegister(BaseModel):
    name:     str
    email:    EmailStr
    password: str
    phone:    Optional[str] = None
    state:    Optional[str] = None
    district: Optional[str] = None
    language: Optional[str] = "hi"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v):
        if v and not re.match(r"^\+?[6-9]\d{9}$", v):
            raise ValueError("Enter a valid Indian mobile number")
        return v


class FarmerLogin(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    farmer_id:    str
    name:         str


class FarmerProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name:            Optional[str]   = None
    latitude:        Optional[float] = None
    longitude:       Optional[float] = None
    district:        Optional[str]   = None
    state:           Optional[str]   = None
    land_area_acres: Optional[float] = None
    soil_type:       Optional[str]   = None
    irrigation:      Optional[str]   = None
    language:        Optional[str]   = None


class FarmerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:              UUID            # ← was str, UUID object serializes cleanly
    name:            str
    email:           str
    phone:           Optional[str]
    district:        Optional[str]
    state:           Optional[str]
    land_area_acres: Optional[float]
    soil_type:       Optional[str]
    irrigation:      Optional[str]
    language:        str