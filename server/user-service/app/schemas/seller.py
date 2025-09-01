from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId


class LanguageSchema(BaseModel):
    """Language schema."""
    language: str
    level: str


class ExperienceSchema(BaseModel):
    """Experience schema."""
    company: str = ""
    title: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    currently_working_here: bool = False


class EducationSchema(BaseModel):
    """Education schema."""
    country: str = ""
    university: str = ""
    title: str = ""
    major: str = ""
    year: str = ""


class CertificateSchema(BaseModel):
    """Certificate schema."""
    name: str
    from_org: str
    year: int


class SellerCreate(BaseModel):
    """Seller creation schema."""
    full_name: str
    username: str
    email: str
    profile_picture: str
    description: str
    profile_public_id: str
    oneliner: str = ""
    country: str
    languages: List[LanguageSchema] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)


class SellerUpdate(BaseModel):
    """Seller update schema."""
    full_name: Optional[str] = None
    description: Optional[str] = None
    oneliner: Optional[str] = None
    country: Optional[str] = None
    languages: Optional[List[LanguageSchema]] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[ExperienceSchema]] = None
    education: Optional[List[EducationSchema]] = None
    social_links: Optional[List[str]] = None
    certificates: Optional[List[CertificateSchema]] = None


class SellerResponse(BaseModel):
    """Seller response schema."""
    id: str
    full_name: str
    username: str
    email: str
    profile_picture: str
    description: str
    profile_public_id: str
    oneliner: str
    country: str
    languages: List[LanguageSchema]
    skills: List[str]
    ratings_count: int
    rating_sum: int
    response_time: int
    recent_delivery: Optional[datetime]
    ongoing_jobs: int
    completed_jobs: int
    cancelled_jobs: int
    total_earnings: float
    total_gigs: int
    created_at: datetime

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat() if dt else None
        }
