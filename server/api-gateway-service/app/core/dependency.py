from typing import Any, List, Union

from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from app.utils.security import decode_token
from app.core.logger import logger
from app.core.exceptions import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
)

class TokenBearer(HTTPBearer):
    """
    Token bearer class
    """
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        logger.info(f"Token: {token}")
        token_data = decode_token(token)

        if not self.token_valid(token):
            raise InvalidToken()

        # if await token_in_blocklist(token_data["jti"]):
        #     raise InvalidToken()

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)

        return token_data is not None

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    """
    Access token bearer class
    """
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    """
    Refresh token bearer class
    """
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
    request: Request,
    token_details: dict = Depends(AccessTokenBearer()),
):
    """
    Get current user from token and attach to request.state.
    """
    user_data = token_details["user"]  # contains email, id, roles, etc.

    # Attach to request state for access in proxy_handler
    request.state.user = user_data

    return user_data


