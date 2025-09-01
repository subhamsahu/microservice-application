"""Seller model for MongoDB using Beanie ODM."""

from datetime import datetime
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import Field, BaseModel
from bson import ObjectId


class Language(BaseModel):
    """Language model for seller."""
    language: str
    level: str


class Experience(BaseModel):
    """Experience model for seller."""
    company: str = ""
    title: str = ""
    start_date: str = Field(default="")
    end_date: str = Field(default="")
    description: str = ""
    currently_working_here: bool = Field(default=False)


class Education(BaseModel):
    """Education model for seller."""
    country: str = ""
    university: str = ""
    title: str = ""
    major: str = ""
    year: str = ""


class Certificate(BaseModel):
    """Certificate model for seller."""
    name: str
    from_org: str = Field(alias="from")
    year: int


class RatingCategory(BaseModel):
    """Rating category model."""
    value: int = 0
    count: int = 0


class RatingCategories(BaseModel):
    """Rating categories model."""
    five: RatingCategory = Field(default_factory=RatingCategory)
    four: RatingCategory = Field(default_factory=RatingCategory)
    three: RatingCategory = Field(default_factory=RatingCategory)
    two: RatingCategory = Field(default_factory=RatingCategory)
    one: RatingCategory = Field(default_factory=RatingCategory)


class Seller(Document):
    """Seller document model."""
    
    full_name: str
    username: Indexed(str, unique=True)  # type: ignore
    email: Indexed(str, unique=True)  # type: ignore
    profile_picture: str
    description: str
    profile_public_id: str
    oneliner: str = ""
    country: str
    languages: List[Language] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    ratings_count: int = Field(default=0)
    rating_sum: int = Field(default=0)
    rating_categories: RatingCategories = Field(default_factory=RatingCategories)
    response_time: int = Field(default=0)
    recent_delivery: Optional[datetime] = Field(default=None)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    social_links: List[str] = Field(default_factory=list)
    certificates: List[Certificate] = Field(default_factory=list)
    ongoing_jobs: int = Field(default=0)
    completed_jobs: int = Field(default=0)
    cancelled_jobs: int = Field(default=0)
    total_earnings: float = Field(default=0.0)
    total_catalogs: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        """
        Beanie document settings."""
        name = "sellers"
        use_enum_values = True
        validate_on_save = True

    class Config:
        """
        Pydantic model configuration."""
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat() if dt else None
        }

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["Seller"]:
        """Get buyer by email."""
        return await cls.find_one(cls.email == email)

    @classmethod
    async def get_by_username(cls, username: str) -> Optional["Seller"]:
        """Get buyer by username."""
        return await cls.find_one(cls.username == username)
