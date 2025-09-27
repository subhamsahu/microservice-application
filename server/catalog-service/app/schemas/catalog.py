from pydantic import BaseModel, Field, StringConstraints, ConfigDict
from typing import Annotated, List
from beanie import PydanticObjectId
from bson import ObjectId
import datetime

from app.models.catalog import RatingCategory, RatingCategories


# Helper type alias for non-empty strings
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class CatalogBase(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )


class CatalogCreateSchema(CatalogBase):
    """
    Catalog Create Schema
    """
    seller_id: NonEmptyStr = Field(..., description="Seller Id is required")
    profile_picture: NonEmptyStr = Field(..., description="Profile picture is required")
    title: NonEmptyStr = Field(..., description="Catalog title is required")
    description: NonEmptyStr = Field(..., description="Catalog description is required")
    categories: NonEmptyStr = Field(..., description="Catalog category is required")
    sub_categories: Annotated[List[NonEmptyStr], Field(min_length=1, description="Please add at least one subcategory")]
    tags: Annotated[List[NonEmptyStr], Field(min_length=1, description="Please add at least one tag")]
    price: Annotated[float, Field(gt=4.99, description="Catalog price must be greater than $4.99")]
    cover_image: NonEmptyStr = Field(..., description="Cover image is required")
    expected_delivery: NonEmptyStr = Field(..., description="Expected delivery is required")
    basic_title: NonEmptyStr = Field(..., description="Basic title is required")
    basic_description: NonEmptyStr = Field(..., description="Basic description is required")


class CatalogUpdateSchema(CatalogBase):
    """
    Catalog Update Schema
    """
    title: NonEmptyStr = Field(..., description="Catalog title is required")
    description: NonEmptyStr = Field(..., description="Catalog description is required")
    categories: NonEmptyStr = Field(..., description="Catalog category is required")
    sub_categories: Annotated[List[NonEmptyStr], Field(min_length=1, description="Please add at least one subcategory")]
    tags: Annotated[List[NonEmptyStr], Field(min_length=1, description="Please add at least one tag")]
    price: Annotated[float, Field(gt=4.99, description="Catalog price must be greater than $4.99")]
    cover_image: NonEmptyStr = Field(..., description="Cover image is required")
    expected_delivery: NonEmptyStr = Field(..., description="Expected delivery is required")
    basic_title: NonEmptyStr = Field(..., description="Basic title is required")
    basic_description: NonEmptyStr = Field(..., description="Basic description is required")


class CatalogResponseSchema(BaseModel):
    """Schema for Robot Framework test case response."""
    id: PydanticObjectId = Field(alias="id")
    title: str
    description: str
    categories: str
    sub_categories: List[str]
    tags: List[str]
    price: float
    cover_image: str
    expected_delivery: str
    basic_title: str
    basic_description: str

    class Config:
        """Pydantic configuration."""
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            PydanticObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }

class CatalogESSchema(BaseModel):
    """Schema for Robot Framework test case response."""
    id: PydanticObjectId = Field(alias="id")
    title: str
    description: str
    basic_title: str
    basic_description: str
    categories: str
    sub_categories: List[str]
    tags: List[str]
    active: bool
    expected_delivery: str
    price: float
    ratings_count: int
    rating_sum: int
    rating_categories: RatingCategories
    cover_image: str
    sort_id: int
    created_at: datetime.datetime

    class Config:
        """Pydantic configuration."""
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            PydanticObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
