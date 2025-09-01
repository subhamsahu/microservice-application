"""
This module contains the router for the auth API.
"""
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.services.buyer_service import BuyerService
from app.schemas.buyer import BuyerResponse, BuyerUpdate
from app.core.middlewares import get_current_user

router = APIRouter()

@router.get(
    "/email",
    status_code=status.HTTP_200_OK,
    response_model=BuyerResponse,
    response_description="Buyer Email API",
    tags=["Buyer"],
    operation_id="user_buyer_by_email_v1"
)
async def user_buyer_by_email_handler(
    current_user: dict = Depends(get_current_user)
):
    """
    User signup endpoint to register a new user.
    """
    buyer = await BuyerService.get_buyer_by_email(current_user["email"])
    return buyer


@router.get(
    "/username",
    status_code=status.HTTP_200_OK,
    response_description="Buyer Username API",
    response_model=BuyerResponse,
    tags=["Buyer"],
    operation_id="user_buyer_by_username_v1"
)
async def user_buyer_by_username_handler(
    current_user: dict = Depends(get_current_user)
):
    """
    User signup endpoint to register a new user.
    """
    buyer = await BuyerService.get_buyer_by_username(current_user["username"])
    return buyer


@router.get(
    "/username/{username}",
    status_code=status.HTTP_200_OK,
    response_description="Buyer Get by Username API",
    response_model=BuyerResponse,
    tags=["Buyer"],
    operation_id="user_buyer_by_username_v1"
)
async def user_get_buyer_by_username_handler(
    username: str,
):
    """Get buyer by username."""
    buyer = await BuyerService.get_buyer_by_username(username)
    return buyer

@router.put(
    "/{buyer_id}",
    status_code=status.HTTP_200_OK,
    response_description="Update Buyer API",
    response_model=BuyerResponse,
    tags=["Buyer"],
    operation_id="user_buyer_update_v1"
)
async def user_update_buyer_handler(
    buyer_id: str,
    payload: BuyerUpdate,
):
    """Update buyer profile by id."""
    updated = await BuyerService.update_buyer(buyer_id, payload)
    return updated
