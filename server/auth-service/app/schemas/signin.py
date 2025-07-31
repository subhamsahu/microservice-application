from pydantic import BaseModel, EmailStr, model_validator, Field
from typing import Optional
import re

class SigninSchema(BaseModel):
    """Schema for user login."""
    username: str = Field(..., description="Username or Email")
    password: str = Field(..., min_length=4, max_length=12, description="Password must be 4-12 characters long")
    browserName: Optional[str] = Field(None)
    deviceType: Optional[str] = Field(None)

    @model_validator(mode='after')
    def validate_username(cls, values):
        """Validates the username field to accept either a valid email or a username."""
        username = values.get("username")
        if not username:
            raise ValueError("Username is a required field")

        is_email = re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", username)
        if is_email:
            # Valid email format
            return values
        else:
            # Treat as username, apply min/max length manually
            if len(username) < 4 or len(username) > 12:
                raise ValueError("Invalid username: must be between 4 and 12 characters")
        return values
