"""
This module contains the router for the health API.
"""
from fastapi import APIRouter, status

from app.core.logger import logger

from app.core.exceptions import AppException
from app.core.constants import SERVICE_NAME

router = APIRouter()

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_description="Health Check API",
    tags=["Health"]
)
async def check_health():
    """
    Health check endpoint to verify the service is running.
    """
    try:
        logger.info(f"{SERVICE_NAME}: check_health() method called")
        return {
            "health_status": "healthy",
            "message": f"{SERVICE_NAME} is running smoothly."
        }
    except AppException as e:
        logger.error(f"{SERVICE_NAME}: check_health() error method: {e}")
        return {
            "error": str(e)
        }
