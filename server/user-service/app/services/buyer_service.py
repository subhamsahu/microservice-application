"""
Module for buyer-related operations.
"""
from typing import Optional, Dict, Any
from bson import ObjectId

from app.core.exceptions import DocumentNotFound
from app.models.buyer import Buyer
from app.schemas.buyer import BuyerUpdate
from app.core.logger import logger


class BuyerService:
    """Service class for buyer-related operations."""

    @staticmethod
    async def get_buyer_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get buyer by email."""
        buyer = await Buyer.get_by_email(email)
        logger.info(f"Retrieved buyer by email {email}: {buyer.model_dump() if buyer else None}")
        if buyer is None:
            raise DocumentNotFound("Buyer with the specified email not found.")
        return buyer.model_dump()

    @staticmethod
    async def get_buyer_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Get buyer by username."""
        buyer = await Buyer.get_by_username(username)
        logger.info(f"Retrieved buyer by email {username}: {buyer.model_dump() if buyer else None}")
        if buyer is None:
            raise DocumentNotFound("Buyer with the specified email not found.")
        return buyer.model_dump()

    @staticmethod
    async def update_buyer(buyer_id: str, buyer_data: BuyerUpdate) -> Optional[Dict[str, Any]]:
        """Update buyer by id with provided data. Returns updated document or None."""
        try:
            obj_id = ObjectId(buyer_id)
        except Exception:
            return None

        buyer = await Buyer.get(obj_id)
        if not buyer:
            raise DocumentNotFound("Buyer with the specified ID not found.")

        # Update only provided fields
        update_data = buyer_data.model_dump(exclude_unset=True, by_alias=True)
        for field, value in update_data.items():
            setattr(buyer, field, value)

        await buyer.save()
        return buyer.model_dump()
    
    @staticmethod
    async def create_buyer_from_auth(user_data: dict) -> dict:
        """Create buyer from auth service data."""
        buyer = Buyer(
            username=user_data.get("username"),
            email=user_data.get("email"),
            profile_picture=user_data.get("profile_picture") or "",
            country=user_data.get("country") or "",
            is_seller=False
        )
        await buyer.save()
        logger.info(f"Buyer created from auth service: {buyer.model_dump()}")
        return buyer.model_dump()
