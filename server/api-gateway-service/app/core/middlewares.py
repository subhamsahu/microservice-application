"""
Middleware for handling authentication and authorization in FastAPI.
This module provides a middleware that verifies JWT tokens from the session,
sets the current user in the request state, and provides utility functions
for checking user authentication.
"""
import jwt
from jwt import InvalidTokenError
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import config  # pylint: disable=E0401


class NotAuthorizedError(HTTPException):
    """
    Custom exception for unauthorized access.
    """
    def __init__(self, message: str, source: str):
        super().__init__(status_code=401, detail={"error": message, "source": source})


class BadRequestError(HTTPException):
    """
    Custom exception for bad request.
    """
    def __init__(self, message: str, source: str):
        super().__init__(status_code=400, detail={"error": message, "source": source})


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware that verifies JWT token from session.
    Sets request.state.current_user if token is valid.
    """

    async def dispatch(self, request: Request, call_next):
        token = request.session.get("jwt") if hasattr(request, "session") else None

        if not token:
            raise NotAuthorizedError(
                message="Token is not present in request. Please login again.",
                source="GatewayService verifyAuthToken() method error"
            )

        try:
            payload = jwt.decode(token, config.JWT_TOKEN, algorithms=["HS256"])
            request.state.current_user = payload
        except InvalidTokenError as exc:
            raise NotAuthorizedError(
                message="Token is not valid. Please login again.",
                source="GatewayService verifyAuthToken() method invalid session error"
            ) from exc

        response: Response = await call_next(request)
        return response


def check_user(request: Request):
    """
    Dependency function to verify the user was authenticated by middleware.
    """
    if not hasattr(request.state, "current_user"):
        raise BadRequestError(
            message="Authentication is required to access this route.",
            source="GatewayService checkAuthentication() method error"
        )
