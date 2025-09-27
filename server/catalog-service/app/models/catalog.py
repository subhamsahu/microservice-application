from datetime import datetime
from typing import List, Optional

from beanie import Document, Indexed
from pydantic import BaseModel, Field, ConfigDict


# Nested rating category model
class RatingCategory(BaseModel):
    value: int = Field(default=0)
    count: int = Field(default=0)


class RatingCategories(BaseModel):
    five: RatingCategory = Field(default_factory=RatingCategory)
    four: RatingCategory = Field(default_factory=RatingCategory)
    three: RatingCategory = Field(default_factory=RatingCategory)
    two: RatingCategory = Field(default_factory=RatingCategory)
    one: RatingCategory = Field(default_factory=RatingCategory)


class Catalog(Document):
    seller_id: Indexed(str) # type:ignore
    title: str
    description: str
    basic_title: str
    basic_description: str
    categories: str
    sub_categories: List[str] = Field(default_factory=list, min_length=1)
    tags: List[str] = Field(default_factory=list)
    active: bool = True
    expected_delivery: str = ""
    ratings_count: int = 0
    rating_sum: int = 0
    rating_categories: RatingCategories = Field(default_factory=RatingCategories)
    price: float = 0.0
    sort_id: Optional[int] = None
    cover_image: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )

    class Settings:
        name = "catalog"  # MongoDB collection name
