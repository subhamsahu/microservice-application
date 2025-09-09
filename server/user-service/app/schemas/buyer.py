"""Pydantic schemas for request/response models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from beanie import PydanticObjectId

class BuyerResponse(BaseModel):
    """Buyer response schema."""
    id: PydanticObjectId = Field(alias="_id")
    username: str
    email: str
    profile_picture: str = Field(alias="profilePicture")
    country: str
    is_seller: bool = Field(alias="isSeller")
    purchased_catalogs: List[str] = Field(alias="purchasedCatalogs")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        """Pydantic configuration."""
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            PydanticObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }


class BuyerUpdate(BaseModel):
    """Buyer update schema."""
    username: Optional[str] = None
    email: Optional[str] = None
    profile_picture: Optional[str] = None
    country: Optional[str] = None
    purchased_catalogs: Optional[List[str]] = None
    is_seller: bool | None = None
