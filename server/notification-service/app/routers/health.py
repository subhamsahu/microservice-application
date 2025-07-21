"""
This module contains the router for the health API.
"""
from fastapi import APIRouter, status

from server_shared.logger import Logger

from app.core.exceptions import AppException

router = APIRouter()
logger = Logger()

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
        logger.info("Notification Service: check_health() method called")
        return {
            "health_status": "healthy",
            "message": "Notification Service is running smoothly."
        }
    except AppException as e:
        logger.error(f"Notification Service: check_health() error method: {e}")
        return {
            "error": str(e)
        }
