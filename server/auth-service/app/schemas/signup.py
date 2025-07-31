from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class SignupSchema(BaseModel):
    """Schema for user signup."""
    username: str = Field(..., min_length=4, max_length=12, description="Username must be between 4 and 12 characters")
    first_name: str = Field(..., min_length=4, max_length=12, description="Username must be between 4 and 12 characters")
    last_name: str = Field(..., min_length=4, max_length=12, description="Username must be between 4 and 12 characters")
    password: str = Field(..., min_length=4, max_length=12, description="Password must be between 4 and 12 characters")
    country: str = Field(..., description="Country is required")
    email: EmailStr = Field(..., description="A valid email is required")
    profilePicture: str = Field(..., description="Profile picture is required")
    browserName: Optional[str] = Field(None, description="Browser name (optional)")
    deviceType: Optional[str] = Field(None, description="Device type (optional)")

class UpdateUserSchema(BaseModel):
    """Schema for user update."""
    username: str = Field(..., min_length=4, max_length=12, description="Username must be between 4 and 12 characters")
    password: str = Field(..., min_length=4, max_length=12, description="Password must be between 4 and 12 characters")
    country: str = Field(..., description="Country is required")
    email: EmailStr = Field(..., description="A valid email is required")
    profilePicture: str = Field(..., description="Profile picture is required")
    browserName: Optional[str] = Field(None, description="Browser name (optional)")
    deviceType: Optional[str] = Field(None, description="Device type (optional)")
