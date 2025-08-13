"""
This module defines the security methods to be used by the  service
"""

from datetime import datetime, timedelta
import logging
import jwt
from app.core.config import config

# Use GATEWAY_JWT_TOKEN for creating gateway tokens for inter-service communication
JWT_SECRET = config.GATEWAY_JWT_TOKEN
JWT_ALGORITHM = "HS256"

def create_gateway_token(token_id: str):
    """
    create gateway token for the request
    """
    payload = {
        "id": token_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Remove debug print statement - this should not be in production code
# print(create_gateway_token("auth"))  # Replace "auth" with your valid ID

def decode_token(token: str) -> dict | None:
    """
    Decode a JWT token.
    """
    try:
        token_data = jwt.decode(
            jwt=token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )

        return token_data

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
