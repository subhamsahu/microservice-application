"""
User Table Model
"""

from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlmodel import SQLModel, Field, UniqueConstraint
from enum import Enum


class ROLES(str, Enum):
    """
    Enum representing user roles.
    """
    ADMIN = "Admin"
    STAFF = "Staff"
    USER = "User"


class User(SQLModel, table=True):
    """Model representing user authentication details."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email"),
        UniqueConstraint("username"),
        UniqueConstraint("email_verification_token"),
    )

    uuid: UUID = Field(default_factory=uuid4, primary_key=True)

    username: str = Field(nullable=False, index=True, max_length=50)
    password: str = Field(nullable=False)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    role: ROLES = Field(default=ROLES.USER, nullable=False)

    email: str = Field(nullable=False, index=True, max_length=100)
    email_verification_token: Optional[str] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)

    profile_public_id: Optional[str] = Field(default=None, nullable=True)
    profile_picture: Optional[str] = Field(default=None, nullable=True)

    country: Optional[str] = Field(default=None, nullable=True)
    browser_name: Optional[str] = Field(default=None, nullable=True)
    device_type: Optional[str] = Field(default=None, nullable=True)

    otp: Optional[str] = Field(default=None, nullable=True)
    otp_expiration: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    password_reset_token: Optional[str] = Field(default=None, nullable=True)
    password_reset_expires: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
