"""
Schemas for user signup and update.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from typing import Literal

class SignupSchema(BaseModel):
    """Schema for user signup."""
    username: str = Field(
        ...,
        min_length=4,
        max_length=12,
        description="Username must be between 4 and 12 characters"
    )
    first_name: str = Field(
        ...,
        min_length=4,
        max_length=12,
        description="Username must be between 4 and 12 characters"
    )
    last_name: str = Field(
        ...,
        min_length=4,
        max_length=12,
        description="Username must be between 4 and 12 characters"
    )
    password: str = Field(
        ...,
        min_length=4,
        max_length=12,
        description="Password must be between 4 and 12 characters"
    )
    email: EmailStr = Field(
        ...,
        description="A valid email is required"
    )

class UserOutSchema(BaseModel):
    """User Out Schema"""
    uuid: UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    profile_public_id: str | None = None  # Optional if needed

    model_config = ConfigDict(from_attributes=True)
class SignupDataSchema(BaseModel):
    """Schema for user signup data."""
    user: UserOutSchema
    token: str

class SignupResponseSchema(BaseModel):
    """Schema for user signup response."""
    message: Literal["User created successfully"]
    data: SignupDataSchema
    class Config:
        """Config for user signup response."""
        orm_mode = True


class UpdateUserSchema(BaseModel):
    """Schema for user update."""
    username: str = Field(..., min_length=4, max_length=12,
                          description="Username must be between 4 and 12 characters")
    password: str = Field(..., min_length=4, max_length=12,
                          description="Password must be between 4 and 12 characters")
    country: str = Field(..., description="Country is required")
    email: EmailStr = Field(..., description="A valid email is required")
    profilePicture: str = Field(..., description="Profile picture is required")
    browserName: Optional[str] = Field(
        None, description="Browser name (optional)")
    deviceType: Optional[str] = Field(
        None, description="Device type (optional)")
