# app/models/auth.py

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, UniqueConstraint

class User(SQLModel, table=True):
    """Model representing user authentication details."""
    
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email"),
        UniqueConstraint("username"),
        UniqueConstraint("email_verification_token"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, index=True, max_length=50)
    password: str = Field(nullable=False)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)

    email: str = Field(nullable=False, index=True, max_length=100)
    email_verification_token: Optional[str] = Field(default=None, nullable=True)
    email_verified: bool = Field(default=False)

    profile_public_id: Optional[str] = Field(default=None, nullable=True)
    profile_picture: Optional[str] = Field(default=None, nullable=True)

    country: Optional[str] = Field(default=None, nullable=True)
    browser_name: Optional[str] = Field(default=None, nullable=True)
    device_type: Optional[str] = Field(default=None, nullable=True)

    otp: Optional[str] = Field(default=None, nullable=True)
    otp_expiration: datetime = Field(default_factory=datetime.now)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    password_reset_token: Optional[str] = Field(default=None, nullable=True)
    password_reset_expires: datetime = Field(default_factory=datetime.now)

