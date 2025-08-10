"""
This module contains the router for the users API.
"""
from uuid import UUID
from fastapi import APIRouter, status, Depends, Query
from fastapi.responses import JSONResponse

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.logger import logger
from app.services.user_service import UserService
from app.schemas.signup import UserOutSchema

router = APIRouter()


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    response_description="List Users API",
    response_model=list[UserOutSchema],
    operation_id="auth_signin_v1"
)
async def auth_list_users_handler(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_service: UserService = Depends()
) -> JSONResponse:
    """
    User signin endpoint to register a new user.
    """
    users = await user_service.list_users(limit, offset)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=users
    )


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserOutSchema,
    operation_id="auth_get_user_by_id"
)
async def auth_get_user_by_id_handler(
    user_id: UUID,
    user_service: UserService = Depends()
):
    """
    User signin endpoint to register a new user.
    """
    user = await user_service.get_user_by_id(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=user
    )

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    operation_id="auth_delete_user_by_id"
)
async def auth_delete_user_by_id_handler(
    user_id: UUID,
    user_service: UserService = Depends()
):
    """
    User signin endpoint to register a new user.
    """
    success = await user_service.delete_user(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": success,
        }
    )
