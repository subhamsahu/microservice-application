"""Buyer model for MongoDB using Beanie ODM."""

from datetime import datetime
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import Field, EmailStr, ConfigDict
from bson import ObjectId


class Buyer(Document):
    """Buyer document model."""
    
    username: Indexed(str, unique=True)  # type: ignore
    email: Indexed(EmailStr, unique=True)  # type: ignore
    profile_picture: str = Field(default="")
    country: str
    is_seller: bool = Field(default=False)
    purchased_catalogs: List[ObjectId] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        """
        Beanie document settings."""
        name = "buyers"
        use_enum_values = True
        validate_on_save = True
        use_revision = False

    # Pydantic v2 configuration to allow arbitrary types (ObjectId) and custom JSON encoders
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda dt: dt.isoformat(),
        },
    )

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["Buyer"]:
        """Get buyer by email."""
        return await cls.find_one(cls.email == email)

    @classmethod
    async def get_by_username(cls, username: str) -> Optional["Buyer"]:
        """Get buyer by username."""
        return await cls.find_one(cls.username == username)
       
