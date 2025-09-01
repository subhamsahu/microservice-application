"""
This module contains the router for the auth API.
"""
from typing import List
from fastapi import APIRouter, status, Path

from app.services.seller_service import SellerService
from app.schemas.seller import SellerCreate, SellerUpdate, SellerResponse
from app.core.logger import logger

router = APIRouter()


@router.get(
    "/id/{seller_id}",
    status_code=status.HTTP_200_OK,
    response_description="Seller Email API",
    response_model=SellerResponse,
    tags=["Seller"],
    operation_id="user_seller_by_id_v1"
)
async def get_seller_by_id(seller_id: str):
    """Get seller by ID."""
    seller = await SellerService.get_seller_by_id(seller_id)
    return seller


@router.get(
    "/username/{username}",
    status_code=status.HTTP_200_OK,
    response_description="Seller get by username API",
    response_model=SellerResponse,
    tags=["Seller"],
    operation_id="user_seller_by_username_v1"
)
async def get_seller_by_username(username: str):
    """Get seller by username."""
    seller = await SellerService.get_seller_by_username(username)
    return seller


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_description="Create Seller API",
    response_model=SellerResponse,
    tags=["Seller"],
    operation_id="user_create_seller_v1"
)
async def create_seller(
    seller_data: SellerCreate
):
    """Create a new seller profile."""
    logger.info(f"Creating seller with data: {seller_data}")
    seller = await SellerService.create_seller(seller_data)
    return seller


@router.put(
    "/{seller_id}",
    status_code=status.HTTP_200_OK,
    response_description="Update Seller API",
    response_model=SellerResponse,
    tags=["Seller"],
    operation_id="user_update_seller_v1")
async def update_seller(
    seller_id: str,
    seller_data: SellerUpdate,
):
    """Update seller profile."""
    logger.info(f"Updating seller {seller_id} with data: {seller_data}")
    seller = await SellerService.update_seller(seller_id, seller_data)
    return seller


@router.post(
    "/seed/{count}",
    status_code=status.HTTP_200_OK,
    response_description="Seed Seller API",
    response_model=List[SellerResponse],
    tags=["Seller"],
    operation_id="user_createseller_v1"
)
async def seed_sellers(
    count: int = Path(..., ge=1, le=100)
):
    """Seed random seller profiles for testing."""
    sellers = await SellerService.seed_sellers(count)

    return sellers
