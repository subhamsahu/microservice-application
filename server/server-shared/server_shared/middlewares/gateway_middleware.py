"""
Gateway Middleware for FastAPI
It provides a middleware function to verify that incoming requests to the FastAPI application
are authorized by checking a gateway token in the request headers.
"""
from typing import Set

from fastapi import Request, HTTPException

from jwt import decode, exceptions as jwt_exceptions
from starlette.status import HTTP_401_UNAUTHORIZED
from ..error import NotAuthorizedError

# List of valid token sources (e.g., different microservices)
VALID_TOKEN_IDS: Set[str] = {
    "auth", "seller", "catalog", "search", "buyer", "message", "order", "review"
}

# Replace with your actual JWT secret key
JWT_SECRET: str = "your_gateway_secret_key_here"
JWT_ALGORITHM: str = "HS256"


async def verify_gateway_request(request: Request) -> None:
    """   
    Verifies the gateway token in the request headers to ensure the request is coming from the API gateway.

    This function checks the 'gatewaytoken' header in the request. 
    If the header is missing or the token is invalid,
    it raises a `NotAuthorizedException` with an appropriate error message.

    It also verifies the JWT token payload to ensure the request is coming from a valid source
    (i.e., the ID in the payload is included in the VALID_TOKEN_IDS set).

    Args:
        request (Request): The incoming FastAPI request.

    Raises:
        NotAuthorizedException: If the token is missing, invalid, or from an untrusted source.
    """
    gateway_token = request.headers.get("gatewaytoken")

    # Check if the gatewaytoken header exists
    if not gateway_token:
        raise NotAuthorizedError(
            message="Invalid request: verify_gateway_request() method - Request not coming from API gateway",
            coming_from="Gateway Middleware"
        )

    try:
        # Decode the JWT token using the shared secret and expected algorithm
        payload = decode(gateway_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        token_id = payload.get("id")

        # Validate that the token ID is one of the known/authorized sources
        if token_id not in VALID_TOKEN_IDS:
            raise NotAuthorizedError(
                message="Invalid request: verify_gateway_request() method - Token payload ID is not valid",
                coming_from="Gateway Middleware"
            )
        # ✅ Attach user details if present
        user = payload.get("user")
        if user:
            request.state.user = user
    except jwt_exceptions.ExpiredSignatureError as exc:
        raise NotAuthorizedError("Token has expired",coming_from="Gateway Middleware") from exc
    except jwt_exceptions.DecodeError as exc:
        raise NotAuthorizedError("Token could not be decoded",coming_from="Gateway Middleware") from exc
    except jwt_exceptions.InvalidTokenError as exc:
        raise NotAuthorizedError("Invalid token",coming_from="Gateway Middleware") from exc
