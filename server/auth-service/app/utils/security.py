"""
This module contains the security functions for handling user-related operations.
"""
import logging
import uuid
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

import jwt
from passlib.context import CryptContext

from app.core.config import config

passwd_context = CryptContext(schemes=["bcrypt"])


ACCESS_TOKEN_EXPIRY = 3600


def generate_password_hash(password: str) -> str:
    """
    Generate a password hash.
    """
    hash = passwd_context.hash(password)
    return hash


def verify_password(password: str, hash: str) -> bool:
    """
    Verify a password against a hash.
    """
    return passwd_context.verify(password, hash)


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    """
    Create an access token.
    """
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload["jti"] = str(uuid.uuid4())

    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload, key=config.JWT_SECRET, algorithm=config.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> dict | None:
    """
    Decode a JWT token.
    """
    try:
        token_data = jwt.decode(
            jwt=token, key=config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )

        return token_data

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None

serializer = URLSafeTimedSerializer(
    secret_key=config.JWT_SECRET, salt="email-configuration"
)

def create_url_safe_token(data: dict):
    """
    Create a URL-safe token.
    """

    token = serializer.dumps(data)

    return token

def decode_url_safe_token(token: str, max_age: int = 300):
    """
    Decode a URL-safe signed token with shared expiry.
    """
    try:
        token_data = serializer.loads(token, max_age=max_age)
        return token_data
    except SignatureExpired:
        logging.error("Token expired")
        return None
    except BadSignature:
        logging.error("Invalid token signature")
        return None
  