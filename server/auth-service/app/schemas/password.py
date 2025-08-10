"""
Module contains schemas for email and password
"""

from pydantic import BaseModel, EmailStr, Field


class EmailSchema(BaseModel):
    """Email Schema"""
    email: EmailStr = Field(..., description="Valid email address")


class PasswordSchema(BaseModel):
    """Password Schema"""
    password: str = Field(..., min_length=4, max_length=12)

class ChangePasswordSchema(BaseModel):
    """Change Password Schema"""
    current_password: str = Field(..., min_length=4, max_length=8)
    new_password: str = Field(..., min_length=4, max_length=12)

